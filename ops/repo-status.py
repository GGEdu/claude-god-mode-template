#!/usr/bin/env python3
"""Estado de las piezas aplicadas con ops/apply.py en un repo (lo lee agent-deck).

Estados por pieza (manifiesto .claude/.template-manifest.yaml → items):
  al-dia              igual que el catálogo
  catalogo-mas-nuevo  copia fijada y el catálogo ha cambiado → `apply.py` otra vez
  editado-localmente  la copia del repo ya no es la que se aplicó (alguien la tocó)
  enlace-roto         symlink que no apunta a nada (catálogo movido o pieza borrada)
  falta               el manifiesto la registra pero no está en el repo

Uso: repo-status.py <repo> [--json]    Exit 1 si algo no está al día.
"""
import argparse
import sys
from pathlib import Path

import yaml

from apply import MANIFEST, source_for
from catalog_lib import digest, emit


def status_of(repo: Path, item: dict) -> str:
    dst = repo / item["path"]
    if dst.is_symlink() and not dst.exists():
        return "enlace-roto"
    if not dst.exists():
        return "falta"
    if item["mode"] == "link":
        return "al-dia"
    if digest(dst) != item["sha256"]:
        return "editado-localmente"
    src, _ = source_for(item["harness"], item["type"], item["name"])
    return "al-dia" if src.exists() and digest(src) == item["sha256"] else "catalogo-mas-nuevo"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    repo = Path(a.repo).expanduser().resolve()
    path = repo / MANIFEST
    items = ((yaml.safe_load(path.read_text()) or {}).get("items") or []) if path.is_file() else []
    rows = [{**{k: i[k] for k in ("harness", "type", "name", "mode", "path")}, "status": status_of(repo, i)}
            for i in items]
    pending = sum(1 for r in rows if r["status"] != "al-dia")

    def human(d):
        for r in d["items"]:
            print(f"  {r['status']:<19} {r['harness']:<9} {r['type']}:{r['name']} ({r['mode']})")
        print(f"{d['pending']} pendiente(s)" if d["pending"] else f"OK: {len(d['items'])} pieza(s) al día")
    emit({"repo": str(repo), "pending": pending, "items": rows}, a.json, human)
    return 1 if pending else 0


if __name__ == "__main__":
    sys.exit(main())
