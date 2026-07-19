#!/usr/bin/env python3
"""
Write or update .claude/.template-manifest.yaml in a project.

Records the template version (git SHA), compilation params, and SHA-256
checksums of all generated files so drift can be detected later.

Usage:
    python3 ops/write-manifest.py \
        --project /ruta/proyecto \
        --template /ruta/template \
        --stack laravel \
        [--layers react,ts] \
        [--domain healthcare]

If the manifest already exists, symlinks_enabled is preserved and the rest
is updated.
"""

import argparse
import hashlib
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import yaml


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return f"sha256:{h.hexdigest()}"


def collect_checksums(project: Path) -> dict:
    """Compute SHA-256 for every generated file under .claude/."""
    checksums: dict = {}

    agents_dir = project / ".claude" / "agents"
    if agents_dir.is_dir():
        checksums["agents"] = {
            p.stem: sha256_file(p)
            for p in sorted(agents_dir.glob("*.md"))
        }

    commands_dir = project / ".claude" / "commands"
    if commands_dir.is_dir():
        checksums["commands"] = {
            p.stem: sha256_file(p)
            for p in sorted(commands_dir.glob("*.md"))
        }

    rules_dir = project / ".claude" / "rules" / "stack"
    if rules_dir.is_dir():
        checksums["rules"] = {
            p.name: sha256_file(p)
            for p in sorted(rules_dir.glob("*.md"))
        }

    pipeline = project / ".claude" / "pipeline.yaml"
    if pipeline.is_file():
        checksums["pipeline_yaml"] = sha256_file(pipeline)

    return checksums


def get_template_sha(template: Path) -> tuple[str, str]:
    """Return (short_sha, iso_timestamp) of HEAD in the template repo."""
    try:
        sha = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=template,
            text=True,
        ).strip()
        timestamp = subprocess.check_output(
            ["git", "log", "-1", "--format=%cI", "HEAD"],
            cwd=template,
            text=True,
        ).strip()
        return sha, timestamp
    except subprocess.CalledProcessError as e:
        print(f"❌ No se pudo leer git SHA del template: {e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Write .template-manifest.yaml")
    parser.add_argument("--project", required=True, help="Ruta al proyecto")
    parser.add_argument("--template", required=True, help="Ruta al template repo")
    parser.add_argument("--stack", required=True, help="Stack usado (ej: laravel)")
    parser.add_argument("--layers", default="", help="Layers separados por coma (ej: react,ts)")
    parser.add_argument("--domain", default="", help="Domain overlay (ej: healthcare)")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    template = Path(args.template).resolve()

    manifest_path = project / ".claude" / ".template-manifest.yaml"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    # Preserve user overrides from existing manifest
    existing: dict = {}
    if manifest_path.exists():
        with open(manifest_path) as f:
            existing = yaml.safe_load(f) or {}

    commit_sha, committed_at = get_template_sha(template)
    now = datetime.now(timezone.utc).isoformat()

    layers_list = [l.strip() for l in args.layers.split(",") if l.strip()]

    manifest = {
        "version": "1.0",
        "template": {
            "path": str(template),
            "commit_sha": commit_sha,
            "committed_at": committed_at,
        },
        "compilation": {
            "stack": args.stack,
            "layers": layers_list,
            "domain": args.domain,
            "timestamp": now,
        },
        "checksums": collect_checksums(project),
        "symlinks_enabled": existing.get("symlinks_enabled", False),
    }

    with open(manifest_path, "w") as f:
        yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    print(f"  ✅ Manifest escrito → {manifest_path.relative_to(project)} (SHA: {commit_sha})")


if __name__ == "__main__":
    main()
