#!/usr/bin/env python3
"""Compara lo instalado en ~/.claude con el catálogo (skills, agentes, reglas).

Estados por pieza:
  igual          instalada y idéntica al catálogo
  difiere        instalada, pero su contenido no es el del catálogo
  solo-instalada existe en ~/.claude y no en el catálogo → sin copia de seguridad
  externa        la instala otra herramienta (ops/global-install.yaml → external)
  retirada       quitada del catálogo a propósito y aún instalada → desinstalar
  no-instalada   está en el catálogo y no en ~/.claude (normal: `make install` solo
                 instala lo que usan los stacks); solo se lista con --all

Uso: drift.py [--json] [--all] [--kind skill|agent|rule]
Salida: exit 1 si hay alguna pieza `difiere`, `solo-instalada` o `retirada`.
"""
import argparse
import sys

from catalog_lib import (CATALOG, GLOBAL_DIR, KINDS, changed_files, digest, emit, external_names,
                         item_path, list_names, retired_names)

PROBLEM = {"difiere", "solo-instalada", "retirada"}
ICON = {"igual": "·", "difiere": "≠", "solo-instalada": "!", "externa": "↗", "retirada": "✗", "no-instalada": "-"}


def compare(kind: str) -> list[dict]:
    catalog, installed = list_names(CATALOG, kind), list_names(GLOBAL_DIR, kind)
    external, retired = external_names(kind), retired_names(kind)
    rows = []
    for name in sorted(catalog | installed):
        if name in external:
            status = "externa"
        elif name in retired and name in installed:
            status = "retirada"
        elif name not in installed:
            status = "no-instalada"
        elif name not in catalog:
            status = "solo-instalada"
        else:
            same = digest(item_path(CATALOG, kind, name)) == digest(item_path(GLOBAL_DIR, kind, name))
            status = "igual" if same else "difiere"
        row = {"kind": kind, "name": name, "status": status}
        if status == "difiere":
            row["files"] = changed_files(item_path(CATALOG, kind, name), item_path(GLOBAL_DIR, kind, name))
        rows.append(row)
    return rows


def human(data: dict) -> None:
    for row in data["items"]:
        print(f"  {ICON[row['status']]} {row['kind']:<5} {row['name']:<34} {row['status']}")
        for f in row.get("files", [])[:4]:
            print(f"        {f}")
        if len(row.get("files", [])) > 4:
            print(f"        … y {len(row['files']) - 4} más")
    counts = ", ".join(f"{k}: {v}" for k, v in data["counts"].items())
    print(f"\n{counts}")
    if data["problems"]:
        print("Arreglo: `solo-instalada` → `make collect KIND=… NAME=…`; `difiere` → decide qué lado vale\n"
              "(`make install` impone el catálogo; `make collect … OVERWRITE=1` recoge lo instalado); "
              "`retirada` → borrarla de ~/.claude.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--all", action="store_true", help="incluir también las no instaladas")
    ap.add_argument("--kind", choices=list(KINDS))
    args = ap.parse_args()

    rows = [r for k in ([args.kind] if args.kind else KINDS) for r in compare(k)]
    counts: dict[str, int] = {}
    for r in rows:
        counts[r["status"]] = counts.get(r["status"], 0) + 1
    shown = rows if args.all else [r for r in rows if r["status"] not in ("no-instalada", "igual")]
    problems = sum(1 for r in rows if r["status"] in PROBLEM)
    data = {"catalog": str(CATALOG), "installed": str(GLOBAL_DIR), "counts": counts,
            "problems": problems, "items": shown}
    emit(data, args.json, human)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
