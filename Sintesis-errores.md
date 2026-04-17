# Auditoría de Sintesis.md

---

## Pasada 1

**Fecha:** 2026-04-17
**Auditor:** Arquitecto Zero-Trust
**Scope:** Viabilidad como documento normativo para operación autónoma de Claude Code

---

## 1. Veredicto de Viabilidad

Sintesis.md es un manifiesto filosófico sólido pero NO un contrato ejecutable. Describe el "qué" y el "por qué" con precisión, pero carece de los mecanismos de enforcement que convierten directivas en comportamiento determinista. En producción autónoma, un agente que opera sobre directivas suaves produce agentes que *intentan* seguir las reglas, no agentes que *no pueden* violarlas.

---

## 2. Vulnerabilidades Lógicas y Estructurales

### CRÍTICO-1: Ausencia de máquina de estados para operación autónoma

El flujo `explorar → planificar → ejecutar` es una directiva textual, no un autómata. No hay estados válidos, transiciones, condiciones de entrada/salida, ni estado de error.

**Consecuencia:** Claude puede saltar de "explorar" a "ejecutar" sin planificar. La directiva "si algo se tuerce, PARAR" compite con el sesgo de "parchear hacia adelante" reconocido en el propio documento.

**Solución:** State machine con gates obligatorios implementados como hooks PreToolUse:
```
EXPLORE → [gate: plan_exists?] → PLAN → [gate: plan_approved?] → EXECUTE → [gate: tests_pass?] → VERIFY → DONE
         ↓ (fail)                      ↓ (fail)                          ↓ (fail)
       BLOCKED                     RE-PLAN (max 2)                   ROLLBACK → RE-PLAN
```

---

### CRÍTICO-2: Commitment Checkpoint inoperante en modo autónomo

El documento exige aprobación del usuario para desviarse del plan. En routines y loops autónomos, NO hay usuario. El checkpoint es un NOP en el escenario que más lo necesita.

**Solución:** Commitment como artefacto persistente (PLAN.md). Hook PostToolUse compara archivos modificados vs. declarados en el plan. Diff no planificado → bloquear + registrar desviación.

---

### CRÍTICO-3: Dependencia circular en auto-validación

El mismo modelo genera código Y tests. Tiende a testear la implementación, no la especificación. El documento reconoce esto para pipelines multi-agente pero NO para sesión individual.

**Solución:**
- TDD estricto enforced: tests ANTES del código
- Si tests se crean DESPUÉS: hook fuerza revisión por agente independiente (modelo diferente o prompt adversarial)

---

### ALTO-4: Sin circuit breaker para loops autónomos

No se define: máximo de iteraciones, qué hacer si no converge, escalación a humano, presupuesto máximo de tokens/costes.

**Consecuencia:** Loop que falla puede consumir tokens indefinidamente o generar commits basura.

**Solución:** Todo loop declara: `max_iterations`, `timeout`, `cost_ceiling`, fallback (`abort + notify` o `create_issue + stop`).

---

### ALTO-5: Rollback strategy ausente

Nunca define cómo revertir un cambio autónomo incorrecto. Sin commits atómicos, tags pre-ejecución, ni branching strategy para trabajo autónomo.

**Solución:** Cada operación autónoma:
1. Crear snapshot (tag git) antes de empezar
2. Commits atómicos por unidad de trabajo
3. Tests tras cada commit — si falla, revert automático al snapshot

---

### MEDIO-6: Skills auto-activados sin threshold

Matching semántico = falsos positivos. Mencionar "security" en contexto de negocio podría activar el skill de seguridad. Sin confidence threshold, confirmación, ni log de activaciones.

**Solución:** Log estructurado: `{skill, trigger_text, confidence, timestamp}`. Skills de alto impacto requieren confirmación o threshold mínimo.

---

### MEDIO-7: Non-goals declarativos sin enforcement

Claude puede declarar non-goals y luego construir exactamente eso. Sin comparación non-goals vs diff final.

**Solución:** Non-goals como patrones glob en plan. Hook PostToolUse detecta writes a paths coincidentes → warning/bloqueo.

---

## 3. Optimización de Tokens y Prevención de Alucinaciones

### Token waste

1. **Sintesis.md consume ~4K tokens** como prosa narrativa. Necesita versión operativa compacta (bullets) + versión referencial (esta).
2. **Sin priorización de MEMORY.md**: 200 líneas cargadas sin política de qué va primero. Entradas recientes (triviales) desplazan a las importantes.
3. **Wiki sin indexación**: crece indefinidamente, Claude lee archivos completos para buscar info.

### Guardrails de alucinación ausentes

1. **Sin validación de datos factuales**: no obliga a verificar existencia de archivos/funciones antes de afirmar. Regla: antes de afirmar → `grep`/`read_file`. Nunca de memoria.

2. **Tabla de racionalización es reactiva**: depende de auto-reconocimiento de sesgos. Equivalente a pedir al sospechoso que se interrogue.
   - **Solución:** Convertir en hook PreToolUse sobre commit/task_complete: checklist programático (¿tests? ¿tests fallan sin implementación? ¿diff no planificado?).

3. **Sin structured output para artefactos**: plans, lessons, memory en free-form Markdown. Impide validación automática y búsqueda eficiente.
   - **Solución:** Schemas YAML mínimos para lessons, plans, memory entries.

---

## 4. Arquitectura de Memoria y Aprendizaje Autónomo

### CRÍTICO-A: Criterios de promoción subjetivos

"Decisiones de arquitectura confirmadas" — ¿quién confirma? Sin señal explícita, Claude adivina.

**Solución:** Promoción requiere:
- Señal explícita: `/promote <entry>`
- Señal implícita: entry sobrevive 3+ sesiones sin contradicción
- Señal de consenso: 2+ agentes referencian la misma decisión

---

### CRÍTICO-B: Sin detección de contradicciones en memoria

Lecciones contradictorias coexisten sin conflicto. Sesión 1: "usar JWT". Sesión 5: "usar session cookies". Ambas activas.

**Solución:** Al escribir entry, buscar existentes con keywords solapantes. Contradicción detectada → marcar anterior como `superseded_by: <new>` + registrar en log.

---

### ALTO-C: Sin TTL ni garbage collection

Entries nunca expiran. Tras 50 sesiones: workarounds para bugs corregidos, lecciones sobre APIs deprecated, decisiones revertidas — todo activo.

**Solución:** Campo `last_referenced: date`. Proceso periódico (routine semanal) marca entries no referenciadas en 30+ días para revisión/archivado.

---

### ALTO-D: Feedback loop incompleto

No define: cómo detectar corrección (vs. cambio de opinión), cómo verificar que la regla funciona, cuándo promover lección a regla permanente.

**Solución:**
- Corrección = usuario revierte cambio O dice "eso está mal"
- Regla validada retrospectivamente: 5 sesiones sin repetición → promover. Si se repite → insuficiente, escalar a hook
- Lecciones no promovidas en 10 sesiones → archivar

---

## Resumen de severidades

| ID | Severidad | Descripción |
|---|---|---|
| CRÍTICO-1 | 🔴 | Sin state machine — flujo autónomo no-determinista |
| CRÍTICO-2 | 🔴 | Commitment checkpoint inoperante en modo autónomo |
| CRÍTICO-3 | 🔴 | Auto-validación circular (mismo modelo genera y testea) |
| CRÍTICO-A | 🔴 | Promoción de memoria sin criterios objetivos |
| CRÍTICO-B | 🔴 | Sin detección de contradicciones en memoria |
| ALTO-4 | 🟠 | Sin circuit breaker para loops |
| ALTO-5 | 🟠 | Sin estrategia de rollback |
| ALTO-C | 🟠 | Sin TTL ni garbage collection de memoria |
| ALTO-D | 🟠 | Feedback loop incompleto |
| MEDIO-6 | 🟡 | Skills auto-activados sin threshold |
| MEDIO-7 | 🟡 | Non-goals declarativos sin enforcement |

