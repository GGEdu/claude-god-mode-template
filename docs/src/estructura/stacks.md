# Directorio: `stacks/`

Fuente de verdad de los **14 tech stacks** del template. `make init-project STACK=<nombre>` activa un stack en un proyecto destino, copiando reglas, CLAUDE.md base y generando agentes compilados.

> Cada stack es un subdirectorio con `stack.yaml`, `rules/*.md` y `CLAUDE.md`. `ops/compile-agents.py` lee `stack.yaml` para saber qué skills incrustar en cada agente.

---

## Inventario de los 14 stacks

- cpp: C++20, backend C++, sin frontend/db, tests GoogleTest.
- flutter: Flutter 3, backend y frontend Dart, tests flutter_test.
- go-api: backend Go, db PostgreSQL, tests go-test.
- java-springboot: backend Java, db PostgreSQL, tests JUnit 5.
- kotlin-multiplatform: backend/frontend Kotlin, db PostgreSQL, tests Kotest.
- laravel-react: backend PHP, frontend TypeScript (React), db MySQL, tests Pest + Vitest.
- ml-pytorch: backend Python, sin frontend/db, tests pytest.
- nextjs-saas: backend/frontend TypeScript (Next.js), db PostgreSQL, tests Vitest + Playwright.
- nuxt-saas: backend/frontend TypeScript (Vue 3), db PostgreSQL, tests Vitest + Playwright.
- odoo: backend Python, frontend JavaScript (OWL), db PostgreSQL, tests unittest.
- perl: backend Perl, db PostgreSQL, tests Test2.
- python-api: backend Python, db PostgreSQL, tests pytest.
- rust-api: backend Rust, db PostgreSQL, tests cargo-test.
- swift-ios: backend/frontend Swift (SwiftUI), sin db, tests XCTest.

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

## Skills por agente (ejemplo: `laravel-react`)

- architect: api-design, laravel-patterns, architecture-decision-records, deployment-patterns, docker-patterns.
- planner: laravel-patterns, search-first.
- tdd-guide: tdd-workflow, laravel-tdd.
- code-reviewer: laravel-verification, verification-loop.
- typescript-reviewer: frontend-patterns, coding-standards, design-system.
- security-reviewer: security-review, laravel-security.
- database-reviewer: database-migrations.
- e2e-runner: e2e-testing.
- loop-operator: safety-guard.
- docs-lookup: documentation-lookup.
- resto (12 agentes): sin skills adicionales.

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

- `jedi-review` (todos los 14 stacks): review de 3 expertos en paralelo.
- `workflow-runner` (todos los 14 stacks): pipeline feature/hotfix/refactor.
- `canary-watch` (todos los 14 stacks): monitoreo post-deploy con Playwright.
- `benchmark` (todos los 14 stacks): medir rendimiento antes/después de un PR.
- `codebase-onboarding` (todos los 14 stacks): guía de onboarding al entrar en un repo.
- `git-workflow` (todos los 14 stacks): recordatorio de commits y PRs.
- `design-md` (flutter, laravel-react, nextjs-saas, nuxt-saas, swift-ios): identidad visual.
- `last30days` (laravel-react, nextjs-saas): validar conocimiento reciente antes de `/plan`.
- `laravel-plugin-discovery` (laravel-react): buscar paquetes Laravel.

---

## Agentes activados por stack

Todos los stacks activan 20 agentes comunes, con 2 agentes dependientes del lenguaje:

- typescript-reviewer: laravel-react, nextjs-saas, nuxt-saas (stacks con TypeScript frontend).
- python-reviewer: odoo, python-api, ml-pytorch (stacks Python).

Total instalado: 22 agentes (20 comunes + typescript-reviewer en 3 stacks + python-reviewer en 3 stacks).

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
