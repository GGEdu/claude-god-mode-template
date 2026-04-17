# Plan de Integracion: Unificacion de Skills, Agentes y Workflows

> Este plan unifica la reorganizacion de skills/agentes con los requisitos normativos de Sintesis.md.
> Cada decision ha sido validada contra las 17 secciones de Sintesis.md.
> Las contradicciones detectadas se documentan con su resolucion obligatoria.

---

## 0. Resumen Ejecutivo

**Objetivo:** Reorganizar 147 skills y 36 agentes en un sistema coherente con workflows predefinidos, eliminando orphans y redundancia, sin violar las reglas de Sintesis.md.

**Decisiones confirmadas:**
1. `pipeline.yaml` se copia a `.claude/pipeline.yaml` del proyecto via `make init-project` — **SI**
2. Workflow `feature` es el default cuando el usuario dice "implementa X" — **SI**
3. Los 9 orchestrators se eliminan completamente — **SI**

**Resultado esperado:**
- 36 → 35 agentes (1 fusion: `code-simplifier` absorbido en `refactor-cleaner`)
- 147 → 138 skills (9 orchestrators eliminados)
- 6 workflows predefinidos via `pipeline.yaml` reemplazando orchestrators
- `compile-agents.py` con soporte `skill_map` para aliases canonicos
- Sintesis.md actualizado para reflejar pipeline.yaml como artefacto del sistema

---

## 1. Validacion Cruzada contra Sintesis.md

### 1.1 Fusion code-simplifier → refactor-cleaner

| Seccion Sintesis | Contenido relevante | Impacto | Contradiccion |
|---|---|---|---|
| §4.2 | "`/simplify` — invocar agentes de revision (code-simplifier, refactor-cleaner)" | Referencia explicita a AMBOS agentes | **SI — CONTRADICCION-1** |
| §8 | "Agentes solo para decisiones que requieren razonamiento" | Ambos cumplen — la fusion no viola este principio | NO |
| §1.2 | "Procedimientos repetitivos = Skills" | La fusion reduce un agente repetitivo → alineado | NO |
| §16 | "Kill Process, Don't Optimize It" | Si ambos agentes hacen "mejorar codigo sin cambiar comportamiento", uno sobra | ALINEADO |
| §1.9 | "Elegancia balanceada — no sobre-ingenierar" | 2 agentes para "mejorar codigo" puede ser sobre-ingenieria | ALINEADO |

**Analisis detallado de la fusion:**

| Aspecto | code-simplifier (351 lineas) | refactor-cleaner (86 lineas) |
|---|---|---|
| **Foco** | Readability: early returns, async/await, extract nested logic | Cleanup: dead code, duplicados, deps no usadas |
| **Herramientas** | Read, Grep, Glob, Bash, Edit | Read, Write, Edit, Bash, Grep, Glob |
| **Modelo** | sonnet | sonnet |
| **Destructividad** | Baja (transforma, no elimina) | Media (elimina codigo) |
| **Deteccion** | Manual (analisis de patrones) | Automatizada (knip, depcheck, ts-prune) |

**Riesgo de la fusion:** El agente fusionado tendra ~437 lineas. Esto excede el limite recomendado de 200-400 lineas (regla de coding-style.md). 

**Mitigacion:** Extraer las instrucciones detalladas de simplificacion (before/after patterns, ~200 lineas) a un skill `code-simplification-patterns/SKILL.md` que se embebe en el agente fusionado via `stack.yaml`. El agente base queda en ~230 lineas.

### 1.2 Eliminacion de 9 orchestrators

| Seccion Sintesis | Contenido relevante | Impacto | Contradiccion |
|---|---|---|---|
| §7 | Skills auto-activados por contexto | Los orchestrators NUNCA se activaron (0 refs en stack.yaml) | ALINEADO — eliminar orphans |
| §16 | "Kill Process, Don't Optimize It" | Proceso muerto = eliminar | ALINEADO |
| §1.2 | "Procedimientos repetitivos = Skills" | Los orchestrators SON procedimientos pero nunca se usaron como skills | ALINEADO |
| §8 | Pipeline de agentes architect → coder → tester → reviewer | pipeline.yaml implementa esto de forma mas clara | ALINEADO |

**No hay contradiccion.** Los orchestrators nunca se integraron en ningun stack. Son orphans con 0% de uso.

**Contenido a preservar:** Cada orchestrator define fases con skills concretos por lenguaje (ej: `laravel-tdd`, `rust-patterns`). Este conocimiento ya esta capturado en:
- `stack.yaml` de cada stack (skills asignados a agentes)
- `pipeline.yaml` de cada stack (orden de ejecucion de agentes)