---

## Conclusión de Pasada 1

**5 vulnerabilidades CRÍTICAS, 4 ALTAS, 2 MEDIAS.**

El documento establece principios correctos pero falla en enforcement. Para producción autónoma necesita:
1. Convertir directivas textuales en hooks/gates programáticos
2. Schemas estructurados para artefactos de memoria
3. Circuit breakers con límites duros
4. Detección de contradicciones y TTL en memoria
5. Validación cruzada por agentes independientes (no auto-validación)

---
---

## Pasada 2

**Fecha:** 2026-04-17
**Auditor:** Arquitecto Zero-Trust
**Scope:** Auditoría post-corrección — viabilidad de los mecanismos de enforcement introducidos en Pasada 1

---

### 1. Veredicto de Viabilidad

Las correcciones de Pasada 1 cerraron las vulnerabilidades conceptuales pero introdujeron problemas de implementación. Los hooks son el pilar de enforcement y tienen 3 fallos de viabilidad técnica que convierten el sistema en un castillo de naipes si un solo hook falla silenciosamente. La economía de tokens del propio sistema de metadatos (lessons, plans, logs, indexes) consume más contexto del que ahorra.

---

### 2. Vulnerabilidades Lógicas y Estructurales

#### CRÍTICO-P2-1: Paradoja del plan-gate hook — Claude no puede escribir el plan

El hook `plan-gate` (§10.1) bloquea `Write/Edit` si no existe `PLAN.md`. Pero Claude necesita usar `Write` para CREAR `PLAN.md`. El hook se bloquea a sí mismo. El documento no define una excepción para la escritura del propio plan.

**Solución:** Whitelist de archivos de metadatos en el hook. El `plan-gate` debe excluir rutas que coincidan con `**/PLAN.md`, `**/RESEARCH.md`, archivos en `.claude/memory/`, y artefactos de exploración. Solo bloquea escritura de archivos de código fuente.

---

#### CRÍTICO-P2-2: Los hooks son scripts shell — no pueden implementar la lógica descrita

Los hooks de Claude Code son scripts shell con acceso limitado a stdin (JSON del evento). §1.6 describe lógica como "verificar que existan tests para el módulo" y "el diff solo incluye archivos declarados en el plan". Esto requiere:
- Parsear PLAN.md (YAML embebido en Markdown)
- Determinar qué archivo es "test" vs "implementación" (heurística por proyecto)
- Correlacionar el archivo escrito con `files_affected`
- Evaluar patrones glob de `non_goals`

Ninguna de estas operaciones es trivial en bash.

**Solución:** Especificar un hook runner en Python/Node con dependencias mínimas (solo stdlib). Cada hook es un script autocontenido que recibe JSON por stdin, devuelve `{"decision": "allow"|"block", "reason": "..."}` por stdout. Incluir spec de implementación completa (§10.2 nuevo).

---

#### CRÍTICO-P2-3: Sin health check del sistema de hooks

Si un hook falla silenciosamente (error de sintaxis, dependencia faltante, timeout), TODOS los gates se desactivan. El documento no define:
- Verificación de hooks al inicio de sesión
- Fallback si un hook no responde
- Log de ejecución de hooks

Equivalente: un sistema de seguridad donde si la alarma se desconecta, las puertas quedan abiertas.

**Solución:** Hook `session-start` que ejecuta dry-run de cada hook con fixture de test. Hook que falla dry-run → sesión arranca en modo degradado con warning persistente. Fallback: hook sin respuesta en 5s → bloquear por defecto (fail-closed, no fail-open).

---

#### ALTO-P2-4: Estado BLOCKED sin salida definida

La state machine (§2.1) muestra `EXPLORE → fail → BLOCKED`. No define:
- Cómo sale Claude de BLOCKED
- Si requiere intervención humana
- Si genera issue/notificación
- Si hay timeout en BLOCKED

Un agente autónomo que entra en BLOCKED queda en deadlock permanente.

**Solución:** BLOCKED tiene timeout (`blocked_timeout_minutes: 15`). Al expirar → crear GitHub issue con contexto + label `agent-blocked` + STOP. En sesión interactiva → notificar al usuario con diagnóstico.

---

#### ALTO-P2-5: Rollback no distingue severidad de error

§12.1 define: "Tests fallan → git revert HEAD". No diferencia entre:
- Error de sintaxis (fix trivial)
- Error de diseño (requiere re-plan)
- Error de dependencia (requiere exploración)
- Falso negativo del test (el test es incorrecto)

**Solución:** Clasificación de errores antes de rollback:

| Tipo de error | Señal | Acción |
|---|---|---|
| Sintaxis/import | Error en compilación/lint | Fix inline (max 2 intentos) → rollback si persiste |
| Test falla por implementación | Test existía antes del cambio | Rollback + fix implementación |
| Test falla por test incorrecto | Test creado en este commit | Revisar test primero, no rollback |
| Error de diseño | Múltiples tests fallan tras cambio | Rollback + RE-PLAN |
| Dependencia externa | Error de red/API/paquete | Retry con backoff (max 3) → BLOCKED |

---

#### ALTO-P2-6: Backward propagation sin audit trail del plan

§1.8 dice "proponer actualización del plan ANTES de continuar". No hay:
- Versionado del plan
- Registro de POR QUÉ cambió
- Validación del plan actualizado

**Solución:** Al mutar PLAN.md:
1. Copiar versión actual a `PLAN.v{N}.md`
2. Añadir sección `## Change log` al plan con: `{timestamp, field_changed, old_value, new_value, reason}`
3. Plan mutado pasa por GATE-2 nuevamente (re-validación de coherencia)

---

### 3. Optimización de Tokens y Prevención de Alucinaciones

#### CRÍTICO-P2-8: Validación factual es regla, no hook

§1.6 dice "Claude MUST ejecutar grep/read_file para verificar" antes de afirmar que un archivo existe. Pero esto es una instrucción textual en CLAUDE.md, NO un hook programático. No hay mecanismo para detectar que Claude afirmó la existencia de algo sin verificar.

**Solución:** Esta es una limitación fundamental — no se puede hookear el "pensamiento" de Claude, solo sus acciones de herramientas. Mitigar con:
1. Rule en CLAUDE.md con authority language máxima (MUST, non-negotiable)
2. Hook PostToolUse sobre `Write/Edit`: si el código referencia un import/archivo, verificar que ese archivo existe con `find`. Warning si no existe.
3. Agente `code-reviewer` como segunda barrera con prompt: "Verifica que cada archivo referenciado en el diff existe realmente"

---

#### ALTO-P2-9: TDD gate no previene tests vacíos

El `tdd-gate` verifica que existan tests ANTES de implementación. Pero no verifica que los tests:
- Realmente testeen comportamiento (no `expect(true).toBe(true)`)
- Fallen antes de la implementación
- Cubran los criterios de aceptación del plan

**Solución:** Añadir al hook `commit-checklist`:
1. Contar assertions en archivos de test modificados. Mínimo: 1 assertion por test function
2. Verificar que los test names correlacionen con `acceptance_criteria` del plan (heurística por keywords)
3. Aceptar limitación: validar calidad del test al 100% es imposible en hook. El `code-reviewer` agente cubre el gap restante.

---

#### ALTO-P2-11: El metasistema consume más tokens de los que ahorra

Overhead estimado por sesión: ~850 tokens de metadatos antes de leer código del proyecto. Esto es > 4x el presupuesto de CLAUDE.md (~200 líneas).

