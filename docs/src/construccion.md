# Arquitectura interna

> Esta página es para quienes mantienen o extienden el god-mode template. Si solo quieres usarlo en un proyecto, ve a [Instalación](/instalacion).

---

## Estructura del repositorio

```text
claude-god-mode-template/
├── agents/                  ← Fuente de verdad de los 38 agentes (make install los copia a ~/.claude/agents/)
├── hooks/
│   └── session-consolidate.sh  ← Hook de memoria (make install → ~/.claude/hooks/)
├── skills/                  ← 139 skills organizadas por nombre
│   ├── laravel-patterns/
│   │   └── SKILL.md
│   ├── jedi-review/
│   │   └── SKILL.md
│   └── ...
├── rules/                   ← 12 reglas universales (fuente de verdad — make install → ~/.claude/rules/common/)
├── stacks/                  ← 15 tech stacks
│   ├── common/
│   │   └── workflows/       ← GitHub Actions agnósticos de stack (init-project los copia a .github/workflows/)
│   │       ├── agent-pr-review.yml
│   │       ├── agent-issue-triage.yml
│   │       └── agent-scheduled-audit.yml
│   ├── laravel/
│   │   ├── stack.yaml       ← Declara agentes con skills, comandos y MCPs
│   │   ├── CLAUDE.md        ← Plantilla de CLAUDE.md para el proyecto
│   │   └── rules/           ← Reglas específicas del stack (solo backend)
│   │       └── laravel.md
│   ├── nextjs-saas/
│   └── ...
├── layers/                  ← Layers técnicos composables (se aplican sobre cualquier stack)
│   ├── react/
│   │   ├── layer.yaml       ← Skills, comandos y reglas del layer
│   │   ├── CLAUDE-append.md ← Contexto adicional para CLAUDE.md
│   │   └── rules/           ← Reglas del layer (React/TypeScript)
│   │       ├── react.md
│   │       └── ...
│   └── ...
├── domains/                 ← 4 domain overlays (se combinan con cualquier stack)
│   ├── healthcare/
│   │   ├── domain.yaml      ← Skills extra para agentes del stack
│   │   ├── rules/           ← Reglas del dominio
│   │   └── CLAUDE-append.md ← Contexto adicional para CLAUDE.md
│   ├── ai-agent/
│   ├── content-creator/
│   └── supply-chain/
├── ops/                     ← Scripts de operaciones
│   ├── compile-agents.py    ← Compila agentes + skills embebidas
│   ├── detect-stack.py      ← Auto-detecta stack por archivos
│   ├── audit-task.sh        ← Auditoría post-tarea
│   ├── triggers/            ← Triggers programados (Antigravity)
│   │   ├── README.md        ← Formato YAML y activación
│   │   ├── weekly-security-audit.yaml
│   │   ├── weekly-docs-health.yaml
│   │   └── daily-memory-consolidation.yaml
│   └── sessions/            ← Output de triggers (gitignored)
├── docs/                    ← VitePress site (desplegado en GitHub Pages)
├── docs/patterns/           ← 7 skills de referencia (no activables)
├── .claude/                 ← Configuración del template como proyecto de Claude Code
│   ├── agents/              ← Agentes COMPILADOS con skills embebidas
│   ├── commands/            ← Comandos standalone activos en este repo
│   ├── rules/
│   │   └── stack/           ← Reglas del stack activo (make dev-stack STACK=x)
│   └── memory/              ← Memoria de sesiones de trabajo sobre el template
├── Makefile                 ← Panel de control (make install, make init-project, etc.)
└── settings.json            ← Configuración base de Claude Code
```

---

## Dónde vive cada cosa y por qué

### `agents/` (raíz) ≠ `.claude/agents/`

Son dos directorios distintos con propósitos distintos:

| Directorio | Para qué | Cuándo se usa |
| --- | --- | --- |
| `agents/` | Fuente de verdad de los agentes del template | `make install` los copia a `~/.claude/agents/` |
| `.claude/agents/` | Agentes instalados localmente para el template como proyecto | Cuando trabajas en el template con Claude Code |

**Regla:** Si añades un agente nuevo, debe estar en `agents/` para que `make install` lo distribuya. `.claude/agents/` se actualiza manualmente o via `make install` ejecutado en este mismo repositorio.

### `skills/` — una carpeta por skill

Cada skill tiene exactamente un archivo `SKILL.md` dentro de su directorio:

```text
skills/
├── jedi-review/
│   └── SKILL.md    ← El prompt del skill
├── laravel-tdd/
│   └── SKILL.md
└── ...
```