**Archivos a eliminar (9 directorios):**
```
skills/cpp-orchestrator/
skills/django-orchestrator/
skills/golang-orchestrator/
skills/kotlin-orchestrator/
skills/laravel-orchestrator/
skills/perl-orchestrator/
skills/python-orchestrator/
skills/rust-orchestrator/
skills/springboot-orchestrator/
```

### 1.3 pipeline.yaml como artefacto del proyecto

| Seccion Sintesis | Contenido relevante | Impacto | Contradiccion |
|---|---|---|---|
| §3.1 | Estructura de `.claude/` — NO incluye pipeline.yaml | pipeline.yaml no esta en la anatomia | **SI — CONTRADICCION-2** |
| §2.7 | Ubicacion canonica de artefactos | Solo define plans/ y state.yaml | **SI — CONTRADICCION-3** |
| §2.1 | State machine EXPLORE → PLAN → EXECUTE → VERIFY | Workflows mapean a la state machine pero con mas granularidad | **SI — CONTRADICCION-4** |
| §2.6 | state.yaml actualizado por hooks | Workflows deben actualizar state.yaml entre pasos | **SI — CONTRADICCION-5** |
| §17 | Orden de setup progresivo | pipeline.yaml no aparece en la secuencia | **SI — CONTRADICCION-6** |

### 1.4 Feature workflow como default

| Seccion Sintesis | Contenido relevante | Impacto | Contradiccion |
|---|---|---|---|
| §2.1 | FAST_PATH: tareas ≤3 archivos, ≤50 lineas → sin plan | Feature workflow SIEMPRE empieza con Plan | **SI — CONTRADICCION-7** |
| §7.1 | Skills auto-activados: impacto medio → notificar; alto → confirmar | Auto-seleccionar workflow = decision de impacto medio | **SI — CONTRADICCION-8** |
| §4.1 | "Claude ejecuta la state machine" | Si Feature es default, Claude ejecuta el WORKFLOW, no la state machine directamente | TENSION (no contradiccion si se coordinan) |

### 1.5 skill_map en compile-agents.py

| Seccion Sintesis | Contenido relevante | Impacto | Contradiccion |
|---|---|---|---|
| §1.5 | "Minimizar decision latency" | skill_map elimina ambiguedad → alineado | ALINEADO |
| §3.1 | Anatomia del repositorio | Cambio interno en build tool, no visible en runtime | NO |

**No hay contradiccion.** Es infraestructura de build.

---

## 2. Contradicciones Detectadas y Resoluciones

### CONTRADICCION-1: §4.2 referencia explicitamente code-simplifier Y refactor-cleaner

**Texto actual en Sintesis.md §4.2:**
> `/simplify` — invocar agentes de revision (code-simplifier, refactor-cleaner). `[TO BUILD]`

**Problema:** Si fusionamos los agentes, §4.2 referencia un agente que ya no existe.

**Resolucion OBLIGATORIA:**
- Actualizar §4.2: `/simplify` — invocar agente `refactor-cleaner` (simplificacion + cleanup). `[TO BUILD]`
- El command `/simplify` invoca UN agente (`refactor-cleaner`) en lugar de dos
- El pipeline.yaml `refactor` workflow actualiza la referencia:
  ```yaml
  # ANTES
  - agent: code-simplifier
  # DESPUES
  - agent: refactor-cleaner
  ```

---

### CONTRADICCION-2: §3.1 no incluye pipeline.yaml en la anatomia

**Texto actual en Sintesis.md §3.1:**
```
.claude/
    ├── settings.json
    ├── rules/
    ├── commands/
    ├── skills/
    ├── agents/
    └── hooks/
```

**Problema:** `pipeline.yaml` se copiara a `.claude/` pero no aparece en la estructura canonica.

**Resolucion OBLIGATORIA:**
```
.claude/
    ├── settings.json
    ├── pipeline.yaml        # ← NUEVO: Workflows para workflow-runner
    ├── rules/
    ├── commands/
    ├── skills/
    ├── agents/
    └── hooks/
```

---

### CONTRADICCION-3: §2.7 no incluye pipeline.yaml en artefactos canonicos

**Texto actual:**
```
.claude/
├── plans/
│   ├── PLAN.md
│   └── PLAN.v1.md
├── state.yaml
└── hooks/
```

**Resolucion OBLIGATORIA:**
```
.claude/
├── pipeline.yaml            # ← NUEVO: Definicion de workflows
├── plans/
│   ├── PLAN.md
│   └── PLAN.v1.md
├── state.yaml
└── hooks/
```

---

### CONTRADICCION-4: Workflows vs State Machine — dos capas de orquestacion

**El problema central:** Sintesis §2 define una state machine (EXPLORE → PLAN → EXECUTE → VERIFY → DONE) implementada por hooks. Los workflows (pipeline.yaml) definen una secuencia de agentes (Research → Plan → Implement → Test → Review). Son DOS capas de orquestacion que podrian conflictar.

**Analisis de la relacion:**

