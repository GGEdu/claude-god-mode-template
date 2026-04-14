# Claude God Mode Template

Template maestro para proyectos con Claude Code: rules siempre activas, stacks configurables, sistema de memoria, agentes especializados y MCPs preconfigurados.

## Prerequisitos

- [Claude Code](https://docs.anthropic.com/claude-code) v2.1.0+
- Node.js v18+
- Python v3.10+ y [uv](https://astral.sh/uv)
- Git
- Cuenta Anthropic con plan Pro, Max o API activo

## Quick Start

```bash
# 1. Clonar
git clone https://github.com/ggarrido/claude-god-mode-template.git
cd claude-god-mode-template

# 2. Instalar globalmente (agentes, reglas, hook de memoria)
make install

# 3. Inicializar un proyecto con un stack (+ domain overlay opcional)
make init-project STACK=laravel-react PROJECT=/ruta/al/proyecto
make init-project STACK=python-api DOMAIN=healthcare PROJECT=/ruta/al/proyecto
```

Sigue la guía completa en [`docs/src/instalacion.md`](docs/src/instalacion.md).

## Lo que incluye

- **Rules universales** en `.claude/rules/common/` — siempre activas en cada sesión
- **14 tech stacks** configurables (`laravel-react`, `nextjs-saas`, `python-api`, `go-api`, `odoo`, `cpp`, `flutter`, `java-springboot`, `kotlin-multiplatform`, `ml-pytorch`, `nuxt-saas`, `perl`, `rust-api`, `swift-ios`)
- **4 domain overlays** opcionales (`healthcare`, `ai-agent`, `content-creator`, `supply-chain`) — se combinan con cualquier tech stack
- **21 agentes** especializados con skills embebidas por compilación (`planner`, `architect`, `tdd-guide`, `security-reviewer`, etc.)
- **9 Stack Orchestrators** (Pipeline Managers) actuando como Tech Leads para delegación automática del ciclo de vida (`laravel-orchestrator`, `django-orchestrator`, etc.)
- **130+ skills** organizadas en `skills/` — activadas por stack, no globalmente
- **Sistema de memoria** en `.claude/memory/` — persistencia de decisiones, actualizada automáticamente al terminar cada sesión
- **MCPs preconfigurados** — GitHub activo por defecto, NotebookLM y n8n opcionales

## Documentación

| Documento | Descripción |
| --- | --- |
| [`docs/src/instalacion.md`](docs/src/instalacion.md) | Instalación completa paso a paso |
| [`docs/src/primeros-pasos.md`](docs/src/primeros-pasos.md) | Primera sesión de trabajo |
| [`docs/src/nuevo-proyecto.md`](docs/src/nuevo-proyecto.md) | Inicializar un nuevo proyecto |
| [`docs/src/referencia.md`](docs/src/referencia.md) | Referencia de comandos y estructura |
| [`docs/src/stacks/`](docs/src/stacks/) | Guías por stack tecnológico |
