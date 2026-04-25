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
- **15 tech stacks** configurables (`laravel`, `laravel-livewire`, `nextjs-saas`, `python-api`, `go-api`, `odoo`, `cpp`, `flutter`, `java-springboot`, `kotlin-multiplatform`, `ml-pytorch`, `nuxt-saas`, `perl`, `rust-api`, `swift-ios`) + **layers técnicos** composables (`react`, `requirements-engineering`, …)
- **4 domain overlays** opcionales (`healthcare`, `ai-agent`, `content-creator`, `supply-chain`) — se combinan con cualquier tech stack
- **37 agentes** especializados con skills embebidas por compilación (`planner`, `architect`, `tdd-guide`, `ui-engineer`, `business-analyst`, `change-manager`, `repo-reviewer`, etc.)
- **Pipeline workflows** (`.claude/pipeline.yaml`) ejecutables vía `/workflow-runner` para orquestación de ciclos de vida (`feature`, `hotfix`, `refactor`, `requirements`, `change-review`) con soporte de `parallel_with`, `approval_gate`, `outputs:` y compuertas humanas entre fases
- **141 skills** organizadas en `skills/` — activadas por stack, no globalmente
- **Caveman selectivo** (`skills/caveman/`) — compresión de output 22–87% en agentes de acción (`refactor-cleaner`, `*-build-resolver`, `doc-updater`, `e2e-runner`, `memory-consolidator`, `loop-operator`); excluido de planner/architect/reviewers para preservar auditabilidad
- **Layer `requirements-engineering`** — pipeline de 7 fases (descubrimiento → C4/STRIDE → backlog MoSCoW → diagramas → VitePress → GitHub Issues → gestión de cambios) adaptado de [Maya-AQSS/agentics-extractor-requisitos](https://github.com/Maya-AQSS/agentics-extractor-requisitos); composable sobre cualquier stack
- **Sistema de memoria** en `.claude/memory/` — persistencia de decisiones, actualizada automáticamente al terminar cada sesión
- **MCPs preconfigurados** — GitHub activo por defecto, NotebookLM y n8n opcionales

## Documentación

| Documento | Descripción |
| --- | --- |
| [`docs/src/instalacion.md`](docs/src/instalacion.md) | Instalación completa paso a paso |
| [`docs/src/primeros-pasos.md`](docs/src/primeros-pasos.md) | Primera sesión de trabajo |
| [`docs/src/inicializar-proyecto.md`](docs/src/inicializar-proyecto.md) | Inicializar un nuevo proyecto |
| [`docs/src/referencia.md`](docs/src/referencia.md) | Referencia de comandos y estructura |
| [`docs/src/stacks/`](docs/src/stacks/) | Guías por stack tecnológico |
