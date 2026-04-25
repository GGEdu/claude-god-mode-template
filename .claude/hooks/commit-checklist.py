#!/usr/bin/env python3
"""GATE-3: Verifica que existen tests con assertions antes de git commit (Sintesis.md §1.6).
   Loggea bypasses --no-verify para audit trail (HIGH-1)."""
import json, sys, os, glob, subprocess
from datetime import datetime, timezone

TEST_PATTERNS = [
    "tests/**/*.test.ts", "tests/**/*.spec.ts",
    "tests/**/*.test.py", "tests/**/*.spec.py",
    "tests/**/*.test.php", "tests/**/*.spec.php",
    "test/**/*.test.*", "spec/**/*.spec.*",
    "__tests__/**/*.test.*",
]
ASSERTION_KEYWORDS = ["assert", "expect(", "should", "it(", "test(", "describe(", "$this->assert", "->assert"]
BYPASS_LOG = ".claude/memory/commit-bypass.log"


def log_bypass(command: str, reason: str = "explicit --no-verify"):
    try:
        os.makedirs(".claude/memory", exist_ok=True)
        timestamp = datetime.now(timezone.utc).isoformat()
        with open(BYPASS_LOG, "a") as f:
            f.write(f"{timestamp} | BYPASS | {reason} | cmd={command[:200]}\n")
    except Exception:
        pass


def find_tests() -> list[str]:
    matches = []
    for pattern in TEST_PATTERNS:
        matches.extend(glob.glob(pattern, recursive=True))
    return matches


def has_assertions(test_files: list[str]) -> bool:
    for f in test_files[:15]:
        try:
            content = open(f).read().lower()
            if any(kw.lower() in content for kw in ASSERTION_KEYWORDS):
                return True
        except Exception:
            pass
    return False


def get_staged_files() -> list[str]:
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True, text=True, timeout=5
        )
        lines = result.stdout.strip().split("\n")
        return [l for l in lines if l.strip()]
    except Exception:
        return []


def main():
    event = json.load(sys.stdin)
    command = event.get("tool_input", {}).get("command", "")

    if not command.strip().startswith("git commit"):
        json.dump({"decision": "allow", "reason": "No es git commit"}, sys.stdout)
        sys.exit(0)

    if "--no-verify" in command:
        log_bypass(command)
        json.dump({
            "decision": "allow",
            "reason": "Bypass explícito --no-verify (registrado en .claude/memory/commit-bypass.log)"
        }, sys.stdout)
        sys.exit(0)

    staged = get_staged_files()
    if not staged:
        json.dump({"decision": "allow", "reason": "Sin archivos staged"}, sys.stdout)
        sys.exit(0)

    test_files = find_tests()
    if not test_files:
        json.dump({
            "decision": "block",
            "reason": "GATE-3: No se encontraron tests en el proyecto. Escribe tests antes de commitear (RED→GREEN→REFACTOR)."
        }, sys.stdout)
        sys.exit(1)

    if not has_assertions(test_files):
        json.dump({
            "decision": "block",
            "reason": f"GATE-3: {len(test_files)} archivos de test encontrados pero sin assertions detectadas. ¿Son tests reales?"
        }, sys.stdout)
        sys.exit(1)

    json.dump({
        "decision": "allow",
        "reason": f"GATE-3: {len(test_files)} archivos de test con assertions — OK para commitear."
    }, sys.stdout)
    sys.exit(0)


if __name__ == "__main__":
    main()
