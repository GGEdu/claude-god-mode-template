# Orchestration Decisions & Architecture (Histórico)

> **Status: SUPERSEDED (2026-04-17)** — Este documento describe una arquitectura previa que fue reemplazada. Se conserva como referencia histórica. La arquitectura actual está en [Sintesis.md §workflow-runner](./Sintesis.md) y [`.claude/pipeline.yaml`](./.claude/pipeline.yaml).

## Resumen del cambio

Antes de 2026-04-17 existían **9 orquestadores de stack**:
`laravel-orchestrator`, `django-orchestrator`, `golang-orchestrator`, `kotlin-orchestrator`, `perl-orchestrator`, `python-orchestrator`, `rust-orchestrator`, `springboot-orchestrator`, `cpp-orchestrator`.

**Eran skills/agents que encadenaban llamadas a otras skills** siguiendo un flujo `tdd → patterns → security → verification` específico de cada stack. Vivían en `skills/<stack>-orchestrator/SKILL.md`.

**Fueron eliminados** en favor de:

| Antes | Ahora |
|---|---|
| Skill `laravel-orchestrator` con flujo embebido | Workflow declarativo en `.claude/pipeline.yaml` |
| Comando `/laravel-orchestrator` | `/workflow-runner feature` (con stack auto-detectado) |
| Lógica de orquestación en cada skill | Lógica genérica en `workflow-runner`, reutilizable |
| Difícil de customizar por proyecto | Cada proyecto edita su `.claude/pipeline.yaml` |

## Razones para el cambio

1. **Duplicación**: 9 orquestadores reproducían el mismo patrón con keywords distintos.
2. **Acoplamiento**: cambiar el flujo requería editar 9 archivos.
3. **Falta de transparencia**: la lógica de orquestación quedaba dentro de la skill, no expuesta al usuario.
4. **Bajo nivel de customización**: por-proyecto era difícil saltar un step o reordenar.

## Decisiones de diseño que se mantienen (rescatadas en pipeline.yaml)

Las siguientes decisiones del sistema antiguo se preservaron al diseñar `pipeline.yaml`:

### 1. Pattern `Test → Audit → Verify`
Siguen siendo el orden canónico. Todo workflow `feature` o `hotfix` empieza con `tdd-guide` antes de cualquier implementación.

### 2. Multi-perspective analysis paralelo
`pipeline.yaml` soporta `parallel_with` para que `code-reviewer` y `security-reviewer` corran a la vez (ver workflow `review`).

### 3. Feedback loop ante fallos de security
`security-reviewer` con flag `block_on_critical: true` (en agente) provoca que workflow-runner aborte y reinicie en `tdd-guide` para añadir tests del vector de ataque.

### 4. Configuración y nombrado
Slash commands ahora viven en `.claude/commands/` (no en skills), y workflows en `.claude/pipeline.yaml`. La convención `<stack>-orchestrator/SKILL.md` ya no aplica.

## Mapeo histórico: orquestador antiguo → workflow nuevo

Estos flujos siguen siendo enforced, ahora vía pipeline.yaml workflows + skills genéricos:

| Stack legacy | Skills antiguos (orquestador) | Equivalente actual |
|---|---|---|
| Laravel | `laravel-tdd → (laravel-patterns & laravel-security) → laravel-verification` | `/workflow-runner feature` con stack=laravel |
| Django | `django-tdd → (django-patterns & django-security) → django-verification` | `/workflow-runner feature` con stack=python-api |
| Spring Boot | `springboot-tdd → (springboot-patterns & springboot-security) → springboot-verification` | `/workflow-runner feature` con stack=java-springboot |
| Kotlin | `kotlin-testing → (kotlin-patterns & kotlin-coroutines-flows)` | `/workflow-runner feature` con stack=kotlin-multiplatform |
| Python | `python-testing → python-patterns` | `/workflow-runner feature` con stack=python-api |
| Go | `golang-testing → golang-patterns` | `/workflow-runner feature` con stack=go-api |
| Rust | `rust-testing → rust-patterns` | `/workflow-runner feature` con stack=rust-api |
| C++ | `cpp-testing → cpp-coding-standards` | `/workflow-runner feature` con stack=cpp |
| Perl | `perl-testing → (perl-patterns & perl-security)` | `/workflow-runner feature` con stack=perl |

## ¿Quién enforce el flujo ahora?

**workflow-runner** (skill en `.claude/commands/workflow-runner.md`) lee `.claude/pipeline.yaml`, valida que cada `agent` y `skill` referenciado existe, y ejecuta los steps en orden respetando `parallel_with`, `always`, `continue_on_failure` (ver gramática completa en [`.claude/pipeline.schema.yaml`](./.claude/pipeline.schema.yaml)).

Los hooks (`plan-gate.py`, `tdd-gate.py`, `commit-checklist.py`, `non-goal-guard.py`) actúan como *guardias programáticas* que enforce las invariantes incluso si el usuario salta el workflow. Ver [Sintesis.md §2](./Sintesis.md#2-máquina-de-estados-para-operación-autónoma).

## Lecciones aprendidas

1. **Orquestación por convención > por código**: declarativo (YAML) bate imperativo (skill que encadena llamadas).
2. **Genericidad > especificidad por stack**: 1 workflow-runner que lee config supera a 9 orquestadores hardcoded.
3. **Visibilidad > opacidad**: el usuario debe poder leer y editar el flujo en un YAML, no descifrarlo de un prompt embebido en una skill.
4. **Skills delgadas, workflows gordos**: cada skill (`tdd-guide`, `code-reviewer`) hace una cosa. La composición vive en pipeline.yaml.
