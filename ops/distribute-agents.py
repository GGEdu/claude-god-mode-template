#!/usr/bin/env python3
"""
Distribute compiled Claude Code agents to Antigravity and Copilot formats.

Usage:
    python3 ops/distribute-agents.py <stack.yaml> <agents_dir> <project_dir>

Reads the `agents:` section from stack.yaml, then for each agent:
  - Skips agents that require MCP tools (Claude Code only)
  - Generates Antigravity skill:  <project_dir>/.agent/skills/<name>.md
  - Generates Copilot prompt:     <project_dir>/.github/prompts/<name>.prompt.md
  - Adds a compatibility warning for agents that use Bash (shell-only)

Agents with `mcp__*` tools are excluded entirely — they only run in Claude Code.
"""

import json
import os
import re
import sys

import yaml


BASH_WARNING = (
    "> ⚠️ **Compatibilidad limitada:** Este agente usa comandos de shell que solo "
    "están disponibles en Claude Code. En este entorno, úsalo como guía de análisis "
    "— los comandos no se ejecutarán."
)

MCP_WARNING = (
    "> ⚠️ **MCP no disponible:** Este agente usa herramientas MCP (Model Context "
    "Protocol) que solo funcionan en Claude Code. En este entorno, las operaciones "
    "de integración no se ejecutarán."
)


def parse_frontmatter(content):
    """Parse YAML frontmatter from agent file. Returns (frontmatter_dict, body_str)."""
    match = re.match(r"^---\n(.*?)\n---\n+(.*)", content, re.DOTALL)
    if not match:
        return {}, content
    try:
        fm = yaml.safe_load(match.group(1)) or {}
    except Exception:
        fm = {}
    body = match.group(2)
    return fm, body


def parse_tools(fm):
    """Return list of tool names from frontmatter tools field."""
    tools = fm.get("tools", [])
    if isinstance(tools, str):
        try:
            tools = json.loads(tools)
        except Exception:
            tools = []
    return tools if isinstance(tools, list) else []


def compatibility_warnings(tools):
    """Return list of warning blockquotes for the given tool list."""
    warnings = []
    if "Bash" in tools:
        warnings.append(BASH_WARNING)
    if any(t.startswith("mcp__") for t in tools):
        warnings.append(MCP_WARNING)
    return warnings


def has_mcp_tools(tools):
    return any(t.startswith("mcp__") for t in tools)


def to_antigravity(name, fm, body, warnings):
    """Generate Antigravity skill format."""
    description = fm.get("description", "").split(".")[0].strip()
    title = fm.get("name", name).replace("-", " ").title()

    lines = [f"# {title} Skill", "", description, ""]
    for w in warnings:
        lines += [w, ""]
    lines += [
        "## Cuándo usar este skill",
        "",
        f"Usa `@{name}` cuando necesites:",
        f"- {description}",
        "",
        "## Instrucciones",
        "",
        body.strip(),
    ]
    return "\n".join(lines) + "\n"


def to_copilot(name, fm, body, warnings):
    """Generate Copilot prompt format."""
    description = fm.get("description", "").split(". ")[0].strip()
    title = fm.get("name", name).replace("-", " ").title()

    front = f'---\ndescription: "{description}"\nmode: agent\n---\n'
    lines = [front]
    for w in warnings:
        lines += [w, ""]
    lines += [f"# {title}", "", body.strip()]
    return "\n".join(lines) + "\n"


def main():
    if len(sys.argv) < 4:
        print(f"Usage: {sys.argv[0]} <stack.yaml> <agents_dir> <project_dir>")
        sys.exit(1)

    stack_yaml_path = sys.argv[1]
    agents_dir = sys.argv[2]
    project_dir = sys.argv[3]

    with open(stack_yaml_path, encoding="utf-8") as f:
        stack = yaml.safe_load(f)

    agents = stack.get("agents", {})
    agent_names = list(agents.keys()) if isinstance(agents, dict) else list(agents)

    antigravity_dir = os.path.join(project_dir, ".agent", "skills")
    copilot_dir = os.path.join(project_dir, ".github", "prompts")
    os.makedirs(antigravity_dir, exist_ok=True)
    os.makedirs(copilot_dir, exist_ok=True)

    distributed = 0
    skipped = 0

    for name in agent_names:
        src = os.path.join(agents_dir, f"{name}.md")
        if not os.path.exists(src):
            print(f"  ⚠️  Agent not found: {name}")
            continue

        with open(src, encoding="utf-8") as f:
            content = f.read()

        fm, body = parse_frontmatter(content)
        tools = parse_tools(fm)

        if has_mcp_tools(tools):
            print(f"  ⏭️  {name} (MCP only — Claude Code exclusivo)")
            skipped += 1
            continue

        warnings = compatibility_warnings(tools)

        ag_path = os.path.join(antigravity_dir, f"{name}.md")
        with open(ag_path, "w", encoding="utf-8") as f:
            f.write(to_antigravity(name, fm, body, warnings))

        cp_path = os.path.join(copilot_dir, f"{name}.prompt.md")
        with open(cp_path, "w", encoding="utf-8") as f:
            f.write(to_copilot(name, fm, body, warnings))

        warn_note = " ⚠️ Bash" if "Bash" in tools else ""
        print(f"  ✅ {name}{warn_note}")
        distributed += 1

    print(f"\n  {distributed} agentes distribuidos ({skipped} omitidos — MCP only)")


if __name__ == "__main__":
    main()