| Workflow Step | State Machine State | Hook que aplica |
|---|---|---|
| Research (docs-lookup) | EXPLORE | Ninguno (solo lee) |
| Plan (planner) | PLAN | plan-gate permite crear PLAN.md (whitelist) |
| Implement (tdd-guide) | EXECUTE | plan-gate verifica PLAN.md existe, tdd-gate verifica tests |
| Test (verificacion) | EXECUTE → VERIFY | commit-checklist en GATE-3 |
| Review (code-reviewer) | VERIFY | Agente independiente, no hook |
| Memory (memory-consolidator) | post-DONE | Complementa session-consolidate |

**Conclusion:** Los workflows son una capa CONCRETA sobre la state machine ABSTRACTA. No conflictan si el workflow respeta los gates:
- El planner escribe PLAN.md → plan-gate lo permite (whitelist §2.2)
- El tdd-guide escribe tests → tdd-gate lo permite (son tests, no implementacion)
- El implementador escribe codigo → plan-gate verifica PLAN.md existe (deberia existir porque el planner ya lo creo)

**Resolucion OBLIGATORIA:**
El workflow-runner DEBE actualizar `state.yaml` entre pasos para mantener la coherencia:

```python
# Pseudo-codigo del workflow-runner al ejecutar cada paso
def execute_step(step, state):
    if step.agent == "planner":
        update_state(current_state="PLAN")
    elif step.agent in ["tdd-guide", "implementor"]:
        update_state(current_state="EXECUTE")
    elif step.agent in ["code-reviewer", "security-reviewer"]:
        update_state(current_state="VERIFY")
    elif step.agent == "memory-consolidator":
        update_state(current_state="DONE")
    
    # Invocar agente
    result = invoke_agent(step.agent, context)
    return result
```

**Esto requiere:** Anadir un nuevo campo a state.yaml:
```yaml
# .claude/state.yaml — campo nuevo
workflow_active: "feature"    # null si no hay workflow activo
workflow_step: 3              # Paso actual del workflow (1-indexed)
```

**Actualizacion necesaria en Sintesis.md §2.6:** Anadir estos campos al schema de state.yaml.

---

### CONTRADICCION-5: state.yaml no contempla workflows

Ver resolucion en CONTRADICCION-4.

---

### CONTRADICCION-6: §17 Setup Progresivo no incluye pipeline.yaml

**Texto actual §17:**
```
7. Skills y Agents → Cuando un workflow complejo se repita. No antes.
```

**Resolucion OBLIGATORIA:** pipeline.yaml se instala JUNTO con skills y agents (paso 7), ya que depende de que ambos existan. Actualizar §17:
```
7. Skills, Agents y Workflows → Cuando un workflow complejo se repita. 
   `pipeline.yaml` define la secuencia de agentes por tipo de tarea.
```

---

### CONTRADICCION-7: Feature como default vs FAST_PATH (CRITICO)

**El conflicto:** §2.1 define FAST_PATH para tareas triviales (≤3 archivos, ≤50 lineas) que NO necesitan plan. Pero si Feature es el workflow default, tareas triviales serian enrutadas al ciclo completo Research → Plan → Implement → Test → Review.

**Ejemplo concreto:** Usuario dice "arregla el typo en auth.ts" → workflow-runner selecciona Feature → ejecuta Research, Plan, etc. para un typo de 1 linea. Esto viola §2.1 FAST_PATH Y §16 "Kill Process, Don't Optimize It".

**Resolucion OBLIGATORIA — el workflow-runner debe respetar la state machine:**

```
Usuario dice "implementa X"
  │
  ├── workflow-runner evalua trivialidad (mismos criterios que plan-gate §2.1):
  │     - ≤3 archivos estimados
  │     - ≤50 lineas estimadas  
  │     - No involucra auth/security/payments
  │     - No es modulo nuevo
  │
  ├── SI trivial → workflow "hotfix" (sin Research ni Plan)
  │     state.yaml: mode: fast_path
  │
  └── NO trivial → workflow "feature" (ciclo completo)
        state.yaml: mode: full_path
```

**Importante:** La decision de trivialidad la hace Claude basandose en la descripcion del usuario, NO un hook. El hook (plan-gate) es el enforcement — verifica que la decision fue correcta. El workflow-runner es el router.

**Actualizacion en workflow-runner skill:** Anadir seccion de routing con criterios de FAST_PATH.

---

### CONTRADICCION-8: Auto-seleccion de workflow vs §7.1 impact levels

**El conflicto:** §7.1 define que skills de impacto medio deben notificar al usuario. Auto-seleccionar un workflow completo (que incluye crear plan, escribir tests, hacer code review) es una decision de impacto medio-alto.

