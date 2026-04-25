
> Leyenda de markers de implementación:
> - `[BUILT-IN]` — Funcionalidad nativa de Claude Code. Solo configurar.
> - `[TO BUILD]` — Requiere implementación (hooks, scripts, estructura). Incluye spec o pseudocódigo.
> - `[CONVENTION]` — Acuerdo de equipo/individuo. No requiere código, solo disciplina.

## 1. Filosofía Central (El Modelo Operativo) `[CONVENTION]`

El repositorio se rige por un **modelo de 5 capas + 3 sistemas de enforcement**:

### 1.1 Contexto siempre activo reducido

El archivo CLAUDE.md contiene solo contexto "siempre activo" y reglas inmutables.

- **Límite ~200 líneas.** Más diluye la atención y empeora resultados.
- **Poda agresiva:** Si Claude ya lo hace bien sin la instrucción → eliminar o convertir en hook.
- **Solo el "qué":** Comandos build/test, decisiones de arquitectura, gotchas no obvios, convenciones.
- **No incluir:** lo que el linter ya cubre, dumps de documentación, explicaciones teóricas.
- **Cuatro niveles de carga:** Org policy → `~/.claude/CLAUDE.md` (global) → `CLAUDE.md` (proyecto) → `CLAUDE.md` en subdirectorios + primeras 200 líneas de `MEMORY.md`. Lo más específico gana.
- **Overrides personales:** `CLAUDE.local.md` en la raíz (gitignored automáticamente).
- **Asumir contexto cero:** Redactar como si Claude no supiera NADA del proyecto.

### 1.2 Procedimientos repetitivos = Skills

Cualquier tarea repetida >2 veces → skill, comando o regla explícita.
- Crear skills desde ejemplos: pegar output excelente y pedir conversión a skill reutilizable.
- **Versionado de skills:** Duplicar al refinar, no editar el activo. Previene regresiones.

### 1.3 Higiene de sesión estricta

- Separar proyectos no relacionados en sesiones distintas (evitar context bleed).
- Podar periódicamente memory, archivos e instrucciones (evitar drift acumulado).
- **Memoria por worktree:** Cada Git worktree tiene su propio directorio de auto-memory. Las notas de un worktree no contaminan otro.

### 1.4 Paralelización aislada

Trabajo paralelo o complejo → worktrees o ramas independientes con supervisión estricta.

### 1.5 Guardarraíles inteligentes

Auto Mode para tareas rutinarias + validación programática obligatoria antes de fusionar.
- **Minimizar decision latency:** Cada decisión recurrente codificada en rule/hook/allow = latencia eliminada permanentemente. Reservar intervención humana para decisiones genuinamente nuevas o de alto riesgo.

### 1.6 Autovalidación con enforcement programático

> La autovalidación NO depende de auto-reflexión del modelo. Se implementa con hooks programáticos.

- **TDD estricto enforced por hook:** Un hook `PreToolUse` sobre `Write`/`Edit` verifica que existan tests para el módulo ANTES de permitir escribir código de implementación. Si los tests se crean DESPUÉS del código → hook fuerza revisión por agente independiente con prompt adversarial.
- **Validación factual obligatoria:** Antes de afirmar que un archivo/función/API existe o tiene cierto comportamiento, Claude MUST ejecutar `grep`/`read_file` para verificar. Nunca afirmar de memoria. Esto es una regla non-negotiable en CLAUDE.md.

> Esta regla es textual — no hookeable al nivel del "pensamiento" del modelo. Se mitiga con capas:
> 1. **Capa 1 (rule):** Authority language máxima en CLAUDE.md: `MUST verify, non-negotiable, no exceptions`
> 2. **Capa 2 (hook PostToolUse sobre Write/Edit):** Si el código contiene imports/requires, verificar con `find` que los archivos referenciados existen. Warning si no.
> 3. **Capa 3 (agente):** `code-reviewer` con prompt adversarial: "Verifica que cada archivo, función y API referenciados en el diff existen realmente en el codebase. Ejecuta grep para confirmar."
> **Limitación reconocida:** No se puede prevenir que Claude piense algo falso — solo se puede verificar que lo que escribe como código/texto sea correcto. Las 3 capas cubren el output, no el razonamiento.
- **Checklist programático pre-commit** (hook `PreToolUse` sobre `Bash(git commit*)`):
  1. ¿Existen tests para los archivos modificados?
  2. ¿Los tests fallan sin la implementación? (prueba de que el test detecta el fallo)
  3. ¿El diff incluye solo archivos declarados en el plan?
  4. Si alguna respuesta es NO → bloquear commit + registrar razón.

> El checklist pre-commit también valida calidad mínima de tests:
  5. ¿Los archivos de test modificados contienen al menos 1 assertion por función de test? (heurística: buscar `assert`, `expect`, `should`, `toBe`)
  6. ¿Los nombres de test correlacionan con `acceptance_criteria` del plan? (heurística por keywords — best effort, no bloqueante)
  **Limitación reconocida:** Validar calidad de test al 100% es imposible en un hook. El agente `code-reviewer` cubre el gap con prompt: "Verifica que los tests cubran los criterios de aceptación y no sean triviales."

- **Tabla de racionalización como DENY list programática:**

  | Si el agente intenta... | El hook hace... |
  |---|---|
  | Commit sin tests | Bloquea. Mensaje: "Tests requeridos. Crear tests primero." |
  | Marcar tarea completa sin verificación | Bloquea. Ejecuta test suite automáticamente. |
  | Modificar archivo fuera del plan | Warning + log. Requiere justificación persistida. |
  | Skip de code review | Bloquea. Invoca agente `code-reviewer` automáticamente. |

### 1.7 Nunca usar `--dangerously-skip-permissions`

Usar `allow` en settings.json para comandos rutinarios específicos. Mismo efecto, sin riesgo destructivo.

### 1.8 Self-Improvement Loop con enforcement cerrado

> El loop de mejora tiene criterios objetivos, detección de contradicciones, TTL y promoción basada en evidencia.

**Protocolo de registro de lecciones:**

Después de CADA corrección del usuario → registrar con schema estructurado:

```yaml
# Lesson entry — schema obligatorio
id: lesson-YYYY-MM-DD-NNN
date: 2026-04-17
scope: "api-auth"             # Namespace explícito para detección de contradicciones
trigger: "Qué causó el error (acción concreta)"
pattern: "Qué hacía mal (patrón reconocible)"
fix: "Qué debe hacer en su lugar (acción correctiva)"
rule_created: false
sessions_without_repeat: 0
last_referenced: 2026-04-17
supersedes: null          # ID de lesson anterior que esta reemplaza
superseded_by: null       # ID de lesson que reemplaza esta
status: active            # active | promoted | archived | superseded
```

> Detección de contradicciones usa `scope` + keywords, no solo keywords.

**Detección de contradicciones:** Al escribir una nueva lesson, buscar entries existentes con **mismo `scope`** Y keywords solapantes. Solo `scope` idéntico → potencial contradicción. Scopes diferentes → no contradicción aunque compartan keywords. Si se detecta contradicción → marcar la anterior como `status: superseded` + `superseded_by: <new_id>` + registrar en log de cambios.

> `last_referenced` se actualiza automáticamente — no depende de que Claude recuerde.

**Enforcement de `last_referenced`:** El hook `session-consolidate` (Stop hook) lee `.claude/session-reads.log` (generado por `session-read-logger`, §10.1) y actualiza `last_referenced` de TODAS las entries que aparecieron en la sesión. No depende de acción manual de Claude.