**Solución:** Carga lazy de metadatos:
- **Siempre cargado:** CLAUDE.md (200 líneas) + MEMORY.md CRITICAL section (50 líneas) = ~250 líneas
- **On-demand:** Lessons (solo las referenciadas), skill activation log (nunca auto-cargado), _index.yaml (solo cuando Claude necesita buscar en wiki)
- **En PLAN.md:** Solo campos activos. Omitir `circuit_breaker` si usa defaults del proyecto. Template con defaults implícitos:

```yaml
# PLAN.md — solo campos obligatorios (los demás usan defaults de settings.json)
plan_id: plan-YYYY-MM-DD-NNN
approach: "..."
files_affected: [...]
acceptance_criteria: [...]
# circuit_breaker, rollback_tag, etc. → defaults si no se declaran
```

---

#### MEDIO-P2-10: Sin guardrail contra fabricación de resultados

Claude puede decir "todos los tests pasan" sin ejecutarlos. El hook solo verifica en commit.

**Solución:** Aceptar como riesgo mitigado — el `commit-checklist` hook es la barrera real. Añadir regla en CLAUDE.md: "Ejecutar tests con `Bash` tool — nunca reportar resultado sin output de terminal visible".

---

#### MEDIO-P2-12 + P2-13: Logs y índices sin límite

Skill activation log y _index.yaml crecen indefinidamente.

**Solución:** Políticas de rotación:
- `skill-activations.log`: Rotar semanalmente. Mantener última semana. Archivar en `skill-activations.{date}.log`.
- `_index.yaml`: Máximo 200 entries. Al superar → `session-consolidate` archiva las 50 entries con `last_updated` más antiguo a `_index.archive.yaml`.

---

### 4. Arquitectura de Memoria y Aprendizaje Autónomo

#### ALTO-P2-14: Detección de contradicciones por keywords demasiado cruda

Keywords solapantes generan falsos positivos. "JWT para API" y "session cookies para web" comparten keyword "auth" pero no son contradictorias.

**Solución:** Añadir campo `scope` obligatorio a lessons:

```yaml
id: lesson-2026-04-17-001
scope: "api-auth"           # Namespace explícito
trigger: "..."
pattern: "..."
fix: "..."
```

Contradicción = mismo `scope` + keywords solapantes. Scopes diferentes → no contradicción aunque compartan keywords.

---

#### ALTO-P2-15: `last_referenced` sin enforcement

No hay mecanismo que fuerce la actualización de `last_referenced`.

**Solución:** Hook `session-consolidate` (ya existe) actualiza `last_referenced` de TODAS las entries que aparecen en el contexto de la sesión. No depende de que Claude recuerde — es automático al cierre. Implementación: el hook escanea el historial de herramientas de la sesión buscando lecturas de archivos de lessons.

---

#### MEDIO-P2-16: Routines no participan en promoción

Routines cloud son single-shot, sin memoria entre ejecuciones.

**Solución:** Las routines escriben un artefacto `routine-output.md` al branch `claude/`. El hook `session-consolidate` de la siguiente sesión interactiva procesa estos artefactos y los integra al sistema de lessons/wiki.

---

#### MEDIO-P2-17: session-consolidate doble responsabilidad

Promover y archivar en la misma ejecución puede causar race conditions.

**Solución:** Orden determinista:
1. Primero: archivar entries con `last_referenced > 30 días`
2. Segundo: promover entries elegibles (solo entries que sobrevivieron el paso 1)
3. Tercero: actualizar `_index.yaml`

---

### 5. Viabilidad de Implementación

#### CRÍTICO-P2-18: Sin especificación de implementación de hooks

7 hooks obligatorios sin spec técnica.

**Solución:** Nuevo §10.2 con spec completa. Cada hook define:
- Lenguaje: Python 3.10+ (stdlib only, sin dependencias externas)
- Input: JSON por stdin con schema documentado
- Output: JSON por stdout `{"decision": "allow"|"block", "reason": "..."}`
- Exit code: 0 = allow, 1 = block, 2 = error (fail-closed)
- Timeout: 10s max por hook
- Dependencias: `python3`, `git`, `find` (presentes en cualquier dev environment)

---

#### ALTO-P2-19: Mezcla normativo/descriptivo

El implementador no distingue "esto ya existe" de "esto hay que construirlo".

**Solución:** Markers en cada sección:
- `[BUILT-IN]` — Funcionalidad nativa de Claude Code. Solo configurar.
- `[TO BUILD]` — Requiere implementación. Incluye spec o pseudocódigo.
- `[CONVENTION]` — Acuerdo de equipo. No requiere código, solo disciplina.

---

#### MEDIO-P2-7: "Unidad de trabajo" no definida

**Solución:** Definir: una unidad de trabajo = un criterio de aceptación del plan. Cada `acceptance_criteria` entry en PLAN.md → un commit atómico. Esto alinea granularidad de commits con verificabilidad.

---

#### MEDIO-P2-20: Sin taxonomía de errores para RE-PLAN

**Solución:** Clasificar antes de re-planificar:

| Error | Acción | Cuenta como RE-PLAN |
|---|---|---|
| Bug de implementación (1-3 archivos) | Fix inline | NO |
| Test incorrecto | Corregir test | NO |
| Diseño inadecuado (múltiples criterios fallan) | RE-PLAN | SÍ |
| Scope insuficiente (faltan archivos/módulos) | Actualizar plan + continuar | NO |
| Conflicto con non-goals | STOP + escalar | N/A |

---

### Resumen de severidades — Pasada 2

| ID | Severidad | Descripción | Estado |
|---|---|---|---|
| CRÍTICO-P2-1 | 🔴 | plan-gate bloquea la creación del propio plan | Solución propuesta |
| CRÍTICO-P2-2 | 🔴 | Hooks shell no pueden implementar la lógica descrita | Solución propuesta |
| CRÍTICO-P2-3 | 🔴 | Sin health check — hooks fallidos = gates desactivados | Solución propuesta |
| CRÍTICO-P2-8 | 🔴 | Validación factual sin enforcement programático | Mitigación (limitación fundamental) |
| CRÍTICO-P2-18 | 🔴 | Sin spec de implementación de hooks | Solución propuesta |
| ALTO-P2-4 | 🟠 | Estado BLOCKED sin salida definida | Solución propuesta |
| ALTO-P2-5 | 🟠 | Rollback no distingue severidad de error | Solución propuesta |
| ALTO-P2-6 | 🟠 | Plan mutable sin audit trail | Solución propuesta |
| ALTO-P2-9 | 🟠 | TDD gate no previene tests vacíos | Solución propuesta |
| ALTO-P2-11 | 🟠 | Metasistema consume > tokens de los que ahorra | Solución propuesta |
| ALTO-P2-14 | 🟠 | Detección de contradicciones por keyword genera FP | Solución propuesta |
| ALTO-P2-15 | 🟠 | `last_referenced` sin enforcement | Solución propuesta |
| ALTO-P2-19 | 🟠 | Mezcla normativo/descriptivo confunde implementador | Solución propuesta |
| MEDIO-P2-7 | 🟡 | "Unidad de trabajo" no definida | Solución propuesta |
| MEDIO-P2-10 | 🟡 | Sin guardrail contra fabricación de resultados | Riesgo aceptado + mitigación |
| MEDIO-P2-12 | 🟡 | Skill log sin rotación | Solución propuesta |
| MEDIO-P2-13 | 🟡 | _index.yaml sin límite | Solución propuesta |
| MEDIO-P2-16 | 🟡 | Routines no participan en promoción | Solución propuesta |
| MEDIO-P2-17 | 🟡 | session-consolidate doble responsabilidad | Solución propuesta |
| MEDIO-P2-20 | 🟡 | Sin taxonomía de errores para RE-PLAN | Solución propuesta |

---

### Conclusión de Pasada 2

**5 CRÍTICAS, 8 ALTAS, 7 MEDIAS.**