**Resolucion OBLIGATORIA:**
- workflow-runner auto-detecta el workflow candidato
- SIEMPRE notifica al usuario cual workflow selecciono:
  ```
  "▶ Workflow seleccionado: feature (planificacion + TDD + review). 
   Archivos estimados: ~5. ¿Continuar? [Enter/n]"
  ```
- En modo autonomo (routines): el workflow se declara explicitamente en el prompt de la routine, no se auto-detecta. §13 ya requiere prompts completamente deterministas.

---

### CONTRADICCION ADICIONAL-9: pipeline.yaml no incluye paso Research

**Estado actual:** Los 14 pipeline.yaml existentes empiezan por `planner`, NO por research/explore.

**Conflicto con Sintesis:** §2.1 state machine empieza en EXPLORE. §2.2 GATE-1 requiere "artefacto de exploracion" antes de PLAN.

**Resolucion:**
- Opcion A: Anadir paso Research a todos los pipeline.yaml (agente: docs-lookup o architect en modo exploracion)
- Opcion B: Considerar que el planner agent INCLUYE exploracion en su flujo (lee codigo, busca patrones antes de planificar)

**Decision: Opcion A para el pipeline.yaml comun, con `continue_on_failure: true`:**
```yaml
feature:
  steps:
    - agent: docs-lookup
      description: "Explorar codebase y documentacion relevante"
      continue_on_failure: true    # No bloquear si no encuentra docs
    - agent: planner
      description: "Crear plan de implementacion"
    # ... resto
```

Esto alinea el workflow con la state machine: Research = EXPLORE, Plan = PLAN, etc.

---

### CONTRADICCION ADICIONAL-10: Eliminacion de orchestrators vs documentacion

**Archivos que referencian orchestrators y necesitan actualizacion:**

| Archivo | Tipo de referencia | Accion |
|---|---|---|
| `README.md` | "9 Stack Orchestrators (Pipeline Managers)" | Actualizar: reemplazar por referencia a pipeline.yaml |
| `ORCHESTRATION_DECISIONS.md` | ADR explicando el patron orchestrator | Actualizar: documentar migracion a pipeline.yaml |
| `docs/src/skills.md` | Documentacion de skills | Eliminar entradas de orchestrators |
| `docs/src/referencia.md` | Referencia general | Actualizar |
| `docs/src/instalacion.md` | Guia de instalacion | Verificar y actualizar |
| `docs/src/estructura/agents.md` | Estructura de agentes | Verificar y actualizar |
| `docs/src/estructura/claude-config.md` | Config de Claude | Verificar y actualizar |
| `docs/src/examples/orquestacion-laravel-react.md` | Ejemplo de orquestacion | Actualizar con pipeline.yaml |
| `rules/orchestration.md` | Reglas de orquestacion | Nota: referencia `github-orchestrator` (agente, no skill) — mantener |

---

## 3. Cambios Detallados por Archivo

### 3.A — Fusion code-simplifier → refactor-cleaner

#### `agents/refactor-cleaner.md` — MODIFICAR (absorber simplifier)

Anadir al agente fusionado:
1. Seccion "Code Simplification" con las 6 tecnicas del simplifier (early returns, async/await, extract nested, eliminate redundant state, simplify booleans, flatten collections)
2. Mantener seccion "Dead Code Cleanup" original

**Alternativa recomendada (para respetar limite de ~400 lineas):**
- Extraer las instrucciones detalladas de simplificacion a un skill: `skills/code-simplification-patterns/SKILL.md`
- El agente fusionado hace referencia al skill via stack.yaml
- Las instrucciones de alto nivel quedan en el agente; los patrones before/after van al skill

**Estructura resultante:**
```yaml
# En cada stack.yaml
refactor-cleaner:
  skills:
    - code-simplification-patterns   # ← NUEVO skill con patrones del antiguo simplifier
```

#### `agents/code-simplifier.md` — ELIMINAR

#### `skills/code-simplification-patterns/SKILL.md` — CREAR

Contenido: Las 6 tecnicas de simplificacion con ejemplos before/after (extraidas de code-simplifier.md lineas 16-247).

#### `stacks/*/stack.yaml` (15 archivos) — MODIFICAR

En cada stack.yaml:
1. Eliminar la entrada `code-simplifier: skills: []`
2. Anadir skill `code-simplification-patterns` a `refactor-cleaner`

```yaml
# ANTES
refactor-cleaner:
  skills: []
code-simplifier:
  skills: []

# DESPUES
refactor-cleaner:
  skills:
    - code-simplification-patterns
# code-simplifier: ELIMINADO
```

#### `stacks/*/pipeline.yaml` (14 archivos) — MODIFICAR

En el workflow `refactor`, cambiar:
```yaml
# ANTES
- agent: code-simplifier
  description: "Simplificar codigo"

# DESPUES
- agent: refactor-cleaner
  description: "Simplificar y limpiar codigo"
```

### 3.B — Eliminacion de orchestrators

