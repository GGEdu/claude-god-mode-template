# Instalación

Dos partes: **setup global** (una vez por máquina) y **setup por proyecto** (una vez por proyecto).

---

## Prerequisitos

```bash
claude --version   # v2.1.0 o superior
node --version     # v18 o superior
git --version
```

Si falta Claude Code:

```bash
npm install -g @anthropic-ai/claude-code
```

Necesitas cuenta Anthropic con plan **Pro**, **Max** o **API** activo.

---

## Parte 1 — Setup global (una vez por máquina)

### Paso 1 — Clonar el template

```bash
git clone https://github.com/tu-usuario/claude-god-mode-template
cd claude-god-mode-template
```

### Paso 2 — Instalar el god-mode globalmente

```bash
make install
```

Copia a `~/.claude/` de una vez:

- 12 reglas comunes (coding-style, security, testing, git-workflow, orchestration...)
- 22 agentes especializados (planner, tdd-guide, code-reviewer, github-orchestrator...)
- Hook `session-consolidate.sh` — actualiza `.claude/memory/` al terminar cada sesión
- `settings.json` con modelo, tokens y permisos preconfigurados

::: tip Skills por proyecto, no globales
Las 140 skills (slash commands) **no se instalan globalmente**. Se activan por stack cuando inicializas un proyecto: `make init-project STACK=laravel PROJECT=/ruta`. Los agentes se **compilan** con skills embebidas del stack — el developer no necesita invocar skills manualmente.
:::

::: tip settings.json ya existe
Si ya tienes `~/.claude/settings.json`, `make install` no lo sobreescribe. Verifica manualmente que incluye el Stop hook apuntando a `$HOME/.claude/hooks/session-consolidate.sh`.
:::

### Paso 3 — Verificar la instalación global

```bash
make check
```

Salida esperada:

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

Si ves `❌` en la sección global → ejecuta `make install` y reinicia Claude Code.

### Paso 4 (opcional) — NotebookLM MCP

Permite usar notebooks de Google como base de conocimiento. Solo actívalo cuando lo necesites — consume 35 herramientas del contexto.

```bash
uv tool install notebooklm-mcp-cli
nlm setup add claude-code
nlm auth login    # abre el navegador para autenticar con Google
nlm doctor        # verifica que todo funciona
```

---

## Parte 2 — Setup por proyecto (una vez por proyecto)

### Paso 5 — Inicializar el proyecto con el stack

Desde la raíz del template:

```bash
# Ver stacks disponibles
make list-stacks

# Ver domain overlays disponibles (opcional)
make list-domains

# Inicializar un proyecto existente
make init-project STACK=laravel PROJECT=/ruta/al/proyecto

# Con layer frontend (ej: React SPA)
make init-project STACK=laravel LAYERS=react PROJECT=/ruta/al/proyecto

# Con domain overlay (ej: healthcare para apps médicas)
make init-project STACK=laravel LAYERS=react DOMAIN=healthcare PROJECT=/ruta/al/proyecto
```

::: warning Rutas con espacios
Si la ruta del proyecto contiene espacios (p.ej. `Desarrollo CEEDCV/mi-app`), usa siempre comillas dobles alrededor del valor de `PROJECT`:

```bash
make init-project STACK=laravel-livewire PROJECT="/ruta/con espacios/mi-proyecto"
```

:::

Stacks disponibles más habituales:

| Stack | Descripción |
| --- | --- |
| `laravel` + `LAYERS=react` | Laravel (API REST) + React 19 (SPA) + Sanctum |
| `laravel-livewire` | Laravel (monolito) + Livewire 4 + Alpine.js + TailwindCSS |
| `nextjs-saas` | Next.js 15 (App Router) + Supabase + Stripe |
| `python-api` | Django REST Framework o FastAPI + PostgreSQL |
| `go-api` | Go — API REST + PostgreSQL |

Salida:

```text
Inicializando stack 'laravel' + layer 'react' en /ruta/al/proyecto...
  ✅ Stack rules copiadas a /ruta/al/proyecto/.claude/rules/stack/
  Compilando agentes con skills embebidas...
  ✅ Agentes compilados (22 agentes con skills del stack)
  ✅ Comandos: /jedi-review, /git-workflow, /design-md, ...
  ✅ GitHub Actions copiados a .github/workflows/ — añade ANTHROPIC_API_KEY en Settings → Secrets
  ✅ CLAUDE.md creado — edita los [PLACEHOLDER] con el contexto del proyecto

Proyecto listo.
```

### Paso 6 — Personalizar el CLAUDE.md del proyecto

```bash
# Abre el archivo generado
code /ruta/al/proyecto/.claude/CLAUDE.md
```

Rellena los `[PLACEHOLDER]` con el contexto real: nombre del proyecto, arquitectura, decisiones de seguridad, convenciones del equipo. Claude lee este archivo al iniciar cada sesión.

### Paso 7 — Configurar el token de GitHub

Crea `.env` en la raíz del proyecto (no se sube a git):

```bash
echo "GITHUB_TOKEN=ghp_tu_token_aqui" > .env
```

Genera el token en: GitHub → Settings → Developer settings → Personal access tokens (scope: `repo`).

### Paso 8 — Verificación completa dentro del proyecto

Entra al proyecto e inicia Claude Code:

```bash
cd /ruta/al/proyecto
claude
```

Claude lee `.claude/CLAUDE.md` automáticamente al iniciar. Si hay error de contexto, revisa que `.claude/CLAUDE.md` existe y tiene contenido real (no solo `[PLACEHOLDER]`).

---

## Verificación rápida — checklist completo

| Verificación | Comando |
| --- | --- |
| Instalación global | `make check` desde el template |
| Claude Code arranca | `claude` en el proyecto |
| Comandos disponibles | `/jedi-review` o `"Planifica: [feature]"` dentro de Claude Code |
| Agentes disponibles | "Usa el agente planner para..." |
| Hook activo | Termina la sesión → revisa `.claude/memory/` |
| Stack configurado | El CLAUDE.md no tiene `[PLACEHOLDER]` sin rellenar |
