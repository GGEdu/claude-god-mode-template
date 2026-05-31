#!/usr/bin/env python3
"""
Dry-run check: shows what would change if make update were run.

Reads .claude/.template-manifest.yaml from the project, then uses git log
to find commits in the template since the recorded SHA that touch files
relevant to the compiled output.

Usage:
    python3 ops/check-updates.py <project_path> [--template /ruta/template]

Exit codes:
    0 — project is up to date
    1 — updates available
    2 — error (missing manifest, missing template, etc.)
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

import yaml


# Map template source paths to artifact categories
_SOURCE_PATTERNS = [
    ("agents/", "agents"),
    ("skills/", "agents"),       # skill changes re-compile agents
    ("stacks/{stack}/", "agents,rules,pipeline,commands"),
    ("layers/", "agents,rules,commands"),
    ("domains/", "agents,rules,commands"),
]


def load_manifest(project: Path) -> dict:
    manifest_path = project / ".claude" / ".template-manifest.yaml"
    if not manifest_path.exists():
        print(
            f"❌ Sin manifest en {manifest_path}\n"
            "   Ejecuta: make generate-manifest PROJECT=/ruta STACK=<stack>",
            file=sys.stderr,
        )
        sys.exit(2)
    with open(manifest_path) as f:
        return yaml.safe_load(f) or {}


def resolve_template(manifest: dict, template_arg: str | None) -> Path:
    """Find the template directory via arg > env var > manifest path."""
    for candidate in filter(None, [
        template_arg,
        os.environ.get("CLAUDE_TEMPLATE_PATH"),
        manifest.get("template", {}).get("path"),
    ]):
        p = Path(candidate)
        if p.is_dir() and (p / "Makefile").exists():
            return p.resolve()

    print(
        "❌ Template no encontrado. Opciones:\n"
        "   1. make check-updates PROJECT=/ruta TEMPLATE=/ruta/template\n"
        "   2. export CLAUDE_TEMPLATE_PATH=/ruta/template",
        file=sys.stderr,
    )
    sys.exit(2)


def git_commits_since(template: Path, since_sha: str, path_filter: str) -> list[str]:
    """Return list of commit lines since SHA touching the given path."""
    try:
        result = subprocess.check_output(
            ["git", "log", "--oneline", f"{since_sha}..HEAD", "--", path_filter],
            cwd=template,
            text=True,
        ).strip()
        return [l for l in result.splitlines() if l]
    except subprocess.CalledProcessError:
        return []


def changed_files_since(template: Path, since_sha: str, path_filter: str) -> list[str]:
    try:
        result = subprocess.check_output(
            ["git", "diff", "--name-only", f"{since_sha}..HEAD", "--", path_filter],
            cwd=template,
            text=True,
        ).strip()
        return [l for l in result.splitlines() if l]
    except subprocess.CalledProcessError:
        return []


def main() -> None:
    parser = argparse.ArgumentParser(description="Check for template updates (dry-run)")
    parser.add_argument("project", help="Ruta al proyecto")
    parser.add_argument("--template", default=None, help="Ruta al template (opcional)")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    manifest = load_manifest(project)
    template = resolve_template(manifest, args.template)

    since_sha = manifest.get("template", {}).get("commit_sha", "")
    stack = manifest.get("compilation", {}).get("stack", "")

    if not since_sha:
        print("❌ Manifest sin commit_sha — ejecuta make generate-manifest", file=sys.stderr)
        sys.exit(2)

    # Verify SHA exists in the template repo
    try:
        subprocess.check_output(
            ["git", "cat-file", "-e", since_sha],
            cwd=template,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        print(
            f"⚠️  SHA {since_sha} no encontrado en {template}\n"
            "   El template puede haber cambiado de ubicación o el historial fue reescrito.",
            file=sys.stderr,
        )
        sys.exit(2)

    # Paths to check, expanding {stack}
    watch_paths = [
        "agents/",
        "skills/",
        f"stacks/{stack}/",
        "layers/",
        "domains/",
    ]

    all_changed: set[str] = set()
    for path in watch_paths:
        all_changed.update(changed_files_since(template, since_sha, path))

    if not all_changed:
        print(f"✅ El proyecto está al día con el template (SHA: {since_sha})")
        sys.exit(0)

    # Categorize what would be affected
    affects: set[str] = set()
    for f in all_changed:
        if f.startswith("agents/") or f.startswith("skills/"):
            affects.add("agents (recompilar)")
        if f.startswith(f"stacks/{stack}/rules"):
            affects.add("rules")
        if f.startswith(f"stacks/{stack}/pipeline"):
            affects.add("pipeline.yaml")
        if f.startswith(f"stacks/{stack}/commands") or "commands" in f:
            affects.add("commands")
        if f.startswith("layers/") or f.startswith("domains/"):
            affects.add("agents (recompilar)")
            affects.add("rules")

    # Count new commits
    all_commits: set[str] = set()
    for path in watch_paths:
        for line in git_commits_since(template, since_sha, path):
            all_commits.add(line.split()[0])  # deduplicate by SHA

    print(f"⚡ {len(all_commits)} commit(s) nuevo(s) desde {since_sha}")
    print(f"   Stack: {stack} | Template: {template}")
    print()
    print("Artefactos que cambiarían:")
    for a in sorted(affects):
        print(f"   • {a}")
    print()
    print(f"Archivos fuente modificados ({len(all_changed)}):")
    for f in sorted(all_changed)[:20]:
        print(f"   - {f}")
    if len(all_changed) > 20:
        print(f"   ... y {len(all_changed) - 20} más")
    print()
    print(f"Para aplicar: make update PROJECT={project}")
    sys.exit(1)


if __name__ == "__main__":
    main()
