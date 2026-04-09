# [NOMBRE DEL PROYECTO]

## Stack
- **Backend**: Go 1.23+
- **Base de datos**: PostgreSQL 17
- **Tests**: go test (table-driven tests)
- **Linter**: golangci-lint

## Arquitectura
[DESCRIPCIÓN: qué hace este servicio, si es API REST, gRPC, microservicio, etc.]

## Convenciones
- Commits: Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`)
- Tests obligatorios: mínimo 80% cobertura
- Accept interfaces, return structs
- Errores siempre wrapeados con contexto: `fmt.Errorf("contexto: %w", err)`

## Comandos críticos
- `/plan` — Antes de implementar cualquier feature
- `/jedi-review` — Para código crítico
- `/tdd` — Ciclo RED-GREEN-REFACTOR
- `/security-scan` — Antes de cada release

## Estructura del proyecto
```
cmd/
├── api/
│   └── main.go           ← Entrypoint
internal/
├── handler/              ← HTTP handlers (delgados)
├── service/              ← Lógica de negocio
├── repository/           ← Acceso a datos
└── domain/               ← Tipos y entidades
pkg/                      ← Código reutilizable
migrations/               ← Migraciones SQL
```

## Variables de entorno necesarias
- `DATABASE_URL` — Conexión PostgreSQL
- `PORT` — Puerto del servidor (default: 8080)
- `ENV` — Entorno (development/production)