Las correcciones de Pasada 1 resolvieron los problemas conceptuales pero revelaron un meta-problema: **el sistema de enforcement (hooks) es el nuevo punto único de fallo**. Si los hooks no pueden implementarse técnicamente (P2-2, P2-18), fallan silenciosamente (P2-3), o se auto-bloquean (P2-1), toda la arquitectura colapsa al estado pre-Pasada 1.

**Prioridad de corrección para Sintesis.md:**
1. Resolver la paradoja plan-gate (P2-1) — sin esto el sistema no arranca
2. Especificar implementación técnica de hooks (P2-2 + P2-18) — sin esto no se puede construir
3. Añadir health check de hooks (P2-3) — sin esto no hay confianza en el enforcement
4. Separar normativo de descriptivo (P2-19) — sin esto el implementador no sabe qué construir
5. Corregir economía de tokens (P2-11) — sin esto el overhead del sistema anula sus beneficios

---
---

## Pasada 3

**Fecha:** 2026-04-17
**Auditor:** Arquitecto Zero-Trust (fresh — análisis desde cero sobre documento actual)
**Scope:** Viabilidad real de implementar Sintesis.md tal como está escrito hoy (~970 líneas, 17 secciones)

---

### 1. Veredicto de Viabilidad

El documento ha evolucionado de manifiesto filosófico a especificación técnica. Los mecanismos de enforcement están definidos con specs concretas (Python hooks, JSON contracts, YAML schemas). Sin embargo, esta pasada identifica problemas de **viabilidad operativa**: el sistema diseñado es internamente coherente pero choca con la realidad de cómo Claude Code funciona y cómo los desarrolladores trabajan.

**Problema central:** El documento asume sesiones mono-tarea lineales (una tarea → un plan → ejecución → done). La realidad es sesiones multi-tarea con contexto cambiante, tareas triviales intercaladas con complejas, y trabajo no planificable. El sistema tal como está penalizaría el 70% del uso real de Claude Code para proteger el 30% que realmente lo necesita.

---

### 2. Vulnerabilidades de Viabilidad Operativa

#### CRÍTICO-P3-1: La state machine asume sesiones mono-tarea — la realidad es multi-tarea

§2.1 define un flujo lineal: `EXPLORE → PLAN → EXECUTE → VERIFY → DONE`. Pero una sesión real incluye:
- "Arregla este typo en auth.ts" (trivial, no necesita plan)
- "Refactoriza el módulo de pagos" (complejo, necesita plan)
- "¿Qué hace esta función?" (consulta, no es tarea)
- "Añade un campo al formulario" (medio, quizás necesita plan)

El documento no distingue entre tareas que requieren el flujo completo y las que no. Con el sistema actual, corregir un typo requeriría: crear PLAN.md → pasar GATE-2 → escribir el fix → pasar GATE-3 → commit. Esto convierte 10 segundos de trabajo en 2 minutos de ceremonia.

**Consecuencia:** Los desarrolladores desactivarán los hooks por fricción excesiva, eliminando TODO el enforcement.

**Solución:**
1. Definir **umbral de plan obligatorio** basado en heurística:
   - Cambio ≤ 3 archivos Y ≤ 50 líneas → `FAST_PATH` (sin plan, solo commit-checklist)
   - Cambio > 3 archivos O > 50 líneas O nuevo módulo → `FULL_PATH` (state machine completa)
2. El `plan-gate` hook implementa esta heurística: si no existe PLAN.md, verifica si el cambio es trivial. Si lo es → allow con log `{mode: "fast_path"}`. Si no → block.
3. Añadir estado `FAST_PATH` al diagrama de la state machine como bypass para tareas triviales.

---

#### CRÍTICO-P3-2: No existe almacenamiento del estado de la state machine

§2.1 define estados (EXPLORE, PLAN, EXECUTE, etc.) pero NUNCA especifica dónde se persiste el estado actual. Los hooks necesitan saber "¿en qué estado estamos?" para tomar decisiones, pero:
- No hay archivo `.claude/state.json` definido
- No hay mecanismo para transicionar entre estados
- Los hooks individuales infieren el estado implícitamente (ej: `plan-gate` asume "si no hay PLAN.md → estamos antes de PLAN"), pero esto es frágil

**Consecuencia:** Sin estado persistido, los hooks no pueden coordinarse. El `plan-gate` no sabe si estamos en EXPLORE (legítimo no tener plan) o en EXECUTE (error no tener plan).

**Solución:**
```yaml
# .claude/state.yaml — actualizado automáticamente por hooks
current_task:
  state: EXECUTE          # EXPLORE | PLAN | EXECUTE | VERIFY | DONE | BLOCKED | FAST_PATH
  plan_id: plan-2026-04-17-001
  entered_at: "2026-04-17T10:30:00Z"
  previous_state: PLAN
  fast_path: false
history:
  - {state: EXPLORE, entered: "...", exited: "..."}
  - {state: PLAN, entered: "...", exited: "..."}
```
Cada hook lee y actualiza este archivo. Las transiciones son atómicas (file lock o rename).

---

#### CRÍTICO-P3-3: `tdd-gate` es inviable como hook genérico

§10.1 define un hook que "verifica que existan tests para el módulo ANTES de permitir escribir código." Problemas:

1. **¿Cómo mapea módulo → test?** La convención varía por proyecto:
   - Jest: `src/auth.ts` → `src/__tests__/auth.test.ts` O `src/auth.test.ts`
   - Pytest: `app/services/auth.py` → `tests/test_auth.py` O `tests/services/test_auth.py`
   - Go: `auth.go` → `auth_test.go` (mismo directorio)
   - El hook necesitaría configuración por proyecto, no especificada

2. **Módulos nuevos no tienen tests previos.** Escribir `src/services/new-feature.ts` por primera vez → el hook bloquea porque no existe `new-feature.test.ts`. Pero es imposible escribir el test sin saber la API del módulo. El TDD puro dice "escribe el test primero", pero el test importa del módulo que aún no existe → error de import.

3. **No todo archivo es "implementación".** Configs, types, constants, migrations, fixtures, assets — ninguno requiere test previo. El hook necesita otra whitelist.

**Consecuencia:** El hook bloqueará trabajo legítimo constantemente, generando desactivación por frustración.

**Solución:**
1. Hacer `tdd-gate` **configurable por proyecto** en settings.json:
   ```json
   {
     "tddGate": {
       "testPattern": "tests/**/*.test.ts",
       "sourcePattern": "src/**/*.ts",
       "excludePatterns": ["**/*.d.ts", "**/types/**", "**/constants/**", "**/migrations/**"],
       "mode": "warn"  // "block" | "warn" | "off"
     }
   }
   ```
2. Modo default: `warn` (no `block`). El bloqueo es opt-in para equipos que quieren TDD estricto.
3. Para módulos nuevos: el hook permite crear archivo de test Y archivo de implementación en la misma "transacción" (no bloquea si ambos se crean en la misma sesión).

---

#### ALTO-P3-4: `session-consolidate` (Stop hook) asume acceso al historial de sesión — no lo tiene

§10.1 + FIX P2-17 describe que `session-consolidate` debe:
1. "Actualizar `last_referenced` de entries consultadas en la sesión"
2. "Escanear el historial de herramientas de la sesión buscando lecturas de archivos de lessons"

Pero un Stop hook de Claude Code recibe por stdin solo el evento de cierre, NO el historial completo de la sesión. El hook no tiene acceso a "qué archivos se leyeron durante la sesión".

**Consecuencia:** El paso 1 de session-consolidate (y el FIX P2-15 completo) no funciona como está especificado. `last_referenced` nunca se actualizaría automáticamente.

