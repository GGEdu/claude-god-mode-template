# Claude God Mode Template

## Stack
- **Lenguaje principal**: Bash, YAML, Makefile, shell scripts
- **Docs**: VitePress (Markdown en `docs/src/`)
- **Tests**: Sin framework — verificación manual con `make check`
- **Linter**: markdownlint (docs)

## Arquitectura

Sistema de configuración para Claude Code. No es una app — es un conjunto de archivos
que se instalan en `~/.claude/` (global) o en `.claude/` del proyecto (local).

Cuatro capas:
1. **Global** (`~/.claude/`) — `make install` — agents, common rules, hooks, settings
2. **Stack** (`.claude/rules/stack/`, `.claude/commands/`, `.claude/agents/`) — `make init-project` — gitignored, generado
3. **Layer** (`layers/*/`) — overlays técnicos composables (frontend, infra) — se aplican con `LAYERS=`
4. **Proyecto** (`.claude/CLAUDE.md`, `.claude/memory/`) — el usuario lo rellena

## Convenciones
- Commits: Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`)
- `agents/` es la fuente de verdad — nunca editar solo `.claude/agents/`
- `stacks/*/stack.yaml` declara qué se activa — `ops/compile-agents.py` compila agentes con skills embebidas
- Los skills NO van globalmente — solo por stack vía `init-project`
- `domains/*/domain.yaml` añade skills de negocio (healthcare, ai-agent...) — merge, no reemplazo
- `layers/*/layer.yaml` añade skills técnicos (frontend, infra) — mismo mecanismo que domains
- Los layers pueden añadir agentes nuevos al stack (ej. `typescript-reviewer` en un stack Python)

## Comandos críticos para este repo
- `make check` — verifica instalación global y sincronización de agentes
- `make list-stacks` — stacks disponibles
- `make list-layers` — layers técnicos disponibles
- `make list-domains` — domain overlays disponibles
- `make dev-stack STACK=x` — activa un stack en ESTE repo para desarrollarlo
- `make dev-stack STACK=x LAYERS=react` — stack + layer técnico
- `make dev-stack STACK=x DOMAIN=y` — stack + domain overlay
- `make install` — instala todo globalmente en `~/.claude/`

## Estructura del proyecto

```text
claude-god-mode-template/
├── agents/           ← FUENTE DE VERDAD — 36 agentes
├── stacks/           ← 13 tech stacks (cada uno con stack.yaml, rules/, CLAUDE.md)
├── layers/           ← Layers técnicos composables (react, ...)
├── domains/          ← 4 domain overlays (healthcare, ai-agent, content-creator, supply-chain)
├── skills/           ← 146 skills (se activan por stack)
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

## Cómo usar el agente repo-reviewer

El agente `repo-reviewer` tiene un flujo formal de dos fases y **requiere estar compilado** en `.claude/agents/` para funcionar correctamente.

### Prerequisito: compilar el agente

```bash
make dev-stack STACK=<stack-activo>
# o si ya tienes un stack activo:
make install
```

Verifica que existe: `ls .claude/agents/repo-reviewer.md`

### Invocar el agente

Dentro de una sesión Claude Code:

```
"Usa el agente repo-reviewer para evaluar https://github.com/<owner>/<repo>"
```

**NO invocar como `general-purpose` agent** — el agente real usa `gh` CLI con herramientas restringidas (`Read, Bash, Glob, Grep`) y ejecuta el flujo Haiku screening → Sonnet deep-dive.

### Qué hace automáticamente

1. Lee `ops/sessions/repo-evaluations.md` para evitar re-evaluaciones
2. Fase 1 (Haiku): metadata + README → score/100
3. Si score ≥ 50 → Fase 2 (Sonnet): deep-dive de estructura y archivos clave
4. **Guarda la entrada en `ops/sessions/repo-evaluations.md`** con formato estandarizado
5. Propone templates de skills/agents/rules a crear (no los crea — solo propone)

### Si el agente no está compilado (workaround)

Claude puede ejecutar el flujo manualmente usando `Bash` + `gh` CLI:

```
"Ejecuta el flujo del repo-reviewer para <URL> usando gh CLI directamente y 
guarda el resultado en ops/sessions/repo-evaluations.md"
```

En este caso, Claude debe guardar el resultado **manualmente** siguiendo el formato del archivo.

## Integración de everything-claude-code (ECC)

Repo evaluado: `https://github.com/affaan-m/everything-claude-code` (Score 82/100, Tier INCLUDE).
Integrado el 2026-04-16. Todos los activos están en `agents/` y `skills/`.

### Skills integradas (universales — activas en todos los stacks)

| Skill | Ubicación | Propósito |
|-------|-----------|-----------|
| `council` | `skills/council/SKILL.md` | Decisiones adversariales con 4 voces: Architect, Skeptic, Pragmatist, Critic |
| `santa-method` | `skills/santa-method/SKILL.md` | Verificación dual independiente con convergence loop (max 3 iter) |
| `agent-introspection-debugging` | `skills/agent-introspection-debugging/SKILL.md` | Auto-debugging estructurado en 4 fases |
| `hookify-rules` | `skills/hookify-rules/SKILL.md` | Sintaxis y patrones para escribir reglas Hookify |

Estas skills se inyectan en todos los stacks vía `stack.yaml`:
- `council` + `agent-introspection-debugging` → `planner.skills`
- `santa-method` → `code-reviewer.skills`
- `hookify-rules` → `harness-optimizer.skills`

### Agentes integrados (stack-específicos)

**Language Reviewers** — activos en su stack correspondiente:

| Agente | Stack | Herramientas |
|--------|-------|--------------|
| `go-reviewer` | go-api | `golangci-lint`, concurrencia, seguridad |
| `java-reviewer` | java-springboot | checkstyle, Maven/Gradle, JPA, Spring patterns |
| `kotlin-reviewer` | kotlin-multiplatform | detekt, Compose, coroutines, KMP |
| `python-reviewer` | python-api, ml-pytorch, odoo | mypy, ruff, PEP8, type hints |
| `cpp-reviewer` | cpp | cppcheck, clang-tidy, C++20 idioms |
| `csharp-reviewer` | (ninguno aún — listo para activar) | dotnet build, async patterns, nullable |
| `flutter-reviewer` | flutter | flutter analyze, Dart, widget patterns |

**Build Resolvers** — activos en su stack correspondiente:

| Agente | Stack | Alcance |
|--------|-------|---------|
| `go-build-resolver` | go-api | go build, vet, module errors |
| `java-build-resolver` | java-springboot | Maven/Gradle, compilation errors |
| `kotlin-build-resolver` | kotlin-multiplatform | Kotlin/Gradle errors |
| `cpp-build-resolver` | cpp | CMake, linker, template errors |
| `dart-build-resolver` | flutter | pub, build_runner, Flutter errors |

**Meta-agente:**

| Agente | Activación | Propósito |
|--------|-----------|-----------|
| `harness-optimizer` | Todos los stacks | Mejora la configuración del harness (settings.json, stack.yaml, agent quality) |

### Para activar csharp-reviewer en un stack

Si el proyecto es C#/.NET, añadir a `stacks/<stack>/stack.yaml`:

```yaml
agents:
  csharp-reviewer:
    model: sonnet
    skills: [csharp-patterns]
```

Y re-compilar: `make dev-stack STACK=<stack>`

## Variables de entorno relevantes
- `MAX_THINKING_TOKENS` — límite de tokens de razonamiento (default: 10000)
- `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` — compresión de contexto (default: 50%)
- `CLAUDE_CODE_SUBAGENT_MODEL` — modelo para subagentes (default: haiku)