**Criterios de promoción (lesson → rule):**
- **Señal explícita:** Usuario ejecuta `/promote <lesson-id>`
- **Señal implícita:** `sessions_without_repeat >= 5` Y `status == active`
- **Señal de consenso:** 2+ agentes referencian la misma lección en sesiones distintas
- Al promover: crear/actualizar rule en `.claude/rules/` + actualizar `rule_created: true` + `status: promoted`

**Garbage collection (TTL):**
- Campo `last_referenced` se actualiza cada vez que la lesson es consultada.
- **Routine semanal:** Entries con `last_referenced` > 30 días Y `status == active` → `status: archived` + mover a `lessons/archive/`.
- Entries `superseded` se archivan inmediatamente.

**Detección de corrección vs cambio de opinión:**
- **Corrección** = usuario revierte un cambio de Claude O dice explícitamente "eso está mal/incorrecto/no funciona".
- **Cambio de opinión** = usuario pide una dirección diferente sin indicar error. No genera lesson.

**Backward propagation:** Cuando la implementación diverge del plan → Claude MUST proponer actualización del plan/CLAUDE.md ANTES de continuar con la nueva dirección. El plan vivo debe reflejar la realidad actual.

> Toda mutación del plan deja audit trail:

**Protocolo de mutación de PLAN.md:**
1. Copiar versión actual a `PLAN.v{N}.md` (snapshot inmutable)
2. Añadir entrada al `## Change log` del plan:
   ```yaml
   - timestamp: "2026-04-17T14:30:00Z"
     field: "files_affected"
     old: ["src/auth.ts"]
     new: ["src/auth.ts", "src/middleware/cors.ts"]
     reason: "CORS middleware necesario para auth cross-origin"
   ```
3. Plan mutado pasa por GATE-2 nuevamente (re-validación de coherencia)
4. Si la mutación toca `non_goals` → requiere aprobación humana (modo interactivo) o STOP (modo autónomo)

### 1.9 Elegancia balanceada

- Cambios no triviales: pausar → "¿hay una forma más elegante?"
- Fix hacky: reimplementar con conocimiento acumulado.
- Fixes simples y obvios: NO sobre-ingenierar.

### 1.10 Bug fixing autónomo

- Diagnosticar y resolver sin pedir ayuda al usuario.
- Investigar logs, errores, tests fallidos de forma independiente.
- Cero cambio de contexto requerido del usuario.

---

## 2. Máquina de Estados para Operación Autónoma `[TO BUILD]`

> El flujo de trabajo ya no es una directiva textual — es un autómata con estados, transiciones y gates obligatorios.

### 2.1 Estados y transiciones

```
                              ┌─────────────────────────────────────────┐
                              │                                         │
INIT → EXPLORE → [GATE-1] → PLAN → [GATE-2] → EXECUTE → [GATE-3] → VERIFY → DONE
  │      │                     │                   │                    │
  │      │                     │                   │                    │
  │      ↓ (fail)              ↓ (fail, max 2)     ↓ (fail)            ↓ (fail)
  │    BLOCKED              RE-PLAN              ROLLBACK            ROLLBACK
  │                            ↑                   │                    │
  │                            └───────────────────┘                    │
  │                            ↑                                        │
  │                            └────────────────────────────────────────┘
  │
  └→ [trivial?] → FAST_PATH → [GATE-3] → DONE
```

**FAST_PATH — bypass para tareas triviales:**

No toda tarea necesita plan formal. El sistema distingue dos modos:

| Criterio | FAST_PATH | FULL_PATH |
|---|---|---|
| Archivos afectados | ≤ 3 | > 3 |
| Líneas cambiadas | ≤ 50 | > 50 |
| Nuevo módulo/servicio | NO | SÍ |
| Involucra auth/security/payments | NO | SÍ |

**Heurística de decisión (implementada en `plan-gate`):**
1. Si no existe PLAN.md → evaluar si el cambio es trivial (criterios arriba)
2. Si trivial → allow con `{mode: "fast_path"}` en log. Solo aplica GATE-3 (commit-checklist)
3. Si no trivial → block. Requiere PLAN.md completo (FULL_PATH)
4. Si existe PLAN.md → siempre FULL_PATH (el plan ya fue creado)

**FAST_PATH NO exime de:** tests (commit-checklist los verifica), non-goal checks, auto-format.

> Taxonomía de errores para decidir si RE-PLAN es necesario:
>
> | Error | Acción | ¿Cuenta como RE-PLAN? |
> |---|---|---|
> | Bug de implementación (1-3 archivos) | Fix inline | NO |
> | Test incorrecto | Corregir test | NO |
> | Diseño inadecuado (múltiples criterios fallan) | RE-PLAN completo | SÍ |
> | Scope insuficiente (faltan archivos) | Actualizar plan (§1.8) + continuar | NO |
> | Conflicto con non-goals | STOP + escalar | N/A |
>
> Solo errores de diseño consumen iteraciones de RE-PLAN (max 2). Los demás se resuelven sin penalizar el contador.

> El estado BLOCKED tiene salida definida:

**BLOCKED — protocolo de salida:**
- **Timeout:** `blocked_timeout_minutes: 15` (configurable en settings.json)
- **En sesión interactiva:** Notificar al usuario con diagnóstico: qué información falta, qué exploración falló, qué se necesita para desbloquear.
- **En modo autónomo:** Al expirar timeout → crear GitHub issue con label `agent-blocked` + contexto completo + STOP inmediato.
- **BLOCKED nunca es terminal silencioso.** Siempre produce un artefacto de diagnóstico.

### 2.2 Gates obligatorios (implementados como hooks) `[TO BUILD]`

> Los gates tienen whitelist de archivos de metadatos. El `plan-gate` NO bloquea la escritura del propio plan, artefactos de exploración ni archivos de memoria.

**Whitelist de metadatos (excluidos de plan-gate y tdd-gate):**
```
**/PLAN.md
**/RESEARCH.md
**/VERIFICATION.md
**/pipeline.yaml
.claude/memory/**
docs/src/wiki/**
**/*.log
```

| Gate | Tipo | Precondición | Si falla | Whitelist |
|---|---|---|---|---|
| **GATE-1** (Explore→Plan) | PreToolUse(Write) | Existe artefacto de exploración (archivos leídos, contexto documentado) | Bloquea escritura de plan. Volver a EXPLORE. | Solo aplica a PLAN.md |
| **GATE-2** (Plan→Execute) | PreToolUse(Write/Edit) | Existe `PLAN.md` con: archivos_afectados, non_goals, criterios_aceptacion, tests_requeridos | Bloquea escritura de código fuente. Volver a PLAN. | Excluye metadatos (whitelist arriba) |
| **GATE-3** (Execute→Verify) | PreToolUse(Bash:git commit) | Tests pasan + diff solo incluye archivos declarados en plan | Bloquea commit. Si tests fallan → ROLLBACK. | N/A |

### 2.3 Artefacto de plan (schema obligatorio)

