"""Utilidades compartidas por los comandos del catálogo (drift, collect, catalog, apply).

Rutas: el catálogo es la raíz de este repo; lo instalado es ~/.claude (o
$CLAUDE_GLOBAL_DIR). Ningún comando imprime nunca el contenido de un fichero.
"""
import hashlib
import json
import os
import sys
from pathlib import Path

import yaml

CATALOG = Path(__file__).resolve().parent.parent
GLOBAL_DIR = Path(os.environ.get("CLAUDE_GLOBAL_DIR", Path.home() / ".claude"))

# tipo → (carpeta en el catálogo, carpeta instalada, es directorio)
KINDS = {
    "skill": ("skills", "skills", True),
    "agent": ("agents", "agents", False),
    "rule": ("rules", "rules/common", False),
}
IGNORED_NAMES = {"__pycache__", ".DS_Store", "node_modules", ".git"}


def item_path(root: Path, kind: str, name: str) -> Path:
    folder = KINDS[kind][0] if root == CATALOG else KINDS[kind][1]
    return root / folder / (name if KINDS[kind][2] else f"{name}.md")


def list_names(root: Path, kind: str) -> set[str]:
    folder = root / (KINDS[kind][0] if root == CATALOG else KINDS[kind][1])
    if not folder.is_dir():
        return set()
    if KINDS[kind][2]:
        return {p.name for p in folder.iterdir() if (p / "SKILL.md").is_file()}
    return {p.stem for p in folder.glob("*.md")}


def files_of(path: Path) -> list[Path]:
    if path.is_file():
        return [path]
    return sorted(p for p in path.rglob("*")
                  if p.is_file() and not IGNORED_NAMES.intersection(p.relative_to(path).parts))


def digest(path: Path) -> str:
    """Huella estable de un fichero o de un directorio (rutas relativas + contenido)."""
    h = hashlib.sha256()
    base = path if path.is_dir() else path.parent
    for f in files_of(path):
        h.update(str(f.relative_to(base)).encode() + b"\0")
        h.update(hashlib.sha256(f.read_bytes()).digest())
    return h.hexdigest()


def load_global_install() -> dict:
    return yaml.safe_load((CATALOG / "ops/global-install.yaml").read_text()) or {}


def save_global_install(data: dict) -> None:
    path = CATALOG / "ops/global-install.yaml"
    lines = path.read_text().splitlines(keepends=True)
    header = "".join(l for l in lines[:next((i for i, l in enumerate(lines) if not l.startswith("#")), len(lines))])
    body = yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    path.write_text(header + body)


def external_names(kind: str) -> set[str]:
    ext = (load_global_install().get("external") or {}).get(f"{kind}s") or []
    return {e["name"] for e in ext}


def retired_names(kind: str) -> set[str]:
    ret = (load_global_install().get("retired") or {}).get(f"{kind}s") or []
    return {e["name"] for e in ret}


def changed_files(a: Path, b: Path) -> list[str]:
    """Rutas relativas que difieren entre dos versiones de una pieza (a = catálogo, b = instalada)."""
    if a.is_file() or b.is_file():
        return [a.name]
    fa = {str(f.relative_to(a)): hashlib.sha256(f.read_bytes()).digest() for f in files_of(a)}
    fb = {str(f.relative_to(b)): hashlib.sha256(f.read_bytes()).digest() for f in files_of(b)}
    out = []
    for rel in sorted(fa.keys() | fb.keys()):
        if rel not in fb:
            out.append(f"{rel} (falta instalado)")
        elif rel not in fa:
            out.append(f"{rel} (solo instalado)")
        elif fa[rel] != fb[rel]:
            out.append(rel)
    return out


def emit(data, as_json: bool, human) -> None:
    if as_json:
        json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
        sys.stdout.write("\n")
    else:
        human(data)
