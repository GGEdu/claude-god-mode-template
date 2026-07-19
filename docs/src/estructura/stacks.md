# Directorio: `stacks/`

Fuente de verdad de los **15 tech stacks** del template. `make init-project STACK=<nombre>` activa un stack en un proyecto destino, copiando reglas, CLAUDE.md base y generando agentes compilados.

> Cada stack es un subdirectorio con `stack.yaml`, `rules/*.md` y `CLAUDE.md`. `ops/compile-agents.py` lee `stack.yaml` para saber qué skills incrustar en cada agente.

Los stacks son **puros por capa de negocio** (backend, fullstack, mobile). Para añadir un frontend React a un stack backend, usa `LAYERS=react` — ver [Composición con layers](#composición-con-layers).

---

## Inventario de los 15 stacks

- cpp: C++20, backend C++, sin frontend/db, tests GoogleTest.
- flutter: Flutter 3, backend y frontend Dart, tests flutter_test.
- go-api: backend Go, db PostgreSQL, tests go-test.
- java-springboot: backend Java, db PostgreSQL, tests JUnit 5.
- kotlin-multiplatform: backend/frontend Kotlin, db PostgreSQL, tests Kotest.
- laravel: backend PHP (Laravel 13), db MySQL, tests Pest. _(React frontend → usar `LAYERS=react`)_
- laravel-livewire: backend PHP (Laravel 12, monolito), frontend PHP+JS (Livewire 4 + Alpine.js), db MySQL, tests Pest.
- ml-pytorch: backend Python, sin frontend/db, tests pytest.
- nextjs-saas: backend/frontend TypeScript (Next.js), db PostgreSQL, tests Vitest + Playwright.
- nuxt-saas: backend/frontend TypeScript (Vue 3), db PostgreSQL, tests Vitest + Playwright.
- odoo: backend Python, frontend JavaScript (OWL), db PostgreSQL, tests unittest.
- perl: backend Perl, db PostgreSQL, tests Test2.
- python-api: backend Python, db PostgreSQL, tests pytest.
- rust-api: backend Rust, db PostgreSQL, tests cargo-test.
- swift-ios: backend/frontend Swift (SwiftUI), sin db, tests XCTest.

---

## Composición con layers

Los **layers** son overlays técnicos composables que se aplican sobre cualquier stack backend. Ejemplo: añadir React a Laravel o Python:

```bash
# Laravel + React SPA
make init-project STACK=laravel LAYERS=react PROJECT=/ruta

# Python API + React dashboard
make init-project STACK=python-api LAYERS=react PROJECT=/ruta

# Laravel + React + dominio healthcare
make init-project STACK=laravel LAYERS=react DOMAIN=healthcare PROJECT=/ruta
```

Ver la documentación completa en [`layers/`](./layers.md).

---

## Contenido de cada stack

```text
stacks/<nombre>/
├── stack.yaml      ← Declaración completa (tech, agents, skills, commands)
├── CLAUDE.md       ← Template de CLAUDE.md para el proyecto destino
└── rules/
    ├── <framework>.md   ← Reglas del framework backend
    └── <frontend>.md    ← Reglas del frontend (si aplica)
```

---

## Formato de `stack.yaml`

```yaml
name: <nombre>
description: <descripción corta>
backend: <lenguaje>
frontend: <lenguaje o vacío>
database: <tipo o vacío>
tests_backend: <framework>
tests_frontend: <framework o vacío>
linter_backend: <herramienta>
linter_frontend: <herramienta o vacío>

rules:
  - <nombre>.md    # archivos en stacks/<stack>/rules/

agents:
  <nombre-agente>:
    skills:
      - <skill-name>   # directorio en skills/<skill-name>/

commands:
  <nombre-command>:
    when: <descripción de cuándo usarlo>

mcps:
  notebooklm: false
  n8n: false
```

---

## Skills por agente (ejemplo: `laravel` + `LAYERS=react`)

**Stack `laravel` (backend puro):**

- architect: laravel-patterns, architecture-decision-records, deployment-patterns, docker-patterns.
- planner: laravel-patterns, search-first.
- tdd-guide: tdd-workflow, laravel-tdd.
- code-reviewer: laravel-verification, verification-loop.
- security-reviewer: security-review, laravel-security.
- database-reviewer: database-migrations.
- loop-operator: safety-guard.
- docs-lookup: documentation-lookup.
- resto (12 agentes): sin skills adicionales.

**Con `LAYERS=react` (añadido por el layer):**

- architect: ← añade `api-design`.
- typescript-reviewer: frontend-patterns, coding-standards, design-system. _(agente nuevo, no existe en el stack puro)_
- e2e-runner: ← añade `e2e-testing`.

### Skills universales (todos los stacks)

- architect: architecture-decision-records, deployment-patterns, docker-patterns.
- planner: search-first.
- code-reviewer: verification-loop.
- loop-operator: safety-guard.
- docs-lookup: documentation-lookup.

---

## Comandos por stack

### 15 comandos universales (todos los stacks)

- `continuous-learning`: extrae patrones de sesiones (v1).
- `continuous-learning-v2`: extrae patrones de sesiones (v2).
- `ck`: memoria persistente por proyecto, git-aware.
- `plankton-code-quality`: auto-format/lint en tiempo de escritura.
- `strategic-compact`: sugiere `/compact` en puntos lógicos.
- `security-scan`: escanea `.claude/` por vulnerabilidades.
- `context-budget`: audita consumo de tokens en la sesión.
- `skill-comply`: verifica que skills/rules se siguen.
- `skill-stocktake`: audita calidad de skills del proyecto.
- `prompt-optimizer`: mejora prompts del developer.
- `repo-scan`: auditoría cross-stack del código fuente.
- `product-lens`: diagnóstico de producto pre-feature.
- `token-budget-advisor`: controla profundidad de respuesta.
- `team-builder`: compone equipos de agentes para tareas.
- `rules-distill`: extrae principios cross-cutting hacia rules.

### Comandos stack-específicos comunes

- `jedi-review` (todos los 15 stacks): review de 3 expertos en paralelo.
- `workflow-runner` (todos los 15 stacks): pipeline feature/hotfix/refactor.
- `canary-watch` (todos los 15 stacks): monitoreo post-deploy con Playwright.
- `benchmark` (todos los 15 stacks): medir rendimiento antes/después de un PR.
- `codebase-onboarding` (todos los 15 stacks): guía de onboarding al entrar en un repo.
- `git-workflow` (todos los 15 stacks): recordatorio de commits y PRs.
- `design-md` (flutter, nextjs-saas, nuxt-saas, swift-ios, y cuando `LAYERS=react`): identidad visual.
- `last30days` (laravel, nextjs-saas): validar conocimiento reciente antes de planificar un feature.
- `laravel-plugin-discovery` (laravel): buscar paquetes Laravel.

---

## Agentes activados por stack

Todos los stacks activan los mismos 20 agentes comunes (incluye `harness-optimizer`), más agentes específicos según el stack y sus layers/domains:

- **Lenguaje/UI** (13, cada uno solo en el/los stack(s) que lo necesitan): `ui-engineer`, `typescript-reviewer`, `python-reviewer`, `go-reviewer`, `go-build-resolver`, `java-reviewer`, `java-build-resolver`, `kotlin-reviewer`, `kotlin-build-resolver`, `cpp-reviewer`, `cpp-build-resolver`, `flutter-reviewer`, `dart-build-resolver`
- **Sin stack fijo** (5, se activan por layer o son de invocación ad-hoc/meta): `business-analyst` y `change-manager` (layer `requirements-engineering`), `architecture-auditor` y `repo-reviewer` (pipeline/trigger, no stack), `csharp-reviewer` (reservado — no hay stack .NET todavía)

Total: 38 agentes (20 comunes + 13 de lenguaje/UI + 5 sin stack fijo).

---

## Añadir un nuevo stack

1. Crear `stacks/<nombre>/` con:
   - `stack.yaml` — rellenar todos los campos
   - `CLAUDE.md` — template para el proyecto destino
   - `rules/<framework>.md` — reglas específicas del framework

2. Asignar skills a agentes en `stack.yaml` (sección `agents:`)

3. Añadir comandos stack-específicos en `stack.yaml` (sección `commands:`)

4. Probar compilación:

   ```bash
   make dev-stack STACK=<nombre>
   make check
   ```

5. Documentar en `docs/src/estructura/stacks.md` (esta página)