```yaml
# PLAN.md — schema mínimo obligatorio
plan_id: plan-YYYY-MM-DD-NNN
status: draft | approved | executing | completed | failed
approach: "Descripción del enfoque elegido"
skill_used: "nombre-del-skill (si aplica)"
files_affected:
  - path: "src/services/auth.ts"
    action: create | modify | delete
    reason: "Por qué se toca este archivo"
non_goals:
  - pattern: "**/admin/**"
    reason: "No se construye UI de admin en esta tarea"
  - pattern: "**/notifications/**"
    reason: "Sistema de notificaciones fuera de scope"
acceptance_criteria:
  - "Los tests de auth pasan"
  - "No hay regresiones en test suite existente"
tests_required:
  - "tests/auth.test.ts — login flow"
  - "tests/auth.test.ts — token refresh"
rollback_tag: "pre-plan-YYYY-MM-DD-NNN"
max_iterations: 3          # Para loops autónomos (default: 10 en settings.json)
timeout_minutes: 60        # Tiempo máximo (default: 120)
cost_ceiling_usd: 5.00    # Presupuesto estimado (advisory — Claude Code no expone API de costes en tiempo real)
```

> Los campos `max_iterations`, `timeout_minutes`, `cost_ceiling_usd` usan **defaults de settings.json** si no se declaran. Solo incluirlos en PLAN.md cuando el valor difiere del default.
> - `cost_ceiling_usd` es **advisory**: el hook estima coste basándose en iteraciones × coste medio por iteración (configurable). No hay acceso a la API de billing en tiempo real. El circuit breaker usa `max_iterations` y `timeout_minutes` como enforcement duro.
> - `rollback_tag` se genera automáticamente si no se declara: `pre-{plan_id}`.
> - El plan mínimo viable tiene solo 4 campos obligatorios: `plan_id`, `approach`, `files_affected`, `acceptance_criteria`. Todo lo demás es opcional con defaults sensatos.
> - **Carga lazy de metadatos:** Solo CLAUDE.md (200 líneas) + MEMORY.md sección CRITICAL (50 líneas) se cargan siempre. Lessons, logs de skills, _index.yaml → solo on-demand cuando Claude los necesita.

### 2.4 Commitment checkpoint en modo autónomo

> En sesión interactiva: desviarse del plan requiere aprobación explícita del usuario.
> **En modo autónomo (routines/loops):** El commitment se valida programáticamente:

- Hook `PostToolUse` sobre `Write`/`Edit` compara archivos modificados vs `files_affected` del plan.
- Si el diff toca un archivo NO declarado en el plan:
  1. Log: `{timestamp, file, reason: "unplanned_write"}`
  2. Si el archivo coincide con un patrón de `non_goals` → **BLOQUEAR** inmediatamente + ROLLBACK
  3. Si no coincide con non_goals → **WARNING** + continuar + registrar para revisión post-ejecución

### 2.5 Non-goals con enforcement

> Los non-goals se persisten como patrones glob en el plan y se validan automáticamente.

- Non-goals se declaran en `PLAN.md` como patrones glob (ver schema arriba).
- Hook `PostToolUse(Write/Edit)` compara cada archivo escrito contra los patrones.
- Match con non-goal → bloqueo + log + rollback del archivo.
- Al finalizar la tarea, el agente `code-reviewer` verifica que ningún non-goal fue violado en el diff total.

### 2.6 Persistencia de estado — `.claude/state.yaml` `[TO BUILD]`

Los hooks necesitan saber en qué estado de la máquina se encuentra la sesión. Sin persistencia, cada hook opera sin contexto.

**Ubicación:** `.claude/state.yaml` (gitignored — estado local de sesión, no compartido).

**Schema:**
```yaml
# .claude/state.yaml — actualizado por hooks, leído por hooks
session_id: "uuid-de-la-sesion-actual"
current_state: "EXPLORE"   # EXPLORE | PLAN | EXECUTE | VERIFY | DONE | BLOCKED | RE-PLAN | FAST_PATH
mode: "full_path"           # full_path | fast_path
plan_path: null             # Ruta al PLAN.md activo (null si no existe)
replan_count: 0             # Contador de RE-PLANs (max 2 antes de escalar)
last_gate_passed: null      # GATE-1 | GATE-2 | GATE-3
last_updated: "2026-04-17T10:30:00Z"
blocked_since: null         # Timestamp si está en BLOCKED
error_log: []               # Últimos errores para diagnóstico
workflow_active: null        # Nombre del workflow activo (null si no hay)
workflow_step: 0             # Paso actual del workflow (0 si no hay)
```

**Protocolo de actualización:**
- `plan-gate` (PreToolUse): transiciona `EXPLORE → PLAN → EXECUTE` según el gate que evalúa
- `commit-checklist` (PreToolUse): transiciona `EXECUTE → VERIFY → DONE` al pasar GATE-3
- Rollback o RE-PLAN: actualiza `current_state` + incrementa `replan_count`
- FAST_PATH: `mode: fast_path`, `current_state: FAST_PATH`
- **Cada hook lee state.yaml al inicio y lo escribe al final si cambió el estado**

**Inicialización:** Si `.claude/state.yaml` no existe al iniciar sesión, `hook-health-check` lo crea con estado `EXPLORE`. Si existe pero `session_id` difiere → reset a `EXPLORE` (nueva sesión).

### 2.7 Ubicación canónica de artefactos `[CONVENTION]`

```
.claude/
├── pipeline.yaml             # Workflows de agentes (§workflow-runner)
├── plans/
│   ├── PLAN.md               # Plan activo (el vigente)
│   └── PLAN.v1.md            # Snapshots inmutables (§1.8)
├── state.yaml                # Estado de máquina (§2.6, gitignored)
└── hooks/                    # Scripts de enforcement (§10)
```

- `plan-gate` busca PLAN.md en `[".claude/plans/PLAN.md", "PLAN.md"]` (prioridad al canónico)
- Snapshots: `PLAN.v{N}.md` en el mismo directorio que el plan activo

---

## 3. Anatomía del Repositorio `[BUILT-IN]`

### 3.1 Proyecto (`.claude/` — parcialmente committed)

```
proyecto/
├── CLAUDE.md                  # Reglas del equipo (~200 líneas máx)
├── CLAUDE.local.md            # Overrides personales (gitignored)
└── .claude/
    ├── settings.json          # Permisos y config (committed)
    ├── settings.local.json    # Permisos personales (gitignored)
    ├── pipeline.yaml          # Workflows de agentes (committed) → /workflow-runner
    ├── pipeline.schema.yaml   # Documentación formal de la gramática (committed)
    ├── rules/                 # Reglas modulares (gitignored — instalado por stack)
    ├── commands/              # Slash commands (gitignored — copia stack-specific)
    ├── skills/                # Workflows auto-invocados (gitignored — copia stack-specific)
    ├── agents/                # Sub-agentes especializados (gitignored — copia stack-specific)
    ├── hooks/                 # Hooks programáticos (committed — enforcement universal)
    ├── memory/                # Memoria persistente (parcial gitignored)
    │   ├── lessons/           # Lessons del Self-Improvement Loop §1.8
    │   ├── plan-drift.log    # Log de violaciones de non-goals
    │   └── commit-bypass.log  # Audit trail de --no-verify
    ├── plans/                 # PLAN.md activo + snapshots PLAN.v*.md
    └── state.yaml             # Estado de la state machine (gitignored, §2.6)
```

> **Patrón template/instalado**: el catálogo completo (`agents/`, `skills/`, `rules/`, `stacks/` en la raíz del repo) NO está en `.claude/`. `make init-project STACK=<stack>` filtra por stack y copia a `.claude/agents/`, `.claude/skills/`, `.claude/rules/`. Por esto `.claude/agents/` puede tener menos entries que el catálogo raíz `/agents/` — es esperado.

### 3.2 Global (`~/.claude/` — personal)

```
~/.claude/
├── CLAUDE.md                  # Preferencias globales
├── settings.json              # Permisos globales
├── commands/                  # → /user:nombre
├── skills/
├── agents/
└── projects/<proyecto>/
    └── memory/
        ├── MEMORY.md          # Índice auto-gestionado (≤200 líneas al inicio)
        ├── debugging.md       # Archivos topic on-demand
        └── ...
```