#### `skills/*-orchestrator/` (9 directorios) — ELIMINAR

```
skills/cpp-orchestrator/
skills/django-orchestrator/
skills/golang-orchestrator/
skills/kotlin-orchestrator/
skills/laravel-orchestrator/
skills/perl-orchestrator/
skills/python-orchestrator/
skills/rust-orchestrator/
skills/springboot-orchestrator/
```

**Pre-eliminacion:** Verificar que el conocimiento de cada orchestrator esta cubierto:

| Orchestrator | Conocimiento clave | Cubierto por |
|---|---|---|
| laravel-orchestrator | laravel-tdd → laravel-patterns → laravel-security → laravel-verification | stack.yaml agents + pipeline.yaml |
| python-orchestrator | python-testing → python-patterns → mypy | stack.yaml agents + pipeline.yaml |
| rust-orchestrator | rust-testing → rust-patterns → cargo clippy/fmt | stack.yaml agents + pipeline.yaml |
| golang-orchestrator | go testing → go-patterns → go vet | stack.yaml agents + pipeline.yaml |
| cpp-orchestrator | cpp testing → cpp-patterns → cppcheck/clang-tidy | stack.yaml agents + pipeline.yaml |
| springboot-orchestrator | java testing → java patterns → Maven/Gradle | stack.yaml agents + pipeline.yaml |
| kotlin-orchestrator | kotlin testing → kotlin patterns → detekt | stack.yaml agents + pipeline.yaml |
| perl-orchestrator | perl testing → perl patterns | stack.yaml agents + pipeline.yaml |
| django-orchestrator | django testing → django patterns → mypy | stack.yaml agents + pipeline.yaml |

**Resultado:** Todo el conocimiento ya esta distribuido en stack.yaml (skills por agente) y pipeline.yaml (orden de ejecucion). Los orchestrators son duplicacion pura.

#### Documentacion que referencia orchestrators — ACTUALIZAR

Ver tabla en CONTRADICCION-10 arriba.

### 3.C — Pipeline comun y pipelines por stack

#### `stacks/common/pipeline.yaml` — CREAR

```yaml
# stacks/common/pipeline.yaml — 6 workflows genericos
# Copiado a .claude/pipeline.yaml por make init-project
# Los agentes usan skills del stack activo (resueltos por compile-agents.py)

workflows:
  feature:
    description: "Feature completa: exploracion, planificacion, TDD y revision"
    steps:
      - agent: docs-lookup
        description: "Explorar codebase y documentacion relevante"
        continue_on_failure: true
      - agent: planner
        description: "Crear plan de implementacion con acceptance criteria"
      - agent: tdd-guide
        description: "Escribir tests primero, luego implementar"
      - agent: code-reviewer
        description: "Revisar calidad del codigo"
      - agent: security-reviewer
        description: "Verificar vulnerabilidades"
        parallel_with: code-reviewer
      - audit: true
        description: "Ejecutar verificaciones automaticas"
      - agent: memory-consolidator
        description: "Guardar decisiones en memoria"
        always: true

  hotfix:
    description: "Fix rapido con revision minima — para FAST_PATH"
    steps:
      - agent: tdd-guide
        description: "Escribir test para el fix, luego implementar"
      - agent: code-reviewer
        description: "Revisar el fix"
      - audit: true
      - agent: memory-consolidator
        description: "Guardar decisiones"
        always: true

  refactor:
    description: "Mejora de codigo sin cambio de comportamiento"
    steps:
      - agent: planner
        description: "Planificar el refactoring"
      - agent: refactor-cleaner
        description: "Simplificar y limpiar codigo"
      - agent: code-reviewer
        description: "Revisar cambios"
      - audit: true
      - agent: memory-consolidator
        description: "Guardar decisiones"
        always: true

  review:
    description: "Revision profunda de codigo existente"
    steps:
      - agent: code-reviewer
        description: "Revision de calidad"
      - agent: security-reviewer
        description: "Revision de seguridad"
        parallel_with: code-reviewer
      - agent: silent-failure-hunter
        description: "Buscar errores silenciados"
      - agent: memory-consolidator
        description: "Guardar hallazgos"
        always: true

  security-audit:
    description: "Auditoria de seguridad exhaustiva"
    steps:
      - agent: security-reviewer
        description: "Scan completo de vulnerabilidades"
      - agent: silent-failure-hunter
        description: "Detectar errores silenciados"
      - agent: code-reviewer
        description: "Revision de correcciones"
      - agent: memory-consolidator
        description: "Registrar hallazgos y decisiones"
        always: true

  documentation:
    description: "Actualizacion de documentacion del proyecto"
    steps:
      - agent: docs-lookup
        description: "Explorar estado actual de la documentacion"
        continue_on_failure: true
      - agent: doc-updater
        description: "Escribir y actualizar documentacion"
      - agent: code-reviewer
        description: "Revisar precision de la documentacion"
      - agent: memory-consolidator
        description: "Registrar cambios de documentacion"
        always: true
```

