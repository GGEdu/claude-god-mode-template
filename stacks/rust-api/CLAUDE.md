# [NOMBRE DEL PROYECTO]

## Stack
- **Backend**: Rust (stable)
- **Framework**: Axum (o Actix Web)
- **Base de datos**: PostgreSQL + SQLx
- **Tests**: cargo test
- **Linter**: Clippy + rustfmt

## Arquitectura
[DESCRIPCIÓN: API REST, microservicio, CLI, etc.]

## Convenciones
- Commits: Conventional Commits
- Tests: mínimo 80% cobertura (cargo-tarpaulin)
- Error handling: `thiserror` para librería, `anyhow` para app
- Ownership: prefer borrowing, clone solo cuando es necesario

## Comandos críticos
- `/plan` — Antes de implementar cualquier feature
- `/tdd` — Ciclo RED-GREEN-REFACTOR
- `/jedi-review` — Para código crítico

## Estructura del proyecto
```
src/
├── main.rs              ← Entry point + router setup
├── config.rs            ← Environment config
├── routes/              ← Handler functions
├── services/            ← Business logic
├── models/              ← Domain types + DB models
├── repositories/        ← SQLx queries
└── error.rs             ← Error types (thiserror)
tests/
└── integration/         ← Integration tests
migrations/              ← SQLx migrations
```

## Variables de entorno necesarias
- `DATABASE_URL` — postgres://...
- `RUST_LOG` — Nivel de logging (info, debug)
- `PORT` — Puerto del servidor

## Notas del proyecto
[AGREGAR: crates clave, features flags, etc.]