**MEMORY.md vs CLAUDE.md:** `CLAUDE.md` es donde tú escribes instrucciones. `MEMORY.md` es el scratchpad de Claude — lo crea y actualiza automáticamente.

**Regla de precedencia:** Org policy → global → proyecto → subdirectorio → MEMORY.md. Lo más específico gana.

**MEMORY.md — política de priorización de las 200 líneas:**

> Las primeras ~200 líneas de MEMORY.md siguen esta estructura por secciones. Los headers son los delimitadores — los rangos de líneas son orientativos de tamaño, no posiciones fijas:

```markdown
# MEMORY.md — Estructura obligatoria

## CRITICAL — Nunca desplazado (~50 líneas)
<!-- Decisiones de arquitectura vigentes, reglas de negocio activas, gotchas confirmados -->

## ACTIVE — Lecciones activas ordenadas por last_referenced desc (~100 líneas)
<!-- Lessons con status:active, más recientes primero -->

## RECENT — Buffer de sesión (~50 líneas)
<!-- Notas de la última sesión, pendientes de clasificar -->

## OVERFLOW — Solo accesible on-demand (línea 201+)
<!-- Todo lo demás, cargado solo cuando Claude lo necesita explícitamente -->
```

- Entradas que se confirman como permanentes → promueven de ACTIVE a CRITICAL.
- Entradas no referenciadas en 30+ días → bajan a OVERFLOW o se archivan.

---

## 4. Flujo de Trabajo Diario `[CONVENTION + BUILT-IN]`

### 4.1 Ritual de Mañana (10 minutos)

* **Tú:** Abres la rama, revisas CLAUDE.md.
* **Claude:** Ejecuta la state machine: EXPLORE → PLAN → (espera aprobación o auto-valida) → EXECUTE → VERIFY.
  - Commitment checkpoint obligatorio (ver §2.4).
  - Non-goals explícitos y persistidos como glob patterns (ver §2.5).
  - **Si algo se tuerce → PARAR → estado RE-PLAN** (no parchear hacia adelante). Máximo 2 re-planes antes de escalar a humano.
* **Tú:** Decides sesión simple o worktrees paralelos.

### 4.2 Durante el Día

* **Hilo principal limpio.** No mezclar debates con ejecución.
* **Consultas rápidas:** `/btw` o `Ctrl+;` (side chat transient). `[BUILT-IN]`
* **Exploración de alternativas:** `/fork` para bifurcar sin contaminar. `[BUILT-IN]`
* **Corrección:** `/rewind` (doble Esc) para borrar contexto fallido. `[BUILT-IN]`
* **Regla de los 2 intentos:** 2 correcciones fallidas → `/clear` + reescribir incorporando lo aprendido. `[BUILT-IN]`
* **Investigaciones acotadas:** Nunca "investiga X" sin scope. Acotar o delegar a subagentes.
* **Refactorización:** `/simplify` — invocar agente `refactor-cleaner` (simplificación + cleanup de código). `[TO BUILD]` — crear como slash command que invoca el agente.
* **Tareas masivas:** `/batch` — dividir en worktrees independientes con supervisión. `[TO BUILD]` — crear como slash command que orquesta worktrees.

### 4.3 Ritual de Fin de Día

* **Claude:** Limpieza de cabos sueltos + actualización de lessons (schema §1.8).
* **Tú:** Actualizas CLAUDE.md o `/memory` con reglas nuevas.
* **Claude:** Ejecuta detección de contradicciones (§1.8) sobre todas las entries del día.
* **Tú:** Cierras bucles, matas sesiones ruidosas, dejas handoff claro.

---

## 5. Rules — Reglas Modulares con Scoping `[BUILT-IN]`

Cuando CLAUDE.md crece demasiado → fragmentar en `.claude/rules/`:

```
.claude/rules/
├── code-style.md
├── testing.md
├── api-conventions.md
└── security.md
```

- **Sin frontmatter `paths:`** → se carga en TODAS las sesiones.
- **Con frontmatter `paths:`** → solo cuando Claude toca archivos que coinciden:

```yaml
---
paths:
  - "src/api/**/*.ts"
  - "src/handlers/**/*.ts"
---
# Reglas de API
- Todos los handlers retornan { data, error }
- Validación con zod en cada handler
```

Contexto limpio = mejores resultados.

---

## 6. Slash Commands `[BUILT-IN]`

Un archivo `.md` en `.claude/commands/` → slash command automático:

- `review.md` → `/project:review`
- `fix-issue.md` → `/project:fix-issue`

**Sintaxis especial:**
- `` !`comando shell` `` — ejecuta y alimenta output al prompt
- `$ARGUMENTS` — parámetros del usuario

**Ejemplo (code review):**
```markdown
---
description: Review del branch actual antes de merge
---
## Cambios
!`git diff --name-only main...HEAD`
## Diff completo
!`git diff main...HEAD`
Revisa: calidad, seguridad, cobertura de tests, performance.
Feedback específico y accionable por archivo.
```

**Ejemplo (fix issue):**
```markdown
---
description: Investigar y corregir un issue de GitHub
argument-hint: [número-de-issue]
---
Analiza el issue #$ARGUMENTS.
!`gh issue view $ARGUMENTS`
Encuentra la causa raíz, corrígelo, y escribe un test que lo habría detectado.
```

- **Equipo:** `.claude/commands/` → `/project:nombre` (committed)
- **Personal:** `~/.claude/commands/` → `/user:nombre`

---

## 7. Skills vs Commands `[BUILT-IN]`

| Aspecto | Commands | Skills |
|---------|----------|--------|
| Activación | Solo manual (`/nombre`) | Automática por contexto O manual |
| Estructura | Un solo archivo `.md` | Carpeta con `SKILL.md` + archivos companion |
| Referencia a otros archivos | No | Sí, con `@ARCHIVO.md` |
| Ubicación | `.claude/commands/` | `.claude/skills/nombre/SKILL.md` |

**Unificación:** Un skill y un command con el mismo nombre generan el mismo slash command.

### 7.1 Skills auto-activados con guardrails

> Los skills auto-activados tienen threshold de confianza, log obligatorio y confirmación para skills de alto impacto.

**Skills se auto-activan** cuando Claude detecta coincidencia con la `description` del frontmatter YAML. Para prevenir falsos positivos:

**Log obligatorio de activación:**
```yaml
# Cada auto-activación se registra en .claude/memory/skill-activations.log
- timestamp: "2026-04-17T10:30:00Z"
  skill: "security-review"
  trigger_text: "fragmento que disparó la activación"
  match_type: exact | partial | fuzzy   # Tipo de coincidencia con description
  confirmed: true | false     # si el usuario confirmó
  false_positive: false        # marcado post-hoc si fue innecesario
```

> Política de rotación: `skill-activations.log` se rota semanalmente por `session-consolidate`. Mantener última semana activa. Archivar en `skill-activations.{date}.log`. Máximo 4 archivos de archivo (1 mes).

**Niveles de activación por impacto:**

| Impacto del skill | Threshold | Comportamiento |
|---|---|---|
| **Bajo** (formatting, linting) | Cualquier match | Auto-activa silenciosamente |
| **Medio** (code-review, testing) | `exact` o `partial` match | Auto-activa + notifica al usuario |
| **Alto** (security, deploy, delete) | Solo `exact` match + confirmación | Propone activación, espera confirmación explícita |

