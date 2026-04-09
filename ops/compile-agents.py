#!/usr/bin/env python3
"""
Compile agents with their stack-assigned skills embedded.

Usage:
    python3 ops/compile-agents.py <stack.yaml> <skills_dir> <agents_dir> <output_dir> [domain.yaml]

Reads the `agents:` section from stack.yaml (dict format with skills mapping),
reads each agent .md file + assigned skill SKILL.md files, and writes compiled
agents to output_dir with skill content appended.

If domain.yaml is provided, its `agent_skills:` are merged (appended) onto the
stack's agent skills — overlays ONLY ADD, never replace.

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


def merge_domain_skills(agents, domain_yaml_path):
    """Merge domain agent_skills onto stack agents (append only)."""
    with open(domain_yaml_path, encoding="utf-8") as f:
        domain = yaml.safe_load(f)

    domain_skills = domain.get("agent_skills", {})
    if not domain_skills:
        return agents

    for agent_name, extra_skills in domain_skills.items():
        if agent_name not in agents:
            continue
        config = agents[agent_name]
        if not isinstance(config, dict):
            config = {"skills": []}
            agents[agent_name] = config
        existing = config.get("skills", [])
        # Append without duplicates, preserving order
        seen = set(existing)
        for skill in extra_skills:
            if skill not in seen:
                existing.append(skill)
                seen.add(skill)
        config["skills"] = existing

    return agents


def main():
    if len(sys.argv) < 5:
        print(f"Usage: {sys.argv[0]} <stack.yaml> <skills_dir> <agents_dir> <output_dir> [domain.yaml]")
        sys.exit(1)

    stack_yaml_path = sys.argv[1]
    skills_base = sys.argv[2]
    agents_base = sys.argv[3]
    output_dir = sys.argv[4]
    domain_yaml_path = sys.argv[5] if len(sys.argv) > 5 else None

    with open(stack_yaml_path, encoding="utf-8") as f:
        stack = yaml.safe_load(f)

    agents = stack.get("agents", {})

    # Merge domain overlay skills if provided
    if domain_yaml_path and os.path.exists(domain_yaml_path) and isinstance(agents, dict):
        agents = merge_domain_skills(agents, domain_yaml_path)

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