**Solución:**
- Opción A: Añadir un hook `PostToolUse(Read)` que APPENDA a un archivo `.claude/memory/session-reads.log` cada archivo leído durante la sesión. Luego `session-consolidate` lee ese log al cierre.
- Opción B: `session-consolidate` escanea los session logs de Claude Code (`~/.claude/projects/<proj>/sessions/`) directamente — pero estos logs son internos de Claude y no tienen API estable.
- **Recomendación: Opción A** — un hook PostToolUse(Read) ligero que hace append a un log temporal.

---

#### ALTO-P3-5: PLAN.md sin ubicación definida — `plan-gate.py` asume raíz del proyecto

§2.3 define el schema de PLAN.md pero nunca dice dónde vive. El ejemplo `plan-gate.py` (§10.2) hace `os.path.exists("PLAN.md")` → raíz del proyecto. Problemas:
- Proyectos reales no quieren metadata en la raíz (contamina el directorio)
- Múltiples tareas concurrentes necesitarían múltiples planes
- No hay convención para archivar planes completados

**Solución:** Definir ubicación canónica: `.claude/plans/PLAN.md` (plan activo). Planes completados → `.claude/plans/archive/plan-{id}.md`. Actualizar `plan-gate.py` para buscar en esta ruta.

---

#### ALTO-P3-6: `hook-health-check` no tiene trigger — no existe hook "SessionStart" en Claude Code

§10.3 dice "Al inicio de sesión: hook-health-check.py ejecuta dry-run de cada hook." Pero Claude Code solo tiene 3 tipos de hook: `PreToolUse`, `PostToolUse`, `Stop`. No existe `SessionStart`.

**Consecuencia:** El health check no se ejecutaría nunca automáticamente.

**Solución:**
- Opción A: Convertir en regla en CLAUDE.md: "Al iniciar sesión, ejecutar `python3 .claude/hooks/hook-health-check.py --dry-run` como primera acción." Depende de que Claude lo obedezca (regla textual).
- Opción B: Implementar como `PreToolUse` en la PRIMERA invocación de herramienta de la sesión. El hook mantiene un flag `.claude/hooks/.health-checked` con timestamp. Si el timestamp es > 1 hora → ejecutar dry-run. Si < 1 hora → skip.
- **Recomendación: Opción B** — se integra en el sistema de hooks existente y es determinista.

---

#### ALTO-P3-7: `sessions_without_repeat` nunca se incrementa

§14.4 dice "Entry sobrevive 3+ sesiones sin contradicción" como criterio de promoción implícita. El lesson schema (§1.8) tiene campo `sessions_without_repeat`. Pero NINGÚN hook ni mecanismo incrementa este contador.

Los 5 pasos de `session-consolidate` (FIX P2-17) son:
1. Actualizar `last_referenced` ← (ya tiene problemas, ver P3-4)
2. Archivar entries > 30 días
3. Promover entries elegibles
4. Actualizar `_index.yaml`
5. Rotar skill log

No hay paso que incremente `sessions_without_repeat`. El criterio de promoción implícita es letra muerta.

**Solución:** Añadir paso 1.5 a session-consolidate: "Incrementar `sessions_without_repeat` de todas las entries con `status: active` que NO fueron referenciadas en la sesión actual (no generaron error). Reset a 0 si la entry fue referenciada Y el error se repitió."

---

#### ALTO-P3-8: §4 "Flujo de Trabajo Diario" sin marker [CONVENTION]

Única sección sin marker de implementación. Rompe la promesa del sistema de markers (P2-19). Además, §4 contiene comandos como `/btw`, `/fork`, `/rewind`, `/simplify`, `/batch` que NO se definen en ningún otro lugar del documento. El lector no sabe si son built-in de Claude Code, si hay que crearlos, o si son ejemplos hipotéticos.

**Solución:** Añadir marker `[CONVENTION + BUILT-IN]` y clarificar cada comando:
- `/btw` / `Ctrl+;` → `[BUILT-IN]` (side chat)
- `/fork` → `[BUILT-IN]` (bifurcar sesión)
- `/rewind` / doble Esc → `[BUILT-IN]` (borrar contexto)
- `/clear` → `[BUILT-IN]` (limpiar sesión)
- `/simplify` → `[TO BUILD]` (command que invoca agentes de revisión)
- `/batch` → `[TO BUILD]` (command que divide en worktrees)

---

### 3. Coherencia Interna y Contradicciones

#### MEDIO-P3-9: `cost_ceiling_usd` (§11.1) es inimplementable localmente

El circuit breaker define `cost_ceiling_usd: 10.00` como límite de presupuesto. Pero:
- Claude Code no expone consumo de tokens a scripts externos
- Un hook no puede saber cuántos tokens se han consumido
- Solo la API de Anthropic tiene esta información

El campo existe en el schema pero nadie puede verificarlo.

**Solución:** Reconocer como campo advisory (no enforced por hook). Marcar como `[API-DEPENDENT]` — solo funciona si se implementa un wrapper que consulta la Anthropic API. Alternativa: usar `max_iterations` como proxy práctico del coste.

---

#### MEDIO-P3-10: Skill `confidence` (§7.1) no existe como concepto en Claude Code

El log de activación de skills registra `confidence: high|medium|low`. Pero Claude Code activa skills por matching binario contra la `description` del frontmatter. No hay score de confianza disponible. Claude tendría que auto-asignar la confianza, lo cual es una estimación subjetiva del modelo — exactamente lo que el documento critica en otros contextos.

**Solución:** Reemplazar `confidence` por `match_type: exact|partial|inferred` — más objetivo:
- `exact`: la descripción del skill coincide exactamente con la tarea
- `partial`: coincide con parte de la tarea
- `inferred`: Claude decidió que el skill aplica por razonamiento, no por match directo

---

#### MEDIO-P3-11: Branch naming conflict entre §12.2 y §13

- §12.2: "Routines trabajan en branch `claude/<plan_id>`"
- §13: "Solo push a `claude/`"

`claude/<plan_id>` crea ramas como `claude/plan-2026-04-17-001`. §13 dice "solo push a `claude/`" — ¿es eso una rama llamada `claude/` o un prefijo? Si es prefijo, `claude/<plan_id>` es válido pero la redacción es ambigua. Si es rama literal, hay conflicto.

Además, no hay política de cleanup de ramas `claude/*` tras merge.

**Solución:** Clarificar: "Solo push a ramas con prefijo `claude/`. Formato: `claude/{plan_id}`. Tras merge de PR → eliminar la rama automáticamente. Ramas `claude/*` sin actividad en 7 días → cleanup automático."

---

#### MEDIO-P3-12: ~25 anotaciones `[FIX ...]` contaminan el documento normativo

El documento tiene ~25 bloques como `> **[FIX CRÍTICO-P2-8]** ...`, `> **[FIX ALTO-P2-5]** ...`, etc. Estos son audit trail útil para auditoría pero hacen el documento un 30% más largo y dificultan su lectura como referencia normativa. Un implementador necesita saber QUÉ hacer, no la historia de POR QUÉ se decidió.

**Solución:** Dos opciones:
- **A (conservadora):** Mover los `[FIX]` a un apéndice al final del documento o a `Sintesis-changelog.md`
- **B (agresiva):** Eliminar todas las anotaciones `[FIX]` del documento, dejar solo el contenido corregido. El audit trail ya está en `Sintesis-errores.md`.
- **Recomendación: Opción B.** El audit trail está completo en este archivo. El documento normativo debe ser limpio.

---

#### MEDIO-P3-13: MEMORY.md usa posicionamiento por líneas — frágil ante ediciones

§3.2 define "CRITICAL (líneas 1-50)", "ACTIVE (líneas 51-150)", "RECENT (líneas 151-200)". Pero:
- Cualquier edición que añada/quite líneas desplaza las secciones
- Claude no cuenta líneas al escribir — usa headers de Markdown
- Los límites de línea son una ilusión de control

