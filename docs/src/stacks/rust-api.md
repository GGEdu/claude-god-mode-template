# Stack: Rust API

**Versiones:** Rust 1.80+ (stable) · Axum / Actix Web · PostgreSQL · SQLx · Clippy · rustfmt

## Inicializar

```bash
make dev-stack STACK=rust-api
```

Activa: reglas Rust, slash commands, CLAUDE.md con plantilla.

---

## Slash commands activados

| Comando | Cuándo usarlo |
| --- | --- |
| `/jedi-review` | Para código crítico — review de 3 expertos en paralelo |
| `/git-workflow` | Si necesitas recordar el workflow de commits y PRs |
| `/workflow-runner <nombre>` | Para ejecutar un pipeline completo: `feature`, `hotfix`, `refactor` |
| `/canary-watch URL` | Post-deploy — monitoreo con Playwright en URLs live |
| `/codebase-onboarding` | Al entrar en un repo nuevo — genera guía de onboarding |
| `/benchmark` | Medir rendimiento antes/después de un PR o cambio |
| `/security-scan` | Escanea `.claude/` por vulnerabilidades |

Las skills `rust-patterns`, `rust-testing`, `api-design`, `security-review` y `database-migrations` se aplican como skills embebidas en los agentes del stack.

---

## Convenciones clave

### Arquitectura — capas explícitas

```text
src/
├── main.rs              ← Entry point, router, dependency wiring
├── config.rs            ← Configuración via environment variables
├── routes/              ← Handlers HTTP (delgados, parse + respuesta)
├── services/            ← Lógica de negocio
├── repositories/        ← Queries SQLx
├── models/              ← Tipos de dominio
└── error.rs             ← Error types con thiserror
tests/
└── integration/         ← Tests de integración
migrations/              ← Migraciones SQLx
```

### Error handling con thiserror

```rust
// src/error.rs
use thiserror::Error;
use axum::http::StatusCode;
use axum::response::{IntoResponse, Response};

#[derive(Error, Debug)]
pub enum AppError {
    #[error("not found")]
    NotFound,
    #[error("unauthorized")]
    Unauthorized,
    #[error("database error: {0}")]
    Database(#[from] sqlx::Error),
}

impl IntoResponse for AppError {
    fn into_response(self) -> Response {
        let status = match &self {
            AppError::NotFound => StatusCode::NOT_FOUND,
            AppError::Unauthorized => StatusCode::UNAUTHORIZED,
            AppError::Database(_) => StatusCode::INTERNAL_SERVER_ERROR,
        };
        (status, self.to_string()).into_response()
    }
}
```

### Handler con Axum

```rust
// src/routes/users.rs
pub async fn get_user(
    State(pool): State<PgPool>,
    Path(id): Path<Uuid>,
) -> Result<Json<User>, AppError> {
    let user = sqlx::query_as!(
        User,
        "SELECT id, email, name FROM users WHERE id = $1",
        id
    )
    .fetch_optional(&pool)
    .await?
    .ok_or(AppError::NotFound)?;

    Ok(Json(user))
}
```

### Tests de integración con SQLx

```rust
#[sqlx::test]
async fn test_create_user(pool: PgPool) {
    let user = create_user(&pool, "alice@example.com", "Alice").await.unwrap();
    assert_eq!(user.email, "alice@example.com");

    let found = find_user_by_id(&pool, user.id).await.unwrap();
    assert_eq!(found.id, user.id);
}
```

### Principios Rust

- **Ownership first**: prefer borrowing (`&T`, `&mut T`), clone solo si es necesario
- **Error propagation**: usar `?` en todo el stack, no `.unwrap()` en producción
- **`thiserror`** para crates/librerías, **`anyhow`** para binarios/scripts
- **`tracing`** para logging, nunca `println!` en producción
- **Estado compartido**: `Arc<T>` para datos inmutables, `Arc<Mutex<T>>` para mutables

---

## Anti-patrones a evitar

- `.unwrap()` o `.expect()` en handlers de producción — retornar `Result`
- `clone()` excesivo para evitar problemas de lifetime — revisar la arquitectura
- Estado global mutable — usar inyección de dependencias via `State<T>`
- Bloqueos síncronos (`std::sync::Mutex`) en código async — usar `tokio::sync::Mutex`
- Queries SQL con interpolación de strings — usar `sqlx::query!` con parámetros

---

## Comandos útiles

```bash
# Desarrollo
cargo run

# Tests
cargo test
cargo test -- --nocapture    # ver output en tests

# Lint
cargo clippy -- -D warnings

# Format
cargo fmt

# Cobertura (con cargo-tarpaulin)
cargo tarpaulin --out Html

# Migraciones (SQLx CLI)
sqlx migrate run
sqlx migrate revert
sqlx migrate add nombre_migracion
```

## Variables de entorno

```bash
DATABASE_URL=postgres://user:pass@localhost:5432/myapp
RUST_LOG=info
PORT=8080
JWT_SECRET=
```
