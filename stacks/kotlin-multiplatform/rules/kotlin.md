---
paths:
  - "**/*.kt"
  - "**/*.kts"
---
# Kotlin — Reglas del stack

## Idioms
- Data classes para DTOs, sealed classes para estados
- Extension functions para utilidades — no utility classes
- `when` exhaustivo: siempre cubrir todos los casos (sealed)
- Scope functions: `let` para null check, `apply` para builder, `also` para side effects

## Coroutines
- NUNCA `GlobalScope` — usar structured concurrency con CoroutineScope
- `Flow` para streams de datos — `StateFlow` para estado en UI
- `withContext(Dispatchers.IO)` para I/O, nunca bloquear el Main
- `supervisorScope` cuando los hijos pueden fallar independientemente

## Ktor (backend)
- Routing DSL con `route {}` — handlers delgados, delegar a services
- Serialización con `kotlinx.serialization` — no Jackson
- Content negotiation configurado globalmente
- Auth con plugins de Ktor — no middlewares manuales

## Anti-patrones
- `var` donde `val` basta — preferir inmutabilidad
- `!!` (non-null assertion) — usar `?.let {}` o `requireNotNull()`
- Callbacks anidados — usar coroutines/Flow
- Platform types sin anotación — anotar nullability en boundaries Java