**Solución:** Usar headers de Markdown como delimitadores (ya están definidos: `## CRITICAL`, `## ACTIVE`, `## RECENT`, `## OVERFLOW`). Los rangos de línea son indicativos de tamaño, no posicionales. Reformular: "## CRITICAL — máximo ~50 líneas", "## ACTIVE — máximo ~100 líneas", "## RECENT — máximo ~50 líneas".

---

#### MEDIO-P3-14: §12.1 → §12.3 → §12.2 — secciones desordenadas

Las sub-secciones de §12 van en orden: 12.1, 12.3, 12.4, 12.2. Parece un error de inserción durante las correcciones de Pasada 2. El orden lógico debería ser: 12.1 (Snapshots) → 12.2 (Branching) → 12.3 (Unidad de trabajo) → 12.4 (Clasificación de errores).

**Solución:** Renumerar las sub-secciones en orden lógico.

---

### 4. Gaps Funcionales (Lo Que Falta)

#### ALTO-P3-15: Sin protocolo de recuperación tras crash/desconexión

El documento define qué pasa cuando las cosas van mal lógicamente (tests fallan, plan invalido, etc.). Pero no cubre:
- Sesión interrumpida a mitad de ejecución (crash, pérdida de conexión)
- Estado parcialmente escrito (archivo a medio escribir)
- Hooks que dejaron estado inconsistente

**Solución:** Añadir a §12:
- Al iniciar sesión: verificar si hay estado `EXECUTE` o `VERIFY` en `state.yaml` sin `DONE` → **sesión interrumpida detectada**
- Acción: mostrar al usuario el último commit + estado del plan + preguntar si continuar o rollback
- Si modo autónomo: rollback automático al último commit exitoso (tag `pre-{plan_id}`)

---

#### MEDIO-P3-16: Sin estrategia de migración para adopción gradual

§17 define "Orden de Setup Progresivo" pero en 8 pasos planos. No hay guía de migración para proyectos existentes:
- ¿Cómo adoptarlo en un repo que ya tiene CLAUDE.md?
- ¿Qué hooks instalar primero?
- ¿Cómo validar que los hooks funcionan antes de confiar en ellos?

**Solución:** Añadir sub-sección "17.1 Migración para proyectos existentes" con:
1. Instalar `hook-health-check` primero (validación sin enforcement)
2. Activar hooks en modo `warn` durante 1 semana
3. Revisar logs de warnings → ajustar whitelists/config
4. Cambiar a modo `block` progresivamente (primero commit-checklist, último plan-gate)

---

### Resumen de severidades — Pasada 3

| ID | Severidad | Descripción | Tipo |
|---|---|---|---|
| CRÍTICO-P3-1 | 🔴 | State machine mono-tarea — penaliza 70% del uso real | Diseño |
| CRÍTICO-P3-2 | 🔴 | Estado de la state machine no se persiste en ningún archivo | Implementación |
| CRÍTICO-P3-3 | 🔴 | `tdd-gate` inviable como hook genérico sin configuración por proyecto | Implementación |
| ALTO-P3-4 | 🟠 | `session-consolidate` asume acceso al historial — Stop hook no lo tiene | Implementación |
| ALTO-P3-5 | 🟠 | PLAN.md sin ubicación canónica definida | Especificación |
| ALTO-P3-6 | 🟠 | `hook-health-check` sin trigger — no existe SessionStart hook | Implementación |
| ALTO-P3-7 | 🟠 | `sessions_without_repeat` nunca se incrementa | Implementación |
| ALTO-P3-8 | 🟠 | §4 sin marker + comandos no definidos (`/simplify`, `/batch`) | Especificación |
| ALTO-P3-15 | 🟠 | Sin protocolo de recuperación tras crash/desconexión | Gap funcional |
| MEDIO-P3-9 | 🟡 | `cost_ceiling_usd` inimplementable sin acceso a API Anthropic | Implementación |
| MEDIO-P3-10 | 🟡 | Skill `confidence` no existe como concepto en Claude Code | Especificación |
| MEDIO-P3-11 | 🟡 | Branch naming ambiguo entre §12.2 y §13 | Coherencia |
| MEDIO-P3-12 | 🟡 | ~25 anotaciones `[FIX]` contaminan documento normativo | Mantenibilidad |
| MEDIO-P3-13 | 🟡 | MEMORY.md con límites posicionales por línea — frágil | Diseño |
| MEDIO-P3-14 | 🟡 | §12 sub-secciones desordenadas (12.1 → 12.3 → 12.4 → 12.2) | Estructura |
| MEDIO-P3-16 | 🟡 | Sin estrategia de migración gradual para proyectos existentes | Gap funcional |

---

### Conclusión de Pasada 3

**3 CRÍTICAS, 6 ALTAS, 7 MEDIAS.**

Las pasadas anteriores resolvieron coherencia interna pero no validaron contra la realidad operativa. Esta pasada revela que:

1. **El sistema es demasiado rígido para uso real.** Requiere un `FAST_PATH` para tareas triviales o los desarrolladores desactivarán todo.
2. **Faltan piezas de infraestructura.** Estado persistido (state.yaml), ubicación de PLAN.md, acceso al historial de sesión para hooks — sin estos, los hooks no pueden coordinarse.
3. **Algunos campos/features son unimplementables** con la infraestructura actual de Claude Code (cost_ceiling, confidence, SessionStart hook).

**Prioridad de corrección:**
1. `FAST_PATH` para tareas triviales (P3-1) — sin esto, el sistema es inutilizable
2. `state.yaml` para persistir estado (P3-2) — sin esto, los hooks no coordinan
3. `tdd-gate` configurable por proyecto (P3-3) — sin esto, bloquea trabajo legítimo
4. `PostToolUse(Read)` logger para session-consolidate (P3-4) — sin esto, el learning loop no funciona
5. Ubicación canónica de PLAN.md (P3-5) — sin esto, ambigüedad estructural

---
---

## Pasada 4

**Fecha:** 2026-04-17
**Auditor:** Arquitecto Zero-Trust (Opus 4.6 — auditoría de ejecución real)
**Scope:** Timing, concurrencia, bootstrap, y mecanismos sin implementación definida. Audita lo que las pasadas 1-3 introdujeron como correcciones y lo que sigue ausente.

---

### 1. Veredicto de Viabilidad

El documento ha madurado de manifiesto a especificación técnica. La state machine, los gates, y el `plan-gate.py` son avances reales. Sin embargo, esta pasada encuentra **15 fallos** en la capa de ejecución real: hooks que se auto-bloquean, heurísticas que miden en el momento incorrecto, estado compartido sin coordinación, y mecanismos definidos conceptualmente pero sin ruta de implementación. El sistema es internamente coherente en papel pero colapsaría en los primeros 5 minutos de uso real.

---

### 2. Vulnerabilidades de Timing, Concurrencia y Bootstrap

#### CRÍTICO-P4-1: FAST_PATH heuristic mide en el momento incorrecto

§10.2 `plan-gate.py` línea ~789: `is_trivial_change()` usa `git diff --cached --stat` para determinar si el cambio es trivial.

**Problema:** plan-gate es un hook `PreToolUse(Write)` — se ejecuta ANTES de que el archivo se escriba. En ese instante:
- `git diff --cached` muestra lo que estaba staged ANTES de esta operación
- El archivo que se está a punto de escribir NO está staged aún
- La primera escritura de cualquier sesión siempre tiene staged vacío → `is_trivial_change()` retorna True → FAST_PATH siempre pasa

**Consecuencia:** Una tarea compleja de 20 archivos pasa FAST_PATH en su primera escritura. Cada escritura individual evalúa solo el staged acumulado, no el total planeado. La heurística es retroactiva, no predictiva.