El impacto se declara en el frontmatter del skill:
```yaml
---
description: Security review exhaustivo
impact: high
---
```

---

## 8. Agents — Sub-agentes Especializados `[BUILT-IN]`

Definidos en `.claude/agents/`, con contexto aislado:

```yaml
---
name: code-reviewer
description: Revisor experto. Usar PROACTIVAMENTE al revisar PRs.
model: sonnet
tools: Read, Grep, Glob
---
Eres un revisor senior enfocado en corrección y mantenibilidad.
- Flaggea bugs, no solo estilo
- Sugiere fixes concretos, no mejoras vagas
- Verifica edge cases y manejo de errores
- Performance solo cuando importa a escala
```

**Campos clave:**
- `model:` — modelo diferente por agente (haiku para rápido, opus para razonamiento profundo).
- `tools:` — restricción deliberada de permisos. Auditor de seguridad solo lee.
- **Contexto separado:** trabaja aislado, devuelve resumen. No infla el hilo principal.

**Aislamiento de contexto en pipelines:**
- architect → coder → tester → reviewer: cada agente recibe **solo el output de sus dependencias**, no todo el contexto acumulado.
- El architect planifica sin detalles de implementación.
- El tester testea sin saber qué el coder consideró "fine".
- El reviewer revisa sin el sesgo optimista del implementador.

**Agente ≠ upgrade de un workflow:** Si el path está completamente definido → script, command o hook. Agentes solo para decisiones que requieren razonamiento: múltiples paths, outputs variables, resultados inesperados.

---

## 9. Permisos — settings.json `[BUILT-IN]`

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Read", "Write", "Edit"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(curl *)",
      "Read(./.env)",
      "Read(./.env.*)"
    ]
  }
}
```

**Tres zonas:**
- `allow` — ejecución silenciosa
- `deny` — bloqueado absoluto
- **Todo lo demás** — Claude pide permiso

**`settings.local.json`** para overrides personales (gitignored).

**Control de auto-memory:**
- `"autoMemoryEnabled": false` en settings.json del proyecto o global.
- `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` para CI/CD.
- Toggle en sesión: `/memory` → `Auto-memory: on/off`.

---

## 10. Hooks — Acciones Automáticas Sin Excepción `[BUILT-IN + TO BUILD]`

Los hooks se ejecutan **siempre**, sin variación ni juicio de Claude:

- **PreToolUse:** Validación antes de ejecutar
- **PostToolUse:** Acción después de ejecutar
- **Stop:** Verificación al cerrar sesión

**Hook vs rule:** 100% de las veces sin excepción → hook. Depende del contexto → rule o skill.

### 10.1 Hooks de enforcement obligatorios

> Estos hooks implementan los gates de la state machine (§2) y los guardrails de validación (§1.6).

| Hook | Tipo | Trigger | Acción |
|---|---|---|---|
| `plan-gate` | PreToolUse(Write/Edit) | Intento de escribir código sin PLAN.md | Bloquea + mensaje: "Plan requerido. Ejecuta EXPLORE → PLAN primero." |
| `tdd-gate` | PreToolUse(Write/Edit) | Escribir implementación sin tests previos | Bloquea + mensaje: "Tests primero. Escribir tests que fallen antes de implementar." Configurable por proyecto (ver abajo). |
| `commit-checklist` | PreToolUse(Bash:git commit) | Intento de commit | Ejecuta checklist: tests existen, tests pasan, diff planificado. Bloquea si falla. |
| `non-goal-guard` | PostToolUse(Write/Edit) | Archivo escrito coincide con non_goal glob | Bloquea + rollback del archivo + log. |
| `plan-drift-detector` | PostToolUse(Write/Edit) | Archivo modificado no está en files_affected | Warning + log. Si coincide con non_goal → bloqueo. |
| `auto-format` | PostToolUse(Write/Edit) | Cualquier escritura | Ejecuta formatter del proyecto. |
| `session-consolidate` | Stop | Cierre de sesión | Promueve conocimiento elegible al wiki + archiva lessons expiradas. |
| `session-read-logger` | PostToolUse(Read) | Cualquier lectura de archivo | Registra path + timestamp en `.claude/session-reads.log`. Insumo para `session-consolidate`. |

> `session-consolidate` ejecuta en orden determinista:

**Configuración de `tdd-gate` por proyecto:**

El tdd-gate es configurable en `settings.json` para adaptarse a diferentes proyectos (legacy, prototipos, etc.):

```jsonc
// .claude/settings.json
{
  "hooks": {
    "tdd-gate": {
      "mode": "warn",                    // "block" | "warn" | "off"
      "sourcePattern": "src/**/*.{ts,py,rs}",  // Archivos de código fuente
      "testPattern": "tests/**/*.test.{ts,py}", // Dónde buscar tests
      "excludePatterns": [               // Archivos excluidos del gate
        "src/generated/**",
        "src/migrations/**",
        "*.config.*",
        "*.d.ts"
      ],
      "allowNewModules": true            // Permite crear módulos sin tests previos (warn al commit)
    }
  }
}
```

| `mode` | Comportamiento |
|---|---|
| `block` | Impide escribir implementación sin tests. TDD estricto. |
| `warn` | Permite escribir pero emite warning visible. **Default recomendado.** |
| `off` | Desactiva tdd-gate (prototipos, spikes, exploración). |

**Heurística del tdd-gate:**
1. Recibe evento de Write/Edit sobre archivo que matchea `sourcePattern`
2. Si `mode == off` → allow
3. Si el archivo matchea algún `excludePatterns` → allow
4. Busca test correspondiente según `testPattern` + convención de nombres (ej. `auth.ts` → `auth.test.ts`)
5. Si test no existe y `allowNewModules == true` → allow con warning
6. Si test no existe y `allowNewModules == false` → block/warn según `mode`
7. Si test existe → allow
> 1. Actualizar `last_referenced` de entries consultadas en la sesión (lee `.claude/session-reads.log`)
> 1.5. Incrementar `sessions_without_repeat` de entries cuyo `trigger` NO apareció en la sesión actual. Reset a 0 para entries cuyo trigger SÍ ocurrió (recurrencia detectada).
> 2. Archivar entries con `last_referenced > 30 días`
> 3. Promover entries elegibles (solo las que sobrevivieron paso 2)
> 4. Actualizar `_index.yaml`
> 5. Rotar `skill-activations.log` si aplica
>
> Regla adicional en CLAUDE.md: "Ejecutar tests con `Bash` tool — nunca reportar resultado sin output de terminal visible."

### 10.2 Especificación técnica de hooks `[TO BUILD]`

> Los hooks NO son directivas textuales — son scripts ejecutables con contrato de I/O definido.

**Runtime:** Python 3.10+ (stdlib only, cero dependencias externas). Alternativa: bash + `jq` para hooks triviales (auto-format).

**Contrato de I/O:**

```
stdin  → JSON del evento (schema de Claude Code)
stdout → JSON de respuesta: {"decision": "allow"|"block", "reason": "..."}
exit 0 → allow (si stdout vacío)
exit 1 → block
exit 2 → error del hook (fail-closed: se trata como block)
```

**Schema de entrada (stdin):**
```json
{
  "tool_name": "Write",
  "tool_input": {
    "file_path": "src/services/auth.ts",
    "content": "..."
  },
  "session_id": "uuid",
  "timestamp": "2026-04-17T10:30:00Z"
}
```

**Timeout:** 10 segundos max por hook. Timeout → exit 2 (fail-closed).

**Dependencias del entorno:** `python3`, `git`, `find`, `jq` — presentes en cualquier dev environment estándar.

**Estructura de archivos:**
```
hooks/                        # Fuente de verdad (make install → ~/.claude/hooks/)
└── session-consolidate.sh    # IMPLEMENTADO: Stop hook — consolidación al cierre

