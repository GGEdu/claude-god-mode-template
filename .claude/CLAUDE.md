# Claude God Mode Template

## Stack
- **Lenguaje principal**: Bash, YAML, Makefile, shell scripts
- **Docs**: VitePress (Markdown en `docs/src/`)
- **Tests**: Sin framework — verificación manual con `make check`
- **Linter**: markdownlint (docs)

## Arquitectura

Sistema de configuración para Claude Code. No es una app — es un conjunto de archivos
que se instalan en `~/.claude/` (global) o en `.claude/` del proyecto (local).

Tres capas:
1. **Global** (`~/.claude/`) — `make install` — agents, common rules, hooks, settings
2. **Stack** (`.claude/rules/stack/`, `.claude/commands/`, `.claude/agents/`) — `make init-project` — gitignored, generado
3. **Proyecto** (`.claude/CLAUDE.md`, `.claude/memory/`) — el usuario lo rellena

## Convenciones
- Commits: Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`)
- `agents/` es la fuente de verdad — nunca editar solo `.claude/agents/`
- `stacks/*/stack.yaml` declara qué se activa — `ops/compile-agents.py` compila agentes con skills embebidas
- Los skills NO van globalmente — solo por stack vía `init-project`
- `domains/*/domain.yaml` añade skills extra a los agentes del tech stack (merge, no reemplazo)

## Comandos críticos para este repo
- `make check` — verifica instalación global y sincronización de agentes
- `make list-stacks` — stacks disponibles
- `make list-domains` — domain overlays disponibles
- `make dev-stack STACK=x` — activa un stack en ESTE repo para desarrollarlo
- `make dev-stack STACK=x DOMAIN=y` — stack + domain overlay
- `make install` — instala todo globalmente en `~/.claude/`

## Estructura del proyecto

```text
claude-god-mode-template/
├── agents/           ← FUENTE DE VERDAD — 21 agentes
├── stacks/           ← 14 tech stacks (cada uno con stack.yaml, rules/, CLAUDE.md)
├── domains/          ← 4 domain overlays (healthcare, ai-agent, content-creator, supply-chain)
├── skills/           ← 130 skills (se activan por stack)
├── rules/common/     ← 11 reglas universales (fuente de verdad — make install las copia a ~/.claude/)
├── ops/              ← compile-agents.py, detect-stack.py, audit-task.sh
├── hooks/            ← session-consolidate.sh (Stop hook global)
├── docs/patterns/    ← 7 skills de referencia (no activables)
├── .claude/
│   ├── CLAUDE.md     ← Este archivo
│   ├── settings.json ← Permisos, modelo, hooks
│   ├── memory/       ← Contexto de sesión (gitignored *.md)
│   ├── agents/       ← Agentes compilados (gitignored — generados)
│   ├── commands/     ← Comandos slash (gitignored — generados)
│   └── rules/        ← Reglas del stack activo (gitignored — generadas)
├── docs/src/         ← Documentación VitePress (español)
└── Makefile          ← Panel de control
```

## Variables de entorno relevantes
- `MAX_THINKING_TOKENS` — límite de tokens de razonamiento (default: 10000)
- `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` — compresión de contexto (default: 50%)
- `CLAUDE_CODE_SUBAGENT_MODEL` — modelo para subagentes (default: haiku)
