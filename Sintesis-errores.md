# Auditoría de Sintesis.md — Pasada 1

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
