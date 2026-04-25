#!/usr/bin/env python3
"""PostToolUse(Read): registra lecturas en .claude/session-reads.log.
   Insumo para session-consolidate — actualiza last_referenced de lessons."""
import json, sys, os
from datetime import datetime, timezone

LOG_PATH = ".claude/session-reads.log"


def main():
    event = json.load(sys.stdin)
    file_path = event.get("tool_input", {}).get("file_path", "")
    if not file_path:
        sys.exit(0)

    try:
        log_dir = os.path.dirname(LOG_PATH)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        timestamp = datetime.now(timezone.utc).isoformat()
        session_id = event.get("session_id", "unknown")
        with open(LOG_PATH, "a") as f:
            f.write(f"{timestamp} session={session_id} path={file_path}\n")
    except Exception:
        pass  # Logging is non-critical — never block on it

    sys.exit(0)


if __name__ == "__main__":
    main()
