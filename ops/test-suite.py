#!/usr/bin/env python3
"""
Suite de tests integral para claude-god-mode-template.

Inicializa cada stack en proyectos/{stack}/, verifica todos los archivos
generados, testea cada skill, y persiste el progreso en .claude/memory/
para sobrevivir crashes.

Uso:
    python3 ops/test-suite.py [--stack STACK] [--resume] [--domain DOMAIN]
                              [--no-invoke] [--keep] [--verbose]

Flags:
    --stack STACK    Ejecutar solo ese stack
    --resume         Reanudar desde el último checkpoint
    --domain DOMAIN  Probar también un domain overlay
    --no-invoke      Solo struct + embed, sin invocaciones claude --print
    --keep           Mantener directorios proyectos/ tras los tests
    --verbose        Mostrar detalles en fallos
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

import yaml

# ── Constantes ─────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).parent.parent
STACKS_DIR = REPO_ROOT / "stacks"
AGENTS_DIR = REPO_ROOT / "agents"
SKILLS_DIR = REPO_ROOT / "skills"
DOMAINS_DIR = REPO_ROOT / "domains"
PROYECTOS_DIR = REPO_ROOT / "proyectos"
MEMORY_DIR = REPO_ROOT / ".claude" / "memory"

PROGRESS_FILE = MEMORY_DIR / "test-progress.md"
ERRORS_FILE = MEMORY_DIR / "test-errors.md"

# Orden de ejecución: stacks más simples primero
STACK_ORDER = [
    "perl",
    "cpp",
    "rust-api",
    "go-api",
    "python-api",
    "flutter",
    "swift-ios",
    "ml-pytorch",
    "java-springboot",
    "kotlin-multiplatform",
    "laravel-livewire",
    "odoo",
    "nuxt-saas",
    "nextjs-saas",
    "laravel-react",
]

# Prompts de invocación por categoría de skill
SKILL_INVOKE_PROMPTS = {
    "tdd": ("List the steps to write a failing test first in 3 bullet points.", ["test", "fail", "pass"]),
    "patterns": ("Name 2 key architectural patterns for this stack.", ["pattern", "layer"]),
    "api-design": ("What HTTP method creates a resource? One sentence.", ["POST", "201"]),
    "security": ("List 3 security checks before a commit. Be brief.", ["inject", "secret", "auth"]),
    "deployment": ("What does a basic deployment pipeline look like?", ["CI", "deploy", "build"]),
    "coding-standards": ("Name the most important linting rule. One sentence.", ["lint", "format", "style"]),
    "orchestrator": ("In 2 sentences, what are your orchestration responsibilities?", ["agent", "task"]),
    "default": ("In one sentence, what does this skill provide?", []),
}


# ── Data classes ────────────────────────────────────────────────────────────────

@dataclass
class SkillResult:
    stack: str
    agent: str
    skill: str
    struct_ok: bool = False
    embed_ok: bool = False
    invoke_ok: Optional[bool] = None  # None = not tested
    invoke_warn: bool = False
    error_msg: str = ""
    improvement: str = ""

    @property
    def status(self) -> str:
        if not self.struct_ok:
            return "❌ struct FAIL"
        if not self.embed_ok:
            return "❌ embed FAIL"
        if self.invoke_ok is None:
            return "✅ struct+embed"
        if not self.invoke_ok:
            return "❌ invoke FAIL"
        if self.invoke_warn:
            return "⚠️  invoke WARN"
        return "✅ struct+embed+invoke"

    @property
    def passed(self) -> bool:
        return self.struct_ok and self.embed_ok and (self.invoke_ok is not False)


@dataclass
class StackResult:
    stack: str
    checks: dict = field(default_factory=dict)
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    skill_results: list = field(default_factory=list)
    timestamp: str = ""

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    @property
    def status(self) -> str:
        if self.passed:
            return "✅ PASS"
        return f"❌ FAIL"


# ── Utilidades ──────────────────────────────────────────────────────────────────

def load_yaml(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def parse_frontmatter(content: str) -> dict:
    """Parse YAML frontmatter from a markdown file."""
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    try:
        return yaml.safe_load(match.group(1)) or {}
    except Exception:
        return {}


def count_sections(content: str) -> int:
    """Count ## headings in markdown content."""
    return len(re.findall(r"^## ", content, re.MULTILINE))


