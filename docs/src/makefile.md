# Referencia del Makefile

El Makefile es el panel de control del template. Permite instalar, inicializar proyectos, activar MCPs y verificar la configuración con un solo comando.

Para ver todos los targets disponibles:

```bash
make help
```

---

## Setup y verificación

### `make setup`

Configura los git hooks del template. Ejecutar una sola vez al clonar.

```bash
make setup
```

Lo que hace:

1. Configura git para usar la carpeta `.githooks` (`git config core.hooksPath .githooks`)
2. Muestra los pasos siguientes para instalar los plugins dentro de Claude Code

### `make install`

Instala la configuración global en `~/.claude/`. Ejecutar **una vez por máquina**.

```bash
make install
```

Lo que hace:

1. Copia `rules/*.md` → `~/.claude/rules/common/`
   Las 12 reglas universales (coding-style, security, git-workflow, testing, orchestration...) quedan **siempre activas** en todos los proyectos.

2. Copia `agents/*.md` → `~/.claude/agents/`
   Los 22 agentes especializados quedan disponibles en todos los proyectos como subprocesos autónomos.

3. **No copia skills** — Las skills se activan por stack con `make init-project` en cada proyecto. Solo se copian las relevantes para ese stack a `project/.claude/commands/`.

4. Copia `hooks/session-consolidate.sh` → `~/.claude/hooks/`
   El hook que revisa el trabajo de la sesión y actualiza `.claude/memory/` automáticamente al terminar.

5. Copia `settings.json` → `~/.claude/settings.json` (solo si no existe)
   Configura modelo, tokens, permisos y el Stop hook preconfigurados para todos los proyectos.

### `make check`

Verifica que todo está correctamente configurado. Útil después de instalar o para diagnosticar problemas.

```bash
make check
```

Comprueba en cinco secciones:

- Instalación global (`~/.claude/`): reglas, agentes, hook, settings
- Este repositorio (`.claude/`): git hooks, archivos críticos, MCPs
- MCPs opcionales: notebooklm
- Sincronización de agentes: conteo source/local/global
- Scripts ops/: herramientas de compilación presentes

Ejemplo de salida correcta:

```text
Verificando configuracion...

── Instalacion global (~/.claude/) ──────────────────
  ✅ settings.json global
  ✅ Reglas comunes globales (12 archivos)
  ✅ Agentes globales (22 agentes)
  ✅ Hook de consolidacion de memoria

── Este repositorio (.claude/) ──────────────────────
  ✅ Git hooks configurados
  ✅ .claude/settings.json
  ✅ .claude/CLAUDE.md
  ✅ .mcp.json

── MCPs opcionales ──────────────────────────────────
  ✅ NotebookLM MCP instalado

── Sincronización de agentes ────────────────────────
  Fuente: 22 agentes en agents/
  Local:  22 agentes en .claude/agents/ (compilados con skills del stack activo)
  Global: 22 agentes en ~/.claude/agents/
  ✅ Agentes fuente disponibles

── ops/ scripts ─────────────────────────────────────
  ✅ compile-agents.py
  ✅ detect-stack.py
  ✅ audit-task.sh
```

Si ves `❌` en la sección global, ejecuta `make install` y reinicia Claude Code.

---

## Control de MCPs

Los MCPs (Model Context Protocol servers) se configuran en `.mcp.json`. Cada servidor activo carga herramientas en el contexto de Claude — activar demasiados reduce la ventana de contexto disponible.

### `make activate-notebooklm`

Activa el MCP de NotebookLM para el proyecto actual.

```bash
make activate-notebooklm
# Reinicia Claude Code después para que tenga efecto
```

NotebookLM tiene 35 herramientas. Úsalo cuando necesites investigar documentación externa o crear/consultar notebooks. Desactívalo cuando termines para recuperar espacio de contexto.

**Prerequisito:** Haber ejecutado `nlm auth login` durante la instalación.

### `make deactivate-notebooklm`

Desactiva NotebookLM y recupera ~35 herramientas de contexto.

```bash
make deactivate-notebooklm
```

### `make activate-n8n`

Activa el MCP de n8n para automatizaciones de workflows.

```bash
make activate-n8n
# Reinicia Claude Code después
```

### `make deactivate-n8n`

Desactiva n8n.

```bash
make deactivate-n8n
```

---

## Git Hooks

### `make hooks-install`

Activa los git hooks. Equivalente a `git config core.hooksPath .githooks`.

```bash
make hooks-install
```

Los hooks activos:

