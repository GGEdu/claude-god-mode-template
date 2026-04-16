#!/usr/bin/env python3
"""
Compile agents with their stack-assigned skills embedded.

Usage:
    python3 ops/compile-agents.py <stack.yaml> <skills_dir> <agents_dir> <output_dir> [overlay.yaml...]

Reads the `agents:` section from stack.yaml (dict format with skills mapping),
reads each agent .md file + assigned skill SKILL.md files, and writes compiled
agents to output_dir with skill content appended.

Zero or more overlay YAMLs (layers or domains) can be provided after the 4th arg.
Each overlay's `agent_skills:` are merged (appended) onto the stack agents — overlays
ONLY ADD, never replace. Overlays can also ADD new agents not present in the stack.

Supports two formats:
  - Legacy (list):  agents: [architect, planner, ...]
  - New (dict):     agents: { architect: { skills: [api-design] }, ... }
"""

import os
import re
import shutil
import sys

import yaml


def read_file(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def strip_yaml_frontmatter(content):
    """Remove YAML frontmatter (--- ... ---) from a skill file."""
    return re.sub(r"^---\n.*?---\n+", "", content, count=1, flags=re.DOTALL)


def compile_agent(agent_path, skill_entries):
    """Read an agent file and append skill content inline."""
    content = read_file(agent_path)

    if not skill_entries:
        return content

    content += "\n\n---\n\n"
    content += "# Embedded Skills Reference\n\n"
    content += (
        "> These skills are loaded automatically as part of your expertise.\n"
        "> Use this knowledge directly — the developer does NOT need to invoke them.\n\n"
    )

    for skill_name, skill_path in skill_entries:
        if not os.path.exists(skill_path):
            continue
        skill_content = read_file(skill_path)
        skill_content = strip_yaml_frontmatter(skill_content)
        content += f"## Skill: {skill_name}\n\n{skill_content.strip()}\n\n"

    return content


def merge_domain_skills(agents, overlay_yaml_path):
    """Merge overlay agent_skills onto stack agents (append only).

    Overlays (layers or domains) can ADD new agents not present in the stack.
    This allows e.g. layers/react/ to inject typescript-reviewer into a backend-only stack.
    """
    with open(overlay_yaml_path, encoding="utf-8") as f:
        overlay = yaml.safe_load(f)

    overlay_skills = overlay.get("agent_skills", {})
    if not overlay_skills:
        return agents

    for agent_name, extra_skills in overlay_skills.items():
        if agent_name not in agents:
            # Layer/domain can ADD new agents (not just extend existing ones)
            agents[agent_name] = {"skills": list(extra_skills or [])}
            continue
        config = agents[agent_name]
        if not isinstance(config, dict):
            config = {"skills": []}
            agents[agent_name] = config
        existing = config.get("skills", [])
        # Append without duplicates, preserving order
        seen = set(existing)
        for skill in (extra_skills or []):
            if skill not in seen:
                existing.append(skill)
                seen.add(skill)
        config["skills"] = existing

    return agents


def main():
    if len(sys.argv) < 5:
        print(f"Usage: {sys.argv[0]} <stack.yaml> <skills_dir> <agents_dir> <output_dir> [overlay.yaml...]")
        sys.exit(1)

    stack_yaml_path = sys.argv[1]
    skills_base = sys.argv[2]
    agents_base = sys.argv[3]
    output_dir = sys.argv[4]
    overlay_paths = sys.argv[5:]  # Zero or more layer/domain overlay YAMLs

    with open(stack_yaml_path, encoding="utf-8") as f:
        stack = yaml.safe_load(f)

    agents = stack.get("agents", {})

    # Merge overlay skills in order: layers first, then domain (last overlay wins on conflicts)
    if isinstance(agents, dict):
        for overlay_path in overlay_paths:
            if overlay_path and os.path.exists(overlay_path):
                agents = merge_domain_skills(agents, overlay_path)

    os.makedirs(output_dir, exist_ok=True)

    # Legacy format: list of agent names (no skill injection)
    if isinstance(agents, list):
        for name in agents:
            src = os.path.join(agents_base, f"{name}.md")
            if os.path.exists(src):
                shutil.copy(src, os.path.join(output_dir, f"{name}.md"))
                print(f"  ✅ {name}")
            else:
                print(f"  ⚠️  Agent not found: {name}")
        return

    # New format: dict with optional skills per agent
    compiled_count = 0
    for name, config in agents.items():
        src = os.path.join(agents_base, f"{name}.md")
        if not os.path.exists(src):
            print(f"  ⚠️  Agent not found: {name}")
            continue

        skills = []
        if isinstance(config, dict):
            skills = config.get("skills", [])

        skill_entries = [
            (s, os.path.join(skills_base, s, "SKILL.md"))
            for s in skills
        ]

        compiled = compile_agent(src, skill_entries)

        output_path = os.path.join(output_dir, f"{name}.md")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(compiled)

        compiled_count += 1
        if skills:
            print(f"  ✅ {name} ← {', '.join(skills)}")
        else:
            print(f"  ✅ {name}")

    print(f"\n  {compiled_count} agentes compilados")


if __name__ == "__main__":
    main()
