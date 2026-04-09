---
paths:
  - "**/*.swift"
---
# Swift / SwiftUI — Reglas del stack

## Swift 6.2 Concurrency
- Single-threaded por defecto — todo código es `@MainActor` implícito
- `@concurrent` explícito SOLO para trabajo en background (I/O, cómputo)
- Actors para estado compartido thread-safe
- `async let` para paralelismo, `TaskGroup` para N dinámico

## SwiftUI
- `@Observable` macro (no `ObservableObject`) para ViewModels
- State hoisting: `@Binding` sube estado, closures bajan eventos
- `NavigationStack` con `navigationDestination(for:)` — no NavigationView
- `task {}` para async work en views — se cancela automáticamente
- Lists con `ForEach` + `Identifiable` — no indices manuales

## Persistencia
- SwiftData para modelos locales (reemplaza Core Data)
- Actor-based persistence para thread safety
- `@Query` en views para datos reactivos

## Testing
- Swift Testing framework (`@Test`, `#expect`) — no XCTest para tests nuevos
- Protocol-based DI: definir protocolos para servicios, inyectar mocks
- `@MainActor` en tests que acceden UI state

## Anti-patrones
- Force unwrap (`!`) — usar `guard let` o `if let`
- `DispatchQueue.main.async` — usar `@MainActor`
- Massive ViewModels — extraer lógica a Services
- `AnyView` type erasure — usar `@ViewBuilder` o `some View`
