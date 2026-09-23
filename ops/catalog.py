#!/usr/bin/env python3
"""Índice del catálogo: todas las piezas con su huella, categoría y harness compatibles.

Es el contrato de lectura con agent-deck (plan: ops/plans/plan-catalogo-y-agent-deck-2026-09-23.md §3).

Uso: catalog.py                  → JSON por stdout
     catalog.py --out dist/catalog.json
     catalog.py --summary        → tabla de recuento (humano)
Exit 1 si una skill no tiene categoría o un frontmatter no se puede leer: el índice
nunca se publica incompleto.
"""
import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import Path

import yaml

from catalog_lib import CATALOG, digest, files_of, load_global_install

ALL_HARNESSES = ["claude", "opencode", "freebuff"]
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)


class CatalogError(Exception):
    pass


def frontmatter(path: Path) -> dict:
    m = FRONTMATTER.match(path.read_text(errors="replace"))
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError as e:
        raise CatalogError(f"frontmatter ilegible en {path.relative_to(CATALOG)}: {e.problem}") from e


def base(kind: str, name: str, path: Path, description: str) -> dict:
    files = files_of(path)
    return {"type": kind, "name": name, "description": " ".join(str(description or "").split()),
            "path": str(path.relative_to(CATALOG)), "sha256": digest(path),
            "files": len(files), "bytes": sum(f.stat().st_size for f in files)}


def harnesses_of(fm: dict) -> list[str]:
    raw = (fm.get("metadata") or {}).get("harnesses")
    return [h.strip() for h in raw.split(",")] if raw else list(ALL_HARNESSES)


def usage_index() -> dict[str, list[str]]:
    """skill/agent → stacks, layers y domains que la referencian."""
    used: dict[str, set] = {}
    for kind, pattern in (("stack", "stacks/*/stack.yaml"), ("layer", "layers/*/layer.yaml"),
                          ("domain", "domains/*/domain.yaml")):
        for f in CATALOG.glob(pattern):
            d = yaml.safe_load(f.read_text()) or {}
            ref = f"{kind}:{f.parent.name}"
            agents = d.get("agents") or {}
            names = set(agents if isinstance(agents, list) else agents.keys())
            for v in (agents.values() if isinstance(agents, dict) else []):
                if isinstance(v, dict):
                    names.update(v.get("skills") or [])
            for skills in (d.get("agent_skills") or {}).values():
                names.update(skills or [])
            for n in names:
                used.setdefault(n, set()).add(ref)
    return {k: sorted(v) for k, v in used.items()}


def skills(categories: dict[str, str], used: dict, forced: set[str]) -> list[dict]:
    out = []
    for d in sorted(p for p in (CATALOG / "skills").iterdir() if (p / "SKILL.md").is_file()):
        if d.name not in categories:
            raise CatalogError(f"skill sin categoría en ops/catalog-categories.yaml: {d.name}")
        fm = frontmatter(d / "SKILL.md")
        item = base("skill", d.name, d, fm.get("description"))
        item.update(category=categories[d.name], harnesses=harnesses_of(fm),
                    compatibility=fm.get("compatibility"), used_by=used.get(d.name, []),
                    global_install=d.name in forced or bool(used.get(d.name)))
        out.append(item)
    return out


def markdown_items(kind: str, folder: str, used: dict, forced: set[str]) -> list[dict]:
    out = []
    for f in sorted((CATALOG / folder).glob("*.md")):
        fm = frontmatter(f)
        item = base(kind, f.stem, f, fm.get("description"))
        if kind == "agent":
            item.update(model=fm.get("model"), harnesses=["claude"], used_by=used.get(f.stem, []),
                        global_install=f.stem in forced or bool(used.get(f.stem)))
        elif kind == "command":
            item.update(harnesses=["claude"])
        else:  # rule: la leen los tres vía CLAUDE.md / AGENTS.md
            item.update(harnesses=list(ALL_HARNESSES))
        out.append(item)
    return out


def compositions() -> list[dict]:
    out = []
    for kind, pattern in (("stack", "stacks/*/stack.yaml"), ("layer", "layers/*/layer.yaml"),
                          ("domain", "domains/*/domain.yaml")):
        for f in sorted(CATALOG.glob(pattern)):
            d = yaml.safe_load(f.read_text()) or {}
            item = base(kind, f.parent.name, f.parent, d.get("description"))
            agents = d.get("agents") or {}
            item.update(agents=sorted(agents if isinstance(agents, list) else agents.keys()),
                        harnesses=["claude"])
            out.append(item)
    return out


def workflows() -> list[dict]:
    path = CATALOG / ".claude/pipeline.yaml"
    data = (yaml.safe_load(path.read_text()) or {}).get("workflows") or {}
    return [{"type": "workflow", "name": name, "description": w.get("description", ""),
             "path": f".claude/pipeline.yaml#{name}",
             "agents": [s.get("agent") for s in w.get("steps", []) if isinstance(s, dict) and s.get("agent")],
             "harnesses": ["claude"]} for name, w in data.items()]


def build() -> dict:
    cats = yaml.safe_load((CATALOG / "ops/catalog-categories.yaml").read_text())["categories"]
    category_of = {s: c["id"] for c in cats for s in c["skills"]}
    gi = load_global_install()
    forced_skills = {e["name"] for e in gi.get("skills") or []}
    forced_agents = {e["name"] for e in gi.get("agents") or []}
    used = usage_index()
    items = (skills(category_of, used, forced_skills)
             + markdown_items("agent", "agents", used, forced_agents)
             + markdown_items("rule", "rules", used, set())
             + markdown_items("command", "commands", used, set())
             + compositions() + workflows())
    commit = subprocess.run(["git", "-C", str(CATALOG), "rev-parse", "HEAD"],
                            capture_output=True, text=True).stdout.strip()
    dirty = bool(subprocess.run(["git", "-C", str(CATALOG), "status", "--porcelain"],
                                capture_output=True, text=True).stdout.strip())
    return {"schema": 1, "catalog": str(CATALOG), "commit": commit, "dirty": dirty,
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "categories": [{"id": c["id"], "label": c["label"]} for c in cats],
            "external": gi.get("external") or {}, "retired": gi.get("retired") or {},
            "items": items}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out")
    ap.add_argument("--summary", action="store_true")
    args = ap.parse_args()
    try:
        data = build()
    except CatalogError as e:
        print(f"✗ {e}", file=sys.stderr)
        return 1
    if args.summary:
        counts: dict[str, int] = {}
        for i in data["items"]:
            counts[i["type"]] = counts.get(i["type"], 0) + 1
        claude_only = sum(1 for i in data["items"] if i["type"] == "skill" and i["harnesses"] == ["claude"])
        print(f"catálogo @{data['commit'][:7]}{' (con cambios sin commitear)' if data['dirty'] else ''}")
        print("  " + ", ".join(f"{k}: {v}" for k, v in counts.items()))
        print(f"  skills solo Claude: {claude_only}")
        return 0
    text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        out = CATALOG / args.out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(text)
        print(f"✓ {out.relative_to(CATALOG)} ({len(data['items'])} piezas)")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