- **pre-commit**: Linting automático (Biome para JS/TS, Ruff para Python) + detección de secrets antes de cada commit
- **pre-push**: Tests completos antes de cada push

### `make hooks-uninstall`

Desactiva los git hooks temporalmente (modo relajado).

```bash
make hooks-uninstall
```

Para restaurarlos: `make hooks-install`.

También puedes saltarte los hooks para un commit/push específico sin desinstalarlos:

```bash
git commit --no-verify
git push --no-verify
```

---

## Proyectos

### `make new-project`

Muestra las instrucciones para inicializar un proyecto existente con el god-mode.

```bash
make new-project
```

Salida:

```text
Flujo para usar god-mode en un proyecto existente:

  1. Instalacion global (una vez por maquina):
     make install

  2a. Modo automatico (detecta stack y configura):
      make setup-project PROJECT=/ruta/al/proyecto

  2b. Modo manual (stack explicito):
      make init-project STACK=laravel-react PROJECT=/ruta/al/proyecto

  2c. Con domain overlay (opcional):
      make init-project STACK=laravel-react DOMAIN=healthcare PROJECT=/ruta

  3. Personalizar el contexto del proyecto:
     Edita /ruta/al/proyecto/.claude/CLAUDE.md
     → Reemplaza los [PLACEHOLDER] con el contexto real del proyecto

  Stacks disponibles: make list-stacks
```

---

## Control de stacks

### `make list-stacks`

Lista los stacks disponibles en el directorio `stacks/`.

```bash
make list-stacks
```

Salida:

```text
Stacks disponibles:

  cpp                  C++20 — CMake + GoogleTest
  flutter              Flutter 3 — Dart + Material/Cupertino
  go-api               Go — API REST o microservicio + PostgreSQL
  java-springboot      Java — Spring Boot 3 + PostgreSQL + Maven/Gradle
  kotlin-multiplatform Kotlin — Ktor backend + Compose Multiplatform + Android
  laravel-react        Laravel 13 (API REST) + React 19 (SPA) + Sanctum
  ml-pytorch           Machine Learning — PyTorch + Python + CUDA
  nextjs-saas          Next.js 15 (App Router) + Supabase + Stripe
  nuxt-saas            Nuxt 4 — Vue 3 + Nitro + PostgreSQL
  odoo                 Odoo 19 — módulos Python + XML + OWL frontend + PostgreSQL 17
  perl                 Perl 5.36+ — Mojolicious/Dancer2 + PostgreSQL
  python-api           Python API — Django REST Framework o FastAPI + PostgreSQL
  rust-api             Rust — Axum/Actix Web + PostgreSQL
  swift-ios            Swift — SwiftUI + iOS/macOS/visionOS

Uso: make dev-stack STACK=laravel-react
```

### `make list-domains`

Lista los domain overlays disponibles.

```bash
make list-domains
```

Salida:

```text
Domain overlays disponibles:

  ai-agent             AI Agent Engineering — Multi-agent systems, evals, LLM pipelines
  content-creator      Content Creator — Escritura, social, video, newsletters
  healthcare           Healthcare — EMR/CDSS + HIPAA compliance
  supply-chain         Supply Chain — Logistics, inventory, carrier management

Uso: make init-project STACK=laravel-react DOMAIN=healthcare PROJECT=/ruta
```

### `make init-project STACK=nombre PROJECT=/ruta [DOMAIN=nombre]`

Inicializa un proyecto externo con un stack concreto. Opcionalmente acepta `DOMAIN=` para añadir un domain overlay.

```bash
make init-project STACK=laravel-react PROJECT=/ruta/al/proyecto

# Con domain overlay
make init-project STACK=laravel-react DOMAIN=healthcare PROJECT=/ruta/al/proyecto
```

Lo que hace en el proyecto de destino:

1. Copia `stacks/laravel-react/rules/*.md` → `project/.claude/rules/stack/`
   Las convenciones del stack quedan **siempre activas** en ese proyecto.

2. Si hay `DOMAIN=`, copia también `domains/<DOMAIN>/rules/*.md` al mismo directorio.

3. **Compila agentes** con `ops/compile-agents.py`: embebe skills del stack (+ domain si aplica) en cada agente.

4. Copia comandos standalone al proyecto: `skills/<cmd>/SKILL.md` → `.claude/commands/<cmd>.md`

5. Copia `stacks/common/workflows/*.yml` → `project/.github/workflows/`
   GitHub Actions agnósticos de stack: PR review, issue triage y audit semanal. Requiere añadir `ANTHROPIC_API_KEY` en **Settings → Secrets**.

