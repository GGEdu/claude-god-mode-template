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

# 2. Activar git hooks (obligatorio)
git config core.hooksPath .githooks

# 3. Abrir Claude Code y seguir la guía de instalación
claude
```

Sigue la guía completa en [`docs/src/instalacion.md`](docs/src/instalacion.md).

## Lo que incluye

- **Rules universales** en `.claude/rules/common/` — siempre activas en cada sesión
- **5 stacks** configurables (`laravel-react`, `nextjs-saas`, `python-api`, `odoo`, `go-api`)
- **15 agentes** especializados (`planner`, `architect`, `tdd-guide`, `security-reviewer`, etc.)
- **Sistema de vault** (arscontexta) — segundo cerebro para capturar y conectar conocimiento
- **MCPs preconfigurados** — GitHub y Memory activos por defecto

## Documentación

| Documento | Descripción |
|---|---|
| [`docs/src/instalacion.md`](docs/src/instalacion.md) | Instalación completa paso a paso |
| [`docs/src/primeros-pasos.md`](docs/src/primeros-pasos.md) | Primera sesión de trabajo |
| [`docs/src/nuevo-proyecto.md`](docs/src/nuevo-proyecto.md) | Inicializar un nuevo proyecto |
| [`docs/src/referencia.md`](docs/src/referencia.md) | Referencia de comandos y estructura |
| [`docs/src/stacks/`](docs/src/stacks/) | Guías por stack tecnológico |