def get_skill_category(skill_name: str) -> str:
    """Map a skill name to a test category."""
    if "tdd" in skill_name or "testing" in skill_name or "test" in skill_name:
        return "tdd"
    if "pattern" in skill_name:
        return "patterns"
    if skill_name == "api-design":
        return "api-design"
    if "security" in skill_name or "phi" in skill_name:
        return "security"
    if "deployment" in skill_name or "docker" in skill_name:
        return "deployment"
    if "coding-standards" in skill_name or "coding" in skill_name:
        return "coding-standards"
    if "orchestrator" in skill_name:
        return "orchestrator"
    return "default"


# ── Verificaciones por stack ─────────────────────────────────────────────────────

def check_directories(project_dir: Path, stack: str) -> tuple[list, list]:
    """Verify expected directory structure exists."""
    errors = []
    warnings = []
    expected_dirs = [
        ".claude",
        ".claude/agents",
        ".claude/rules/stack",
        ".claude/commands",
        ".agent/skills",
        ".github/prompts",
        ".github/workflows",
    ]
    for d in expected_dirs:
        p = project_dir / d
        if not p.exists():
            errors.append(f"Directorio ausente: {d}")
        elif not any(p.iterdir()):
            warnings.append(f"Directorio vacío: {d}")
    return errors, warnings


def check_agents(project_dir: Path, stack_data: dict, verbose: bool = False) -> tuple[list, list]:
    """Verify compiled agents: count, skill embedding."""
    errors = []
    warnings = []
    agents_dir = project_dir / ".claude" / "agents"

    compiled = list(agents_dir.glob("*.md")) if agents_dir.exists() else []
    declared_count = len(stack_data.get("agents", {})) if isinstance(stack_data.get("agents"), dict) else len(list(AGENTS_DIR.glob("*.md")))

    if len(compiled) != declared_count:
        errors.append(
            f"Agentes compilados: {len(compiled)} (esperados {declared_count} declarados en stack.yaml)"
        )

    agents_config = stack_data.get("agents", {})
    if isinstance(agents_config, dict):
        for agent_name, config in agents_config.items():
            if not isinstance(config, dict):
                continue
            skills = config.get("skills", [])
            if not skills:
                continue
            agent_file = agents_dir / f"{agent_name}.md"
            if not agent_file.exists():
                errors.append(f"Agente no compilado: {agent_name}.md")
                continue
            content = agent_file.read_text(encoding="utf-8")
            embedded = re.findall(r"^## Skill: (.+)$", content, re.MULTILINE)
            if len(embedded) != len(skills):
                errors.append(
                    f"{agent_name}: {len(embedded)} skills embebidas (esperadas {len(skills)}: {skills})"
                )

    return errors, warnings


def check_rules(project_dir: Path, stack_data: dict) -> tuple[list, list]:
    """Verify stack rules were copied correctly."""
    errors = []
    warnings = []
    rules_dir = project_dir / ".claude" / "rules" / "stack"
    declared_rules = stack_data.get("rules", [])

    if not rules_dir.exists():
        errors.append("Directorio rules/stack/ ausente")
        return errors, warnings

    copied = {f.name for f in rules_dir.glob("*.md")}

    for rule in declared_rules:
        if rule not in copied:
            errors.append(f"Regla no copiada: {rule}")

    for f in copied:
        if f not in declared_rules:
            warnings.append(f"Regla extra no declarada en stack.yaml: {f}")

    return errors, warnings


def check_commands(project_dir: Path, stack_data: dict) -> tuple[list, list]:
    """Verify slash commands were copied."""
    errors = []
    warnings = []
    commands_dir = project_dir / ".claude" / "commands"
    declared = stack_data.get("commands", {}) or {}

    for cmd_name in declared:
        cmd_file = commands_dir / f"{cmd_name}.md"
        if not cmd_file.exists():
            errors.append(f"Comando ausente: /{cmd_name}")
        elif cmd_file.stat().st_size == 0:
            errors.append(f"Comando vacío: /{cmd_name}")

    return errors, warnings


