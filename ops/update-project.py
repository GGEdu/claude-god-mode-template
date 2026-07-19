#!/usr/bin/env python3
"""
Update a project's compiled Claude content from the template.

Reads .claude/.template-manifest.yaml, re-runs the same compilation that
init-project ran (reusing compile-agents.py, copy-commands.py), and updates
the manifest with the new template SHA.

Sacred files never touched: CLAUDE.md, memory/, hooks/, .github/workflows/

Usage:
    python3 ops/update-project.py <project_path> [--template /ruta] [--force]

Exit codes:
    0 — success
    1 — drift detected (run with --force to override)
    2 — error
"""

import argparse
import hashlib
import os
import subprocess
import sys
from pathlib import Path

import yaml


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return f"sha256:{h.hexdigest()}"


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
        "   1. make update PROJECT=/ruta TEMPLATE=/ruta/template\n"
        "   2. export CLAUDE_TEMPLATE_PATH=/ruta/template",
        file=sys.stderr,
    )
    sys.exit(2)


def detect_drift(project: Path, recorded_checksums: dict) -> list[str]:
    """Return list of files whose checksum differs from what was recorded."""
    drifted = []

    agents = recorded_checksums.get("agents", {})
    for name, expected in agents.items():
        p = project / ".claude" / "agents" / f"{name}.md"
        if p.exists() and sha256_file(p) != expected:
            drifted.append(f".claude/agents/{name}.md")

    commands = recorded_checksums.get("commands", {})
    for name, expected in commands.items():
        p = project / ".claude" / "commands" / f"{name}.md"
        if p.exists() and sha256_file(p) != expected:
            drifted.append(f".claude/commands/{name}.md")

    rules = recorded_checksums.get("rules", {})
    for filename, expected in rules.items():
        p = project / ".claude" / "rules" / "stack" / filename
        if p.exists() and sha256_file(p) != expected:
            drifted.append(f".claude/rules/stack/{filename}")

    pipeline_expected = recorded_checksums.get("pipeline_yaml")
    if pipeline_expected:
        p = project / ".claude" / "pipeline.yaml"
        if p.exists() and sha256_file(p) != pipeline_expected:
            drifted.append(".claude/pipeline.yaml")

    return drifted


def run(cmd: list[str], cwd: Path) -> None:
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        print(f"❌ Falló: {' '.join(cmd)}", file=sys.stderr)
        sys.exit(2)


def main() -> None:
    parser = argparse.ArgumentParser(description="Update project from template")
    parser.add_argument("project", help="Ruta al proyecto")
    parser.add_argument("--template", default=None)
    parser.add_argument("--force", action="store_true", help="Ignorar drift local")
    args = parser.parse_args()

    project = Path(args.project).resolve()
    manifest = load_manifest(project)
    template = resolve_template(manifest, args.template)

    stack = manifest.get("compilation", {}).get("stack", "")
    layers = manifest.get("compilation", {}).get("layers", [])
    domain = manifest.get("compilation", {}).get("domain", "")

    if not stack:
        print("❌ Manifest sin stack — ejecuta make generate-manifest", file=sys.stderr)
        sys.exit(2)

    # Drift check
    recorded = manifest.get("checksums", {})
    drifted = detect_drift(project, recorded)
    if drifted and not args.force:
        print("⚠️  Archivos generados modificados localmente:")
        for f in drifted:
            print(f"   - {f}")
        print()
        print("Estos cambios serían sobreescritos por el update.")
        print("Para continuar de todas formas: make update PROJECT=/ruta FORCE=true")
        sys.exit(1)
    elif drifted and args.force:
        print(f"⚠️  --force: sobreescribiendo {len(drifted)} archivo(s) con drift local")

    # Build overlay args list for compile-agents.py and copy-commands.py
    overlay_args: list[str] = []
    for layer in (layers or []):
        layer_yaml = template / "layers" / layer / "layer.yaml"
        if layer_yaml.exists():
            overlay_args.append(str(layer_yaml))
    if domain:
        domain_yaml = template / "domains" / domain / "domain.yaml"
        if domain_yaml.exists():
            overlay_args.append(str(domain_yaml))

    stack_yaml = template / "stacks" / stack / "stack.yaml"
    if not stack_yaml.exists():
        print(f"❌ stack.yaml no encontrado: {stack_yaml}", file=sys.stderr)
        sys.exit(2)

    print(f"Actualizando proyecto desde template (stack: {stack})...")
    print()

    # 1. Recompile agents
    agents_out = project / ".claude" / "agents"
    agents_out.mkdir(parents=True, exist_ok=True)
    print("  Recompilando agentes...")
    run(
        [
            sys.executable,
            str(template / "ops" / "compile-agents.py"),
            str(stack_yaml),
            str(template / "skills"),
            str(template / "agents"),
            str(agents_out),
            *overlay_args,
        ],
        cwd=template,
    )

    # 2. Copy commands
    print("  Actualizando comandos...")
    run(
        [
            sys.executable,
            str(template / "ops" / "copy-commands.py"),
            str(project),
            str(stack_yaml),
            *overlay_args,
        ],
        cwd=template,
    )

    # 3. Copy stack rules
    rules_src = template / "stacks" / stack / "rules"
    rules_dst = project / ".claude" / "rules" / "stack"
    rules_dst.mkdir(parents=True, exist_ok=True)
    if rules_src.is_dir():
        import shutil
        for f in rules_src.glob("*.md"):
            shutil.copy2(f, rules_dst / f.name)
        print(f"  ✅ Rules copiadas ({stack})")

    # 3b. Copy layer rules
    for layer in (layers or []):
        layer_rules = template / "layers" / layer / "rules"
        if layer_rules.is_dir():
            import shutil
            for f in layer_rules.glob("*.md"):
                shutil.copy2(f, rules_dst / f.name)
            print(f"  ✅ Layer rules copiadas ({layer})")

    # 3c. Copy domain rules
    if domain:
        domain_rules = template / "domains" / domain / "rules"
        if domain_rules.is_dir():
            import shutil
            for f in domain_rules.glob("*.md"):
                shutil.copy2(f, rules_dst / f.name)
            print("  ✅ Domain rules copiadas")

    # 4. Copy pipeline.yaml
    import shutil
    for pipeline_src in [
        template / "stacks" / stack / "pipeline.yaml",
        template / "stacks" / "common" / "pipeline.yaml",
    ]:
        if pipeline_src.is_file():
            shutil.copy2(pipeline_src, project / ".claude" / "pipeline.yaml")
            print("  ✅ pipeline.yaml actualizado")
            break

    # 5. Update manifest
    layers_arg = ",".join(layers) if layers else ""
    run(
        [
            sys.executable,
            str(template / "ops" / "write-manifest.py"),
            "--project", str(project),
            "--template", str(template),
            "--stack", stack,
            *(["--layers", layers_arg] if layers_arg else []),
            *(["--domain", domain] if domain else []),
        ],
        cwd=template,
    )

    print()
    print("✅ Proyecto actualizado.")
    print("   Reinicia Claude Code para activar los nuevos agentes.")


if __name__ == "__main__":
    main()
