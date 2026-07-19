#!/usr/bin/env python3
"""GATE-2: Bloquea escritura de código fuente si no existe PLAN.md válido.
   Implementa FAST_PATH bypass para tareas triviales (Sintesis.md §2.1).

   USA-4: actualiza .claude/state.yaml en cada transición (§2.6)."""
import json, sys, os, fnmatch, subprocess

# Importa helpers de state machine si están disponibles
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _paths import transition_state
    HAS_STATE = True
except ImportError:
    HAS_STATE = False
    def transition_state(*args, **kwargs):
        return {}

WHITELIST = [
    "PLAN.md", "PLAN.v*.md", "RESEARCH.md", "VERIFICATION.md",
    "REVIEW.md", "SECURITY.md",
    "**/PLAN.md", "**/PLAN.v*.md", "**/RESEARCH.md", "**/VERIFICATION.md",
    "**/REVIEW.md", "**/SECURITY.md",
    ".claude/memory/**", "docs/src/wiki/**", "**/*.log", "**/*.yaml", "**/*.yml",
    ".claude/hooks/**", ".claude/plans/**", ".claude/commands/**",
    ".gitignore", "**/.gitkeep", "**/.gitignore",
]

PLAN_REQUIRED_FIELDS = ["plan_id", "files_affected", "acceptance_criteria"]
PLAN_LOCATIONS = [".claude/plans/PLAN.md", "PLAN.md"]
# NEW-HIGH-10: cubre tanto archivos en directorios sensibles como archivos
# con nombres sensibles (ej. src/auth.ts no estaba siendo flag).
SENSITIVE_PATTERNS = [
    # Directorios sensibles
    "**/auth/**", "**/security/**", "**/payment*/**", "**/admin/**",
    "**/secrets/**", "**/credentials/**", "**/billing/**",
    # Archivos por nombre (cualquier ubicación)
    "**/auth.*", "**/auth-*.*", "**/*-auth.*",
    "**/security.*", "**/payment*.*",
    "**/login.*", "**/oauth*.*", "**/jwt.*",
    "**/credentials.*", "**/secrets.*",
]

FAST_PATH_MAX_FILES = 3
FAST_PATH_MAX_LINES = 50


def is_whitelisted(file_path: str) -> bool:
    return any(fnmatch.fnmatch(file_path, pattern) for pattern in WHITELIST)


def find_plan() -> str | None:
    for loc in PLAN_LOCATIONS:
        if os.path.exists(loc):
            return loc
    return None


def plan_is_valid(plan_path: str) -> tuple[bool, str]:
    with open(plan_path) as f:
        content = f.read()
    missing = [field for field in PLAN_REQUIRED_FIELDS if field not in content]
    if missing:
        return False, f"PLAN.md incompleto. Faltan: {', '.join(missing)}"
    return True, ""


def is_sensitive(file_path: str) -> bool:
    return any(fnmatch.fnmatch(file_path, p) for p in SENSITIVE_PATTERNS)


def _estimate_pending_change(event: dict) -> tuple[int, int]:
    """Tamaño del write/edit propuesto en ESTE tool call. PreToolUse corre
    antes de que el archivo toque disco, así que git diff nunca lo ve (P4-1:
    Sintesis-errores.md). Sin esto, la primera escritura de la sesión —diff
    acumulado vacío— siempre caía en FAST_PATH sin importar su tamaño real."""
    tool_input = event.get("tool_input", {})
    tool_name = event.get("tool_name", "")
    if tool_name == "Write":
        content = tool_input.get("content", "") or ""
        return 1, (content.count("\n") + 1) if content else 0
    if tool_name == "Edit":
        old = tool_input.get("old_string", "") or ""
        new = tool_input.get("new_string", "") or ""
        return 1, abs(new.count("\n") - old.count("\n")) + 1
    return 1, 0


def is_trivial_change(event: dict | None = None) -> bool:
    file_count = 0
    total_lines = 0
    try:
        diff = subprocess.run(
            ["git", "diff", "--cached", "--stat", "--stat-count=100"],
            capture_output=True, text=True, timeout=5
        )
        if diff.returncode != 0:
            diff = subprocess.run(
                ["git", "diff", "--stat", "--stat-count=100"],
                capture_output=True, text=True, timeout=5
            )
        lines = [l for l in diff.stdout.strip().split("\n") if l.strip()]
        if lines:
            file_count = len(lines) - 1 if len(lines) > 1 else len(lines)
            summary = lines[-1]
            for part in summary.split(","):
                part = part.strip()
                if "insertion" in part or "deletion" in part:
                    try:
                        total_lines += int(part.split()[0])
                    except (ValueError, IndexError):
                        pass
    except Exception:
        return False  # fail-closed: sin certeza sobre el tamaño, exigir PLAN.md

    if event is not None:
        cur_files, cur_lines = _estimate_pending_change(event)
        file_count += cur_files
        total_lines += cur_lines

    return file_count <= FAST_PATH_MAX_FILES and total_lines <= FAST_PATH_MAX_LINES


def main():
    event = json.load(sys.stdin)
    file_path = event.get("tool_input", {}).get("file_path", "")

    if is_whitelisted(file_path):
        json.dump({"decision": "allow", "reason": "Archivo de metadatos (whitelist)"}, sys.stdout)
        sys.exit(0)

    plan_path = find_plan()

    if plan_path:
        valid, reason = plan_is_valid(plan_path)
        if not valid:
            json.dump({"decision": "block", "reason": reason}, sys.stdout)
            sys.exit(1)
        # GATE-2 pasado: PLAN existe y es válido → transicionar a EXECUTE
        transition_state("EXECUTE", gate_passed="GATE-2", extra={"plan_path": plan_path})
        json.dump({"decision": "allow", "reason": f"PLAN.md válido ({plan_path})"}, sys.stdout)
        sys.exit(0)

    if is_sensitive(file_path):
        json.dump({"decision": "block",
                   "reason": f"Archivo sensible ({file_path}) requiere PLAN.md. No FAST_PATH para auth/security/payments."}, sys.stdout)
        sys.exit(1)

    if is_trivial_change(event):
        # FAST_PATH: cambio trivial sin PLAN — transicionar a FAST_PATH
        transition_state("FAST_PATH", extra={"mode": "fast_path"})
        json.dump({"decision": "allow",
                   "reason": "FAST_PATH: cambio trivial (≤3 archivos, ≤50 líneas, no sensible)"}, sys.stdout)
        sys.exit(0)

    json.dump({"decision": "block",
               "reason": "Cambio no trivial sin PLAN.md. Ejecuta EXPLORE → PLAN primero."}, sys.stdout)
    sys.exit(1)


if __name__ == "__main__":
    main()