def check_distribution(project_dir: Path) -> tuple[list, list]:
    """Verify Antigravity and Copilot distribution."""
    errors = []
    warnings = []

    ag_dir = project_dir / ".agent" / "skills"
    cp_dir = project_dir / ".github" / "prompts"

    # Only check agents that were actually compiled for this stack
    compiled_names = {f.stem for f in (project_dir / ".claude" / "agents").glob("*.md")} if (project_dir / ".claude" / "agents").exists() else set()

    # Check MCP-only agents are NOT distributed
    for agent_file in AGENTS_DIR.glob("*.md"):
        # Skip agents that weren't compiled for this stack (stack-specific agents)
        if agent_file.stem not in compiled_names:
            continue
        content = agent_file.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)
        tools = fm.get("tools", [])
        if isinstance(tools, str):
            try:
                tools = json.loads(tools)
            except Exception:
                tools = []

        has_mcp = any(str(t).startswith("mcp__") for t in tools)
        has_bash = "Bash" in tools

        ag_file = ag_dir / f"{agent_file.stem}.md"
        cp_file = cp_dir / f"{agent_file.stem}.prompt.md"

        if has_mcp:
            # Should NOT be distributed
            if ag_file.exists():
                errors.append(f"Agente MCP distribuido (no debería): {agent_file.stem}")
            if cp_file.exists():
                errors.append(f"Agente MCP en Copilot (no debería): {agent_file.stem}")
        else:
            # Should be distributed
            if not ag_file.exists():
                errors.append(f"Agente no distribuido a Antigravity: {agent_file.stem}")
                continue
            if not cp_file.exists():
                errors.append(f"Agente no distribuido a Copilot: {agent_file.stem}")
                continue

            ag_content = ag_file.read_text(encoding="utf-8")
            cp_content = cp_file.read_text(encoding="utf-8")

            if has_bash:
                if "Compatibilidad limitada" not in ag_content:
                    errors.append(f"Antigravity/{agent_file.stem}: falta aviso Bash")
                if "Compatibilidad limitada" not in cp_content:
                    errors.append(f"Copilot/{agent_file.stem}: falta aviso Bash")

            if "mode: agent" not in cp_content:
                warnings.append(f"Copilot/{agent_file.stem}: frontmatter sin 'mode: agent'")

    return errors, warnings


def check_claude_md(project_dir: Path, stack: str) -> tuple[list, list]:
    """Verify CLAUDE.md exists and has placeholder structure."""
    errors = []
    warnings = []
    claude_md = project_dir / ".claude" / "CLAUDE.md"

    if not claude_md.exists():
        errors.append("CLAUDE.md ausente")
        return errors, warnings

    content = claude_md.read_text(encoding="utf-8")
    if "[PLACEHOLDER]" not in content and "[placeholder]" not in content.lower():
        warnings.append("CLAUDE.md sin [PLACEHOLDER] — puede no ser la plantilla del stack")

    return errors, warnings


def check_github_actions(project_dir: Path) -> tuple[list, list]:
    """Verify GitHub Actions workflows were copied."""
    errors = []
    warnings = []
    wf_dir = project_dir / ".github" / "workflows"

    expected_workflows = [
        "agent-pr-review.yml",
        "agent-issue-triage.yml",
        "agent-scheduled-audit.yml",
    ]
    for wf in expected_workflows:
        if not (wf_dir / wf).exists():
            errors.append(f"GitHub Action ausente: {wf}")

    return errors, warnings


# ── Testeo de skills ─────────────────────────────────────────────────────────────

def check_skill_structure(skill_name: str) -> tuple[bool, str]:
    """Validate SKILL.md frontmatter and sections."""
    skill_file = SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_file.exists():
        return False, f"SKILL.md no existe en skills/{skill_name}/"

    content = skill_file.read_text(encoding="utf-8")
    fm = parse_frontmatter(content)

    if not fm.get("name"):
        return False, "Frontmatter sin campo 'name'"
    if not fm.get("description"):
        return False, "Frontmatter sin campo 'description'"

    sections = count_sections(content)
    if sections < 2:
        return False, f"Solo {sections} sección(es) — mínimo 2 esperadas"

    return True, ""


def check_skill_embedding(project_dir: Path, agent_name: str, skill_name: str) -> tuple[bool, str]:
    """Verify skill name appears in compiled agent body."""
    agent_file = project_dir / ".claude" / "agents" / f"{agent_name}.md"
    if not agent_file.exists():
        return False, f"Agente {agent_name}.md no compilado"

    content = agent_file.read_text(encoding="utf-8")
    # The compile script writes "## Skill: {skill_name}"
    if f"## Skill: {skill_name}" not in content:
        return False, f"'## Skill: {skill_name}' no encontrado en agente compilado"

    return True, ""


