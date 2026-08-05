# Referencia completa

Todos los slash commands, agentes, hooks y variables de entorno disponibles en una sola página.

---

## Slash commands (dentro de Claude Code)

### Gestión de sesión

| Comando    | Qué hace                                      | Cuándo                           |
|------------|-----------------------------------------------|----------------------------------|
| `/compact` | Libera contexto sin perder el hilo de trabajo | Después de explorar mucho código |

::: tip Memoria automática
La memoria del proyecto se gestiona **automáticamente** por el Stop hook (`session-consolidate.sh`). Al terminar la sesión, el hook revisa el trabajo y actualiza `.claude/memory/` sin que tengas que hacer nada. Claude también lee `.claude/CLAUDE.md` al iniciar — mantén ese archivo actualizado para retomar el contexto rápido.
:::

---

### Planificación y desarrollo

Planificación y TDD no son slash commands — se invocan mediante lenguaje natural, lo que activa los agentes correspondientes automáticamente:

| Invocación | Agente activado | Cuándo |
| --- | --- | --- |
| `"Planifica: [descripción del feature]"` | `planner` — plan con fases, dependencias y riesgos | Antes de cualquier feature |
| `"Implementa con TDD: [feature]"` | `tdd-guide` — ciclo RED → GREEN → REFACTOR | Al implementar features nuevos |

Ejemplo:

```text
"Planifica: añadir autenticación Sanctum a la API"
→ Fase 1: Instalar laravel/sanctum, publicar config, migrar tabla
→ Fase 2: Endpoints login/logout/me
→ Fase 3: Middleware auth:sanctum en rutas protegidas
→ Riesgos: CORS en SPA, stateful domains para cookies

"Implementa con TDD: endpoint POST /api/login"
→ Escribe primero: tests/Feature/Auth/LoginTest.php
→ Test debe fallar (RED) → implementa → pasa (GREEN) → refactoriza
```

---

### Revisión de código

| Comando | Qué hace | Cuándo |
| --- | --- | --- |
| `/jedi-review` | 3 subagentes en paralelo: Kent Beck + Martin Fowler + Mike Acton | Después de escribir código importante |
| `/security-scan` | Auditoría de seguridad enfocada en OWASP Top 10 | Antes de cada release |

Salida típica de `/jedi-review`:

```text
[KENT BECK] El controlador está limpio. Pero login/logout juntos violan SRP.
[MARTIN FOWLER] Línea 23: $request->all() — usar siempre $request->validated().
[MIKE ACTON] createToken('token') sin nombre descriptivo — usar createToken('spa-web').

Veredicto: B — funcional con 3 correcciones antes de PR.
Top 3 acciones: 1) LoginRequest, 2) createToken('spa-web'), 3) AuthService
```

---

### Post-deploy y workflows especiales

| Comando | Qué hace | Cuándo |
| --- | --- | --- |
| `/canary-watch URL` | Playwright comprueba errores de consola, peticiones fallidas, tiempos de carga | Después de desplegar |
| `/workflow-runner feature` | Ejecuta pipeline completo: planner → tdd-guide → code-reviewer → security-reviewer | Features nuevos |
| `/workflow-runner hotfix` | Pipeline rápido: tdd-guide → security-reviewer → audit | Fixes urgentes |
| `/workflow-runner refactor` | Pipeline de refactor: planner → refactor-cleaner → code-reviewer | Refactorizaciones |

Ejemplo:

```text
/canary-watch https://blog-api.tudominio.com
→ Verificando consola JS... ✅ 0 errores
→ Verificando red... ✅ 0 requests fallidas
→ Tiempo de carga: 1.2s ✅
→ Veredicto: DEPLOY OK
```

---

### Selección de modelo

| Comando | Qué hace |
| --- | --- |
| `/model opus` | Cambia a Opus 4.6 — para decisiones arquitectónicas complejas |
| `/model sonnet` | Cambia a Sonnet 4.6 — trabajo general (valor por defecto) |
| `/model haiku` | Cambia a Haiku 4.5 — tareas simples, más económico |
| `/cost` | Muestra el gasto de tokens en la sesión actual |

### Comandos universales (disponibles en todos los stacks)

| Comando | Qué hace |
| --- | --- |
| `/ck` | Memoria persistente per-project, git-aware |
| `/plankton-code-quality` | Auto-format y lint en cada edición vía hooks |
| `/strategic-compact` | Sugiere `/compact` en puntos lógicos de la sesión |
| `/security-scan` | Escanea `.claude/` por vulnerabilidades y misconfigs |
| `/context-budget` | Audita consumo de tokens del contexto |
| `/skill-comply` | Verifica que skills y rules se siguen realmente |
| `/skill-stocktake` | Audita calidad de skills instaladas |
| `/prompt-optimizer` | Mejora prompts del developer |
| `/repo-scan` | Auditoría cross-stack del código fuente |
| `/product-lens` | Diagnóstico de producto pre-feature |
| `/token-budget-advisor` | Controla profundidad y longitud de respuestas |
| `/team-builder` | Compone equipos de agentes para tareas paralelas |
| `/rules-distill` | Extrae principios cross-cutting → nuevas rules |

