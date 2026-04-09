# Directorio: `skills/`

Cada subdirectorio es una **skill** — un bloque de instrucciones especializado que puede incrustarse en agentes o ejecutarse como comando slash. `ops/compile-agents.py` lee `stack.yaml` y fusiona las skills asignadas al frontmatter de cada agente.

> Las skills NO se instalan globalmente. Solo se activan en proyectos concretos vía `make init-project` o `make dev-stack`.

---

## Cómo funciona una skill

```
skills/laravel-tdd/
└── SKILL.md     ← Contenido que se incrusta en el agente
```

`compile-agents.py` toma el cuerpo de `SKILL.md` (sin el frontmatter YAML) y lo añade bajo `# Embedded Skills Reference` en el archivo del agente compilado.

---

## Clasificación de skills

### 1. Skills universales — incrustadas en todos los stacks

Estas skills van en todos los agentes independientemente del stack:

| Skill | Agente | Propósito |
|-------|--------|-----------|
| `architecture-decision-records` | architect | Formato ADR para documentar decisiones |
| `deployment-patterns` | architect | Patrones de despliegue (blue-green, canary) |
| `docker-patterns` | architect | Containerización y orquestación |
| `search-first` | planner | Buscar antes de construir (GitHub, npm, PyPI) |
| `verification-loop` | code-reviewer | Loop de verificación post-implementación |
| `safety-guard` | loop-operator | Guardianes de seguridad en loops autónomos |
| `documentation-lookup` | docs-lookup | Consulta de docs via Context7 MCP |

### 2. Skills de framework — incrustadas por stack

#### Laravel

| Skill | Agentes que la usan |
|-------|---------------------|
| `laravel-patterns` | architect, planner |
| `laravel-tdd` | tdd-guide |
| `laravel-verification` | code-reviewer |
| `laravel-security` | security-reviewer |
| `laravel-plugin-discovery` | _(comando slash)_ |

#### React / Frontend TypeScript

| Skill | Agentes que la usan |
|-------|---------------------|
| `frontend-patterns` | planner, typescript-reviewer |
| `coding-standards` | typescript-reviewer |
| `design-system` | typescript-reviewer |
| `nextjs-turbopack` | typescript-reviewer (nextjs-saas) |
| `nuxt4-patterns` | typescript-reviewer (nuxt-saas) |

#### Backend genérico

| Skill | Agentes que la usan |
|-------|---------------------|
| `api-design` | architect |
| `backend-patterns` | code-reviewer |
| `database-migrations` | database-reviewer |
| `security-review` | security-reviewer |
| `tdd-workflow` | tdd-guide |
| `e2e-testing` | e2e-runner |
| `verification-loop` | code-reviewer |

#### Go

| Skill | Agentes que la usan |
|-------|---------------------|
| `golang-patterns` | architect, code-reviewer |
| `golang-testing` | tdd-guide |

#### Java / Spring Boot

| Skill | Agentes que la usan |
|-------|---------------------|
| `springboot-patterns` | architect |
| `springboot-security` | security-reviewer |
| `springboot-tdd` | tdd-guide |
| `springboot-verification` | code-reviewer |
| `java-coding-standards` | code-reviewer |
| `jpa-patterns` | database-reviewer |

#### Kotlin

| Skill | Agentes que la usan |
|-------|---------------------|
| `kotlin-patterns` | architect |
| `kotlin-coroutines-flows` | code-reviewer |
| `kotlin-exposed-patterns` | database-reviewer |
| `kotlin-ktor-patterns` | architect |
| `kotlin-testing` | tdd-guide |

#### Python

| Skill | Agentes que la usan |
|-------|---------------------|
| `python-patterns` | architect, code-reviewer |
| `python-testing` | tdd-guide |
| `django-patterns` | architect |
| `django-security` | security-reviewer |
| `django-tdd` | tdd-guide |
| `django-verification` | code-reviewer |
| `pytorch-patterns` | architect (ml-pytorch) |

#### Rust

| Skill | Agentes que la usan |
|-------|---------------------|
| `rust-patterns` | architect, code-reviewer |
| `rust-testing` | tdd-guide |

#### Swift / iOS

| Skill | Agentes que la usan |
|-------|---------------------|
| `swiftui-patterns` | architect |
| `swift-concurrency-6-2` | code-reviewer |
| `swift-actor-persistence` | code-reviewer |
| `swift-protocol-di-testing` | tdd-guide |

#### Flutter

| Skill | Agentes que la usan |
|-------|---------------------|
| `flutter-dart-code-review` | code-reviewer |
| `compose-multiplatform-patterns` | architect (kotlin-multiplatform) |

#### C++

| Skill | Agentes que la usan |
|-------|---------------------|
| `cpp-coding-standards` | code-reviewer |
| `cpp-testing` | tdd-guide |

#### Perl

| Skill | Agentes que la usan |
|-------|---------------------|
| `perl-patterns` | architect |
| `perl-security` | security-reviewer |
| `perl-testing` | tdd-guide |

#### Base de datos

| Skill | Propósito |
|-------|-----------|
| `postgres-patterns` | Patrones PostgreSQL avanzados |

### 3. Skills de comandos slash — disponibles en stacks

