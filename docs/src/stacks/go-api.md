# Stack: Go API

**Versiones:** Go 1.23+ · stdlib / chi · PostgreSQL 17 · golangci-lint

## Inicializar

```bash
make dev-stack STACK=go-api
```

Activa: reglas Go, slash commands, CLAUDE.md con plantilla.

---

## Slash commands activados

| Comando | Cuándo usarlo |
| --- | --- |
| `/jedi-review` | Para código crítico (3 expertos: Beck, Fowler, Acton) |
| `/git-workflow` | Workflow de commits y PRs |
| `/workflow <nombre>` | Ejecutar pipelines (`feature`, `hotfix`, `refactor`) |
| `/canary-watch URL` | Monitoreo post-deploy en staging/producción |
| `/security-scan` | Auditoría de seguridad de configuración y `.claude/` |
| `/benchmark` | Medir regresiones de rendimiento |
| `/codebase-onboarding` | Generar guía de onboarding del repo |

Además de los comandos anteriores, este stack incluye comandos universales (`/ck`, `/plankton-code-quality`, `/context-budget`, etc.).

Las prácticas `golang-patterns`, `golang-testing`, `api-design`, `database-migrations` y `security-review` se aplican como skills embebidas en los agentes del stack.

---

## Convenciones clave

### Arquitectura — Clean Architecture

```text
cmd/
├── api/
│   └── main.go           ← Entrypoint
internal/
├── handler/              ← HTTP handlers (delgados, solo parse + respuesta)
├── service/              ← Lógica de negocio
├── repository/           ← Acceso a datos
└── domain/               ← Tipos y entidades
pkg/                      ← Código reutilizable/exportable
migrations/               ← Migraciones SQL
```

### Principios fundamentales

- **Accept interfaces, return structs** — los handlers dependen de interfaces, no de implementaciones
- **Errores siempre wrapeados con contexto**: `fmt.Errorf("findUser: %w", err)`
- **Inyección de dependencias** vía constructores, nunca variables globales
- **Functional options** para configuración de structs complejos

### Interfaces pequeñas

Define las interfaces donde se usan (en el consumer), no donde se implementan:

```go
// handler/user.go — interfaz definida aquí, no en service/
type userService interface {
    FindByID(ctx context.Context, id int64) (*domain.User, error)
}
```

### Table-driven tests

```go
func TestFindUser(t *testing.T) {
    tests := []struct {
        name    string
        id      int64
        want    *domain.User
        wantErr bool
    }{
        {"found", 1, &domain.User{ID: 1}, false},
        {"not found", 99, nil, true},
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            // ...
        })
    }
}
```

### Error handling

```go
// CORRECTO: error con contexto acumulado
if err != nil {
    return fmt.Errorf("createOrder: validate: %w", err)
}

// INCORRECTO: error sin contexto
if err != nil {
    return err
}
```

---

## Anti-patrones a evitar

- Lógica de negocio en handlers — mover a `service/`
- `panic` para errores recuperables — retornar `error`
- Variables globales para dependencias — inyección por constructor
- `interface{}` / `any` sin necesidad real
- Goroutines sin control de ciclo de vida (`context.Context`)
- Ignorar errores con `_`

---

## Comandos útiles

```bash
# Desarrollo
go run ./cmd/api

# Tests
go test ./...
go test ./... -race          # detector de race conditions
go test ./... -cover         # cobertura

# Lint
golangci-lint run

# Build
go build -o bin/api ./cmd/api

# Migraciones (con migrate)
migrate -path migrations -database $DATABASE_URL up
migrate -path migrations -database $DATABASE_URL down 1
```

## Variables de entorno

```bash
DATABASE_URL=postgres://user:pass@localhost:5432/dbname?sslmode=disable
PORT=8080
ENV=development
```

---

## Ejemplo completo

→ [CLAUDE.md para Go Microservicio](/examples/go-microservice-CLAUDE)