#### `stacks/*/pipeline.yaml` (15 archivos) — ACTUALIZAR

Cada stack mantiene su pipeline.yaml existente PERO:
1. Reemplazar `code-simplifier` → `refactor-cleaner` en workflow `refactor`
2. Anadir paso `docs-lookup` al inicio del workflow `feature` (con `continue_on_failure: true`)
3. Anadir workflows `security-audit` y `documentation` si no existen
4. Verificar que el pipeline del stack no contradiga el comun

**Regla:** Los pipelines por stack OVERRIDEN al comun. Si un stack tiene `feature` definido, se usa ese — no el comun. Esto permite personalizacion por stack.

### 3.D — skill_map en compile-agents.py

#### `ops/compile-agents.py` — MODIFICAR (~15 lineas)

Anadir soporte para `skill_map` en stack.yaml:

```yaml
# En stacks/laravel/stack.yaml
skill_map:
  patterns: laravel-patterns
  testing: laravel-tdd
  security: laravel-security
  verification: laravel-verification
```

**Uso en pipeline.yaml:**
```yaml
# En stacks/common/pipeline.yaml (futuro — no en esta fase)
steps:
  - agent: tdd-guide
    skill_override: testing    # Resuelve a laravel-tdd via skill_map
```

**Implementacion en compile-agents.py:**

```python
# Dentro de compile_stack() — despues de leer stack config
skill_map = stack_config.get("skill_map", {})

# Al resolver skills, verificar aliases
def resolve_skill(skill_name, skill_map):
    """Resuelve alias de skill_map, o retorna el nombre original."""
    return skill_map.get(skill_name, skill_name)
```

**Nota:** En esta fase, `skill_map` se define pero NO se usa activamente en pipeline.yaml. Es infraestructura para futuras mejoras. Los pipeline.yaml actuales usan nombres de agentes (no skills), por lo que no necesitan resolucion de skill_map todavia.

### 3.E — Integracion con Makefile

#### `Makefile` — MODIFICAR

En la regla `init-project`, anadir copia de pipeline.yaml:

```makefile
# Dentro de init-project target
# Copiar pipeline.yaml (stack-specific si existe, sino comun)
@if [ -f "stacks/$(STACK)/pipeline.yaml" ]; then \
    cp "stacks/$(STACK)/pipeline.yaml" "$(PROJECT)/.claude/pipeline.yaml"; \
else \
    cp "stacks/common/pipeline.yaml" "$(PROJECT)/.claude/pipeline.yaml"; \
fi
```

**Importante:** Pipeline del stack tiene prioridad sobre el comun. Esto permite que cada stack tenga workflows personalizados mientras el comun sirve de fallback.

### 3.F — Actualizacion de workflow-runner skill

#### `skills/workflow-runner/SKILL.md` — MODIFICAR

Anadir seccion de routing con FAST_PATH:

```markdown
## Routing de Workflows

Cuando el usuario pide implementar algo sin especificar workflow:

1. Evaluar trivialidad (criterios de Sintesis §2.1 FAST_PATH):
   - ≤3 archivos estimados
   - ≤50 lineas estimadas
   - No involucra auth/security/payments
   - No es modulo/servicio nuevo

2. Si trivial → usar workflow `hotfix`
3. Si no trivial → usar workflow `feature`

4. SIEMPRE notificar al usuario el workflow seleccionado:
   "▶ Workflow seleccionado: {nombre} ({descripcion}). Continuar? [Enter/n]"

5. En modo autonomo (routines): el workflow se declara en el prompt, no se auto-detecta.
```

---

## 4. Actualizaciones OBLIGATORIAS a Sintesis.md

> Cada cambio se lista con la seccion exacta y el texto a modificar.

### 4.1 §3.1 — Anadir pipeline.yaml a la anatomia

**Anadir despues de `├── hooks/`:**
```
    ├── pipeline.yaml          # Workflows para /workflow (copiado de stack)
```

### 4.2 §2.7 — Anadir pipeline.yaml a artefactos canonicos

**Anadir en el arbol de `.claude/`:**
```
├── pipeline.yaml            # Workflows de agentes (§workflow-runner)
```

### 4.3 §4.2 — Actualizar referencia a code-simplifier

**ANTES:**
```
* **Refactorizacion:** `/simplify` — invocar agentes de revision (code-simplifier, refactor-cleaner). `[TO BUILD]`
```

**DESPUES:**
```
* **Refactorizacion:** `/simplify` — invocar agente `refactor-cleaner` (simplificacion + cleanup de codigo). `[TO BUILD]`
```

### 4.4 §2.6 — Anadir campos de workflow a state.yaml