# [TO BUILD] — hooks descritos en este documento, pendientes de implementación:
# .claude/hooks/plan-gate.py              # GATE-2: verifica PLAN.md antes de código (+ FAST_PATH)
# .claude/hooks/tdd-gate.py               # Verifica tests antes de implementación (configurable)
# .claude/hooks/commit-checklist.py       # GATE-3: checklist pre-commit
# .claude/hooks/non-goal-guard.py         # Detecta writes a paths prohibidos
# .claude/hooks/plan-drift-detector.py    # Warning si archivo no está en plan
# .claude/hooks/hook-health-check.py      # Dry-run de todos los hooks al inicio + inicializa state.yaml
# .claude/hooks/session-read-logger.py    # PostToolUse(Read): registra lecturas en session-reads.log
# .claude/hooks/auto-format.sh            # Ejecuta formatter (bash trivial)
```

**Ejemplo de implementación — `plan-gate.py`:**
```python
#!/usr/bin/env python3
"""GATE-2: Bloquea escritura de código fuente si no existe PLAN.md válido.
   Implementa FAST_PATH bypass para tareas triviales (§2.1)."""
import json, sys, os, fnmatch, subprocess

# Whitelist de archivos excluidos del gate (metadatos, no código)
WHITELIST = [
    "**/PLAN.md", "**/PLAN.v*.md", "**/RESEARCH.md", "**/VERIFICATION.md",
    ".claude/memory/**", "docs/src/wiki/**", "**/*.log", "**/*.yaml",
    "**/REVIEW.md", "**/SECURITY.md"
]

PLAN_REQUIRED_FIELDS = ["plan_id", "files_affected", "acceptance_criteria"]

# Ubicación canónica del plan
PLAN_LOCATIONS = [".claude/plans/PLAN.md", "PLAN.md"]

# Patrones que NUNCA son triviales (siempre requieren FULL_PATH)
SENSITIVE_PATTERNS = ["**/auth/**", "**/security/**", "**/payment*/**", "**/admin/**"]

FAST_PATH_MAX_FILES = 3
FAST_PATH_MAX_LINES = 50

def is_whitelisted(file_path: str) -> bool:
    return any(fnmatch.fnmatch(file_path, pattern) for pattern in WHITELIST)

def find_plan() -> str | None:
    """Busca PLAN.md en ubicaciones canónicas."""
    for loc in PLAN_LOCATIONS:
        if os.path.exists(loc):
            return loc
    return None

def plan_is_valid(plan_path: str) -> tuple[bool, str]:
    with open(plan_path) as f:
        content = f.read()
    missing = [field for field in PLAN_REQUIRED_FIELDS if field not in content]
    if missing:
        return False, f"PLAN.md incompleto. Faltan: {', '.join(missing)}"
    return True, ""

def is_sensitive(file_path: str) -> bool:
    return any(fnmatch.fnmatch(file_path, p) for p in SENSITIVE_PATTERNS)

def is_trivial_change() -> bool:
    """Heurística: ≤3 archivos staged y ≤50 líneas cambiadas."""
    try:
        diff = subprocess.run(
            ["git", "diff", "--cached", "--stat", "--stat-count=100"],
            capture_output=True, text=True, timeout=5
        )
        if diff.returncode != 0:
            # Si no hay staged, mirar unstaged
            diff = subprocess.run(
                ["git", "diff", "--stat", "--stat-count=100"],
                capture_output=True, text=True, timeout=5
            )
        lines = [l for l in diff.stdout.strip().split("\n") if l.strip()]
        if not lines:
            return True  # No changes = trivial
        # Última línea es el summary "N files changed, M insertions..."
        file_count = len(lines) - 1 if len(lines) > 1 else len(lines)
        # Parse insertions/deletions from summary
        summary = lines[-1] if lines else ""
        total_lines = 0
        for part in summary.split(","):
            part = part.strip()
            if "insertion" in part or "deletion" in part:
                total_lines += int(part.split()[0])
        return file_count <= FAST_PATH_MAX_FILES and total_lines <= FAST_PATH_MAX_LINES
    except (subprocess.TimeoutExpired, Exception):
        return False  # Fail-closed: asume no-trivial

def main():
    event = json.load(sys.stdin)
    file_path = event.get("tool_input", {}).get("file_path", "")

    if is_whitelisted(file_path):
        json.dump({"decision": "allow", "reason": "Archivo de metadatos (whitelist)"}, sys.stdout)
        sys.exit(0)

    plan_path = find_plan()

    if plan_path:
        # PLAN.md existe → siempre FULL_PATH
        valid, reason = plan_is_valid(plan_path)
        if not valid:
            json.dump({"decision": "block", "reason": reason}, sys.stdout)
            sys.exit(1)
        json.dump({"decision": "allow", "reason": f"PLAN.md válido ({plan_path})"}, sys.stdout)
        sys.exit(0)

    # No hay PLAN.md → evaluar FAST_PATH
    if is_sensitive(file_path):
        json.dump({"decision": "block",
                    "reason": f"Archivo sensible ({file_path}) requiere PLAN.md. No FAST_PATH para auth/security/payments."}, sys.stdout)
        sys.exit(1)

    if is_trivial_change():
        json.dump({"decision": "allow",
                    "reason": "FAST_PATH: cambio trivial (≤3 archivos, ≤50 líneas, no sensible)"}, sys.stdout)
        sys.exit(0)

    json.dump({"decision": "block",
                "reason": "Cambio no trivial sin PLAN.md. Ejecuta EXPLORE → PLAN primero."}, sys.stdout)
    sys.exit(1)

if __name__ == "__main__":
    main()
```

### 10.3 Health check de hooks `[TO BUILD]`

> Si un hook falla silenciosamente, TODOS los gates se desactivan. Esto es inaceptable.

**Protocolo:**

1. **Al inicio de sesión (via `PreToolUse` en la primera invocación):** `hook-health-check.py` se ejecuta como `PreToolUse` hook. Usa un flag de timestamp en `.claude/state.yaml` (`last_health_check`) para ejecutar el dry-run solo una vez por sesión (si `last_health_check` es de la sesión actual → skip). Esto sustituye la necesidad de un hook `SessionStart` que no existe en Claude Code.
2. **En la primera invocación:** dry-run de cada hook con fixtures de test predefinidas.
3. **Resultado por hook:** `pass` | `fail` | `timeout`
4. **Si algún hook falla:**
   - Warning persistente en la sesión: `"⚠️ Hook {name} no operativo. Gates degradados."`
   - Log en `.claude/memory/hook-health.log`
   - La sesión NO se bloquea, pero opera en modo degradado con warnings visibles
4. **Política fail-closed:** Hook que no responde en 10s → se trata como `block`. Nunca como `allow`. Mejor bloquear por error que permitir por fallo.

**Fixture de test (`.claude/hooks/fixtures/`):**
```json
// fixture-write-code.json — simula escritura de archivo de código
{
  "tool_name": "Write",
  "tool_input": {"file_path": "src/test-file.ts", "content": "// test"},
  "session_id": "health-check",
  "timestamp": "2026-01-01T00:00:00Z"
}
```

---

## 11. Circuit Breakers para Operación Autónoma `[TO BUILD]`

> Todo proceso autónomo tiene límites duros no negociables.

### 11.1 Configuración obligatoria para loops y routines

```yaml
# Parámetros obligatorios — declarados en PLAN.md o en la definición del loop/routine
circuit_breaker:
  max_iterations: 10          # Máximo absoluto de iteraciones
  timeout_minutes: 120        # Tiempo máximo total
  cost_ceiling_usd: 10.00    # Presupuesto máximo de tokens (estimado)
  consecutive_failures: 3     # Fallos consecutivos antes de abortar
  fallback: abort_and_notify  # abort_and_notify | create_issue_and_stop | rollback_and_notify
  notify_channel: null        # Slack/email/GitHub issue (opcional)
