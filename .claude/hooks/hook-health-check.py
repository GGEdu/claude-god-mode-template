#!/usr/bin/env python3
"""PreToolUse: inicializa state.yaml al inicio de sesión y hace dry-run de todos los hooks.
   Ejecuta solo una vez por sesión usando session_id derivado del PID de la sesión (Sintesis.md §10.3)."""
import json, sys, os, subprocess, time
from datetime import datetime, timezone

# P4-2 fix (Sintesis-errores.md): comparte el lock best-effort de _paths.py
# con los demás hooks que tocan state.yaml (plan-gate, tdd-gate, commit-checklist)
# para reducir la ventana de race condition. No requiere pyyaml.
try:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from _paths import StateLock
except ImportError:
    class StateLock:
        def __enter__(self): return self
        def __exit__(self, *exc_info): return False

STATE_PATH = ".claude/state.yaml"
HEALTH_LOG = ".claude/memory/hook-health.log"
HOOKS_DIR = ".claude/hooks"
FIXTURE_DIR = ".claude/hooks/fixtures"

HOOKS_TO_CHECK = [
    {"name": "plan-gate", "script": "plan-gate.py", "fixture": "fixture-write-code.json"},
    {"name": "tdd-gate", "script": "tdd-gate.py", "fixture": "fixture-write-code.json"},
    {"name": "commit-checklist", "script": "commit-checklist.py", "fixture": None},
    {"name": "non-goal-guard", "script": "non-goal-guard.py", "fixture": "fixture-write-code.json"},
    {"name": "plan-drift-detector", "script": "plan-drift-detector.py", "fixture": "fixture-write-code.json"},
    {"name": "session-read-logger", "script": "session-read-logger.py", "fixture": None},
]

INITIAL_STATE = """\
session_id: "{session_id}"
current_state: "EXPLORE"
mode: "full_path"
plan_path: null
replan_count: 0
last_gate_passed: null
last_updated: "{timestamp}"
blocked_since: null
last_health_check: "{timestamp}"
error_log: []
workflow_active: null
workflow_step: 0
"""


def get_session_id() -> str:
    """Deriva un session_id estable basado en el PPID (padre = proceso Claude Code)."""
    try:
        return f"sess-{os.getppid()}"
    except Exception:
        return f"sess-{int(time.time())}"


def read_state() -> dict:
    if not os.path.exists(STATE_PATH):
        return {}
    try:
        state = {}
        with open(STATE_PATH) as f:
            for line in f:
                line = line.strip()
                if ":" in line and not line.startswith("#"):
                    key, _, val = line.partition(":")
                    state[key.strip()] = val.strip().strip('"')
        return state
    except Exception:
        return {}


def _atomic_write(content: str):
    """Escritura atómica (tmp + os.replace) — P4-2 fix, mismo mecanismo que
    _paths.py save_state() para que un lector nunca vea el archivo truncado."""
    os.makedirs(".claude", exist_ok=True)
    tmp_path = f"{STATE_PATH}.tmp.{os.getpid()}"
    with open(tmp_path, "w") as f:
        f.write(content)
    os.replace(tmp_path, STATE_PATH)


def write_state(session_id: str, timestamp: str):
    content = INITIAL_STATE.format(session_id=session_id, timestamp=timestamp)
    with StateLock():
        _atomic_write(content)


def update_health_check_timestamp(session_id: str, timestamp: str):
    """Actualiza solo last_health_check y session_id en el state.yaml existente."""
    try:
        with StateLock():
            with open(STATE_PATH) as f:
                lines = f.readlines()
            new_lines = []
            for line in lines:
                if line.startswith("last_health_check:"):
                    new_lines.append(f'last_health_check: "{timestamp}"\n')
                elif line.startswith("session_id:"):
                    new_lines.append(f'session_id: "{session_id}"\n')
                else:
                    new_lines.append(line)
            _atomic_write("".join(new_lines))
    except Exception:
        pass


def log_health(msg: str):
    try:
        os.makedirs(".claude/memory", exist_ok=True)
        timestamp = datetime.now(timezone.utc).isoformat()
        with open(HEALTH_LOG, "a") as f:
            f.write(f"{timestamp} | {msg}\n")
    except Exception:
        pass


def dry_run_hook(hook_info: dict) -> dict:
    """Ejecuta un hook con fixture de test. Retorna {'name': ..., 'status': pass|fail|skip}."""
    name = hook_info["name"]
    script = os.path.join(HOOKS_DIR, hook_info["script"])
    fixture_file = hook_info["fixture"]

    if not os.path.exists(script):
        return {"name": name, "status": "skip", "reason": f"Script no encontrado: {script}"}

    if fixture_file is None:
        return {"name": name, "status": "skip", "reason": "Sin fixture definido para dry-run"}

    fixture_path = os.path.join(FIXTURE_DIR, fixture_file)
    if not os.path.exists(fixture_path):
        return {"name": name, "status": "skip", "reason": f"Fixture no encontrado: {fixture_path}"}

    try:
        with open(fixture_path) as f:
            fixture_data = f.read()

        result = subprocess.run(
            ["python3", script],
            input=fixture_data,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode in (0, 1):
            try:
                output = json.loads(result.stdout)
                decision = output.get("decision", "unknown")
                return {"name": name, "status": "pass", "decision": decision}
            except json.JSONDecodeError:
                return {"name": name, "status": "fail", "reason": f"Output inválido: {result.stdout[:100]}"}
        else:
            return {"name": name, "status": "fail", "reason": f"Exit {result.returncode}: {result.stderr[:100]}"}

    except subprocess.TimeoutExpired:
        return {"name": name, "status": "fail", "reason": "Timeout (10s) — hook no responde"}
    except Exception as e:
        return {"name": name, "status": "fail", "reason": str(e)}


def main():
    event = json.load(sys.stdin)

    session_id = get_session_id()
    timestamp = datetime.now(timezone.utc).isoformat()

    state = read_state()
    stored_session = state.get("session_id", "")

    # Si ya corrimos este chequeo en esta sesión → skip
    if stored_session == session_id and state.get("last_health_check"):
        json.dump({"decision": "allow", "reason": "Health check ya ejecutado esta sesión"}, sys.stdout)
        sys.exit(0)

    # Primera ejecución de la sesión: inicializar o resetear state.yaml
    if not os.path.exists(STATE_PATH) or stored_session != session_id:
        write_state(session_id, timestamp)
        log_health(f"STATE INIT | session={session_id} | estado=EXPLORE")
    else:
        update_health_check_timestamp(session_id, timestamp)

    # Dry-run de todos los hooks
    results = [dry_run_hook(h) for h in HOOKS_TO_CHECK]

    passed = [r for r in results if r["status"] == "pass"]
    failed = [r for r in results if r["status"] == "fail"]
    skipped = [r for r in results if r["status"] == "skip"]

    summary = f"Health check: {len(passed)} pass, {len(failed)} fail, {len(skipped)} skip"
    log_health(summary)

    for r in failed:
        log_health(f"HOOK FAIL | {r['name']} | {r.get('reason', 'sin detalle')}")

    if failed:
        warn_msg = f"⚠️  {len(failed)} hook(s) no operativo(s): {', '.join(r['name'] for r in failed)}. Gates degradados. Ver {HEALTH_LOG}"
        json.dump({"decision": "allow", "reason": warn_msg}, sys.stdout)
    else:
        json.dump({"decision": "allow", "reason": f"{summary} — todos los hooks OK"}, sys.stdout)

    sys.exit(0)


if __name__ == "__main__":
    main()
