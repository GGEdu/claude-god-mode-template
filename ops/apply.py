#!/usr/bin/env python3
"""Aplica piezas sueltas del catálogo a un repo, para uno o varios harness.

Uso:
  apply.py <repo> --items skill:impeccable,agent:ui-engineer,command:plan
           [--harness claude,opencode,freebuff] [--mode auto|link|copy]
           [--remove] [--dry-run] [--json]

Modos (plan §4):
  link  symlink al catálogo — se actualiza solo; solo sirve en esta máquina
  copy  copia fijada — con commit y huella en el manifiesto; la única válida en CI
  auto  copy si el repo tiene .github/workflows, link si no (por defecto)

Destino por harness (rutas verificadas en sus binarios, 2026-09-23):
  claude    skill .claude/skills/<n>/ · agent .claude/agents/<n>.md · command .claude/commands/<n>.md
  opencode  skill .opencode/skills/<n>/ · agent .opencode/agents/<n>.md (adaptador) · command .opencode/commands/<n>.md
  freebuff  skill .agents/skills/<n>/ (sus agentes no se generan todavía)
Un adaptador (agente/comando opencode) siempre se copia: es un fichero generado.

Reglas: skills solo si pasan check-skill-integrity; se respeta metadata.harnesses; nunca
se pisa un fichero que no aplicó este comando (sin --force); todo queda en
.claude/.template-manifest.yaml → items. Exit 0 ok (incluye `no-aplica`: el harness no
admite esa pieza) · 1 algo omitido por conflicto o rechazado · 2 error.
"""
import argparse
import datetime
import shutil
import subprocess
import sys
from pathlib import Path

import yaml

from catalog_lib import CATALOG, digest, emit

TARGETS = {
    ("claude", "skill"): ".claude/skills/{n}", ("claude", "agent"): ".claude/agents/{n}.md",
    ("claude", "command"): ".claude/commands/{n}.md",
    ("opencode", "skill"): ".opencode/skills/{n}", ("opencode", "agent"): ".opencode/agents/{n}.md",
    ("opencode", "command"): ".opencode/commands/{n}.md",
    ("freebuff", "skill"): ".agents/skills/{n}",
}
SOURCES = {"skill": "skills/{n}", "agent": "agents/{n}.md", "command": "commands/{n}.md"}
MANIFEST = ".claude/.template-manifest.yaml"


def git_sha() -> str:
    return subprocess.run(["git", "-C", str(CATALOG), "rev-parse", "--short", "HEAD"],
                          capture_output=True, text=True).stdout.strip()


def skill_harnesses(name: str) -> list[str]:
    text = (CATALOG / "skills" / name / "SKILL.md").read_text()
    fm = yaml.safe_load(text.split("---", 2)[1]) if text.startswith("---") else {}
    raw = ((fm or {}).get("metadata") or {}).get("harnesses")
    return [h.strip() for h in raw.split(",")] if raw else ["claude", "opencode", "freebuff"]


def source_for(harness: str, kind: str, name: str) -> tuple[Path, bool]:
    """(origen, es_adaptador). Los agentes/comandos de opencode salen de dist/opencode."""
    if harness == "opencode" and kind in ("agent", "command"):
        return CATALOG / "dist/opencode" / f"{kind}s" / f"{name}.md", True
    return CATALOG / SOURCES[kind].format(n=name), False


def load_manifest(repo: Path) -> dict:
    path = repo / MANIFEST
    return (yaml.safe_load(path.read_text()) or {}) if path.is_file() else {}


def save_manifest(repo: Path, manifest: dict) -> None:
    path = repo / MANIFEST
    path.parent.mkdir(parents=True, exist_ok=True)
    manifest.setdefault("version", "1.0")
    manifest.setdefault("template", {"path": str(CATALOG)})
    path.write_text(yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False))