Estas skills se usan como comandos slash (`/nombre`), no se incrustan en agentes:

| Skill / Comando | Stacks | Propósito |
|-----------------|--------|-----------|
| `continuous-learning` | Todos | Extrae patrones de sesiones (v1) |
| `continuous-learning-v2` | Todos | Extrae patrones de sesiones (v2) |
| `ck` | Todos | Memoria persistente por proyecto |
| `plankton-code-quality` | Todos | Auto-format/lint en escritura |
| `strategic-compact` | Todos | Sugiere /compact en puntos clave |
| `security-scan` | Todos | Escanea .claude/ por vulnerabilidades |
| `context-budget` | Todos | Audita tokens en la sesión |
| `skill-comply` | Todos | Verifica que skills se siguen |
| `skill-stocktake` | Todos | Audita calidad de skills |
| `prompt-optimizer` | Todos | Mejora prompts del developer |
| `repo-scan` | Todos | Auditoría cross-stack del código |
| `product-lens` | Todos | Diagnóstico pre-feature |
| `token-budget-advisor` | Todos | Controla profundidad de respuesta |
| `team-builder` | Todos | Compone equipos de agentes |
| `rules-distill` | Todos | Extrae principios → rules |
| `jedi-review` | Todos | Review de 3 expertos en paralelo |
| `workflow-runner` | Todos | Pipeline completo feature/hotfix/refactor |
| `canary-watch` | Todos | Monitoreo post-deploy con Playwright |
| `benchmark` | Todos | Medir rendimiento antes/después de PR |
| `codebase-onboarding` | Todos | Genera guía de onboarding |
| `git-workflow` | Todos | Recordatorio de workflow git |
| `design-md` | flutter, laravel-react, nextjs-saas, nuxt-saas, swift-ios | Aplica identidad visual |
| `last30days` | laravel-react, nextjs-saas | Valida conocimiento actual del modelo |
| `laravel-plugin-discovery` | laravel-react | Buscar paquetes Laravel |

### 4. Skills de domain overlays

Activadas solo cuando se combina un stack con un domain:

| Skill | Domain | Agentes afectados |
|-------|--------|-------------------|
| `healthcare-emr-patterns` | healthcare | architect |
| `healthcare-cdss-patterns` | healthcare | architect |
| `healthcare-eval-harness` | healthcare | tdd-guide |
| `healthcare-phi-compliance` | healthcare | code-reviewer, security-reviewer |
| `content-engine` | content-creator | architect, planner |
| `article-writing` | content-creator | architect |
| `deep-research` | ai-agent | _(comando slash)_ |
| `exa-search` | ai-agent | _(comando slash)_ |
| `blueprint` | ai-agent | _(comando slash)_ |
| `dmux-workflows` | ai-agent | _(comando slash)_ |
| `enterprise-agent-ops` | ai-agent | _(comando slash)_ |
| `agent-eval` | ai-agent | _(comando slash)_ |
| `claude-devfleet` | ai-agent | _(comando slash)_ |

### 5. Skills disponibles pero no activadas en ningún stack actual

Skills que existen en el directorio pero no están asignadas a ningún stack. Candidatas para activación o nuevos stacks:

**AI / Engineering:**
`agent-harness-construction`, `agentic-engineering`, `agent-payment-x402`, `ai-first-engineering`, `ai-regression-testing`, `autonomous-loops`, `claude-api`, `continuous-agent-loop`, `cost-aware-llm-pipeline`, `eval-harness`, `fal-ai-media`, `foundation-models-on-device`, `mcp-server-patterns`, `ralphinho-rfc-pipeline`, `videodb`, `x-api`

**Supply chain / Vertical:**
`carrier-relationship-management`, `customs-trade-compliance`, `energy-procurement`, `inventory-demand-planning`, `logistics-exception-management`, `production-scheduling`, `quality-nonconformance`, `returns-reverse-logistics`

**Media / Contenido:**
`crosspost`, `frontend-slides`, `liquid-glass-design`, `market-research`, `video-editing`

**Herramientas:**
`android-clean-architecture`, `browser-qa`, `bun-runtime`, `click-path-audit`, `clickhouse-io`, `data-scraper-agent`, `investor-materials`, `investor-outreach`

---

## Docs de referencia (`docs/patterns/`)

7 skills en `docs/patterns/` son **documentación de referencia**, no activables como skills:

| Archivo | Contenido |
|---------|-----------|
| `api-design.md` | Patrones REST, GraphQL, gRPC |
| `architecture-decision-records.md` | Formato ADR estándar |
| `deployment-patterns.md` | Estrategias de despliegue |
| `docker-patterns.md` | Patrones de containerización |
| `e2e-testing.md` | Estrategias de testing E2E |
| `security-review.md` | Checklist OWASP Top 10 |
| `tdd-workflow.md` | Flujo RED-GREEN-REFACTOR |

---

## Añadir una nueva skill

1. Crear `skills/<nombre>/SKILL.md`
2. Asignarla en `stacks/*/stack.yaml` bajo el agente correspondiente
3. Recompilar: `make dev-stack STACK=<stack>`
4. Verificar que el agente compilado incluye el contenido: `grep -l "<nombre>" .claude/agents/`
