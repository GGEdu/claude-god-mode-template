
## 1. Filosofía Central (El Modelo Operativo)

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

> **[FIX CRÍTICO-3 + Guardrails de alucinación]** La autovalidación NO depende de auto-reflexión del modelo. Se implementa con hooks programáticos.

- **TDD estricto enforced por hook:** Un hook `PreToolUse` sobre `Write`/`Edit` verifica que existan tests para el módulo ANTES de permitir escribir código de implementación. Si los tests se crean DESPUÉS del código → hook fuerza revisión por agente independiente con prompt adversarial.
- **Validación factual obligatoria:** Antes de afirmar que un archivo/función/API existe o tiene cierto comportamiento, Claude MUST ejecutar `grep`/`read_file` para verificar. Nunca afirmar de memoria. Esto es una regla non-negotiable en CLAUDE.md.
- **Checklist programático pre-commit** (hook `PreToolUse` sobre `Bash(git commit*)`):
  1. ¿Existen tests para los archivos modificados?
  2. ¿Los tests fallan sin la implementación? (prueba de que el test detecta el fallo)
  3. ¿El diff incluye solo archivos declarados en el plan?
  4. Si alguna respuesta es NO → bloquear commit + registrar razón.
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

> **[FIX CRÍTICO-A + CRÍTICO-B + ALTO-C + ALTO-D]** El loop de mejora tiene criterios objetivos, detección de contradicciones, TTL y promoción basada en evidencia.

**Protocolo de registro de lecciones:**

Después de CADA corrección del usuario → registrar con schema estructurado:

```yaml
# Lesson entry — schema obligatorio
id: lesson-YYYY-MM-DD-NNN
date: 2026-04-17
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

**Detección de contradicciones:** Al escribir una nueva lesson, buscar entries existentes con keywords solapantes. Si se detecta contradicción → marcar la anterior como `status: superseded` + `superseded_by: <new_id>` + registrar en log de cambios.

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

### 1.9 Elegancia balanceada

- Cambios no triviales: pausar → "¿hay una forma más elegante?"
- Fix hacky: reimplementar con conocimiento acumulado.
- Fixes simples y obvios: NO sobre-ingenierar.

### 1.10 Bug fixing autónomo

- Diagnosticar y resolver sin pedir ayuda al usuario.
- Investigar logs, errores, tests fallidos de forma independiente.
- Cero cambio de contexto requerido del usuario.

---

## 2. Máquina de Estados para Operación Autónoma

> **[FIX CRÍTICO-1 + CRÍTICO-2]** El flujo de trabajo ya no es una directiva textual — es un autómata con estados, transiciones y gates obligatorios.

### 2.1 Estados y transiciones

```
                              ┌─────────────────────────────────────────┐
                              │                                         │
INIT → EXPLORE → [GATE-1] → PLAN → [GATE-2] → EXECUTE → [GATE-3] → VERIFY → DONE
         │                     │                   │                    │
         │                     │                   │                    │
         ↓ (fail)              ↓ (fail, max 2)     ↓ (fail)            ↓ (fail)
       BLOCKED              RE-PLAN              ROLLBACK            ROLLBACK
                               ↑                   │                    │
                               └───────────────────┘                    │
                               ↑                                        │
                               └────────────────────────────────────────┘
```

### 2.2 Gates obligatorios (implementados como hooks)

| Gate | Tipo | Precondición | Si falla |
|---|---|---|---|
| **GATE-1** (Explore→Plan) | PreToolUse(Write) | Existe artefacto de exploración (archivos leídos, contexto documentado) | Bloquea escritura de plan. Volver a EXPLORE. |
| **GATE-2** (Plan→Execute) | PreToolUse(Write/Edit) | Existe `PLAN.md` con: archivos_afectados, non_goals, criterios_aceptacion, tests_requeridos | Bloquea escritura de código. Volver a PLAN. |
| **GATE-3** (Execute→Verify) | PreToolUse(Bash:git commit) | Tests pasan + diff solo incluye archivos declarados en plan | Bloquea commit. Si tests fallan → ROLLBACK. |

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
max_iterations: 3          # Para loops autónomos
timeout_minutes: 60        # Tiempo máximo
cost_ceiling_usd: 5.00    # Presupuesto máximo de tokens
```

### 2.4 Commitment checkpoint en modo autónomo

> En sesión interactiva: desviarse del plan requiere aprobación explícita del usuario.
> **En modo autónomo (routines/loops):** El commitment se valida programáticamente:

- Hook `PostToolUse` sobre `Write`/`Edit` compara archivos modificados vs `files_affected` del plan.
- Si el diff toca un archivo NO declarado en el plan:
  1. Log: `{timestamp, file, reason: "unplanned_write"}`
  2. Si el archivo coincide con un patrón de `non_goals` → **BLOQUEAR** inmediatamente + ROLLBACK
  3. Si no coincide con non_goals → **WARNING** + continuar + registrar para revisión post-ejecución

### 2.5 Non-goals con enforcement