**Solución:**
1. Evaluar FAST_PATH una sola vez al inicio de la tarea (cuando se decide si crear PLAN.md), NO en cada write
2. Persistir la decisión en state.yaml: `mode: fast_path | full_path`. Una vez decidido, no re-evaluar
3. Si no hay PLAN.md y no hay `mode` en state.yaml → evaluar. El resultado se persiste y es definitivo para la tarea

---

#### CRÍTICO-P4-2: state.yaml race condition — múltiples hooks escriben concurrentemente

§2.6: "Cada hook lee state.yaml al inicio y lo escribe al final si cambió el estado."

Un evento `Write` dispara: plan-gate (PreToolUse), tdd-gate (PreToolUse), plan-drift-detector (PostToolUse), non-goal-guard (PostToolUse), auto-format (PostToolUse).

**Problema:** Si PostToolUse hooks ejecutan en paralelo (comportamiento no documentado en Claude Code), state.yaml se corrompe:
1. Hook A lee state.yaml: `{current_state: EXECUTE, replan_count: 0}`
2. Hook B lee state.yaml: `{current_state: EXECUTE, replan_count: 0}`
3. Hook A escribe: `{current_state: EXECUTE, replan_count: 0, last_gate_passed: GATE-2}`
4. Hook B sobrescribe: `{current_state: EXECUTE, replan_count: 0}` ← pierde `last_gate_passed`

**Solución:** Designar un ÚNICO hook escritor por tipo de evento:
- PreToolUse: solo `plan-gate` escribe state.yaml
- PostToolUse: solo `plan-drift-detector` escribe state.yaml
- Los demás hooks leen pero NO escriben state.yaml

---

#### CRÍTICO-P4-3: hook-health-check bootstrap paradox

§10.3 + §2.6: hook-health-check es PreToolUse y es responsable de crear state.yaml si no existe. Pero hook-health-check TAMBIÉN lee state.yaml para saber si debe ejecutarse (`last_health_check`).

**Secuencia de fallo:**
1. Sesión nueva, state.yaml no existe
2. Primer tool use (ej: Read) → dispara PreToolUse hooks
3. hook-health-check intenta leer state.yaml → FileNotFoundError
4. Exit code 2 (error) → fail-closed → BLOCK
5. TODAS las operaciones bloqueadas — ni siquiera se puede leer un archivo

**Consecuencia:** Sesión completamente inutilizable hasta que alguien cree state.yaml manualmente.

**Solución:** hook-health-check DEBE tener un bootstrap path explícito:
```python
def main():
    state_path = ".claude/state.yaml"
    if not os.path.exists(state_path):
        create_initial_state(state_path)  # Bootstrap, no error
        # Continuar con health check normal
    state = read_state(state_path)
    # ... rest of health check
```
Regla: ausencia de state.yaml es condición normal (primera sesión), NO un error. NUNCA exit 2 por este motivo.

---

#### CRÍTICO-P4-4: non-goal-guard rollback sin mecanismo definido

§2.5: "Match con non-goal → bloqueo + log + rollback del archivo."

non-goal-guard es PostToolUse(Write/Edit) — el archivo YA fue escrito cuando el hook ejecuta.

**Problema:** "Rollback del archivo" no tiene implementación:
- Si el archivo existía antes → ¿`git checkout -- file`? Solo funciona si estaba en el último commit
- Si el archivo era nuevo → ¿`rm file`? Operación destructiva
- Si fue Edit (no Write) → ¿revertir solo la edición? Imposible sin estado previo
- Claude Code no proporciona el estado previo del archivo al hook PostToolUse

**Consecuencia:** El hook detecta violaciones pero no puede revertirlas. El daño ya está hecho.

**Solución:** Cambiar estrategia fundamentalmente:
1. Mover non-goal-guard a **PreToolUse** — evaluar ANTES de escribir. El hook recibe `file_path` en el evento y compara contra non_goals. Si match → BLOCK → archivo NUNCA se escribe → no necesita rollback.
2. Mantener un PostToolUse como safety net secundario: si detecta violación (edge case) → log de advertencia + entry en `error_log` de state.yaml. NO intentar rollback automático.

---

### 3. Vulnerabilidades de Implementación

#### ALTO-P4-5: plan-gate.py valida PLAN.md por text search, no por YAML parsing

§10.2 línea ~778: `missing = [field for field in PLAN_REQUIRED_FIELDS if field not in content]`

**Problema:** Busca la CADENA `"plan_id"` en el contenido completo del archivo. Pasa con falsos positivos:
- Comentario: `# Recuerda definir plan_id`
- Code block: `` ```yaml plan_id: ... ``` ``
- Prosa: `"El campo plan_id es obligatorio"`

Además: `PLAN_REQUIRED_FIELDS = ["plan_id", "files_affected", "acceptance_criteria"]` — falta `approach`, que §2.3 lista como campo obligatorio mínimo.

**Solución:** Parsear YAML real. `yaml` está en stdlib de Python 3.10+. Verificar keys del dict parseado, no texto.

---

#### ALTO-P4-6: session-read-logger añade ~10s de overhead por sesión

§10.1: PostToolUse(Read) hook que registra cada lectura de archivo.

**Cálculo:** Sesión típica: 50-200 lecturas. Cada hook: Python startup ~40ms + I/O ~5ms = ~45ms. Total: 200 × 45ms = **9 segundos** de overhead puro por sesión.

**Solución:** Implementar en bash (startup ~5ms):
```bash
#!/bin/bash
echo "$(date -Iseconds) $(echo "$1" | jq -r '.tool_input.file_path')" >> .claude/session-reads.log
```
Reduce overhead a ~200 × 10ms = **2 segundos**. Aceptable.

---

#### ALTO-P4-7: Lesson storage location never specified

§1.8 define el schema YAML de lessons con 11 campos, pero NUNCA dice dónde se almacenan. session-consolidate referencia "entries" genéricamente.

**Consecuencia:** Schema sin storage = modelo de datos sin base de datos.

**Solución:** Ubicación canónica:
```
.claude/memory/
├── lessons/
│   ├── lesson-2026-04-17-001.yaml
│   ├── lesson-2026-04-17-002.yaml
│   └── archive/                       # TTL expirado
├── MEMORY.md
└── session-reads.log
```
Una lesson por archivo YAML. Permite grep, es atómico, y session-consolidate procesa con `glob("lessons/*.yaml")`.

---

#### ALTO-P4-8: GATE-1 (EXPLORE → PLAN) sin hook ni precondición definida

§2.2: "GATE-1: Existe artefacto de exploración (archivos leídos, contexto documentado)."

**Problema:**
- "Artefacto de exploración" no definido (¿archivo? ¿log entry? ¿cuántas lecturas?)
- No hay hook implementado — la tabla §10.1 no lista hook para GATE-1
- GATE-2 y GATE-3 tienen hooks (plan-gate, commit-checklist). GATE-1 es textual.
- Sin enforcement, Claude puede planificar sin explorar → plan basado en alucinaciones

**Solución recomendada:** Eliminar GATE-1 como gate formal. Redefinir como CONVENTION. Un gate programático débil (ej: "≥3 archivos leídos") da falsa sensación de seguridad — 3 lecturas de README no sustituyen exploración real. La exploración se valida indirectamente: plan sin contexto → falla en EXECUTE → RE-PLAN con exploración real.

---

#### ALTO-P4-9: Agent-plan integration undefined

§8: "Cada agente recibe solo el output de sus dependencias."
§2: PLAN.md es artefacto central de la state machine.

**Problema:** No se especifica cómo los agentes acceden al plan:
- ¿code-reviewer lee `.claude/plans/PLAN.md` directamente?
- ¿tdd-guide recibe `acceptance_criteria` extraídos?
- ¿El pipeline architect → coder → tester → reviewer comparte plan completo o extractos?

