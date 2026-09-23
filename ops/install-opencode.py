#!/usr/bin/env python3
"""Instala en opencode (global) lo generado por ops/adapters.py y las reglas.

- Agentes y comandos → ~/.config/opencode/{agents,commands}/. Solo escribe ficheros
  nuevos o que ya llevan la marca «generado desde claude-god-mode-template»; nunca
  pisa uno hecho a mano. Borra los generados cuyo original ya no existe.
- Reglas → clave `instructions` de ~/.config/opencode/opencode.json, apuntando a las
  copias instaladas en ~/.claude/rules/common (lista en ops/harness-rules.yaml).
- MCP: no se toca aquí; `ops/mcp.py diff` avisa si opencode se separa del catálogo.

Uso: install-opencode.py [--write] [--json]   (sin --write: solo muestra el plan)
Antes de modificar opencode.json deja una copia opencode.json.bak-<fecha>-catalogo.
"""
import argparse
import datetime
import json
import shutil
import sys
from pathlib import Path

import yaml

from catalog_lib import CATALOG, GLOBAL_DIR, emit

OPENCODE = Path.home() / ".config/opencode"
MARK = "generado desde claude-god-mode-template"


def plan_files() -> list[dict]:
    actions = []
    for kind in ("agents", "commands"):
        src_dir, dst_dir = CATALOG / "dist/opencode" / kind, OPENCODE / kind
        wanted = {p.name for p in src_dir.glob("*.md")}
        for src in sorted(src_dir.glob("*.md")):
            dst = dst_dir / src.name
            if dst.exists() and MARK not in dst.read_text(errors="replace"):
                actions.append({"action": "omitir", "path": str(dst), "why": "existe y no es generado"})
            elif not dst.exists() or dst.read_text() != src.read_text():
                actions.append({"action": "escribir", "path": str(dst), "src": str(src)})
        for dst in sorted(dst_dir.glob("*.md")) if dst_dir.is_dir() else []:
            if dst.name not in wanted and MARK in dst.read_text(errors="replace"):
                actions.append({"action": "borrar", "path": str(dst), "why": "su original ya no existe"})
    return actions


def plan_instructions() -> dict | None:
    rules = yaml.safe_load((CATALOG / "ops/harness-rules.yaml").read_text())["opencode"]["rules"]
    wanted = [str(GLOBAL_DIR / "rules/common" / r) for r in rules]
    missing = [w for w in wanted if not Path(w).is_file()]
    if missing:
        raise SystemExit(f"✗ faltan reglas instaladas (ejecuta make install): {missing}")
    config = json.loads((OPENCODE / "opencode.json").read_text())
    current = config.get("instructions") or []
    keep = [i for i in current if not i.startswith(str(GLOBAL_DIR / "rules/common"))]
    new = keep + wanted
    return None if new == current else {"action": "instructions", "from": len(current), "to": len(new), "value": new}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if not (CATALOG / "dist/opencode/agents").is_dir():
        print("✗ no hay dist/opencode: ejecuta `make adapters` primero", file=sys.stderr)
        return 1
    files, instr = plan_files(), plan_instructions()

    if a.write:
        for act in files:
            dst = Path(act["path"])
            if act["action"] == "escribir":
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(act["src"], dst)
            elif act["action"] == "borrar":
                dst.unlink()
        if instr:
            cfg_path = OPENCODE / "opencode.json"
            backup = cfg_path.with_name(f"opencode.json.bak-{datetime.date.today():%Y%m%d}-catalogo")
            if not backup.exists():
                shutil.copy2(cfg_path, backup)
            config = json.loads(cfg_path.read_text())
            config["instructions"] = instr["value"]
            cfg_path.write_text(json.dumps(config, ensure_ascii=False, indent=2) + "\n")

    counts: dict[str, int] = {}
    for act in files:
        counts[act["action"]] = counts.get(act["action"], 0) + 1
    data = {"write": a.write, "files": counts, "skipped": [x for x in files if x["action"] == "omitir"],
            "instructions": None if not instr else {"from": instr["from"], "to": instr["to"]}}

    def human(d):
        verb = "Hecho" if d["write"] else "Plan (añade --write para aplicar)"
        print(f"{verb}: ficheros {d['files'] or 'sin cambios'}; instructions "
              + (f"{d['instructions']['from']} → {d['instructions']['to']} reglas" if d["instructions"] else "sin cambios"))
        for s in d["skipped"]:
            print(f"  omitido {s['path']}: {s['why']}")
    emit(data, a.json, human)
    return 0


if __name__ == "__main__":
    sys.exit(main())