`make install` NO copia skills globalmente. Las skills se activan por stack en cada proyecto mediante `make init-project STACK=x PROJECT=/ruta`, que lee `stacks/x/stack.yaml` y copia solo las skills relevantes.

### `stacks/<nombre>/stack.yaml`

Declara qué agentes con skills y qué comandos se activan cuando inicializas un proyecto con ese stack:

```yaml
name: laravel
description: Laravel 13 (API REST) + MySQL + Sanctum

rules:
  - laravel.md
  - react.md

agents:                          # Dict: agente → skills embebidas
  architect:
    skills:
      - api-design
      - laravel-patterns
  tdd-guide:
    skills:
      - tdd-workflow
      - laravel-tdd
  code-reviewer:
    skills:
      - laravel-verification
  build-error-resolver:
    skills: []
  # ... resto de agentes

commands:                        # Slash commands standalone
  jedi-review:
    when: "Para código crítico — review de 3 expertos"
  git-workflow:
    when: "Si necesitas recordar el workflow de commits y PRs"
  # ... 15 comandos universales + específicos del stack

mcps:
  notebooklm: false
  n8n: false
```

**Compilación de agentes:** `ops/compile-agents.py` lee este mapping, toma `agents/<name>.md` como base, y concatena los SKILL.md asignados bajo `# Embedded Skills Reference`. El developer nunca invoca skills manualmente — los agentes ya los conocen.

### `layers/<nombre>/layer.yaml`

Un layer técnico añade un overlay horizontal (frontend, infra) sobre cualquier stack backend. Mismo mecanismo de merge que los domains — pero para tech, no negocio:

```yaml
name: react
description: "Frontend React 19 + TypeScript SPA — layer composable"

agent_skills:                    # Se MERGE con los del stack
  architect:
    - api-design
  typescript-reviewer:           # Puede añadir agentes nuevos al stack
    - frontend-patterns
    - coding-standards
  e2e-runner:
    - e2e-testing

commands:
  design-md:
    when: "Al crear componentes React o refactorizar UI"

rules:
  - react.md
  - coding-style.md
```

Al ejecutar `make init-project STACK=laravel LAYERS=react`, el stack Laravel recibe los agentes y skills del layer React. Los layers se pueden combinar: `LAYERS=react,vue`. Los layers se procesan antes que los domains: `LAYERS=react DOMAIN=healthcare`.

### `domains/<nombre>/domain.yaml`

Un domain overlay añade skills extra a los agentes de cualquier tech stack:

```yaml
name: healthcare
description: "Healthcare — EMR/CDSS + HIPAA compliance"

agent_skills:                    # Se MERGE con los del stack
  architect:
    - healthcare-emr-patterns
    - healthcare-cdss-patterns
  tdd-guide:
    - healthcare-eval-harness
  security-reviewer:
    - healthcare-phi-compliance
```

Al ejecutar `make init-project STACK=python-api DOMAIN=healthcare`, el agente `architect` recibe los skills de `python-api` + los de `healthcare` (append, nunca reemplazo).

---

## Cómo funciona `make install`

```makefile
install:
  cp rules/*.md                 ~/.claude/rules/common/
  # Agentes: solo los usados en algún stack.yaml (filtrado con Python)
  python ops/compile-agents.py → ~/.claude/agents/
  cp hooks/*.sh                 ~/.claude/hooks/
  cp ops/audit-task.sh          ~/.claude/hooks/
  cp settings.json              ~/.claude/settings.json  # solo si no existe
```

Skills NO se copian globalmente como comandos activos — se activan por stack con `init-project`.

---

## Cómo funciona `make init-project`

1. Crea directorios en el proyecto destino: `.claude/rules/stack/`, `.claude/commands/`, `.claude/agents/`, `.claude/memory/`
2. Copia reglas del stack: `stacks/<STACK>/rules/*.md` → `.claude/rules/stack/`
3. Si hay `LAYERS=`, copia también: `layers/<LAYER>/rules/*.md` → `.claude/rules/stack/` (por cada layer)
4. Si hay `DOMAIN=`, copia también: `domains/<DOMAIN>/rules/*.md` → `.claude/rules/stack/`
5. **Compila agentes** con skills embebidas: `ops/compile-agents.py stack.yaml skills agents .claude/agents [layer.yaml...] [domain.yaml]`
   - Los layers pueden añadir agentes nuevos al stack (ej. `typescript-reviewer` en un stack Python puro)