**Solución:** Contrato de integración:
- Agentes dentro de la state machine reciben `plan_path` en su prompt
- Ejemplo: "Lee el plan en `.claude/plans/PLAN.md`. Verifica que el diff cumple `acceptance_criteria` y no viola `non_goals`."
- Esto es una convención de prompt, no un mecanismo técnico — coherente con el modelo de agentes de Claude Code.

---

#### ALTO-P4-10: `sessions_without_repeat` no tiene mecanismo de tracking confiable

§1.8: `sessions_without_repeat: 0` — se incrementa cada sesión donde el trigger NO se repite.
§14.4: Promoción implícita cuando `sessions_without_repeat >= 5`.

**Problema:** session-consolidate (Stop hook) necesita saber "¿el trigger de esta lesson ocurrió en esta sesión?" Pero:
- No tiene acceso al historial de errores/correcciones de la sesión
- session-reads.log solo registra LECTURAS, no correcciones del usuario
- Sin esta información, `sessions_without_repeat` siempre se incrementa → todas las lessons se promueven eventualmente

**Solución pragmática:** `sessions_without_repeat` se incrementa automáticamente SIEMPRE en session-consolidate. El reset a 0 solo ocurre por señal explícita: `/lesson-fail <id>`. Convierte mecanismo automático impreciso en semi-manual confiable.

---

### 4. Coherencia y Gaps Funcionales

#### MEDIO-P4-11: Wiki archival by time removes architecture decisions

§14.3: `_index.yaml` archiva entries con `last_updated > 90 días`.

ADRs ("elegimos PostgreSQL sobre MongoDB") raramente se actualizan pero son siempre relevantes. Archival por tiempo los elimina.

**Solución:** Campo `category` en entries: `decision` (nunca archivado por TTL), `concept` (archival normal), `incident` (archival agresivo: 30 días).

---

#### MEDIO-P4-12: §12.4 `git reset --hard` no aparece en deny ni allow list

§12.4: "Error de diseño → `git reset --hard pre-<plan_id>`"
§9: deny list incluye `rm -rf` pero no `git reset --hard`.

En modo autónomo sin usuario → operación en zona gris → pendiente indefinidamente.

**Solución:** Allow list restringido: `"Bash(git reset --hard pre-plan-*)"` — permite rollback a tags del plan, no arbitrario.

---

#### MEDIO-P4-13: Inter-hook evaluation order undocumented

§10.1: 8 hooks. Un Write dispara 5 de ellos. Si plan-gate ALLOWS pero tdd-gate BLOCKS, ¿cuál gana?

Claude Code ejecuta PreToolUse hooks secuencialmente (primer BLOCK gana — short-circuit AND). Esto no está documentado en Sintesis.md.

**Solución:** Documentar: "PreToolUse: secuencial, primer BLOCK cancela. PostToolUse: todos ejecutan independientemente (no cancelan operación completada)."

---

#### MEDIO-P4-14: Sintesis.md tiene 1149 líneas — viola su propio principio de atención

§1.1: "Límite ~200 líneas. Más diluye la atención."

Sintesis.md es la meta-definición de CLAUDE.md. Un implementador sufre la misma dilución.

**Solución:** Separar en dos documentos:
- `Sintesis.md` → referencia normativa completa (como está)
- `Sintesis-quickstart.md` → extracto de ~200 líneas: state machine, tabla de hooks, schemas, setup progresivo

---

#### MEDIO-P4-15: `cost_ceiling_usd` estimation formula undefined

§2.3: "El hook estima coste basándose en iteraciones × coste medio por iteración (configurable)."

"Coste medio por iteración" no tiene valor default ni ubicación de configuración.

**Solución:** Default en settings.json:
```yaml
circuit_breaker:
  avg_cost_per_iteration_usd: 0.15  # Estimación Sonnet 4.6
  # cost_estimate = iterations × avg_cost_per_iteration_usd
```
Con disclaimer: "Estimación grosera. Para control real, usar API de billing de Anthropic."

---

### Resumen de severidades — Pasada 4

| ID | Severidad | Descripción | Tipo |
|---|---|---|---|
| CRÍTICO-P4-1 | 🔴 | FAST_PATH heuristic mide antes del write — siempre trivial la primera vez | Timing |
| CRÍTICO-P4-2 | 🔴 | state.yaml race condition — múltiples hooks escriben sin coordinación | Concurrencia |
| CRÍTICO-P4-3 | 🔴 | hook-health-check bootstrap paradox — no puede crear lo que necesita para ejecutar | Bootstrap |
| CRÍTICO-P4-4 | 🔴 | non-goal-guard PostToolUse no puede hacer rollback — archivo ya escrito | Timing |
| ALTO-P4-5 | 🟠 | plan-gate.py valida por text search, no YAML parsing + falta campo `approach` | Implementación |
| ALTO-P4-6 | 🟠 | session-read-logger añade ~10s overhead por sesión (Python startup) | Performance |
| ALTO-P4-7 | 🟠 | Lesson storage location never specified — schema sin storage | Especificación |
| ALTO-P4-8 | 🟠 | GATE-1 sin hook ni definición de "artefacto de exploración" | Especificación |
| ALTO-P4-9 | 🟠 | Agent-plan integration undefined — agentes no saben cómo acceder al plan | Especificación |
| ALTO-P4-10 | 🟠 | `sessions_without_repeat` no tiene tracking confiable cross-session | Implementación |
| MEDIO-P4-11 | 🟡 | Wiki archival by TTL elimina architecture decisions vigentes | Diseño |
| MEDIO-P4-12 | 🟡 | `git reset --hard` en zona gris del permission model | Coherencia |
| MEDIO-P4-13 | 🟡 | Inter-hook evaluation order no documentado | Especificación |
| MEDIO-P4-14 | 🟡 | Documento de 1149 líneas viola su propio principio de ~200 líneas | Auto-coherencia |
| MEDIO-P4-15 | 🟡 | `cost_ceiling_usd` sin fórmula ni default definido | Especificación |

---

### Conclusión de Pasada 4

**4 CRÍTICAS, 6 ALTAS, 5 MEDIAS.**

Las pasadas anteriores resolvieron problemas conceptuales (P1), de implementabilidad (P2), y de viabilidad operativa (P3). Esta pasada 4 revela que **el sistema colapsaría en ejecución real** por problemas de timing y coordinación:

1. **Los hooks miden en el momento incorrecto.** FAST_PATH evalúa ANTES del write (siempre trivial). non-goal-guard evalúa DESPUÉS (no puede revertir). Solución: mover non-goal-guard a PreToolUse y persistir la decisión FAST_PATH.

2. **El estado compartido no tiene coordinación.** state.yaml es leído/escrito por 5+ hooks sin locking. Solución: un único escritor por tipo de evento.

3. **El sistema no puede arrancar desde cero.** hook-health-check falla si state.yaml no existe, pero es responsable de crearlo. Solución: bootstrap path explícito con condición `if not exists → create`.

4. **Mecanismos definidos sin ruta de implementación.** Lessons sin storage, GATE-1 sin hook, agent-plan sin contrato, sessions_without_repeat sin tracking. Cada uno es individualmente resoluble, pero juntos representan ~30% del sistema sin implementación.

**Acumulado total (Pasadas 1-4): ~56 issues identificados (14 CRÍTICOS, 24 ALTOS, 18 MEDIOS)**

**Prioridad de corrección para Pasada 4:**
1. Mover non-goal-guard a PreToolUse (P4-4) — sin esto, non-goals no se protegen
2. Bootstrap path en hook-health-check (P4-3) — sin esto, primera sesión muere
3. Persistir FAST_PATH en state.yaml (P4-1) — sin esto, heurística rota
4. Único escritor de state.yaml por tipo de evento (P4-2) — sin esto, estado corrupto
5. Lesson storage location (P4-7) — sin esto, learning loop no tiene dónde escribir