def invoke_skill(skill_name: str, agent_name: str, stack: str) -> tuple[bool, bool, str]:
    """
    Run a minimal claude --print invocation to test the skill.
    Returns (success, has_warning, output_or_error).
    """
    category = get_skill_category(skill_name)
    prompt_text, expected_terms = SKILL_INVOKE_PROMPTS.get(
        category, SKILL_INVOKE_PROMPTS["default"]
    )

    # Build context from the skill file
    skill_file = SKILLS_DIR / skill_name / "SKILL.md"
    if not skill_file.exists():
        return False, False, "SKILL.md no existe"

    skill_content = skill_file.read_text(encoding="utf-8")
    # Strip frontmatter for context
    skill_body = re.sub(r"^---\n.*?---\n+", "", skill_content, count=1, flags=re.DOTALL)

    full_prompt = (
        f"You are an AI assistant with the following skill loaded:\n\n"
        f"--- SKILL: {skill_name} ---\n{skill_body[:800]}\n---\n\n"
        f"{prompt_text}"
    )

    try:
        result = subprocess.run(
            [
                "claude",
                "--print",
                "--model", "claude-haiku-4-5-20251001",
                "--max-turns", "1",
                full_prompt,
            ],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(REPO_ROOT),
        )
        output = result.stdout.strip()

        if result.returncode != 0 or not output:
            return False, False, f"Error: {result.stderr[:200]}"

        if not expected_terms:
            # Default: at least 20 words
            word_count = len(output.split())
            if word_count < 20:
                return True, True, f"Respuesta muy corta ({word_count} palabras)"
            return True, False, output[:100]

        output_lower = output.lower()
        missing = [t for t in expected_terms if t.lower() not in output_lower]
        if missing:
            return True, True, f"Términos esperados ausentes: {missing}"

        return True, False, output[:100]

    except subprocess.TimeoutExpired:
        return False, False, "Timeout (30s)"
    except FileNotFoundError:
        return False, False, "claude CLI no encontrado en PATH"
    except Exception as e:
        return False, False, str(e)


def test_skills(
    project_dir: Path,
    stack: str,
    stack_data: dict,
    no_invoke: bool,
    verbose: bool,
    progress_callback,
) -> list[SkillResult]:
    """Test all skills declared in the stack for each agent."""
    results = []
    agents_config = stack_data.get("agents", {})
    if not isinstance(agents_config, dict):
        return results

    for agent_name, config in agents_config.items():
        if not isinstance(config, dict):
            continue
        skills = config.get("skills", [])
        for skill_name in skills:
            sr = SkillResult(stack=stack, agent=agent_name, skill=skill_name)

            # 1. Structural check
            struct_ok, struct_err = check_skill_structure(skill_name)
            sr.struct_ok = struct_ok
            if not struct_ok:
                sr.error_msg = struct_err
                sr.improvement = f"Completar SKILL.md de '{skill_name}': {struct_err}"
                results.append(sr)
                progress_callback(sr)
                continue

            # 2. Embedding check
            embed_ok, embed_err = check_skill_embedding(project_dir, agent_name, skill_name)
            sr.embed_ok = embed_ok
            if not embed_ok:
                sr.error_msg = embed_err
                sr.improvement = f"Verificar que '{skill_name}' está declarada correctamente en stack.yaml"
                results.append(sr)
                progress_callback(sr)
                continue

            # 3. Invocation check (optional)
            if not no_invoke:
                invoke_ok, invoke_warn, invoke_msg = invoke_skill(skill_name, agent_name, stack)
                sr.invoke_ok = invoke_ok
                sr.invoke_warn = invoke_warn
                if not invoke_ok:
                    sr.error_msg = invoke_msg
                elif invoke_warn:
                    sr.error_msg = invoke_msg
                    sr.improvement = f"Revisar contenido de '{skill_name}': {invoke_msg}"

                if verbose and (not invoke_ok or invoke_warn):
                    print(f"    invoke [{skill_name}]: {invoke_msg}")

            results.append(sr)
            progress_callback(sr)

    return results


# ── Memoria ──────────────────────────────────────────────────────────────────────

def load_completed_stacks() -> set:
    """Read test-progress.md and return set of stacks with ✅ PASS."""
    if not PROGRESS_FILE.exists():
        return set()

    content = PROGRESS_FILE.read_text(encoding="utf-8")
    completed = set()
    for line in content.splitlines():
        if "✅ PASS" in line:
            # Format: | stack_name | ✅ PASS | ...
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 2:
                stack_name = parts[1].strip()
                if stack_name and stack_name != "Stack":
                    completed.add(stack_name)
    return completed


def _init_progress_data() -> dict:
    """Initialize empty progress tracking structure."""
    return {
        "stacks": {},       # stack -> StackResult summary
        "skills": [],       # list of skill checkpoint lines
        "transversal": {
            "skills_coverage": "pendiente",
            "rules_coverage": "pendiente",
            "agents_coverage": "pendiente",
        },
    }