def remove_path(p: Path) -> None:
    if p.is_symlink() or p.is_file():
        p.unlink()
    elif p.is_dir():
        shutil.rmtree(p)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo")
    ap.add_argument("--items", required=True)
    ap.add_argument("--harness", default="claude")
    ap.add_argument("--mode", choices=["auto", "link", "copy"], default="auto")
    ap.add_argument("--remove", action="store_true")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    repo = Path(a.repo).expanduser().resolve()
    if not (repo / ".git").exists():
        emit({"ok": False, "error": f"{repo} no es un repo git"}, a.json, lambda d: print("✗", d["error"]))
        return 2
    mode = a.mode if a.mode != "auto" else ("copy" if (repo / ".github/workflows").is_dir() else "link")
    harnesses = [h.strip() for h in a.harness.split(",")]
    items = [tuple(i.split(":", 1)) for i in a.items.split(",")]
    manifest = load_manifest(repo)
    applied = {(e["harness"], e["type"], e["name"]): e for e in manifest.get("items", [])}
    sha, now = git_sha(), datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
    if any(h == "opencode" and k in ("agent", "command") for h in harnesses for k, _ in items) \
            and not (CATALOG / "dist/opencode").is_dir():
        subprocess.run([sys.executable, str(CATALOG / "ops/adapters.py")], check=True, capture_output=True)

    results = []
    for kind, name in items:
        if kind not in SOURCES:
            results.append({"type": kind, "name": name, "status": "rechazado", "why": "tipo desconocido"})
            continue
        if kind == "skill" and not a.remove:
            check = subprocess.run([sys.executable, str(CATALOG / "ops/check-skill-integrity.py"),
                                    str(CATALOG / "skills"), name], capture_output=True, text=True)
            if check.returncode:
                results.append({"type": kind, "name": name, "status": "rechazado", "why": "no pasa check-skill-integrity"})
                continue
        for harness in harnesses:
            key, row = (harness, kind, name), {"harness": harness, "type": kind, "name": name}
            if (harness, kind) not in TARGETS:
                results.append({**row, "status": "no-aplica", "why": f"{harness} no admite {kind}"})
                continue
            dst = repo / TARGETS[(harness, kind)].format(n=name)
            if a.remove:
                if key not in applied:
                    results.append({**row, "status": "omitido", "why": "no lo aplicó apply.py"})
                    continue
                if not a.dry_run:
                    remove_path(dst)
                    applied.pop(key)
                results.append({**row, "status": "eliminado", "path": str(dst.relative_to(repo))})
                continue
            if kind == "skill" and harness not in skill_harnesses(name):
                results.append({**row, "status": "no-aplica", "why": f"la skill no es compatible con {harness}"})
                continue
            src, adapter = source_for(harness, kind, name)
            if not src.exists():
                results.append({**row, "status": "rechazado", "why": f"no existe en el catálogo: {src.relative_to(CATALOG)}"})
                continue
            if (dst.exists() or dst.is_symlink()) and key not in applied and not a.force:
                results.append({**row, "status": "omitido", "why": "ya existe y no lo aplicó apply.py (usa --force)"})
                continue
            item_mode = "copy" if adapter else mode
            if not a.dry_run:
                remove_path(dst)
                dst.parent.mkdir(parents=True, exist_ok=True)
                if item_mode == "link":
                    dst.symlink_to(src)
                elif src.is_dir():
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
                applied[key] = {**row, "mode": item_mode, "path": str(dst.relative_to(repo)),
                                "catalog_sha": sha, "sha256": digest(src), "applied_at": now}
            results.append({**row, "status": "aplicado", "mode": item_mode, "path": str(dst.relative_to(repo))})

    if not a.dry_run:
        manifest["items"] = sorted(applied.values(), key=lambda e: (e["harness"], e["type"], e["name"]))
        save_manifest(repo, manifest)

    bad = [r for r in results if r["status"] in ("omitido", "rechazado")]
    data = {"ok": not bad, "repo": str(repo), "mode": mode, "dry_run": a.dry_run, "catalog_sha": sha, "results": results}

    def human(d):
        print(f"{'Simulación' if d['dry_run'] else 'Aplicado'} en {d['repo']} (modo {d['mode']}, catálogo @{d['catalog_sha']})")
        for r in d["results"]:
            where = r.get("path") or r.get("why", "")
            print(f"  {r['status']:<10} {r.get('harness', '-'):<9} {r['type']}:{r['name']}  {where}")
    emit(data, a.json, human)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
