---
paths:
  - "**/*.rs"
  - "**/Cargo.toml"
---
# Rust — Reglas del stack

## Ownership y borrowing
- Prefer `&self` y `&str` sobre owned types en parámetros
- `Clone` solo cuando hay razón clara — documentar por qué
- `Cow<'_, str>` cuando el caller puede dar owned o borrowed
- Lifetime elision: no anotar lifetimes innecesarios

## Error handling
- `thiserror` para error types en librerías
- `anyhow::Result` para application-level errors
- `?` operator — nunca `.unwrap()` en producción
- Errores con contexto: `.context("descripción")` (anyhow)

## Async
- Tokio como runtime estándar
- `#[tokio::main]` en main, `#[tokio::test]` en tests
- `Send + Sync` bounds explícitos en traits async
- Evitar `.await` en loops — usar `futures::stream` o `join_all`

## Testing
- `#[cfg(test)]` para unit tests en el mismo archivo
- `tests/` para integration tests
- `proptest` o `quickcheck` para property-based testing
- Mocks con `mockall` — traits para inyección de dependencias

## Anti-patrones
- `.unwrap()` / `.expect()` en prod — usar `?`
- `unsafe` sin documentar invariantes
- `String` donde `&str` basta
- `Arc<Mutex<>>` donde un channel sería más claro
