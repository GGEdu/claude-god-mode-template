#!/usr/bin/env python3
"""PostToolUse(Read): registra lecturas en .claude/session-reads.log.

USA-6 NOTA: hoy este logger genera el archivo pero su consumidor
canónico (`session-consolidate.sh` actualizando `last_referenced` de
lessons) NO está implementado. El log se acumula sin que nada lo
parsee periódicamente.

Razones para mantener el logger activo a pesar de eso:
1. Es overhead trivial (una línea por Read).
2. Cuando session-consolidate.sh implemente parsing, los logs
   históricos serán insumo inmediato sin migración.
3. El log es útil para debugging de sesiones (¿qué leyó Claude?).

Para activar el consumidor:
- Editar .claude/hooks/session-consolidate.sh para parsear este log
  y actualizar lessons/_index.yaml -> last_referenced.
- Ver Sintesis.md §1.8 (enforcement de last_referenced).
"""
import json, sys, os
from datetime import datetime, timezone

LOG_PATH = ".claude/session-reads.log"
MAX_LOG_LINES = 5000  # rotación si excede


def maybe_rotate(path: str):
    try:
        if os.path.exists(path):
            with open(path) as f:
                lines = f.readlines()
            if len(lines) > MAX_LOG_LINES:
                tail = lines[-MAX_LOG_LINES // 2:]
                with open(path, "w") as f:
                    f.writelines(tail)
    except Exception:
        pass


def main():
    event = json.load(sys.stdin)
    file_path = event.get("tool_input", {}).get("file_path", "")
    if not file_path:
        sys.exit(0)

    try:
        log_dir = os.path.dirname(LOG_PATH)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        maybe_rotate(LOG_PATH)
        timestamp = datetime.now(timezone.utc).isoformat()
        session_id = event.get("session_id", "unknown")
        with open(LOG_PATH, "a") as f:
            f.write(f"{timestamp} session={session_id} path={file_path}\n")
    except Exception:
        pass

    sys.exit(0)


if __name__ == "__main__":
    main()
