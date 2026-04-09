# [NOMBRE DEL PROYECTO]

## Stack
- **Lenguaje**: Perl 5.36+
- **Framework**: Mojolicious (o Dancer2)
- **Base de datos**: PostgreSQL + DBI
- **Tests**: Test2::V0 + prove
- **Linter**: Perl::Critic

## Arquitectura
[DESCRIPCIÓN: web app, API, CLI tool, etc.]

## Convenciones
- Commits: Conventional Commits
- Tests: mínimo 80% cobertura (Devel::Cover)
- `use strict; use warnings;` siempre (implícito en 5.36+)
- Subroutine signatures habilitadas

## Comandos críticos
- `/plan` — Antes de implementar cualquier feature
- `/tdd` — Ciclo RED-GREEN-REFACTOR

## Estructura del proyecto
```
lib/
└── MyApp/
    ├── Controller/      ← Route handlers
    ├── Model/           ← Business logic
    └── Schema/          ← DBIx::Class schemas
t/
├── unit/               ← Unit tests
└── integration/        ← Integration tests
script/                 ← Entry points
```

## Notas del proyecto
[AGREGAR: módulos CPAN clave, configuración, etc.]
