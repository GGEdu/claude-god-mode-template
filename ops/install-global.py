#!/usr/bin/env python3
"""Install globally-used agents and skills to ~/.claude/.

Usage: python3 ops/install-global.py <global_dir>

Scans all stacks/*/stack.yaml, domains/*/domain.yaml y layers/*/layer.yaml
para encontrar qué agentes y skills están realmente referenciados, y copia
solo esos a global_dir.
"""
import sys
import glob
import os
import shutil
import yaml

# Agentes "meta" que se invocan por .claude/pipeline.yaml o ops/triggers/*.yaml
# en vez de por stack.yaml/domain.yaml/layer.yaml — este script no escanea
# pipelines ni triggers, así que sin este allowlist nunca se instalarían
# globalmente pese a ser de uso genuino (fix ítem P1-6, auditoría 2026-07-18).
ALWAYS_INSTALL_AGENTS = {
    "architecture-auditor",  # .claude/pipeline.yaml → workflow architecture-audit
    "repo-reviewer",         # ops/triggers/weekly-repo-discovery.yaml
}

# Mismo criterio que ALWAYS_INSTALL_AGENTS pero para skills: meta-tooling de
# invocación manual/on-demand (no ligado a un stack ni disparado por hooks),
# así que sin este allowlist nunca se instalaría (council 2026-07-24: decisión
# deliberada de NO conectarlo a pipeline.yaml/triggers — disponible, no forzado).
ALWAYS_INSTALL_SKILLS = {
    "skill-creator",
}


def main():
    if len(sys.argv) < 2:
        print("Usage: install-global.py <global_dir>", file=sys.stderr)
        sys.exit(1)

    global_dir = sys.argv[1]

    used_agents = set()
    used_skills = set()

    for f in glob.glob("stacks/*/stack.yaml"):
        with open(f) as fh:
            d = yaml.safe_load(fh)
        agents = d.get("agents", {})
        if isinstance(agents, list):
            used_agents.update(agents)
        elif isinstance(agents, dict):
            used_agents.update(agents.keys())
            for v in agents.values():
                if isinstance(v, dict):
                    used_skills.update(v.get("skills", []))
        cmds = d.get("commands", {})
        used_skills.update(cmds.keys())

    for f in glob.glob("domains/*/domain.yaml"):
        with open(f) as fh:
            d = yaml.safe_load(fh)
        for skills in (d.get("agent_skills", {}) or {}).values():
            used_skills.update(skills or [])
        used_skills.update((d.get("commands", {}) or {}).keys())

    for f in glob.glob("layers/*/layer.yaml"):
        with open(f) as fh:
            d = yaml.safe_load(fh)
        for skills in (d.get("agent_skills", {}) or {}).values():
            used_skills.update(skills or [])
        used_skills.update((d.get("commands", {}) or {}).keys())
        # P1-4 fix: layer.yaml puede declarar agentes NUEVOS que aporta al
        # sistema (ver layers/requirements-engineering/layer.yaml → agents:
        # [business-analyst, change-manager]). Antes de este fix solo se leía
        # agent_skills/commands, así que esos agentes nunca llegaban a
        # used_agents ni, por lo tanto, a la instalación global.
        used_agents.update(d.get("agents", []) or [])

    used_agents.update(ALWAYS_INSTALL_AGENTS)
    used_skills.update(ALWAYS_INSTALL_SKILLS)

    agents_dir = os.path.join(global_dir, "agents")
    a_count = 0
    for name in sorted(used_agents):
        src = os.path.join("agents", name + ".md")
        if os.path.exists(src):
            shutil.copy(src, os.path.join(agents_dir, name + ".md"))
            a_count += 1

    print(f"  \u2705 Agentes instalados ({a_count} de {len(used_agents)} referenciados en stacks)")

    s_count = 0
    for name in sorted(used_skills):
        src_dir = os.path.join("skills", name)
        if os.path.exists(os.path.join(src_dir, "SKILL.md")):
            dest_dir = os.path.join(global_dir, "skills", name)
            # Copia el directorio completo, no solo SKILL.md — algunos skills
            # (ck, videodb, skill-comply, skill-creator...) traen scripts/,
            # references/ o assets/ que SKILL.md referencia por ruta relativa
            # y que antes nunca llegaban a global_dir (bug encontrado 2026-07-24).
            if os.path.exists(dest_dir):
                shutil.rmtree(dest_dir)
            shutil.copytree(src_dir, dest_dir)
            s_count += 1

    print(f"  \u2705 Skills instalados ({s_count} referenciados en stacks)")


if __name__ == "__main__":
    main()