def _load_progress_raw() -> dict:
    """Load existing progress or return empty structure."""
    if not PROGRESS_FILE.exists():
        return _init_progress_data()

    data = _init_progress_data()
    content = PROGRESS_FILE.read_text(encoding="utf-8")

    # Parse stack table rows
    for line in content.splitlines():
        if "|" in line and "Stack" not in line and "---" not in line:
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 3 and parts[0] and "/" not in parts[0]:
                # Stack row: | stack | status | errors | timestamp |
                data["stacks"][parts[0]] = {
                    "status": parts[1] if len(parts) > 1 else "?",
                    "errors": parts[2] if len(parts) > 2 else "?",
                    "timestamp": parts[3] if len(parts) > 3 else "?",
                }
            elif len(parts) >= 2 and "/" in parts[0]:
                # Skill row: | stack/agent/skill | status | timestamp |
                data["skills"].append(line)

    return data


def save_stack_progress(result: StackResult) -> None:
    """Atomically update the stack's row in test-progress.md."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    data = _load_progress_raw()

    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    data["stacks"][result.stack] = {
        "status": result.status,
        "errors": str(len(result.errors)),
        "timestamp": ts,
    }

    _write_progress(data)


def save_skill_checkpoint(sr: SkillResult) -> None:
    """Append skill result row to test-progress.md."""
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    data = _load_progress_raw()

    ts = datetime.now().strftime("%H:%M:%S")
    key = f"{sr.stack} / {sr.agent} / {sr.skill}"
    # Remove existing row if present
    data["skills"] = [l for l in data["skills"] if key not in l]
    data["skills"].append(f"| {key} | {sr.status} | {ts} |")

    _write_progress(data)


def _write_progress(data: dict) -> None:
    """Write the complete test-progress.md from current data."""
    today = datetime.now().strftime("%Y-%m-%d")
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines = [
        "---",
        "name: test-progress",
        "description: Estado de la suite de tests por stack — checkpoint crash-safe",
        "type: project",
        f"updated: {today}",
        "---",
        "",
        "## Estado de ejecución",
        "",
        f"Última actualización: {now}",
        "",
        "| Stack | Estado | Errores | Timestamp |",
        "|-------|--------|---------|-----------|",
    ]

    all_stacks = STACK_ORDER + [s for s in data["stacks"] if s not in STACK_ORDER]
    for stack in all_stacks:
        if stack in data["stacks"]:
            d = data["stacks"][stack]
            lines.append(f"| {stack} | {d['status']} | {d['errors']} | {d['timestamp']} |")
        else:
            lines.append(f"| {stack} | ⏳ pendiente | — | — |")

    lines += [
        "",
        "## Skills testeadas",
        "",
        "| Stack / Agente / Skill | Estado | Hora |",
        "|------------------------|--------|------|",
    ]
    lines += data["skills"]

    transversal = data.get("transversal", {})
    lines += [
        "",
        "## Resumen transversal",
        "",
        f"- Skills coverage: {transversal.get('skills_coverage', 'pendiente')}",
        f"- Rules coverage: {transversal.get('rules_coverage', 'pendiente')}",
        f"- Agentes coverage: {transversal.get('agents_coverage', 'pendiente')}",
        "",
        "## Comando para reanudar",
        "",
        "```bash",
        "python3 ops/test-suite.py --resume",
        "```",
    ]

    PROGRESS_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


def log_error(stack: str, errors: list, warnings: list, improvements: list) -> None:
    """Append errors and improvements to test-errors.md."""
    if not errors and not improvements:
        return

    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now().strftime("%Y-%m-%d")

    # Initialize file if needed
    if not ERRORS_FILE.exists():
        ERRORS_FILE.write_text(
            "---\n"
            "name: test-errors\n"
            "description: Log acumulativo de errores y mejoras detectadas\n"
            "type: project\n"
            f"updated: {today}\n"
            "---\n\n"
            "## Errores encontrados\n\n"
            "## Skills huérfanas detectadas\n\n"
            "## Mejoras de arquitectura detectadas\n\n",
            encoding="utf-8",
        )

    content = ERRORS_FILE.read_text(encoding="utf-8")

    entry_lines = [f"\n### [{today}] Stack: {stack}\n"]
    for err in errors:
        entry_lines.append(f"**Error**: {err}")
    for warn in warnings:
        entry_lines.append(f"**Warning**: {warn}")
    for imp in improvements:
        entry_lines.append(f"**Mejora sugerida**: {imp}")
    entry_lines.append("")

    # Insert before "## Skills huérfanas" section
    entry = "\n".join(entry_lines)
    content = content.replace("## Skills huérfanas detectadas", entry + "## Skills huérfanas detectadas")

    # Update date
    content = re.sub(r"updated: \d{4}-\d{2}-\d{2}", f"updated: {today}", content)
    ERRORS_FILE.write_text(content, encoding="utf-8")


def write_project_memory(project_dir: Path, stack: str, skill_results: list[SkillResult]) -> None:
    """Write skill test results to the project's .claude/memory/ dir."""
    mem_dir = project_dir / ".claude" / "memory"
    mem_dir.mkdir(parents=True, exist_ok=True)

    today = datetime.now().strftime("%Y-%m-%d")
    lines = [
        "---",
        f"name: test-skills-resultado",
        f"description: Resultado del testeo de skills del stack {stack}",
        "type: project",
        f"updated: {today}",
        "---",
        "",
        "## Skills testeadas",
        "",
        "| Agente | Skill | Estado | Notas |",
        "|--------|-------|--------|-------|",
    ]

    errors = []
    improvements = []
    for sr in skill_results:
        note = sr.error_msg[:60] if sr.error_msg else "OK"
        lines.append(f"| {sr.agent} | {sr.skill} | {sr.status} | {note} |")
        if not sr.passed:
            errors.append(f"  - [{sr.agent}/{sr.skill}] {sr.error_msg}")
        if sr.improvement:
            improvements.append(f"  - {sr.improvement}")

    lines += ["", "## Errores detectados", ""]
    lines += errors if errors else ["  - ninguno"]

    lines += ["", "## Mejoras sugeridas", ""]
    lines += improvements if improvements else ["  - ninguna"]

    out = mem_dir / "test-skills-resultado.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ── Verificación transversal ─────────────────────────────────────────────────────