> **[FIX MEDIO-7]** Los non-goals se persisten como patrones glob en el plan y se validan automáticamente.

- Non-goals se declaran en `PLAN.md` como patrones glob (ver schema arriba).
- Hook `PostToolUse(Write/Edit)` compara cada archivo escrito contra los patrones.
- Match con non-goal → bloqueo + log + rollback del archivo.
- Al finalizar la tarea, el agente `code-reviewer` verifica que ningún non-goal fue violado en el diff total.

---

## 3. Anatomía del Repositorio

### 3.1 Proyecto (`.claude/` — committed, compartido)

```
proyecto/
├── CLAUDE.md                  # Reglas del equipo (~200 líneas máx)
├── CLAUDE.local.md            # Overrides personales (gitignored)
└── .claude/
    ├── settings.json          # Permisos y config
    ├── settings.local.json    # Permisos personales (gitignored)
    ├── rules/                 # Reglas modulares por tema
    ├── commands/              # Slash commands → /project:nombre
    ├── skills/                # Workflows auto-invocados
    ├── agents/                # Sub-agentes especializados
    └── hooks/                 # Hooks programáticos (enforcement)
```

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

> **[FIX Token waste #2]** Las primeras 200 líneas de MEMORY.md siguen esta estructura fija:

```markdown
# MEMORY.md — Estructura obligatoria

## CRITICAL (líneas 1-50) — Nunca desplazado
<!-- Decisiones de arquitectura vigentes, reglas de negocio activas, gotchas confirmados -->

## ACTIVE (líneas 51-150) — Lecciones activas ordenadas por last_referenced desc
<!-- Lessons con status:active, más recientes primero -->

## RECENT (líneas 151-200) — Buffer de sesión
<!-- Notas de la última sesión, pendientes de clasificar -->

## OVERFLOW (línea 201+) — Solo accesible on-demand
<!-- Todo lo demás, cargado solo cuando Claude lo necesita explícitamente -->
```

- Entradas que se confirman como permanentes → promueven de ACTIVE a CRITICAL.
- Entradas no referenciadas en 30+ días → bajan a OVERFLOW o se archivan.

---

## 4. Flujo de Trabajo Diario

### 4.1 Ritual de Mañana (10 minutos)

* **Tú:** Abres la rama, revisas CLAUDE.md.
* **Claude:** Ejecuta la state machine: EXPLORE → PLAN → (espera aprobación o auto-valida) → EXECUTE → VERIFY.
  - Commitment checkpoint obligatorio (ver §2.4).
  - Non-goals explícitos y persistidos como glob patterns (ver §2.5).
  - **Si algo se tuerce → PARAR → estado RE-PLAN** (no parchear hacia adelante). Máximo 2 re-planes antes de escalar a humano.
* **Tú:** Decides sesión simple o worktrees paralelos.

### 4.2 Durante el Día

* **Hilo principal limpio.** No mezclar debates con ejecución.
* **Consultas rápidas:** `/btw` o `Ctrl+;` (side chat transient).
* **Exploración de alternativas:** `/fork` para bifurcar sin contaminar.
* **Corrección:** `/rewind` (doble Esc) para borrar contexto fallido.
* **Regla de los 2 intentos:** 2 correcciones fallidas → `/clear` + reescribir incorporando lo aprendido.
* **Investigaciones acotadas:** Nunca "investiga X" sin scope. Acotar o delegar a subagentes.
* **Refactorización:** `/simplify` para invocar agentes de revisión.
* **Tareas masivas:** `/batch` para dividir en worktrees independientes.

### 4.3 Ritual de Fin de Día

* **Claude:** Limpieza de cabos sueltos + actualización de lessons (schema §1.8).
* **Tú:** Actualizas CLAUDE.md o `/memory` con reglas nuevas.
* **Claude:** Ejecuta detección de contradicciones (§1.8) sobre todas las entries del día.
* **Tú:** Cierras bucles, matas sesiones ruidosas, dejas handoff claro.

---

## 5. Rules — Reglas Modulares con Scoping

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

## 6. Slash Commands

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

## 7. Skills vs Commands

| Aspecto | Commands | Skills |
|---------|----------|--------|
| Activación | Solo manual (`/nombre`) | Automática por contexto O manual |
| Estructura | Un solo archivo `.md` | Carpeta con `SKILL.md` + archivos companion |
| Referencia a otros archivos | No | Sí, con `@ARCHIVO.md` |
| Ubicación | `.claude/commands/` | `.claude/skills/nombre/SKILL.md` |

**Unificación:** Un skill y un command con el mismo nombre generan el mismo slash command.

### 7.1 Skills auto-activados con guardrails

> **[FIX MEDIO-6]** Los skills auto-activados tienen threshold de confianza, log obligatorio y confirmación para skills de alto impacto.

**Skills se auto-activan** cuando Claude detecta coincidencia con la `description` del frontmatter YAML. Para prevenir falsos positivos:

**Log obligatorio de activación:**
```yaml
# Cada auto-activación se registra en .claude/memory/skill-activations.log
- timestamp: "2026-04-17T10:30:00Z"
  skill: "security-review"
  trigger_text: "fragmento que disparó la activación"
  confidence: high | medium | low
  confirmed: true | false     # si el usuario confirmó
  false_positive: false        # marcado post-hoc si fue innecesario
```

**Niveles de activación por impacto:**

| Impacto del skill | Threshold | Comportamiento |
|---|---|---|
| **Bajo** (formatting, linting) | Cualquier match | Auto-activa silenciosamente |
| **Medio** (code-review, testing) | Medium+ confidence | Auto-activa + notifica al usuario |
| **Alto** (security, deploy, delete) | High confidence + confirmación | Propone activación, espera confirmación explícita |

El impacto se declara en el frontmatter del skill:
```yaml
---
description: Security review exhaustivo
impact: high
---
```

---

## 8. Agents — Sub-agentes Especializados

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

## 9. Permisos — settings.json

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

## 10. Hooks — Acciones Automáticas Sin Excepción

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
| `tdd-gate` | PreToolUse(Write/Edit) | Escribir implementación sin tests previos | Bloquea + mensaje: "Tests primero. Escribir tests que fallen antes de implementar." |
| `commit-checklist` | PreToolUse(Bash:git commit) | Intento de commit | Ejecuta checklist: tests existen, tests pasan, diff planificado. Bloquea si falla. |
| `non-goal-guard` | PostToolUse(Write/Edit) | Archivo escrito coincide con non_goal glob | Bloquea + rollback del archivo + log. |
| `plan-drift-detector` | PostToolUse(Write/Edit) | Archivo modificado no está en files_affected | Warning + log. Si coincide con non_goal → bloqueo. |
| `auto-format` | PostToolUse(Write/Edit) | Cualquier escritura | Ejecuta formatter del proyecto. |
| `session-consolidate` | Stop | Cierre de sesión | Promueve conocimiento elegible al wiki + archiva lessons expiradas. |

---

## 11. Circuit Breakers para Operación Autónoma

> **[FIX ALTO-4]** Todo proceso autónomo tiene límites duros no negociables.

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

## 12. Rollback Strategy

> **[FIX ALTO-5]** Cada operación autónoma es reversible por diseño.

### 12.1 Protocolo de snapshots

1. **Antes de ejecutar:** `git tag pre-<plan_id>` — snapshot del estado limpio
2. **Durante ejecución:** Commits atómicos por unidad de trabajo, cada uno con referencia al plan:
   ```
   feat: implement auth service [plan-2026-04-17-001]
   ```
3. **Después de cada commit:** Ejecutar test suite completa
   - Tests pasan → continuar
   - Tests fallan → `git revert HEAD` + intentar fix (máximo 2 intentos)
   - 2 fixes fallidos → `git reset --hard pre-<plan_id>` + escalar a humano

### 12.2 Branching para trabajo autónomo

- Routines y loops autónomos SIEMPRE trabajan en branch `claude/<plan_id>`
- NUNCA push directo a main
- Al completar → crear PR para revisión humana
- PR incluye: resumen de cambios, tests añadidos, logs de ejecución

---

## 13. Routines — Ejecución Autónoma en la Nube

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

---

## 14. Wiki de Proyecto — Memoria Permanente con Indexación

> **[FIX Token waste #3 + CRÍTICO-A]** El wiki tiene índice estructurado y criterios de promoción objetivos.

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

> **[FIX Token waste #3]** Claude consulta el índice antes de leer archivos completos. El índice es un lookup ligero (~50-100 líneas) que evita leer todo el wiki para encontrar información.

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

### 14.4 Criterios de promoción objetivos (memory → wiki)

> **[FIX CRÍTICO-A]** La promoción NO depende de juicio subjetivo de Claude.

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

## 15. Estructura de Prompts Efectivos

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

## 16. Principios Core de Ingeniería

- **Simplicity First:** Cada cambio, lo más simple posible. Mínimo código.
- **No Laziness:** Causa raíz. Nunca fixes temporales. Estándar senior.
- **Minimal Impact:** Solo tocar lo necesario. No introducir bugs colaterales.
- **Kill Process, Don't Optimize It:** Proceso sin valor = latencia pura. Eliminar, no optimizar.

---

## 17. Orden de Setup Progresivo

1. **`/init`** → CLAUDE.md starter. Recortar a ~20 líneas esenciales.
2. **`settings.json`** → Permisos básicos: allow test/build, deny .env y destructivos.
3. **1-2 commands** → Workflows más repetidos.
4. **`rules/`** → Cuando CLAUDE.md supere ~50 líneas, fragmentar con path scoping.
5. **`~/.claude/CLAUDE.md`** → Preferencias personales globales.
6. **Hooks de enforcement** → Instalar hooks de §10.1 para gates obligatorios.
7. **Skills y Agents** → Cuando un workflow complejo se repita. No antes.
8. **Circuit breakers** → Configurar antes de habilitar cualquier loop/routine.

> **Regla del 95%:** Los pasos 1-6 cubren el 95% de las necesidades.