**Anadir al schema de state.yaml:**
```yaml
workflow_active: null         # Nombre del workflow activo (null si no hay)
workflow_step: 0              # Paso actual del workflow (0 si no hay)
```

### 4.5 §17 — Incluir pipeline.yaml en setup progresivo

**ANTES:**
```
7. **Skills y Agents** → Cuando un workflow complejo se repita. No antes.
```

**DESPUES:**
```
7. **Skills, Agents y Workflows** → Cuando un workflow complejo se repita. 
   `pipeline.yaml` define la secuencia de agentes por tipo de tarea. `make init-project` lo instala.
```

### 4.6 §10.1 — Anadir pipeline.yaml a whitelist de hooks

**Anadir a la whitelist de metadatos (§2.2):**
```
**/pipeline.yaml
```

pipeline.yaml es configuracion, no codigo fuente — no debe ser bloqueado por plan-gate ni tdd-gate.

---

## 5. Archivos a Crear (resumen)

| Archivo | Tipo | Proposito |
|---|---|---|
| `stacks/common/pipeline.yaml` | YAML | 6 workflows genericos (fallback) |
| `skills/code-simplification-patterns/SKILL.md` | Markdown | Patrones de simplificacion extraidos de code-simplifier |

## 6. Archivos a Eliminar (resumen)

| Archivo/Directorio | Razon |
|---|---|
| `agents/code-simplifier.md` | Fusionado en refactor-cleaner |
| `skills/cpp-orchestrator/` | Orphan — reemplazado por pipeline.yaml |
| `skills/django-orchestrator/` | Orphan — reemplazado por pipeline.yaml |
| `skills/golang-orchestrator/` | Orphan — reemplazado por pipeline.yaml |
| `skills/kotlin-orchestrator/` | Orphan — reemplazado por pipeline.yaml |
| `skills/laravel-orchestrator/` | Orphan — reemplazado por pipeline.yaml |
| `skills/perl-orchestrator/` | Orphan — reemplazado por pipeline.yaml |
| `skills/python-orchestrator/` | Orphan — reemplazado por pipeline.yaml |
| `skills/rust-orchestrator/` | Orphan — reemplazado por pipeline.yaml |
| `skills/springboot-orchestrator/` | Orphan — reemplazado por pipeline.yaml |

## 7. Archivos a Modificar (resumen)

| Archivo | Cambio |
|---|---|
| `agents/refactor-cleaner.md` | Absorber responsabilidades de code-simplifier |
| `ops/compile-agents.py` | Anadir soporte skill_map (~15 lineas) |
| `Makefile` | Copiar pipeline.yaml en init-project |
| `skills/workflow-runner/SKILL.md` | Routing FAST_PATH + notificacion |
| `stacks/*/stack.yaml` (x15) | Eliminar code-simplifier, anadir skill a refactor-cleaner |
| `stacks/*/pipeline.yaml` (x14) | code-simplifier → refactor-cleaner + docs-lookup step |
| `Sintesis.md` | §2.6, §2.7, §3.1, §4.2, §10.1 whitelist, §17 |
| `README.md` | Eliminar referencia a 9 orchestrators |
| `ORCHESTRATION_DECISIONS.md` | Documentar migracion a pipeline.yaml |
| `docs/src/skills.md` | Eliminar entradas de orchestrators |

---

## 8. Orden de Implementacion (respetando dependencias)

```
Fase A ─────────────────────────── (sin dependencias — puede empezar)
│ A1: Crear skills/code-simplification-patterns/SKILL.md
│ A2: Fusionar code-simplifier → refactor-cleaner
│ A3: Crear stacks/common/pipeline.yaml
│
Fase B ─────────────────────────── (depende de A)
│ B1: Actualizar 15 stack.yaml (eliminar code-simplifier, add skill)
│ B2: Actualizar 14 pipeline.yaml (code-simplifier → refactor-cleaner + docs-lookup)
│ B3: Actualizar Makefile (copiar pipeline.yaml)
│ B4: Anadir skill_map a compile-agents.py
│
Fase C ─────────────────────────── (depende de B)
│ C1: Eliminar agents/code-simplifier.md
│ C2: Eliminar 9 directorios skills/*-orchestrator/
│ C3: Actualizar documentacion (README, ORCHESTRATION_DECISIONS, docs/src/*)
│
Fase D ─────────────────────────── (depende de A-C)
│ D1: Actualizar workflow-runner skill con routing FAST_PATH
│ D2: Actualizar Sintesis.md (6 secciones)
│
Fase E ─────────────────────────── (verificacion — depende de D)
│ E1: make check (verifica sincronizacion)
│ E2: make dev-stack STACK=laravel (compilacion de prueba)
│ E3: Verificar que /workflow feature funciona con pipeline.yaml
│ E4: Verificar que refactor-cleaner incluye simplificacion
│ E5: Verificar que ningun stack.yaml referencia code-simplifier
│ E6: Verificar que ningun pipeline.yaml referencia code-simplifier
│ E7: Verificar que ningun archivo referencia *-orchestrator (excepto git history)
```