def check_skills_coverage() -> tuple[set, set, dict]:
    """Find orphaned skills and skills not in any stack."""
    declared = set()

    # Collect from all stacks
    for stack_dir in STACKS_DIR.iterdir():
        if not stack_dir.is_dir() or stack_dir.name == "common":
            continue
        yaml_path = stack_dir / "stack.yaml"
        if not yaml_path.exists():
            continue
        data = load_yaml(yaml_path)
        agents_cfg = data.get("agents", {})
        if isinstance(agents_cfg, dict):
            for config in agents_cfg.values():
                if isinstance(config, dict):
                    declared.update(config.get("skills", []))
        commands_cfg = data.get("commands", {}) or {}
        declared.update(commands_cfg.keys())

    # Collect from domains
    for domain_dir in DOMAINS_DIR.iterdir():
        if not domain_dir.is_dir():
            continue
        yaml_path = domain_dir / "domain.yaml"
        if not yaml_path.exists():
            continue
        data = load_yaml(yaml_path)
        for skill_list in data.get("agent_skills", {}).values():
            declared.update(skill_list or [])
        commands_cfg = data.get("commands", {}) or {}
        declared.update(commands_cfg.keys())

    all_skills = {d.name for d in SKILLS_DIR.iterdir() if d.is_dir()}
    orphaned = all_skills - declared
    missing = declared - all_skills

    return orphaned, missing, {"declared": len(declared), "total": len(all_skills)}


def check_rules_coverage() -> list:
    """Find rules declared in stack.yaml that don't exist on disk."""
    issues = []
    for stack_dir in STACKS_DIR.iterdir():
        if not stack_dir.is_dir() or stack_dir.name == "common":
            continue
        yaml_path = stack_dir / "stack.yaml"
        if not yaml_path.exists():
            continue
        data = load_yaml(yaml_path)
        for rule in data.get("rules", []):
            rule_path = stack_dir / "rules" / rule
            if not rule_path.exists():
                issues.append(f"[{stack_dir.name}] Regla declarada pero ausente: {rule}")
    return issues


# ── Runner principal ─────────────────────────────────────────────────────────────

