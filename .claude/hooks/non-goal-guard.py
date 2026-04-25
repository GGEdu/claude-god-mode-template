#!/usr/bin/env python3
"""PostToolUse(Write/Edit): detecta writes a paths de non_goals en PLAN.md.
   Bloquea + rollback si el archivo escrito coincide con un non_goal glob (Sintesis.md §2.5).

   HIGH-3 fix: usa yaml.safe_load para parser robusto.
   HIGH-4 fix: rollback real (git checkout o rm) tras detectar match."""
import json, sys, os, fnmatch, subprocess
from datetime import datetime, timezone

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

PLAN_LOCATIONS = [".claude/plans/PLAN.md", "PLAN.md"]
LOG_PATH = ".claude/memory/plan-drift.log"


def find_plan() -> str | None:
    for loc in PLAN_LOCATIONS:
        if os.path.exists(loc):
            return loc
    return None


def extract_yaml_block(content: str) -> str | None:
    """PLAN.md mezcla markdown con bloques YAML. Extrae el bloque YAML
    que contiene el campo non_goals.

    Soporta dos formatos:
    1. Frontmatter ``---\n...\n---``
    2. Code fence ```yaml ... ```
    3. YAML inline (todo el archivo es YAML)
    """
    if "non_goals" not in content:
        return None

    if content.lstrip().startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            return parts[1]

    lines = content.split("\n")
    in_yaml = False
    block = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```yaml") or stripped.startswith("```yml"):
            in_yaml = True
            continue
        if in_yaml and stripped == "```":
            joined = "\n".join(block)
            if "non_goals" in joined:
                return joined
            block = []
            in_yaml = False
            continue
        if in_yaml:
            block.append(line)

    if "non_goals:" in content and ":" in content:
        return content
    return None


def parse_non_goals(plan_path: str) -> list[dict]:
    """Extrae non_goals usando yaml.safe_load si está disponible, fallback a parser
    manual robusto."""
    try:
        with open(plan_path) as f:
            content = f.read()
    except Exception:
        return []

    if HAS_YAML:
        block = extract_yaml_block(content)
        if block:
            try:
                data = yaml.safe_load(block)
                if isinstance(data, dict) and isinstance(data.get("non_goals"), list):
                    return [
                        {"pattern": str(ng.get("pattern", "")), "reason": str(ng.get("reason", ""))}
                        for ng in data["non_goals"]
                        if isinstance(ng, dict) and ng.get("pattern")
                    ]
            except yaml.YAMLError:
                pass

    return _parse_non_goals_fallback(content)


def _parse_non_goals_fallback(content: str) -> list[dict]:
    """Parser legacy basado en startswith. Solo se usa si pyyaml falla.
    Más permisivo: ignora orden pattern/reason y comentarios inline."""
    non_goals = []
    in_ng = False
    current = {}
    for line in content.split("\n"):
        line_no_comment = line.split("#", 1)[0]
        stripped = line_no_comment.strip()
        if stripped == "non_goals:":
            in_ng = True
            continue
        if in_ng:
            if stripped.startswith("- "):
                if current.get("pattern"):
                    non_goals.append(current)
                current = {}
                stripped = stripped[2:].strip()
            if stripped.startswith("pattern:"):
                current["pattern"] = stripped.split(":", 1)[1].strip().strip("\"'")
            elif stripped.startswith("reason:"):
                current["reason"] = stripped.split(":", 1)[1].strip().strip("\"'")
            elif stripped and not line_no_comment.startswith(" ") and ":" in stripped:
                if current.get("pattern"):
                    non_goals.append(current)
                in_ng = False
                current = {}
    if current.get("pattern"):
        non_goals.append(current)
    return non_goals


def log_event(file_path: str, msg: str, action: str = "BLOCK"):
    try:
        os.makedirs(".claude/memory", exist_ok=True)
        timestamp = datetime.now(timezone.utc).isoformat()
        with open(LOG_PATH, "a") as f:
            f.write(f"{timestamp} | {action} | {file_path} | {msg}\n")
    except Exception:
        pass


def file_was_tracked(file_path: str) -> bool:
    """¿El archivo existía en git antes del write actual?"""
    try:
        result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", file_path],
            capture_output=True, timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def rollback(file_path: str) -> tuple[bool, str]:
    """Intenta deshacer el write. Si el archivo estaba en git → git checkout.
    Si era nuevo → eliminar."""
    if not os.path.exists(file_path):
        return True, "archivo ya no existe"
    try:
        if file_was_tracked(file_path):
            r = subprocess.run(
                ["git", "checkout", "--", file_path],
                capture_output=True, text=True, timeout=5
            )
            if r.returncode == 0:
                return True, "git checkout OK"
            return False, f"git checkout falló: {r.stderr.strip()[:100]}"
        else:
            os.remove(file_path)
            return True, "archivo nuevo eliminado (no estaba en git)"
    except Exception as e:
        return False, f"rollback falló: {e}"


def main():
    event = json.load(sys.stdin)
    file_path = event.get("tool_input", {}).get("file_path", "")

    if not file_path:
        json.dump({"decision": "allow"}, sys.stdout)
        sys.exit(0)

    plan_path = find_plan()
    if not plan_path:
        json.dump({"decision": "allow", "reason": "Sin PLAN.md — sin non_goals que verificar"}, sys.stdout)
        sys.exit(0)

    non_goals = parse_non_goals(plan_path)
    if not non_goals:
        json.dump({"decision": "allow", "reason": "Sin non_goals definidos en el plan"}, sys.stdout)
        sys.exit(0)

    for ng in non_goals:
        if fnmatch.fnmatch(file_path, ng["pattern"]):
            ok, rb_msg = rollback(file_path)
            action = "BLOCK_ROLLBACK_OK" if ok else "BLOCK_ROLLBACK_FAIL"
            msg = (
                f"NON-GOAL VIOLADO: '{file_path}' coincide con patrón '{ng['pattern']}' "
                f"({ng['reason']}). Rollback: {rb_msg}."
            )
            log_event(file_path, msg, action)
            json.dump({"decision": "block", "reason": msg}, sys.stdout)
            sys.exit(1)

    json.dump({
        "decision": "allow",
        "reason": f"{file_path} no coincide con ningún non_goal ({len(non_goals)} verificados)"
    }, sys.stdout)
    sys.exit(0)


if __name__ == "__main__":
    main()
