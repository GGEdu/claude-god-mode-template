#!/usr/bin/env python3
"""Copy stack commands (slash commands) to a project's .claude/commands/ directory.

Usage: python3 ops/copy-commands.py <project_path> <stack_yaml> [domain_yaml]
"""
import sys
import os
import shutil
import yaml


def main():
    if len(sys.argv) < 3:
        print("Usage: copy-commands.py <project_path> <stack_yaml> [domain_yaml]", file=sys.stderr)
        sys.exit(1)

    project = sys.argv[1]
    stack_yaml = sys.argv[2]
    domain_yaml = sys.argv[3] if len(sys.argv) > 3 else ""

    with open(stack_yaml) as f:
        stack_data = yaml.safe_load(f)

    cmds = dict(stack_data.get("commands", {}))

    if domain_yaml and os.path.exists(domain_yaml):
        with open(domain_yaml) as f:
            domain_data = yaml.safe_load(f)
        cmds.update(domain_data.get("commands", {}))

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