def run_stack(
    stack: str,
    domain: Optional[str],
    no_invoke: bool,
    keep: bool,
    verbose: bool,
) -> StackResult:
    """Run all tests for a single stack."""
    result = StackResult(stack=stack, timestamp=datetime.now().strftime("%Y-%m-%d %H:%M"))
    project_dir = PROYECTOS_DIR / stack

    print(f"\n{'─' * 60}")
    print(f"  Stack: {stack}{f' + domain: {domain}' if domain else ''}")
    print(f"{'─' * 60}")

    # 1. Initialize project
    project_dir.mkdir(parents=True, exist_ok=True)
    make_cmd = ["make", "init-project", f"STACK={stack}", f"PROJECT={project_dir}"]
    if domain:
        make_cmd.append(f"DOMAIN={domain}")

    print(f"  → {' '.join(make_cmd[-3:])}")
    proc = subprocess.run(
        make_cmd,
        capture_output=not verbose,
        text=True,
        cwd=str(REPO_ROOT),
    )
    if proc.returncode != 0:
        result.errors.append(f"make init-project falló (exit {proc.returncode})")
        if verbose and proc.stderr:
            print(f"    STDERR: {proc.stderr[:300]}")
        save_stack_progress(result)
        return result

    # Load stack data
    stack_yaml_path = STACKS_DIR / stack / "stack.yaml"
    stack_data = load_yaml(stack_yaml_path)

    # 2. Run all structural checks
    checks = [
        ("directorios", check_directories(project_dir, stack)),
        ("agentes", check_agents(project_dir, stack_data, verbose)),
        ("reglas", check_rules(project_dir, stack_data)),
        ("comandos", check_commands(project_dir, stack_data)),
        ("distribución", check_distribution(project_dir)),
        ("CLAUDE.md", check_claude_md(project_dir, stack)),
        ("github-actions", check_github_actions(project_dir)),
    ]

    for check_name, (errs, warns) in checks:
        result.checks[check_name] = {"errors": errs, "warnings": warns}
        result.errors.extend(errs)
        result.warnings.extend(warns)
        if errs:
            for e in errs:
                print(f"  ❌ [{check_name}] {e}")
        elif warns:
            for w in warns:
                print(f"  ⚠️  [{check_name}] {w}")
        else:
            print(f"  ✅ {check_name}")

    # 3. Test skills with per-skill memory checkpoint
    skill_checkpoint_count = 0

    def on_skill_done(sr: SkillResult):
        nonlocal skill_checkpoint_count
        save_skill_checkpoint(sr)
        skill_checkpoint_count += 1
        symbol = "✅" if sr.passed else ("⚠️ " if sr.invoke_warn else "❌")
        print(f"  {symbol} skill [{sr.agent}/{sr.skill}]: {sr.status}")

    print(f"\n  Testeando skills{'  (sin invocación)' if no_invoke else ''}...")
    skill_results = test_skills(
        project_dir, stack, stack_data, no_invoke, verbose, on_skill_done
    )
    result.skill_results = skill_results

    # Count skill errors
    skill_errors = [sr for sr in skill_results if not sr.passed]
    if skill_errors:
        result.errors.extend([f"Skill {sr.skill} ({sr.agent}): {sr.error_msg}" for sr in skill_errors])

    # 4. Write project memory
    write_project_memory(project_dir, stack, skill_results)
    print(f"\n  → Memoria del proyecto escrita en proyectos/{stack}/.claude/memory/")

    # 5. Cleanup
    if not keep:
        shutil.rmtree(project_dir, ignore_errors=True)
        print(f"  → proyectos/{stack}/ eliminado")

    # 6. Collect improvements
    improvements = [sr.improvement for sr in skill_results if sr.improvement]

    # 7. Persist checkpoint
    save_stack_progress(result)
    log_error(stack, result.errors, result.warnings, improvements)

    # Summary
    status_icon = "✅" if result.passed else "❌"
    print(f"\n  {status_icon} {stack}: {result.status} — {len(result.errors)} errores, {len(result.warnings)} warnings")

    return result


def run_transversal(verbose: bool) -> None:
    """Run cross-stack verification and update progress."""
    print(f"\n{'═' * 60}")
    print("  VERIFICACIÓN TRANSVERSAL")
    print(f"{'═' * 60}")

    # Skills coverage
    orphaned, missing, stats = check_skills_coverage()
    coverage_msg = f"{stats['declared']} declaradas / {stats['total']} totales"
    if orphaned:
        print(f"  ⚠️  Skills huérfanas ({len(orphaned)}): {sorted(orphaned)}")
        coverage_msg += f" — {len(orphaned)} huérfanas: {sorted(orphaned)}"
    else:
        print("  ✅ Skills coverage: ninguna huérfana")
    if missing:
        print(f"  ❌ Skills declaradas pero ausentes ({len(missing)}): {sorted(missing)}")

    # Rules coverage
    rule_issues = check_rules_coverage()
    if rule_issues:
        print(f"  ❌ Reglas declaradas pero ausentes: {len(rule_issues)}")
        if verbose:
            for issue in rule_issues:
                print(f"    {issue}")
    else:
        print("  ✅ Rules coverage: todas las reglas declaradas existen en disco")

    # Update transversal section in progress
    data = _load_progress_raw()
    data["transversal"]["skills_coverage"] = coverage_msg
    data["transversal"]["rules_coverage"] = "OK" if not rule_issues else f"{len(rule_issues)} reglas faltantes"
    data["transversal"]["agents_coverage"] = f"{len(list(AGENTS_DIR.glob('*.md')))} agentes globales"
    _write_progress(data)

    # Log orphaned/missing to errors file
    if orphaned or missing or rule_issues:
        today = datetime.now().strftime("%Y-%m-%d")
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
        if not ERRORS_FILE.exists():
            ERRORS_FILE.write_text(
                "---\nname: test-errors\ndescription: Log acumulativo de errores\ntype: project\n"
                f"updated: {today}\n---\n\n## Errores encontrados\n\n"
                "## Skills huérfanas detectadas\n\n## Mejoras de arquitectura detectadas\n\n",
                encoding="utf-8",
            )
        content = ERRORS_FILE.read_text(encoding="utf-8")
        orphan_lines = []
        for s in sorted(orphaned):
            orphan_lines.append(f"| {s} | No declarada en ningún stack ni domain | Eliminar o añadir a un stack |")
        if orphan_lines:
            orphan_table = (
                "\n| Skill | Motivo | Acción sugerida |\n"
                "|-------|--------|-------------------|\n"
                + "\n".join(orphan_lines) + "\n"
            )
            content = content.replace(
                "## Skills huérfanas detectadas\n",
                "## Skills huérfanas detectadas\n" + orphan_table,
            )
            content = re.sub(r"updated: \d{4}-\d{2}-\d{2}", f"updated: {today}", content)
            ERRORS_FILE.write_text(content, encoding="utf-8")


