#!/usr/bin/env python3
"""Genera las piezas no-skill del catálogo en el formato de cada harness.

Un original (formato Claude Code) → adaptadores generados, nunca editados a mano.
Plan: ops/plans/plan-catalogo-y-agent-deck-2026-09-23.md §2.

Hoy: opencode (agentes y comandos). freebuff lee las skills directamente; sus
agentes (.agents/*.ts) quedan pendientes: el modelo lo decide su servidor entre una
lista gratuita y no está verificado que ejecute agentes locales.

Uso: adapters.py [--harness opencode] [--out dist] [--json]
Formato de agente opencode verificado en su binario 1.18.31: frontmatter
description/mode/permission; el cuerpo es el prompt; campos desconocidos → options.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from catalog_lib import CATALOG, emit

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
MARK = "generado desde claude-god-mode-template"

# Herramientas de Claude → permiso de opencode que las gobierna.
OPENCODE_PERMISSION = {"edit": {"Write", "Edit", "MultiEdit", "NotebookEdit"},
                       "bash": {"Bash"}, "webfetch": {"WebFetch"}}


def commit() -> str:
    return subprocess.run(["git", "-C", str(CATALOG), "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip() or "sin-commit"


def split(path: Path) -> tuple[dict, str]:
    text = path.read_text()
    m = FRONTMATTER.match(text)
    return (yaml.safe_load(m.group(1)) or {}, text[m.end():]) if m else ({}, text)


def tools_of(fm: dict) -> set[str] | None:
    raw = fm.get("tools")
    if raw is None:
        return None  # sin lista = todas las herramientas
    items = raw if isinstance(raw, list) else re.split(r"[,\s]+", str(raw))
    return {t.strip().strip('"\'[]') for t in items if t.strip()}


def header(src: Path, sha: str) -> str:
    return f"<!-- {MARK}@{sha}:{src.relative_to(CATALOG)} — no editar; regenerar con `make adapters` -->\n"


def opencode_agent(src: Path, sha: str) -> str:
    fm, body = split(src)
    tools = tools_of(fm)
    permission = {}
    if tools is not None:
        permission = {perm: "deny" for perm, needs in OPENCODE_PERMISSION.items() if not needs & tools}
    out = {"description": " ".join(str(fm.get("description", "")).split()), "mode": "subagent"}
    if permission:
        out["permission"] = permission
    # `model` se omite a propósito: opencode usa el de la sesión (alias de LiteLLM),
    # y "sonnet"/"opus" de Claude no son nombres válidos allí.
    return ("---\n" + yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=1000)
            + "---\n" + header(src, sha) + body)


def opencode_command(src: Path, sha: str) -> str:
    fm, body = split(src)
    out = {"description": " ".join(str(fm.get("description", "")).split())}
    return ("---\n" + yaml.safe_dump(out, allow_unicode=True, sort_keys=False, width=1000)
            + "---\n" + header(src, sha) + body)


def build_opencode(out: Path) -> dict:
    sha = commit()
    root = out / "opencode"
    if root.exists():
        shutil.rmtree(root)
    written = []
    for kind, folder, render in (("agents", "agents", opencode_agent), ("commands", "commands", opencode_command)):
        (root / kind).mkdir(parents=True)
        for src in sorted((CATALOG / folder).glob("*.md")):
            dst = root / kind / src.name
            dst.write_text(render(src, sha))
            written.append(str(dst.relative_to(CATALOG)))
    rules = yaml.safe_load((CATALOG / "ops/harness-rules.yaml").read_text())["opencode"]
    (root / "instructions.json").write_text(json.dumps({"rules": rules["rules"]}, ensure_ascii=False, indent=2) + "\n")
    written.append(str((root / "instructions.json").relative_to(CATALOG)))
    return {"harness": "opencode", "commit": sha, "files": written}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--harness", choices=["opencode"], default="opencode")
    ap.add_argument("--out", default="dist")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    result = build_opencode(CATALOG / args.out)
    emit(result, args.json, lambda d: print(f"✓ {d['harness']}: {len(d['files'])} ficheros en {args.out}/{d['harness']} (@{d['commit']})"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