6. Copia comandos standalone: `skills/<nombre>/SKILL.md` → `.claude/commands/<nombre>.md`
7. Copia `pipeline.yaml` y `audit-task.sh` si existen
8. Copia `stacks/common/workflows/*.yml` → `.github/workflows/` (GitHub Actions agnósticos de stack)
9. Genera `.claude/CLAUDE.md` desde la plantilla del stack (solo si no existe)
10. Si hay `LAYERS=`, appenda `CLAUDE-append.md` del layer al CLAUDE.md
11. Si hay `DOMAIN=`, appenda `CLAUDE-append.md` del domain al CLAUDE.md

---

## Añadir un nuevo agente

1. Crea `agents/<nombre>.md` con el formato estándar de agente Claude Code
2. Añádelo a los `stack.yaml` de los stacks donde aplique (sección `agents:` con las skills asignadas)
3. Ejecuta `make dev-stack STACK=x` para recompilar los agentes
4. Actualiza el conteo en la documentación

## Añadir un nuevo layer técnico

1. Crea `layers/<nombre>/` con: `layer.yaml`, `rules/*.md`, `CLAUDE-append.md` (opcional)
2. El `layer.yaml` usa el mismo schema que `domain.yaml` pero puede añadir agentes nuevos
3. Las skills del layer se **merge** con las del stack; los agentes nuevos se crean desde cero
4. Prueba composición: `make dev-stack STACK=laravel LAYERS=<nombre>` + `make check`

## Añadir un nuevo stack

1. Crea `stacks/<nombre>/` con: `stack.yaml`, `CLAUDE.md`, `rules/*.md`
2. El `stack.yaml` debe usar el formato actual: `agents: { dict }` + `commands: { dict }`
3. Añade una entrada en `docs/src/stacks/` con la guía del stack
4. Actualiza `docs/.vitepress/config.mts` para añadirlo al sidebar

## Añadir una nueva skill

1. Crea `skills/<nombre>/SKILL.md` con el prompt de la skill
2. Añádela como skill embebida en `agents:` del `stack.yaml` correspondiente
3. O añádela como comando standalone en `commands:` si es invocable por el developer

## Añadir un nuevo domain overlay

1. Crea `domains/<nombre>/` con: `domain.yaml`, `rules/*.md`, `CLAUDE-append.md`
2. `domain.yaml` declara `agent_skills:` con el mapping de skills extra por agente
3. Las skills del domain se **merge** con las del stack (nunca reemplazan)
4. `CLAUDE-append.md` se concatena al CLAUDE.md del proyecto al init

---

## `ops/triggers/` — Triggers programados

Los triggers son trabajos autónomos que Claude Code ejecuta según un cron, sin sesión abierta. Cada trigger es un archivo YAML con esta estructura:

```yaml
name: weekly-security-audit
description: "Auditoría semanal de seguridad"
schedule: "0 9 * * 1"   # cron UTC — lunes 09:00
model: sonnet
output: "ops/sessions/security-audit-$(date +%Y%m%d).md"
tags: [security, weekly]

prompt: |
  Eres el agente security-reviewer. Audita los archivos modificados
  en los últimos 7 días y guarda el reporte en ops/sessions/...
```

Para activar los triggers definidos en `ops/triggers/`:

```bash
make triggers-setup
```

Esto imprime los comandos `/schedule create ...` para pegar en Claude Code. Una vez activos, se listan con `/schedule list` y se eliminan con `/schedule delete <nombre>`.

Los outputs se guardan en `ops/sessions/` con timestamp (gitignored por defecto).

---

## Hook de memoria — `session-consolidate.sh`

El hook se ejecuta como **Stop hook** al terminar cada sesión de Claude Code. Funciona en el contexto del proyecto donde se usa Claude — no en el template.

Flujo:

1. Revisa `git log`, `git diff` y `git status` del proyecto activo
2. Identifica decisiones, patrones y configuraciones de la sesión
3. Escribe o actualiza archivos en `.claude/memory/` del proyecto

El hook se instala en `~/.claude/hooks/session-consolidate.sh` y se activa desde `~/.claude/settings.json` como Stop hook.

---

## Documentación — VitePress

El sitio de documentación está en `docs/`. Se despliega en GitHub Pages automáticamente via CI cuando hay push a `main`.

Para preview local:

```bash
cd docs && npm install && npm run dev
```

El sidebar se configura en `docs/.vitepress/config.mts`. Para añadir una página nueva, añade su ruta al array `sidebar` de la sección correspondiente.