def run_all(
    stack_filter: Optional[str],
    domain: Optional[str],
    resume: bool,
    no_invoke: bool,
    keep: bool,
    verbose: bool,
) -> None:
    """Run the full test suite."""
    print("\n" + "═" * 60)
    print("  SUITE DE TESTS — claude-god-mode-template")
    print("═" * 60)
    print(f"  Modo: {'--no-invoke' if no_invoke else 'completo (struct+embed+invoke)'}")
    print(f"  Resume: {resume} | Keep: {keep} | Domain: {domain or 'ninguno'}")

    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    PROYECTOS_DIR.mkdir(parents=True, exist_ok=True)

    # Determine stacks to run
    if stack_filter:
        stacks_to_run = [stack_filter]
    else:
        available = [d.name for d in STACKS_DIR.iterdir() if d.is_dir() and d.name != "common"]
        stacks_to_run = [s for s in STACK_ORDER if s in available]
        # Add any stacks not in STACK_ORDER
        stacks_to_run += [s for s in available if s not in STACK_ORDER]

    completed = load_completed_stacks() if resume else set()

    results = []
    for stack in stacks_to_run:
        if stack in completed:
            print(f"\n  ⏭️  {stack} — ya completado (--resume)")
            continue

        result = run_stack(stack, domain, no_invoke, keep, verbose)
        results.append(result)

    # Transversal checks only when running full suite
    if not stack_filter:
        run_transversal(verbose)

    # Final summary
    print(f"\n{'═' * 60}")
    print("  RESUMEN FINAL")
    print(f"{'═' * 60}")
    passed = sum(1 for r in results if r.passed)
    failed = len(results) - passed
    print(f"  Stacks: {passed} ✅  {failed} ❌  de {len(results)} ejecutados")
    if resume and completed:
        print(f"  Saltados (--resume): {len(completed)}")
    print(f"\n  Checkpoint: {PROGRESS_FILE}")
    print(f"  Errores:    {ERRORS_FILE}")


# ── CLI ──────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Suite de tests integral para claude-god-mode-template"
    )
    parser.add_argument("--stack", help="Ejecutar solo este stack")
    parser.add_argument("--domain", help="Añadir domain overlay")
    parser.add_argument("--resume", action="store_true", help="Reanudar desde checkpoint")
    parser.add_argument("--no-invoke", action="store_true", help="Solo struct+embed, sin claude invocations")
    parser.add_argument("--keep", action="store_true", help="Mantener proyectos/ tras los tests")
    parser.add_argument("--verbose", action="store_true", help="Mostrar detalles en fallos")
    args = parser.parse_args()

    # Validate stack
    if args.stack:
        stack_dir = STACKS_DIR / args.stack
        if not stack_dir.exists():
            print(f"❌ Stack '{args.stack}' no encontrado. Usa: make list-stacks")
            sys.exit(1)

    # Validate domain
    if args.domain:
        domain_dir = DOMAINS_DIR / args.domain
        if not domain_dir.exists():
            print(f"❌ Domain '{args.domain}' no encontrado. Usa: make list-domains")
            sys.exit(1)

    run_all(
        stack_filter=args.stack,
        domain=args.domain,
        resume=args.resume,
        no_invoke=args.no_invoke,
        keep=args.keep,
        verbose=args.verbose,
    )


if __name__ == "__main__":
    main()