**Paralelismo posible:**
- A1, A2, A3 son independientes → ejecutar en paralelo
- B1, B2, B3, B4 son independientes entre si (pero dependen de A) → ejecutar en paralelo
- C1, C2, C3 son independientes entre si (pero dependen de B) → ejecutar en paralelo

---

## 9. Verificacion End-to-End

### 9.1 Verificacion de integridad

```bash
# Ningun archivo debe referenciar code-simplifier (excepto git history y este plan)
grep -r "code-simplifier" --include="*.yaml" --include="*.md" \
  --exclude="plan-de-integracion.md" --exclude="Sintesis-errores.md" \
  agents/ skills/ stacks/ docs/ rules/
# Esperado: 0 resultados

# Ningun archivo debe referenciar *-orchestrator como skill
grep -r "orchestrator" --include="*.yaml" skills/
# Esperado: 0 resultados (los directorios ya no existen)

# pipeline.yaml debe existir en stacks/common/
test -f stacks/common/pipeline.yaml && echo "OK" || echo "FALTA"

# Compilacion debe funcionar para al menos 3 stacks
make dev-stack STACK=laravel
make dev-stack STACK=python-api
make dev-stack STACK=nextjs-saas
```

### 9.2 Verificacion contra Sintesis.md

| Regla Sintesis | Verificacion |
|---|---|
| §2.1 FAST_PATH | workflow-runner skill contiene seccion de routing con criterios FAST_PATH |
| §2.6 state.yaml | Schema incluye `workflow_active` y `workflow_step` |
| §2.7 Artefactos | pipeline.yaml aparece en el arbol canonico |
| §3.1 Anatomia | pipeline.yaml aparece en la estructura de `.claude/` |
| §4.2 /simplify | Referencia a refactor-cleaner (no code-simplifier) |
| §7.1 Impact | workflow-runner notifica al usuario del workflow seleccionado |
| §10.1 Whitelist | `**/pipeline.yaml` en whitelist de metadatos |
| §17 Setup | pipeline.yaml mencionado en paso 7 |

### 9.3 Verificacion de no-regresion

- `make check` pasa sin errores
- `make list-stacks` muestra todos los stacks sin warnings
- Ningun stack tiene agentes sin compilar despues de `make dev-stack`

---

## 10. Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigacion |
|---|---|---|---|
| refactor-cleaner fusionado demasiado largo | Media | Bajo | Extraer patrones a skill companion |
| Pipeline comun no cubre caso especifico de un stack | Baja | Bajo | Stack override tiene prioridad |
| workflow-runner auto-detecta mal la trivialidad | Media | Medio | Siempre notifica + pide confirmacion |
| Documentacion desactualizada post-eliminacion | Alta | Bajo | Fase C3 cubre actualizacion de docs |
| state.yaml race condition con workflow fields | Baja | Alto | Solo workflow-runner escribe estos campos (CONTRADICCION-4 de Sintesis Pasada 4) |

---

## 11. Notas de Compliance con Sintesis.md

> Checklist final de que ninguna decision viola Sintesis.md.

- [x] §1.1 CLAUDE.md ≤200 lineas — no afectado (cambios son en stack.yaml y pipeline.yaml)
- [x] §1.2 Procedimientos repetitivos = skills — orchestrators eliminados porque eran skills sin uso
- [x] §1.6 Autovalidacion — hooks no cambian, pipeline.yaml respeta gates
- [x] §1.7 No --dangerously-skip-permissions — no aplica
- [x] §1.8 Self-improvement loop — no afectado
- [x] §2.1 State machine — workflow-runner respeta FAST_PATH
- [x] §2.2 Gates — pipeline.yaml en whitelist
- [x] §2.4 Commitment checkpoint — workflows crean PLAN.md → hooks lo validan
- [x] §2.5 Non-goals — no afectado (hooks siguen activos)
- [x] §2.6 state.yaml — actualizado con campos de workflow
- [x] §3.1 Anatomia — actualizada con pipeline.yaml
- [x] §7.1 Skill impact — workflow-runner notifica (medium impact)
- [x] §8 Aislamiento de agentes — no afectado (agents siguen aislados)
- [x] §10 Hooks — no cambian, solo se anade pipeline.yaml a whitelist
- [x] §11 Circuit breakers — workflows locales no los necesitan; routines ya los tienen
- [x] §12 Rollback — no afectado
- [x] §13 Routines — workflows en routines se declaran explicitamente en prompt
- [x] §14 Wiki — no afectado
- [x] §16 "Kill Process" — orchestrators eliminados = latencia eliminada
- [x] §17 Setup — pipeline.yaml incluido en paso 7