```

### 11.2 Comportamiento ante límites

| Límite alcanzado | Acción |
|---|---|
| `max_iterations` | STOP inmediato. Crear issue con estado actual + progreso parcial. |
| `timeout_minutes` | STOP inmediato. Commit parcial de trabajo completado + issue. |
| `cost_ceiling_usd` | STOP inmediato. Log de tokens consumidos + issue. |
| `consecutive_failures` | ROLLBACK al último commit exitoso + issue con logs de errores. |
| Loop no converge (mismos tests fallan 3 veces) | STOP + crear issue con diagnóstico + sugerir intervención humana. |

### 11.3 Escalación a humano

Cuando el circuit breaker actúa:
1. Crear GitHub issue con label `agent-escalation`
2. Incluir: estado actual, progreso completado, punto de fallo, logs relevantes
3. Asignar al owner del repo
4. NO intentar "una iteración más" — el circuit breaker es non-negotiable

---

## 12. Rollback Strategy `[CONVENTION + TO BUILD]`

> Cada operación autónoma es reversible por diseño.

### 12.1 Protocolo de snapshots

1. **Antes de ejecutar:** `git tag pre-<plan_id>` — snapshot del estado limpio
2. **Durante ejecución:** Commits atómicos por unidad de trabajo (ver §12.3), cada uno con referencia al plan:
   ```
   feat: implement auth service [plan-2026-04-17-001]
   ```
3. **Después de cada commit:** Ejecutar test suite completa
   - Tests pasan → continuar
   - Tests fallan → clasificar error (ver §12.4) antes de decidir acción

### 12.2 Branching para trabajo autónomo

- Routines y loops autónomos SIEMPRE trabajan en branch `claude/<plan_id>`
- Formato: `claude/{plan_id}` (ej. `claude/plan-2026-04-17-001`). No confundir con branches del desarrollador (`feature/`, `fix/`)
- NUNCA push directo a main
- Al completar → crear PR para revisión humana
- PR incluye: resumen de cambios, tests añadidos, logs de ejecución
- **Cleanup:** Branches `claude/*` mergeados → eliminar. Branches `claude/*` con >7 días sin actividad → notificar para revisión o eliminación

### 12.3 Definición de "unidad de trabajo" `[CONVENTION]`

**Una unidad de trabajo = un criterio de aceptación del plan.** Cada entry en `acceptance_criteria` de PLAN.md produce un commit atómico. Esto alinea granularidad de commits con verificabilidad.

Ejemplo:
```yaml
acceptance_criteria:
  - "Los tests de login pasan"          → commit 1
  - "Los tests de token refresh pasan"  → commit 2
  - "No hay regresiones"                → verificación final (no commit propio)
```

### 12.4 Clasificación de errores antes de rollback `[CONVENTION]`

| Tipo de error | Señal de detección | Acción | Cuenta como RE-PLAN |
|---|---|---|---|
| **Sintaxis/import** | Error en compilación o lint | Fix inline (max 2 intentos) → rollback si persiste | NO |
| **Test falla por implementación** | Test existía ANTES del cambio actual | `git revert HEAD` + corregir implementación | NO |
| **Test falla por test incorrecto** | Test creado EN ESTE commit | Revisar y corregir el test primero, no rollback | NO |
| **Error de diseño** | Múltiples acceptance_criteria fallan simultáneamente | `git reset --hard pre-<plan_id>` + RE-PLAN | SÍ |
| **Dependencia externa** | Error de red, API, paquete no encontrado | Retry con backoff (max 3) → BLOCKED si persiste | NO |
| **Scope insuficiente** | Se necesitan archivos no declarados en plan | Actualizar plan (§1.8 backward propagation) + continuar | NO |
| **Conflicto con non-goals** | Write a path de non_goal | STOP inmediato + escalar a humano | N/A |

### 12.5 Recuperación ante crash de sesión `[TO BUILD]`

Una sesión puede terminar abruptamente (timeout, cierre de terminal, error de red) sin ejecutar el hook Stop. El sistema debe recuperarse sin perder estado ni dejar artefactos corruptos.

**Protocolo de recuperación (ejecutado por `hook-health-check` al inicio de sesión):**

1. **Detectar sesión interrumpida:** Leer `.claude/state.yaml`. Si `current_state` no es `DONE` y `session_id` difiere del actual → sesión previa no completó
2. **Evaluar estado:**
   - `current_state == EXECUTE` → hay trabajo parcial. Verificar `git status` para cambios uncommitted
   - `current_state == VERIFY` → ejecución completó, verificación no. Relanzar GATE-3
   - `current_state in (EXPLORE, PLAN)` → sin riesgo de datos corruptos. Reset a EXPLORE
3. **Acciones de recuperación:**
   - Si hay cambios uncommitted → `git stash` con label `crash-recovery-{timestamp}` + log
   - Si hay commits después del tag `pre-{plan_id}` sin verificación → marcar para re-verificación
   - Emitir warning: `"⚠️ Sesión anterior interrumpida en estado {state}. Cambios stasheados. Revisar antes de continuar."`
4. **Logging:** Registrar el crash en `.claude/memory/hook-health.log` con timestamp, estado previo, acción tomada

---

## 13. Routines — Ejecución Autónoma en la Nube `[BUILT-IN]`

Una routine = prompt + repositorio GitHub + connectors, ejecutada en infraestructura de Anthropic.

**Modelo de ejecución:**
- VM fresca, clona repo, ejecuta prompt con connectors.
- Sesión discreta — sin estado entre ejecuciones (previene drift).
- `CLAUDE_CODE_REMOTE=true` para detectar ejecución cloud.

**Tres triggers:**

| Trigger | Configuración | Caso de uso |
|---|---|---|
| **Schedule** | Cron via `/schedule` o web UI | Mantenimiento nocturno |
| **API** | Endpoint HTTP + bearer token | Webhooks de Sentry/Datadog |
| **GitHub** | `pull_request.opened`, `release`, tags | PR review, release notes |

**Branch protection:** Solo push a `claude/`. Nunca a main.

**Least privilege:** Solo conectar servicios que la routine necesita.

**Circuit breaker obligatorio:** Toda routine MUST declarar `circuit_breaker` (ver §11.1). Routines sin circuit breaker → no se ejecutan.

**Prompts para routines — completamente deterministas:**
- Cubrir cada punto de decisión
- Qué hacer si no encuentra resultados
- Formato exacto de output
- Acción alternativa ante fallos
- No hay humano para resolver ambigüedades

**Límites diarios:** Pro: 5, Max: 15, Team/Enterprise: 25.

**Tres patrones para empezar:**
1. **Nightly Issue Groomer** (schedule): Labels, equipo responsable, resumen en Slack.
2. **PR Review Bot** (GitHub): Prompt adversarial — edge cases, concurrencia, lógica (no estilo).
3. **Deploy Verifier** (API): Smoke checks + error logs + trace al commit.

**Regla de arranque:** UNA routine schedule de bajo riesgo. Observar una semana antes de escalar.

> Protocolo de integración de output de routines:
> - Routine produce output → lo deja en `ops/sessions/<routine-name>-<date>.md`
> - Al iniciar sesión interactiva, Claude verifica si hay nuevos archivos en `ops/sessions/` desde la última sesión
> - Si existen → mostrar resumen al usuario y preguntar si actuar sobre ellos
> - Output de routines NUNCA se promueve al wiki automáticamente — requiere revisión humana primero

---

## 14. Wiki de Proyecto — Memoria Permanente con Indexación `[TO BUILD]`

> El wiki tiene índice estructurado y criterios de promoción objetivos.

### 14.1 Tres capas de memoria

| Capa | Ubicación | Persistencia | Propósito |
|---|---|---|---|
| `memory/` | `.claude/memory/` | Efímera (gitignored) | Contexto de sesión, WIP |
| `auto-memory` | `~/.claude/projects/<proj>/memory/` | Semi-persistente (local) | MEMORY.md auto-gestionado |
| `wiki/` | `docs/src/wiki/` | Permanente (committed) | Conocimiento confirmado |

### 14.2 Flujo de conocimiento

```
Sesión → .claude/memory/ (captura rápida)
              ↓ criterios de promoción (§14.4)
         docs/src/wiki/ (conocimiento permanente)
```

### 14.3 Estructura del wiki con índice

```
docs/src/wiki/
├── _index.yaml              # Índice semántico para búsqueda eficiente
├── _overview.md              # Propósito, stack, decisiones fundacionales
├── entities/                 # Modelos, servicios, módulos
├── concepts/                 # Patrones, convenciones, reglas de negocio
├── decisions/                # ADRs con contexto y alternativas
├── glossary.md               # Términos del dominio
└── log.md                    # Registro cronológico
```

**Índice semántico (`_index.yaml`):**

> Claude consulta el índice antes de leer archivos completos. El índice es un lookup ligero (~50-100 líneas) que evita leer todo el wiki para encontrar información.

```yaml
# _index.yaml — actualizado automáticamente por session-consolidate hook
entries:
  - file: "decisions/auth-strategy.md"
    keywords: [auth, JWT, session, cookies, login]
    summary: "Decisión: usar session cookies sobre JWT para auth web"
    last_updated: 2026-04-15
  - file: "concepts/error-handling.md"
    keywords: [errors, exceptions, logging, sentry]
    summary: "Patrón de manejo de errores con envelope response"
    last_updated: 2026-04-10
```

> Límite de 200 entries en `_index.yaml`. Al superar → archivar entries con `last_updated > 90 días` a `_index.archived.yaml`. Si tras archivar sigue > 200 → fusionar entries del mismo directorio en una sola con keywords combinados.

### 14.4 Criterios de promoción objetivos (memory → wiki)

> La promoción NO depende de juicio subjetivo de Claude.

| Criterio | Tipo | Condición |
|---|---|---|
| **Explícito** | Usuario ejecuta `/promote <entry>` | Inmediato |
| **Implícito** | Entry sobrevive 3+ sesiones sin contradicción Y `status == active` | Automático en session-consolidate |
| **Consenso** | 2+ agentes referencian la misma entry en sesiones distintas | Automático |
| **Tema elegible** | Decisión de arquitectura, regla de negocio, convención adoptada | Requerido |

**NO se promueve:**
- Workarounds temporales
- Bugs en progreso
- Información tentativa
- Entries con `status != active`

### 14.5 Integración automática

- Hook `session-consolidate` promueve entries elegibles al wiki al cerrar sesión.
- Agente `memory-consolidator` marca entries promovidas como archivadas.
- Agentes `planner`, `architect`, `doc-updater` consultan `_index.yaml` antes de leer el wiki completo.
- Al promover una entry → actualizar `_index.yaml` automáticamente.

---

## 15. Estructura de Prompts Efectivos `[CONVENTION]`

**Context engineering > prompt engineering:** Curar *qué información entra* importa más que *cómo escribes* la instrucción.

Fórmula: `[Rol] + [Tarea] + [Contexto]`

- **Front-load lo importante:** Instrucción crítica al inicio.
- **Ser específico:** Cuanto más preciso, mejor resultado.
- **Incluir verificación:** Tests, outputs esperados, criterios de éxito.
- **Authority language solo en reglas críticas:** MUST, non-negotiable, no exceptions. Si todo es "non-negotiable", nada lo es.

**Interactivo vs Routine:**
- Interactivo: tolera ambigüedad (hay humano).
- Routine: completamente determinista (no hay humano). Cubrir cada punto de decisión + fallbacks.

---

## 16. Principios Core de Ingeniería `[CONVENTION]`

- **Simplicity First:** Cada cambio, lo más simple posible. Mínimo código.
- **No Laziness:** Causa raíz. Nunca fixes temporales. Estándar senior.
- **Minimal Impact:** Solo tocar lo necesario. No introducir bugs colaterales.
- **Kill Process, Don't Optimize It:** Proceso sin valor = latencia pura. Eliminar, no optimizar.

---

## 17. Orden de Setup Progresivo `[CONVENTION]`

1. **`/init`** → CLAUDE.md starter. Recortar a ~20 líneas esenciales.
2. **`settings.json`** → Permisos básicos: allow test/build, deny .env y destructivos.
3. **1-2 commands** → Workflows más repetidos.
4. **`rules/`** → Cuando CLAUDE.md supere ~50 líneas, fragmentar con path scoping.
5. **`~/.claude/CLAUDE.md`** → Preferencias personales globales.
6. **Hooks de enforcement** → Instalar hooks de §10.1 para gates obligatorios.
7. **Skills, Agents y Workflows** → Cuando un workflow complejo se repita. `pipeline.yaml` define la secuencia de agentes por tipo de tarea. `make init-project` lo instala.
8. **Circuit breakers** → Configurar antes de habilitar cualquier loop/routine.

> **Regla del 95%:** Los pasos 1-6 cubren el 95% de las necesidades.

### 17.1 Adopción progresiva en proyectos existentes

Este sistema no requiere instalación "big bang". Adoptar incrementalmente:

| Fase | Qué instalar | Esfuerzo | Valor |
|---|---|---|---|
| **0. Mínimo** | CLAUDE.md (~20 líneas) + settings.json (allow/deny) | 5 min | Alto — contexto + seguridad básica |
| **1. Observar** | `session-read-logger` (PostToolUse) + `auto-format` (PostToolUse) | 10 min | Medio — datos sin disruption |
| **2. Guardrails suaves** | `tdd-gate` en modo `warn` + `plan-drift-detector` | 15 min | Alto — visibilidad sin bloqueo |
| **3. Enforcement** | `plan-gate` + `commit-checklist` + `non-goal-guard` | 30 min | Alto — gates activos |
| **4. Memoria** | MEMORY.md estructura + `session-consolidate` | 20 min | Medio — persistencia |
| **5. Autonomía** | Circuit breakers + branching policy + crash recovery | 30 min | Para routines/loops |

**Regla:** No avanzar a la siguiente fase hasta que la actual funcione sin fricción durante 1 semana.

**Para proyectos legacy sin tests:** Empezar con `tdd-gate.mode: "off"` e ir subiendo a `"warn"` cuando exista cobertura en módulos nuevos.

**Para equipos:** Un miembro instala las fases 0-2. El equipo evalúa durante 1 sprint. Si hay consenso → fases 3-5.
