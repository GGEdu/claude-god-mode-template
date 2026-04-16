#!/usr/bin/env python3
"""Copy stack commands (slash commands) to a project's .claude/commands/ directory.

Usage: python3 ops/copy-commands.py <project_path> <stack_yaml> [overlay.yaml...]

Zero or more overlay YAMLs (layers or domain) can be provided after the stack yaml.
Each overlay's `commands:` are merged (last wins) onto the stack commands.
"""
import sys
import os
import shutil
import yaml


def main():
    if len(sys.argv) < 3:
        print("Usage: copy-commands.py <project_path> <stack_yaml> [overlay.yaml...]", file=sys.stderr)
        sys.exit(1)

    project = sys.argv[1]
    stack_yaml = sys.argv[2]
    overlay_yamls = sys.argv[3:]  # Zero or more layer/domain overlay YAMLs

    with open(stack_yaml) as f:
        stack_data = yaml.safe_load(f)

    cmds = dict(stack_data.get("commands", {}))

    for overlay_yaml in overlay_yamls:
        if overlay_yaml and os.path.exists(overlay_yaml):
            with open(overlay_yaml) as f:
                overlay_data = yaml.safe_load(f)
            cmds.update(overlay_data.get("commands", {}))

    commands_dir = os.path.join(project, ".claude", "commands")
    activated = []

    for name in cmds:
        src = os.path.join("skills", name, "SKILL.md")
        dst = os.path.join(commands_dir, name + ".md")
        if os.path.exists(src):
            shutil.copy(src, dst)
            activated.append(name)

    if activated:
        print("  \u2705 Comandos: " + ", ".join("/" + n for n in activated))
    else:
        print("  \u2705 Sin comandos standalone")


if __name__ == "__main__":
    main()
