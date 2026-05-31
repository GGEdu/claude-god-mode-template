---
name: skills-index
description: Índice navegable de las 139 skills del catálogo, agrupadas por categoría y stack.
type: project
updated: 2026-04-25
---

# Skills — Índice navegable

Total: **139 skills** en `skills/`. Solo se instalan en `.claude/skills/` las skills relevantes al stack/layers/domain elegidos durante `make init-project`.

## Cómo se activan

Las skills se activan automáticamente cuando Claude detecta una intención que coincide con su `description`. No es necesario invocarlas con `/comando`.

Ejemplo: escribir "necesito tests para este endpoint" activa `*-tdd` o `tdd-workflow` según el stack.

## Por categoría

### Testing & TDD (12)

| Skill | Propósito |
|---|---|
| `tdd-workflow` | Ciclo RED→GREEN→REFACTOR genérico |
| `django-tdd` | Pytest + factories en Django |
| `laravel-tdd-livewire` | Pest + Livewire testing |
| `python-testing` | pytest patterns |
| `golang-testing` | Tests en Go |
| `kotlin-testing` | JUnit/MockK para Kotlin |
| `springboot-tdd` | Spring Boot test slices |
| `rust-testing` | Tests con cargo |
| `cpp-testing` | GTest/Catch2 |
| `perl-testing` | Test::More |
| `ai-regression-testing` | Regression suite para flows AI |
| `e2e-testing` | E2E con Playwright/Cypress |

### Security & Audit (9)

| Skill | Propósito |
|---|---|
| `security-scan` | AgentShield — escaneo de configuración Claude |
| `security-review` | Review pre-merge de cambios sensibles |
| `django-security` | OWASP + Django middleware |
| `laravel-security` | Sanctum + CSRF + auth |
| `springboot-security` | Spring Security patterns |
| `perl-security` | Tainting + CGI safety |
| `prompt-injection-defense` | Defensa contra inyección en prompts |
| `secrets-scanning` | Detección de leaks de credenciales |
| `customs-trade-compliance` | Compliance regulatoria |

### Code Review & Quality (10)

| Skill | Propósito |
|---|---|
| `jedi-review` | Panel de 3 expertos (Beck, Fowler, Acton) |
| `simplify` | Reuse + quality + efficiency review |
| `repo-scan` | Audit de assets cross-stack |
| `code-simplification-patterns` | Catálogo de patterns para simplificar |
| `coding-standards` | Estándares por lenguaje |
| `cpp-coding-standards` | C++ Core Guidelines |
| `flutter-dart-code-review` | Best practices Dart/Flutter |
| `pr-test-coverage` | Análisis de cobertura por PR |
| `linting-strategy` | Configuración de linters |
| `commenting-standards` | Comentarios útiles vs ruido |

### Architecture & Design (12)

| Skill | Propósito |
|---|---|
| `architecture-decision-records` | ADRs con template |
| `system-design` | Diseño de sistemas distribuidos |
| `api-design` | REST/GraphQL/gRPC patterns |
| `database-migrations` | Migraciones zero-downtime |
| `backend-patterns` | Patterns server-side |
| `deployment-patterns` | Blue-green, canary, etc. |
| `android-clean-architecture` | Clean Architecture en Android |
| `compose-multiplatform-patterns` | KMP/CMP patterns |
| `django-patterns` | Convenciones Django |
| `laravel-patterns` | Convenciones Laravel |
| `kotlin-patterns` | Patterns idiomáticos Kotlin |
| `kotlin-coroutines-flows` | Concurrencia con coroutines |

### AI & Agent Engineering (15)

| Skill | Propósito |
|---|---|
| `agent-eval` | Evaluación de agents |
| `agent-harness-construction` | Construcción de harness |
| `agentic-engineering` | Patterns para agents |
| `agent-introspection-debugging` | Debug de agent failures |
| `agent-payment-x402` | Pagos x402 para agents |
| `ai-first-engineering` | AI-first dev practices |
| `claude-api` | Integración con Claude API |
| `claude-devfleet` | DevFleet patterns |
| `cost-aware-llm-pipeline` | Pipelines costos optimizados |
| `eval-harness` | Eval framework |
| `enterprise-agent-ops` | Ops para agents enterprise |
| `data-scraper-agent` | Agents de scraping |
| `tool-use-orchestration` | Orquestación tool use |
| `prompt-injection-defense` | Defensa contra inyección |
| `continuous-agent-loop` | Loops autónomos |