---

## Agentes especializados

Claude los activa automáticamente o puedes pedirlos explícitamente:

```text
"Usa el agente architect para diseñar el módulo de pagos"
"Lanza code-reviewer y security-reviewer en paralelo sobre los cambios de auth"
```

### Agentes principales (38 instalados globalmente)

| Agente | Propósito | Se activa automáticamente cuando... |
| --- | --- | --- |
| `planner` | Plan de implementación con fases y riesgos | Solicitas un feature complejo |
| `architect` | Diseño de sistemas y decisiones técnicas | Hay una decisión arquitectónica |
| `tdd-guide` | TDD enforcement RED→GREEN→REFACTOR | Escribes features nuevas o corriges bugs |
| `code-reviewer` | Calidad, patrones, best practices | Escribes o modificas código |
| `security-reviewer` | Vulnerabilidades OWASP Top 10 | Tocas auth, inputs de usuario, pagos |
| `typescript-reviewer` | Issues específicos de TypeScript/JS | En proyectos TypeScript |
| `python-reviewer` | Issues específicos de Python | En proyectos Python |
| `database-reviewer` | Queries, schemas, índices, migraciones | Escribes SQL o modelos de datos |
| `build-error-resolver` | Fix de errores de build y TypeScript | Cuando el build falla |
| `e2e-runner` | Tests end-to-end con Playwright | Para flujos críticos de usuario |
| `performance-optimizer` | Bottlenecks, bundle size, memoria | Al investigar rendimiento |
| `refactor-cleaner` | Dead code, duplicados, análisis con knip/depcheck | Para mantenimiento de código |
| `doc-updater` | READMEs, codemaps, documentación | Al actualizar docs |
| `silent-failure-hunter` | Detecta catch vacíos, fallbacks peligrosos, errores silenciados | Antes de release |
| `pr-test-analyzer` | Analiza coverage de tests en un PR | Antes de hacer merge |
| `comment-analyzer` | Evalúa calidad de comentarios: precisión, obsolescencia | En archivos de lógica crítica |
| `conversation-analyzer` | Analiza la sesión para detectar fricción, correcciones repetidas | Cuando la sesión se siente atascada |
| `refactor-cleaner` | Limpia código muerto y refactoriza para legibilidad sin cambiar comportamiento | Después de que una feature funciona o para mantenimiento |
| `loop-operator` | Ejecuta loops multi-paso con detección de bloqueos | Para tareas de 5+ pasos secuenciales |
| `memory-consolidator` | Consolida `.claude/memory/` cuando crece demasiado | Cuando un archivo supera 150 líneas |
| `docs-lookup` | Busca documentación actualizada de librerías y APIs vía Context7 | Al necesitar docs de una lib específica |
| `github-orchestrator` | Publica resultados de agentes en GitHub: comentarios en PRs, issues desde auditorías | Al publicar reviews o reportes en GitHub |

---

## Hook de sesión

### `session-consolidate.sh`

Se ejecuta **automáticamente al terminar cada sesión** de Claude Code (Stop hook).

**Qué hace:**

1. Revisa `git log`, `git diff` y `git status` del proyecto
2. Identifica decisiones, problemas resueltos y reglas de dominio de la sesión
3. Escribe o actualiza archivos en `.claude/memory/`

**Archivos que puede crear/actualizar:**

- `architecture.md` — Decisiones de arquitectura y por qué
- `domain-rules.md` — Reglas de negocio explicadas en la sesión
- `auth.md` — Configuraciones de autenticación
- Cualquier archivo temático relevante

**Formato de cada archivo en `.claude/memory/`:**

```markdown
---
name: nombre-descriptivo
description: una línea — qué contiene este archivo
type: project
updated: YYYY-MM-DD
---

- Decisión tomada — por qué — cuándo revisar
- Problema encontrado y solución
- Configuración o integración nueva
```

**Regla importante:** El hook solo ve commits y cambios de git. Si tomaste decisiones importantes en la conversación sin hacer commit, escríbelas manualmente en `.claude/memory/` antes de terminar la sesión — o dile a Claude "guarda esta decisión en la memoria del proyecto".

---

## Memoria del proyecto

Los archivos en `.claude/memory/` son la memoria persistente del proyecto:

```text
blog-api/.claude/memory/
├── architecture.md     ← Decisiones de stack y arquitectura
├── auth.md             ← Configuración de Sanctum, CORS, tokens
├── domain-rules.md     ← Reglas de negocio (posts, comentarios, usuarios)
└── index.md            ← Índice generado por memory-consolidator
```

**Se versiona con git** — todos los desarrolladores del equipo comparten la misma memoria.

**Cuándo consolidar:** Cuando un archivo supera 150 líneas o el directorio supera 600 líneas en total.

```text
"Usa el agente memory-consolidator para consolidar .claude/memory/"
```

### Memoria personal (`CLAUDE.local.md`, no compartida)

Además de `CLAUDE.md` (raíz del proyecto, committeado, compartido por todo el equipo), Claude Code carga automáticamente `CLAUDE.local.md` si existe — mismo nivel, raíz del proyecto. Es personal por developer: preferencias propias, URLs de sandbox, datos de test locales. **No se commitea** — `make init-project` lo agrega al `.gitignore` del proyecto por defecto.

Diferencia con `.claude/settings.local.json`: ese archivo es config/permisos locales (qué tools se auto-permiten). `CLAUDE.local.md` es memoria/instrucciones locales (qué le decís a Claude sobre tus preferencias). Ambos coexisten, cada uno cubre una cosa distinta.

```text
blog-api/
├── CLAUDE.md          ← Compartido, committeado (contexto del proyecto)
└── CLAUDE.local.md    ← Personal, gitignored (tus preferencias, no las del equipo)
```

---

## Variables de entorno (settings.json)

Configuradas en `~/.claude/settings.json` bajo `env`:

| Variable | Valor por defecto | Efecto |
| --- | --- | --- |
| `MAX_THINKING_TOKENS` | `10000` | Límite de tokens para razonamiento interno |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | `50` | Compacta contexto al 50% (por defecto 80%) |
| `CLAUDE_CODE_SUBAGENT_MODEL` | `haiku` | Modelo para subagentes (más económico) |

---

## Estructura de archivos clave

```text
proyecto/
├── .claude/
│   ├── CLAUDE.md              ← Contexto del proyecto (se lee al iniciar cada sesión)
│   ├── settings.json          ← Modelo, tokens, permisos locales
│   ├── memory/                ← Memoria persistente (versionada en git)
│   │   ├── architecture.md
│   │   ├── auth.md
│   │   └── domain-rules.md
│   ├── commands/              ← Slash commands standalone (/nombre)
│   │   ├── jedi-review.md
│   │   ├── git-workflow.md
│   │   └── ...
│   ├── agents/                ← Agentes COMPILADOS con skills embebidas
│   │   ├── planner.md         ← Incluye skills del stack dentro del agente
│   │   ├── code-reviewer.md
│   │   └── ...
│   ├── pipeline.yaml          ← Workflows orquestables (/workflow-runner feature)
│   └── rules/
│       ├── common/            ← Reglas universales — siempre activas
│       └── stack/             ← Reglas del stack + domain elegidos — siempre activas
│           ├── laravel.md
│           └── react.md
│
~/.claude/                     ← Instalación global (make install)
├── settings.json              ← Configuración global con Stop hook
├── agents/                    ← 38 agentes base disponibles en todos los proyectos
├── rules/common/              ← Reglas comunes en todos los proyectos
└── hooks/
    └── session-consolidate.sh ← Se ejecuta al terminar cada sesión
```

---

## Domain overlays

Los domains añaden conocimiento de dominio a cualquier tech stack sin reemplazar sus skills:

| Domain | Qué añade |
| --- | --- |
| `healthcare` | EMR, CDSS, HIPAA compliance, PHI protection |
| `ai-agent` | Multi-agent systems, evals, LLM pipelines, cost optimization |
| `content-creator` | Escritura, social media, video, newsletters |
| `supply-chain` | Logistics, inventory, carrier management, customs |

```bash
# Usar un domain overlay al inicializar
make init-project STACK=python-api DOMAIN=healthcare PROJECT=/ruta
```

El domain **merge** skills extra en los agentes del stack. Por ejemplo, `DOMAIN=healthcare` añade `healthcare-emr-patterns` al agente `architect` además de los skills que ya tiene del stack `python-api`.

---

## Resumen rápido — cuándo usar cada cosa

- Voy a implementar algo: `"Planifica: [descripción]"` → agente `planner`
- Escribo código nuevo: `"Implementa con TDD: [feature]"` → agente `tdd-guide`
- Terminé de escribir código: `/jedi-review`
- Código de auth o pagos: `/security-scan` + agente `security-reviewer`
- Deployo a producción: `/canary-watch URL`
- El contexto está lleno: `/compact`
- Memoria creció demasiado: Agente `memory-consolidator`
- Cierro la sesión: nada, el Stop hook actualiza la memoria
