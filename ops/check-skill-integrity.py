#!/usr/bin/env python3
"""Comprueba que cada skill contiene los ficheros que su SKILL.md manda usar.

Motivo: en abril se integró ui-ux-pro-max copiando solo SKILL.md; sus
instrucciones ejecutaban scripts/search.py, que no existía, y el modelo caía en
sus valores por defecto sin que nada avisara. Este check lo habría detectado.

Cuenta una ruta relativa a la skill (scripts/, reference/, data/, assets/…)
solo cuando se usa: ejecutada (node/python/bash…), leída (cat/Read/source) o
enlazada en markdown. Una ruta que es solo un ejemplo del proyecto del usuario
no cuenta. Para excepciones: `<!-- integrity-ignore: ruta -->` en el SKILL.md.

Uso: check-skill-integrity.py [skills_dir] [skill ...]   → exit 1 si falta algo
"""
import re
import sys
from pathlib import Path

PREFIXES = ("scripts", "reference", "references", "data", "assets", "templates", "agents",
            "eval-viewer", "fixtures", "prompts", "hooks", "commands")
# Rutas de ejemplo o del proyecto del usuario, no de la skill.
IGNORE = re.compile(r"<|\*|\{|\$|\.\.\.|example|your-|path/to")
USE = re.compile(r"\b(node|python3?|uv run|bash|sh|bun|npx|deno|cat|source|Read|load)\b[^\n]*$|\]\($")


def referenced_paths(skill_dir: Path) -> set[str]:
    text = (skill_dir / "SKILL.md").read_text(errors="replace")
    name = skill_dir.name
    alts = "|".join(map(re.escape, PREFIXES))
    rx = re.compile(
        rf"(?<![\w./-])(?:(?:\.claude/)?skills/{re.escape(name)}/|{re.escape(name)}/)?((?:{alts})/[\w./-]*\w)")
    ignored = set(re.findall(r"<!--\s*integrity-ignore:\s*(\S+)\s*-->", text))
    found = set()
    for m in rx.finditer(text):
        path = m.group(1)
        line_before = text[text.rfind("\n", 0, m.start()) + 1:m.start()]
        if IGNORE.search(path) or path in ignored or not USE.search(line_before):
            continue
        found.add(path)
    return found


def main() -> int:
    args = sys.argv[1:]
    root = Path(args[0]) if args else Path(__file__).resolve().parent.parent / "skills"
    only = set(args[1:])
    broken = 0
    for skill in sorted(p for p in root.iterdir() if (p / "SKILL.md").is_file()):
        if only and skill.name not in only:
            continue
        missing = sorted(p for p in referenced_paths(skill) if not (skill / p).exists())
        if missing:
            broken += 1
            print(f"✗ {skill.name}: {len(missing)} ruta(s) citada(s) no existen")
            for p in missing[:8]:
                print(f"    {p}")
            if len(missing) > 8:
                print(f"    … y {len(missing) - 8} más")
    print(f"\n{broken} skill(s) con ficheros citados que faltan" if broken else "OK: todas las rutas citadas existen")
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