### Documentation & Onboarding (6)

| Skill | Propósito |
|---|---|
| `codebase-onboarding` | Onboarding a nuevo codebase |
| `documentation-lookup` | Búsqueda en docs |
| `article-writing` | Redacción técnica |
| `crosspost` | Distribución cross-platform |
| `design-md` | DESIGN.md como contexto visual |
| `repo-onboarding` | Onboarding a repos |

### Workflow & Operations (12)

| Skill | Propósito |
|---|---|
| `workflow-runner` | Ejecución de pipeline.yaml |
| `autonomous-loops` | Loops cron de agents |
| `continuous-learning` | Learning loop v1 |
| `continuous-learning` | Learning v2 con confidence scoring |
| `dmux-workflows` | Multi-pane terminal |
| `scheduled-tasks` | Tareas programadas |
| `team-builder` | Composición de agents en paralelo |
| `loop-operator` | Operador de loops |
| `git-workflow` | Patterns de git |
| `deployment-checklist` | Checklist pre-deploy |
| `incident-response` | Respuesta a incidentes |
| `standup` | Generación de standup |

### Stack-specific Verification (9)

| Skill | Propósito |
|---|---|
| `django-verification` | CI checks Django |
| `laravel-verification` | CI checks Laravel |
| `springboot-verification` | CI checks Spring Boot |
| `python-patterns` | Patterns Python |
| `golang-patterns` | Patterns Go |
| `rust-patterns` | Patterns Rust |
| `swift-patterns` | Patterns Swift |
| `flutter-patterns` | Patterns Flutter |
| `bun-runtime` | Bun runtime patterns |

### Performance & Optimization (8)

| Skill | Propósito |
|---|---|
| `benchmark` | Baselines y regresiones |
| `context-budget` | Auditoría de contexto |
| `token-budget-advisor` | Advisor de tokens |
| `performance-optimization` | Optimización general |
| `database-optimization` | Index + query tuning |
| `clickhouse-io` | Optimización ClickHouse |
| `caching-strategies` | Caché multi-nivel |
| `frontend-performance` | Performance web |

### Domain-specific (10)

| Skill | Propósito |
|---|---|
| `carrier-relationship-management` | CRM logística |
| `customs-trade-compliance` | Compliance aduanas |
| `energy-procurement` | Procurement energía |
| `healthcare-hipaa` | HIPAA compliance |
| `supply-chain-orchestration` | Supply chain |
| `content-engine` | Content automation |
| `fal-ai-media` | Generación media via fal.ai |
| `browser-qa` | QA en navegador |
| `click-path-audit` | Análisis click paths |
| `canary-watch` | Canary deploy monitor |

### Misc & Tools (36)

Skills no categorizables fácilmente: `ck`, `council`, `prompt-optimizer`, `last30days`, `exa-search`, `deep-research`, `repo-scan`, `skill-comply`, `skill-stocktake`, `rules-distill`, `santa-method`, `strategic-compact`, `plankton-code-quality`, `laravel-plugin-discovery`, `product-lens`, `blueprint`, etc.

## Filtrar por stack

```bash
# Cuando estás en un proyecto stacks/<stack>/, las skills se filtran automáticamente.
# Para ver qué skills están activas en tu stack:
make list-skills STACK=laravel  # (futuro target)

# Manualmente:
ls .claude/skills/  # solo las del stack instalado
```

## Crear una skill nueva

Ver `skills/skill-creator/` o invocar:

```
/skill-creator
```

Sigue el schema de [Anthropic skills](https://docs.anthropic.com/claude-code/skills) — `name`, `description` con triggers explícitos, `frontmatter` YAML, contenido en markdown.
