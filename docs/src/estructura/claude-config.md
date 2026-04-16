# Directorio: `.claude/`

La configuración local de Claude Code para este repositorio. Esta capa es **específica del proyecto** — cada proyecto tiene su propio `.claude/` con su CLAUDE.md, reglas y memoria.

> `.claude/agents/`, `.claude/commands/` y `.claude/rules/` están gitignored — son artefactos generados. La fuente de verdad son `agents/`, `stacks/` y `rules/common/` en la raíz del repo.

---

## Estructura

```text
.claude/
├── CLAUDE.md           ← Instrucciones del proyecto para Claude
├── settings.json       ← Permisos, modelo, hooks, variables de entorno
├── memory/             ← Contexto de sesión (gitignored *.md)
├── agents/             ← Agentes compilados (gitignored — generados)
├── commands/           ← Comandos slash (gitignored — generados)
└── rules/              ← Reglas del stack activo (gitignored — generadas)
    └── stack/          ← Ej: laravel.md, react.md (generadas por dev-stack)
```

---

## `CLAUDE.md`

El archivo de instrucciones principal del proyecto. Claude Code lo carga automáticamente al iniciar una sesión en el directorio.

**Estructura mínima recomendada:**

```markdown
# [Nombre del proyecto]

## Stack
- **Backend**: Laravel 13
- **Frontend**: React 19 + TypeScript
- **DB**: MySQL 8

## Arquitectura
[Descripción de qué hace el proyecto]

## Convenciones
- Commits: Conventional Commits
- Tests: mínimo 80% cobertura

## Comandos críticos
- `"Planifica: [descripción]"` — Antes de cualquier feature (activa agente `planner`)
- `/jedi-review` — Para código crítico

## Estructura del proyecto
[árbol de directorios relevante]
```

En stacks con `make init-project`, se copia el `CLAUDE.md` base del stack (`stacks/<stack>/CLAUDE.md`) como punto de partida.

---

## `settings.json`

Configuración de permisos, modelo y hooks para este proyecto.

### Estructura completa de este repo

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "env": {
    "MAX_THINKING_TOKENS": "10000",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "50",
    "CLAUDE_CODE_SUBAGENT_MODEL": "haiku"
  },
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test*)",
      "Bash(npm run build)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(git log *)",
      "Bash(python -m pytest*)",
      "Bash(ruff check*)",
      "Bash(ruff format*)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Bash(git push --force*)",
      "Bash(rm -rf /*)"
    ]
  },
  "model": "sonnet",
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "$HOME/.claude/hooks/session-consolidate.sh"
      }]
    }]
  }
}
```

### Variables de entorno clave

| Variable | Valor | Efecto |
|----------|-------|--------|
| `MAX_THINKING_TOKENS` | `10000` | Limita tokens de razonamiento extendido |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | `50` | Compacta contexto al 50% de capacidad |
| `CLAUDE_CODE_SUBAGENT_MODEL` | `haiku` | Subagentes usan Haiku (más económico) |

---

## `rules/common/` — Las 12 reglas universales

> **Fuente de verdad:** `rules/common/` en la raíz del repo (no dentro de `.claude/`). `make install` las copia a `~/.claude/rules/common/`. Claude Code las carga automáticamente en todos los proyectos del usuario.

| Archivo | Contenido |
|---------|-----------|
| `agents.md` | Inventario de agentes disponibles y cuándo usarlos. Orquestación paralela. |
| `code-review.md` | Cuándo hacer review (triggers), severidades (CRITICAL/HIGH/MEDIUM/LOW), agentes a usar. |
| `coding-style.md` | Inmutabilidad, organización de archivos (200-400 líneas), manejo de errores, validación. |
| `development-workflow.md` | Pipeline completo: Research → Plan → TDD → Code Review → Commit. |
| `git-workflow.md` | Formato de commits (Conventional Commits), proceso de PRs. |
| `hooks.md` | Tipos de hooks (PreToolUse, PostToolUse, Stop), buenas prácticas de TodoWrite. |
| `output-efficiency.md` | Sin openers/closers, lead with code, prefer edit over rewrite, reglas para subagentes. |
| `patterns.md` | Repository Pattern, API Response Format, Skeleton Projects. |
| `performance.md` | Selección de modelo (Haiku/Sonnet/Opus), gestión de contexto, Extended Thinking. |
| `orchestration.md` | GitHub Actions, Antigravity triggers, github-orchestrator, modos de ejecución (local/CI/scheduled). |
| `security.md` | Checklist pre-commit, gestión de secretos, protocolo de respuesta a vulnerabilidades. |
| `testing.md` | 80% cobertura mínima, flujo TDD (RED-GREEN-REFACTOR), 3 tipos de tests. |

### `.claude/rules/stack/` (gitignored — generado)

Reglas específicas del framework activo. Se generan con `make dev-stack` o `make init-project` y son locales al proyecto (nunca committeadas):

- `laravel.md` — Controladores delgados, FormRequest, API Resources, eager loading
- `react.md` — SWR/React Query, React Hook Form, Zod, rutas protegidas
- `nextjs.md` — App Router, Server Components, Server Actions, middleware
- `supabase.md` — RLS, SSR client, webhooks Stripe
- _(uno por stack activo — fuente en `stacks/<stack>/rules/`)_

---

## `memory/`

Archivos de contexto de sesión generados automáticamente por `hooks/session-consolidate.sh` al finalizar cada sesión. **Gitignored** — son efímeros.

```text
.claude/memory/
├── agents.md           ← Inventario de agentes y skills activos
├── skills.md           ← Clasificación de skills del stack actual
├── project_overview.md ← Estado del proyecto, decisiones recientes
├── improvement-plan.md ← Hoja de ruta activa (no migrar a docs)
└── audit-log.md        ← Log de auditorías post-tarea (audit-task.sh)
```

**Los archivos de memoria son complementarios a esta documentación**, no sustitutos. El contenido estable (inventarios, clasificaciones) vive en `docs/src/estructura/`. La memoria contiene solo el contexto específico de la sesión actual: qué se hizo, decisiones tomadas, estado en curso.

---

## Dos niveles de configuración

| Nivel | Ubicación | Instalado con | Alcance |
|-------|-----------|---------------|---------|
| **Global** | `~/.claude/` | `make install` | Todos los proyectos del usuario |
| **Proyecto** | `.claude/` | `make init-project` | Solo este proyecto |

El nivel de proyecto hereda el global y puede sobreescribir configuraciones específicas. Las reglas en `rules/common/` (fuente de verdad en la raíz del repo) se instalan globalmente vía `make install`.
