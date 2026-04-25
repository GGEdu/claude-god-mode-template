---
name: tdd
description: Ciclo Test-Driven Development RED→GREEN→REFACTOR — invoca el agente `tdd-guide` para escribir tests primero, ver fallar, implementar mínimo y refactorizar.
---

# /tdd — Ciclo Test-Driven Development

Usa este comando para implementar features siguiendo TDD estricto. Aplica los 3 pasos:
1. **RED** — escribir test que falla.
2. **GREEN** — implementar lo mínimo para que pase.
3. **REFACTOR** — limpiar sin romper tests.

## Qué hace

1. Invoca el agente `tdd-guide` con el contexto de la tarea actual.
2. El agente:
   - Identifica el comportamiento a testear desde el PLAN.md (si existe) o desde la conversación.
   - Escribe un test que **falla** y lo ejecuta para confirmar el fallo (paso RED).
   - Implementa el código mínimo para que el test pase (paso GREEN).
   - Refactoriza preservando la suite verde (paso REFACTOR).
   - Verifica cobertura ≥ 80% antes de cerrar.
3. Cumple con `tdd-gate.py` (PreToolUse hook) que verifica existencia de tests antes de permitir escribir código de implementación.

## Cuándo usarlo

- Feature nueva — siempre escribir test primero.
- Bug fix — escribir test que reproduce el bug, después fixearlo (test = regression check).
- Refactor con cambio de comportamiento — tests previos garantizan que no rompiste nada.

## Cuándo NO usarlo

- Solo escribiendo docs o markdown.
- Configuración pura (`.json`, `.yaml`, `.env.example`) sin lógica.
- Migraciones de schema sin lógica de datos (ya hay validación a nivel DB).

## Frameworks soportados (auto-detectados por stack)

| Stack | Framework | Comando run-test |
|---|---|---|
| Laravel / PHP | Pest, PHPUnit | `./vendor/bin/pest` |
| Python | pytest | `python -m pytest` |
| TypeScript / Next.js | Jest, Vitest | `npm run test` |
| Go | testing | `go test ./...` |
| Rust | cargo test | `cargo test` |
| Java | JUnit | `./gradlew test` |
| Kotlin | JUnit | `./gradlew test` |
| Flutter | flutter_test | `flutter test` |

## Cobertura mínima

- **80%** sobre código modificado (rule global, ver `~/.claude/rules/common/testing.md`).
- Para auth/security/payments: **95%** (rule security, ver `~/.claude/rules/common/security.md`).

## Relación con otros comandos

- `/plan` — ejecutar antes para tener PLAN.md con `tests_required` y `acceptance_criteria` claros.
- `/workflow-runner feature` — ejecuta TDD como uno de los pasos del pipeline.
- `/jedi-review` — revisión post-TDD para validar calidad de tests (no triviales, cubren acceptance criteria).
