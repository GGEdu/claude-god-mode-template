#!/usr/bin/env python3
"""Recoge al catálogo una pieza que existe instalada en ~/.claude (copia de seguridad).

Uso: collect.py <skill|agent|rule> <nombre> [--overwrite] [--no-global] [--no-commit] [--json]

- `solo-instalada`: copia la pieza al catálogo.
- `difiere`: solo con --overwrite (la versión instalada sustituye a la del catálogo;
  el commit deja el diff para revisarlo).
- Añade la pieza a ops/global-install.yaml para que `make install` la reinstale en
  otra máquina (salvo --no-global o que ya la use algún stack).
- Una skill solo entra si pasa ops/check-skill-integrity.py.
- Hace commit en una rama `collect/<nombre>-<fecha>` si se está en `main`; nunca en main.
Exit: 0 recogida · 1 rechazada (integridad, ya igual, difiere sin --overwrite) · 2 error.
"""
import argparse
import datetime
import shutil
import subprocess
import sys

from catalog_lib import (CATALOG, GLOBAL_DIR, KINDS, digest, emit, external_names, item_path,
                         load_global_install, save_global_install)


def git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(CATALOG), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


def fail(msg: str, as_json: bool, code: int = 1) -> int:
    emit({"ok": False, "error": msg}, as_json, lambda d: print(f"✗ {d['error']}", file=sys.stderr))
    return code


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=list(KINDS))
    ap.add_argument("name")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--no-global", action="store_true")
    ap.add_argument("--no-commit", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    src, dst = item_path(GLOBAL_DIR, a.kind, a.name), item_path(CATALOG, a.kind, a.name)
    if a.name in external_names(a.kind):
        return fail(f"{a.name} la gestiona otra herramienta (ops/global-install.yaml → external)", a.json)
    if not src.exists():
        return fail(f"no existe instalada: {src}", a.json)
    has_links = src.is_symlink() or (src.is_dir() and any(p.is_symlink() for p in src.rglob("*")))
    if has_links:
        return fail(f"{src} contiene enlaces simbólicos; recógela a mano", a.json)
    if dst.exists():
        if digest(src) == digest(dst):
            return fail(f"{a.kind} {a.name} ya es igual en el catálogo", a.json)
        if not a.overwrite:
            return fail(f"{a.kind} {a.name} difiere del catálogo; usa --overwrite para recoger la instalada", a.json)

    if not a.no_commit and git("status", "--porcelain", "--", str(dst.relative_to(CATALOG)),
                               "ops/global-install.yaml"):
        return fail("hay cambios sin commitear en la pieza o en ops/global-install.yaml", a.json)

    branch = git("branch", "--show-current")
    if not a.no_commit and branch in ("main", "master"):
        branch = f"collect/{a.name}-{datetime.date.today():%Y%m%d}"
        git("switch", "-c", branch)

    if dst.exists():
        shutil.rmtree(dst) if dst.is_dir() else dst.unlink()
    shutil.copytree(src, dst) if src.is_dir() else shutil.copy2(src, dst)

    if a.kind == "skill":
        check = subprocess.run([sys.executable, str(CATALOG / "ops/check-skill-integrity.py"),
                                str(CATALOG / "skills"), a.name], capture_output=True, text=True)
        if check.returncode != 0:
            shutil.rmtree(dst)
            if a.overwrite:  # devolver la versión del catálogo que se iba a sustituir
                git("checkout", "--", str(dst.relative_to(CATALOG)))
            return fail(f"no pasa check-skill-integrity:\n{check.stdout.strip()}", a.json)

    added_global = False
    if not a.no_global and a.kind in ("skill", "agent"):
        data = load_global_install()
        entries = data.setdefault(f"{a.kind}s", []) or []
        if a.name not in {e["name"] for e in entries}:
            entries.append({"name": a.name, "why": f"recogida desde ~/.claude ({datetime.date.today()})"})
            data[f"{a.kind}s"] = entries
            save_global_install(data)
            added_global = True

    commit = None
    if not a.no_commit:
        git("add", "--", str(dst.relative_to(CATALOG)), "ops/global-install.yaml")
        verb = "sustituir por la versión instalada" if a.overwrite else "recoger desde ~/.claude"
        git("commit", "-q", "-m", f"chore(collect): {a.kind} {a.name} — {verb}")
        commit = git("rev-parse", "--short", "HEAD")

    result = {"ok": True, "kind": a.kind, "name": a.name, "path": str(dst.relative_to(CATALOG)),
              "overwrote": a.overwrite, "global_install": added_global, "branch": branch, "commit": commit}
    emit(result, a.json, lambda d: print(
        f"✓ {d['kind']} {d['name']} → {d['path']}"
        + (" (añadida a global-install.yaml)" if d["global_install"] else "")
        + (f" · commit {d['commit']} en {d['branch']}" if d["commit"] else " · sin commit")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
