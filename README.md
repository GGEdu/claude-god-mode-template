# Claude God Mode Template

Template maestro para proyectos con Claude Code: rules siempre activas, stacks configurables, sistema de memoria, agentes especializados y MCPs preconfigurados.

## Prerequisitos

- [Claude Code](https://docs.anthropic.com/claude-code) v2.1.0+
- Node.js v18+
- Python v3.10+ y [uv](https://astral.sh/uv)
- Git
- Cuenta Anthropic con plan Pro, Max o API activo

### Dependencias Python

Los hooks de `.claude/hooks/` usan `pyyaml` (parser robusto). Instalar con:

```bash
pip install -r requirements.txt
# o con uv (recomendado):
uv pip install -r requirements.txt
```

Si pyyaml no está disponible, los hooks degradan a un parser custom (más frágil, ver `non-goal-guard.py`).

## Quick Start

```bash
# 1. Clonar
git clone https://github.com/ggarrido/claude-god-mode-template.git
cd claude-god-mode-template

# 2. Instalar globalmente (agentes, reglas, hook de memoria)
make install

# 3. Inicializar un proyecto con un stack (+ domain overlay opcional)
make init-project STACK=laravel LAYERS=react PROJECT=/ruta/al/proyecto
make init-project STACK=python-api DOMAIN=healthcare PROJECT=/ruta/al/proyecto
```

Sigue la guía completa en [`docs/src/instalacion.md`](docs/src/instalacion.md).

## Lo que incluye

- **Rules universales** en `.claude/rules/common/` — siempre activas en cada sesión
- **15 tech stacks** configurables (`laravel`, `laravel-livewire`, `nextjs-saas`, `python-api`, `go-api`, `odoo`, `cpp`, `flutter`, `java-springboot`, `kotlin-multiplatform`, `ml-pytorch`, `nuxt-saas`, `perl`, `rust-api`, `swift-ios`) + **layers técnicos** composables (`react`, …)
- **4 domain overlays** opcionales (`healthcare`, `ai-agent`, `content-creator`, `supply-chain`) — se combinan con cualquier tech stack
- **35 agentes** especializados disponibles en el catálogo `agents/` (`planner`, `architect`, `tdd-guide`, `ui-engineer`, `repo-reviewer`, reviewers por lenguaje, etc.). Tras `make init-project`, `.claude/agents/` contiene un subset filtrado por el stack elegido.
- **Pipeline workflows** (`.claude/pipeline.yaml`) ejecutables vía `/workflow-runner` para orquestación de ciclos de vida (`feature`, `hotfix`, `refactor`)
- **139 skills** disponibles en el catálogo `skills/` (raíz del template) — activadas por stack y copiadas a `.claude/skills/` solo del stack/layers elegidos durante `make init-project`
- **Sistema de memoria** en `.claude/memory/` — persistencia de decisiones, actualizada automáticamente al terminar cada sesión. Lessons (Sintesis.md §1.8) en `.claude/memory/lessons/`
- **MCPs preconfigurados** — Memory + NotebookLM + n8n por defecto. GitHub MCP requiere setup explícito

> ⚠️ **Patrón template/instalado**: la raíz del repo (`agents/`, `skills/`, `stacks/`) es el **catálogo completo**. `.claude/` es el **subset instalado** por proyecto via `make init-project`. Ambos coexisten porque este repo es a la vez template Y proyecto trabajando sobre sí mismo.

## Documentación

| Documento | Descripción |
| --- | --- |
| [`docs/src/instalacion.md`](docs/src/instalacion.md) | Instalación completa paso a paso |
| [`docs/src/primeros-pasos.md`](docs/src/primeros-pasos.md) | Primera sesión de trabajo |
| [`docs/src/inicializar-proyecto.md`](docs/src/inicializar-proyecto.md) | Inicializar un nuevo proyecto |
| [`docs/src/referencia.md`](docs/src/referencia.md) | Referencia de comandos y estructura |
| [`docs/src/stacks/`](docs/src/stacks/) | Guías por stack tecnológico |