6. Crea `project/.claude/CLAUDE.md` desde la plantilla del stack
   Solo si no existe — nunca sobreescribe un CLAUDE.md existente.

Salida:

```text
Inicializando stack 'laravel-react' en /ruta/al/proyecto...
  ✅ Stack rules copiadas a /ruta/al/proyecto/.claude/rules/stack/
  Compilando agentes con skills embebidas...
  ✅ Agentes compilados (22 agentes con skills del stack)
  ✅ Comandos: /jedi-review, /git-workflow, /design-md, ...
  ✅ GitHub Actions copiados a .github/workflows/ — añade ANTHROPIC_API_KEY en Settings → Secrets
  ✅ CLAUDE.md creado — edita los [PLACEHOLDER] con el contexto del proyecto

Proyecto listo.
```

### `make dev-stack STACK=nombre`

Activa un stack en el propio repositorio del template. Útil para trabajar en el template mismo.

```bash
make dev-stack STACK=laravel-react
```

A diferencia de `init-project`, actúa sobre el directorio actual (`.claude/` del template).

---

## Triggers programados

Los triggers definen trabajos autónomos que Claude Code ejecuta según un cron. Se configuran como archivos YAML en `ops/triggers/` y se activan una vez mediante comandos `/schedule create` dentro de Claude Code.

### `make triggers-setup`

Imprime los comandos `/schedule create` para activar todos los triggers definidos en `ops/triggers/`.

```bash
make triggers-setup
```

Salida:

```text
Triggers disponibles en ops/triggers/:

  weekly-security-audit      → /schedule create weekly-security-audit --cron "0 9 * * 1" ...
  weekly-docs-health         → /schedule create weekly-docs-health --cron "0 9 * * 2" ...
  daily-memory-consolidation → /schedule create daily-memory-consolidation --cron "0 7 * * *" ...

Pega cada línea dentro de Claude Code para activar el trigger.
Usa /schedule list para ver los activos y /schedule delete <nombre> para eliminar uno.
```

**Prerequisito:** Tener Antigravity activo en la cuenta de Claude.

### `make triggers-list`

Lista los triggers definidos en `ops/triggers/` con su schedule y descripción.

```bash
make triggers-list
```

---

## Proyectos externos (análisis)

### `make load-project URL=...`

Clona un proyecto externo en `projects/<nombre>` para análisis.

```bash
make load-project URL=https://github.com/usuario/repo.git
```

### `make analyze-project NAME=...`

Genera un `REPORT.md` completo del proyecto cargado: stack, arquitectura, seguridad y calidad de código.

```bash
make analyze-project NAME=nombre-del-proyecto
```

---

## Resumen de todos los targets

| Target | Descripción |
| --- | --- |
| `make help` | Lista todos los targets con descripción |
| `make setup` | Configura git hooks del template (una vez) |
| `make install` | Instala agentes, reglas y comandos en `~/.claude/` (una vez por máquina) |
| `make check` | Verifica instalación global y local |
| `make list-stacks` | Lista los 14 stacks disponibles |
| `make list-domains` | Lista los 4 domain overlays disponibles |
| `make setup-project PROJECT=/ruta` | Auto-detecta stack e inicializa proyecto (modo automático) |
| `make init-project STACK=x PROJECT=/ruta [DOMAIN=y]` | Inicializa proyecto externo con un stack (+ domain opcional) |
| `make dev-stack STACK=nombre` | Activa un stack en el template para desarrollo |
| `make new-project` | Instrucciones para inicializar un proyecto |
| `make activate-notebooklm` | Activa NotebookLM MCP |
| `make deactivate-notebooklm` | Desactiva NotebookLM (ahorra ~35 herramientas) |
| `make activate-n8n` | Activa n8n MCP para automatizaciones |
| `make deactivate-n8n` | Desactiva n8n |
| `make hooks-install` | Activa los git hooks |
| `make hooks-uninstall` | Desactiva los git hooks |
| `make setup-labels` | Crea en GitHub las labels necesarias para los agent workflows |
| `make workflows-status` | Muestra los GitHub Actions instalados y el secret requerido |
| `make triggers-setup` | Imprime comandos `/schedule create` para activar triggers en Antigravity |
| `make triggers-list` | Lista los triggers definidos en `ops/triggers/` |
| `make load-project URL=...` | Clona proyecto externo para análisis |
| `make analyze-project NAME=...` | Genera REPORT.md de un proyecto cargado |
