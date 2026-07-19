"""Constantes compartidas para hooks de la state machine (Sintesis.md §2).

CONT-9 fix: centraliza paths y patrones para que plan-gate, non-goal-guard, etc.
no diverjan en su universo de archivos.

USA-4: añade helpers load_state() y save_state() para que los hooks
mantengan viva la state machine (Sintesis.md §2.6).

P4-2 fix (Sintesis-errores.md): save_state() escribe atómicamente (tmp +
os.replace) y transition_state() serializa su read-modify-write con un file
lock best-effort (_StateLock), para que hooks concurrentes no pisen state.yaml
entre sí ni un lector vea un archivo a medio escribir.
"""
import os
import time
from datetime import datetime, timezone
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False

PROJECT_ROOT = Path.cwd()

PLAN_LOCATIONS: list[str] = [
    ".claude/plans/PLAN.md",
    "PLAN.md",
]

STATE_PATH: str = ".claude/state.yaml"
STATE_LOCK_PATH: str = ".claude/state.yaml.lock"
STATE_LOCK_TIMEOUT_SECONDS: float = 3.0
SESSION_READS_LOG: str = ".claude/session-reads.log"
HOOK_HEALTH_LOG: str = ".claude/memory/hook-health.log"
PLAN_DRIFT_LOG: str = ".claude/memory/plan-drift.log"
COMMIT_BYPASS_LOG: str = ".claude/memory/commit-bypass.log"
LESSONS_DIR: str = ".claude/memory/lessons"
LESSONS_INDEX: str = ".claude/memory/lessons/_index.yaml"

META_WHITELIST: list[str] = [
    "PLAN.md", "PLAN.v*.md", "RESEARCH.md", "VERIFICATION.md",
    "REVIEW.md", "SECURITY.md",
    "**/PLAN.md", "**/PLAN.v*.md", "**/RESEARCH.md", "**/VERIFICATION.md",
    "**/REVIEW.md", "**/SECURITY.md",
    ".claude/memory/**", "docs/src/wiki/**",
    "**/*.log", "**/*.yaml", "**/*.yml",
    ".claude/hooks/**", ".claude/plans/**", ".claude/commands/**",
    ".gitignore", "**/.gitkeep", "**/.gitignore",
]

SENSITIVE_PATTERNS: list[str] = [
    "**/auth/**", "**/security/**", "**/payment*/**",
    "**/admin/**", "**/secrets/**", "**/credentials/**",
]

FAST_PATH_MAX_FILES: int = 3
FAST_PATH_MAX_LINES: int = 50

HOOK_TIMEOUT_SECONDS: int = 10
GIT_TIMEOUT_SECONDS: int = 5

PLAN_REQUIRED_FIELDS: list[str] = [
    "plan_id",
    "files_affected",
    "acceptance_criteria",
]

VALID_STATES: list[str] = [
    "INIT", "EXPLORE", "PLAN", "EXECUTE",
    "VERIFY", "DONE", "BLOCKED", "RE-PLAN", "FAST_PATH",
]


# ── State machine helpers (Sintesis.md §2.6) ────────────────────────────────

class StateLock:
    """File lock best-effort para serializar accesos concurrentes a state.yaml
    (P4-2 fix). Si fcntl no está disponible o no se consigue el lock a tiempo,
    sigue sin lock — los hooks no deben bloquear la sesión por esto, solo
    reducir la ventana de la race condition."""

    def __init__(self, timeout: float = STATE_LOCK_TIMEOUT_SECONDS):
        self.timeout = timeout
        self._fh = None

    def __enter__(self):
        if not HAS_FCNTL:
            return self
        try:
            lock_dir = os.path.dirname(STATE_LOCK_PATH) or "."
            os.makedirs(lock_dir, exist_ok=True)
            self._fh = open(STATE_LOCK_PATH, "w")
            deadline = time.monotonic() + self.timeout
            while True:
                try:
                    fcntl.flock(self._fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except OSError:
                    if time.monotonic() >= deadline:
                        break  # best-effort: seguimos sin el lock
                    time.sleep(0.05)
        except OSError:
            self._fh = None
        return self

    def __exit__(self, *exc_info):
        if self._fh is not None:
            try:
                fcntl.flock(self._fh, fcntl.LOCK_UN)
            except OSError:
                pass
            self._fh.close()
        return False


def load_state() -> dict:
    """Carga state.yaml. Devuelve dict con defaults si no existe o está corrupto."""
    defaults = {
        "session_id": "unknown",
        "current_state": "EXPLORE",
        "mode": "full_path",
        "plan_path": None,
        "replan_count": 0,
        "last_gate_passed": None,
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "blocked_since": None,
        "error_log": [],
        "workflow_active": None,
        "workflow_step": 0,
    }
    if not HAS_YAML or not os.path.exists(STATE_PATH):
        return defaults
    try:
        with open(STATE_PATH) as f:
            data = yaml.safe_load(f) or {}
        return {**defaults, **data}
    except Exception:
        return defaults


def save_state(state: dict) -> bool:
    """Persiste state.yaml atómicamente (tmp + os.replace, P4-2 fix) para que
    ningún lector concurrente vea un archivo a medio escribir. No falla —
    devuelve True si OK, False si error. Hooks no deben bloquear por fallo
    de persistencia."""
    if not HAS_YAML:
        return False
    try:
        state["last_updated"] = datetime.now(timezone.utc).isoformat()
        state_dir = os.path.dirname(STATE_PATH) or "."
        os.makedirs(state_dir, exist_ok=True)
        tmp_path = f"{STATE_PATH}.tmp.{os.getpid()}"
        with open(tmp_path, "w") as f:
            yaml.safe_dump(state, f, default_flow_style=False, sort_keys=False)
        os.replace(tmp_path, STATE_PATH)  # atómico en POSIX y Windows
        return True
    except Exception:
        return False


def transition_state(new_state: str, gate_passed: str | None = None,
                     extra: dict | None = None) -> dict:
    """Transiciona la state machine a un estado nuevo.

    Args:
        new_state: estado destino (debe estar en VALID_STATES).
        gate_passed: nombre del gate que validó la transición.
        extra: dict con campos adicionales para mergear (ej. plan_path).

    Returns:
        dict con el estado final (post-merge).
    """
    if new_state not in VALID_STATES:
        new_state = "EXPLORE"
    with StateLock():
        state = load_state()
        state["current_state"] = new_state
        if gate_passed:
            state["last_gate_passed"] = gate_passed
        if extra:
            state.update(extra)
        save_state(state)
    return state
