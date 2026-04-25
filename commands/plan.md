---
name: plan
description: Crea un plan de implementación estructurado antes de codificar — invoca el agente `planner` y genera un PLAN.md alineado con el schema de Sintesis.md §2.3.
---

# /plan — Crear plan estructurado de implementación

Usa este comando antes de implementar cualquier feature no trivial (más de 3 archivos o más de 50 líneas, o que toque auth/security/payments — ver criterios FAST_PATH/FULL_PATH en Sintesis.md §2.1).

## Qué hace

1. Invoca el agente `planner` con el contexto de la conversación actual.
2. El agente:
   - Explora el codebase relevante (Read/Grep/Glob).
   - Identifica dependencias, patrones existentes, archivos a modificar.
   - Genera un PLAN.md siguiendo el schema obligatorio de Sintesis.md §2.3:
     - `plan_id`, `status`, `approach`, `files_affected`, `non_goals`, `acceptance_criteria`, `tests_required`, `rollback_tag`
3. Guarda el plan en `.claude/plans/PLAN.md` (ubicación canónica).
4. El plan pasa por GATE-1 (validación de exploración previa) y queda disponible para GATE-2 antes de cualquier Write/Edit.

## Cuándo usarlo

- Feature nueva con más de 3 archivos afectados.
- Cualquier cambio en auth, payments, security, admin.
- Refactoring que toca múltiples módulos.
- Antes de iniciar el workflow `/workflow-runner feature`.

## Cuándo NO usarlo

- Bug fix de 1-3 archivos sin lógica nueva (FAST_PATH).
- Cambios solo de docs o tests sin código de producción.
- Edits triviales (typos, formato, renombre).

## Ejemplo de uso

```
/plan implementar autenticación OAuth con Google
```

El comando lanza el agente `planner` que produce un PLAN.md como:

```yaml
plan_id: plan-2026-04-25-001
status: draft
approach: "OAuth con Google vía Laravel Socialite"
files_affected:
  - path: "app/Http/Controllers/Auth/GoogleController.php"
    action: create
    reason: "Endpoint de callback OAuth"
  - path: "config/services.php"
    action: modify
    reason: "Registrar credenciales Google"
non_goals:
  - pattern: "**/admin/**"
    reason: "OAuth solo para usuarios end-user, no admin"
acceptance_criteria:
  - "Test E2E: login con cuenta Google funciona"
  - "Tests unitarios: GoogleController dispatcha eventos correctos"
tests_required:
  - "tests/Feature/Auth/GoogleAuthTest.php"
rollback_tag: "pre-plan-2026-04-25-001"
```

## Relación con otros comandos

- `/workflow-runner feature` — ejecuta pipeline completo (planner → tdd-guide → code-reviewer → security-reviewer).
- `/jedi-review` — revisión profunda tras implementar.
- `/tdd` — escribir tests primero (RED→GREEN→REFACTOR).
