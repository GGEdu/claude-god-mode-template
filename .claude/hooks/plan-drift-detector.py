#!/usr/bin/env python3
"""PostToolUse(Write/Edit): detecta archivos modificados que no están en files_affected del PLAN.md.
   Warning + log si el archivo no está declarado. Bloqueo si coincide con non_goals (Sintesis.md §10)."""
import json, sys, os, fnmatch
from datetime import datetime, timezone

PLAN_LOCATIONS = [".claude/plans/PLAN.md", "PLAN.md"]
LOG_PATH = ".claude/memory/plan-drift.log"

WHITELIST = [
    "**/PLAN.md", "**/PLAN.v*.md", "**/RESEARCH.md", "**/VERIFICATION.md",
    ".claude/memory/**", "docs/src/wiki/**", "**/*.log", "**/*.yaml",
    "**/REVIEW.md", "**/SECURITY.md", ".claude/hooks/**", ".claude/plans/**",
    ".gitignore", "**/.gitkeep", ".claude/state.yaml",
]


def is_whitelisted(file_path: str) -> bool:
    return any(fnmatch.fnmatch(file_path, p) for p in WHITELIST)


def find_plan() -> str | None:
    for loc in PLAN_LOCATIONS:
        if os.path.exists(loc):
            return loc
    return None


def parse_plan(plan_path: str) -> tuple[list[str], list[dict]]:
    """Extrae files_affected y non_goals del PLAN.md."""
    files_affected = []
    non_goals = []
    try:
        with open(plan_path) as f:
            content = f.read()

        in_files = False
        in_ng = False
        current_pattern = None

        for line in content.split("\n"):
            stripped = line.strip()

            if stripped == "files_affected:":
                in_files = True
                in_ng = False
                continue
            if stripped == "non_goals:":
                in_ng = True
                in_files = False
                continue

            if in_files:
                if stripped.startswith("- "):
                    files_affected.append(stripped[2:].strip().strip("\"'"))
                elif stripped and not line.startswith(" ") and not stripped.startswith("-"):
                    in_files = False

            if in_ng:
                if stripped.startswith("- pattern:"):
                    current_pattern = stripped.split("pattern:", 1)[1].strip().strip("\"'")
                elif stripped.startswith("reason:") and current_pattern:
                    reason = stripped.split("reason:", 1)[1].strip().strip("\"'")
                    non_goals.append({"pattern": current_pattern, "reason": reason})
                    current_pattern = None
                elif stripped and not line.startswith(" ") and not stripped.startswith("-"):
                    in_ng = False

    except Exception:
        pass
    return files_affected, non_goals


def log_event(file_path: str, msg: str, action: str = "WARN"):
    try:
        os.makedirs(".claude/memory", exist_ok=True)
        timestamp = datetime.now(timezone.utc).isoformat()
        with open(LOG_PATH, "a") as f:
            f.write(f"{timestamp} | {action} | {file_path} | {msg}\n")
    except Exception:
        pass


def matches_any(file_path: str, patterns: list[str]) -> bool:
    return any(fnmatch.fnmatch(file_path, p) for p in patterns)


def main():
    event = json.load(sys.stdin)
    file_path = event.get("tool_input", {}).get("file_path", "")

    if not file_path or is_whitelisted(file_path):
        json.dump({"decision": "allow"}, sys.stdout)
        sys.exit(0)

    plan_path = find_plan()
    if not plan_path:
        json.dump({"decision": "allow", "reason": "Sin PLAN.md — drift indetectable"}, sys.stdout)
        sys.exit(0)

    files_affected, non_goals = parse_plan(plan_path)

    # Non-goal check (block)
    for ng in non_goals:
        if fnmatch.fnmatch(file_path, ng["pattern"]):
            msg = (
                f"NON-GOAL VIOLADO (drift): '{file_path}' coincide con '{ng['pattern']}' "
                f"({ng['reason']}). Fuera de scope según PLAN.md."
            )
            log_event(file_path, msg, "BLOCK")
            json.dump({"decision": "block", "reason": msg}, sys.stdout)
            sys.exit(1)

    # files_affected check (warn)
    if files_affected and not matches_any(file_path, files_affected):
        msg = (
            f"PLAN DRIFT: '{file_path}' no está en files_affected del plan. "
            f"Archivos declarados: {len(files_affected)}. ¿Expandiendo scope sin RE-PLAN?"
        )
        log_event(file_path, msg, "WARN")
        json.dump({
            "decision": "allow",
            "reason": f"⚠️  {msg}"
        }, sys.stdout)
        sys.exit(0)

    json.dump({
        "decision": "allow",
        "reason": f"{file_path} está dentro del scope del plan ({len(files_affected)} archivos declarados)"
    }, sys.stdout)
    sys.exit(0)


if __name__ == "__main__":
    main()
