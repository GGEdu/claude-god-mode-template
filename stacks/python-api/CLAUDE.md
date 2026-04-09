# [NOMBRE DEL PROYECTO]

## Stack
- **Backend**: [Django 5 + Django REST Framework / FastAPI]
- **Base de datos**: PostgreSQL 15
- **Tests**: pytest + pytest-django
- **Linter**: Ruff
- **Containerización**: Docker + Docker Compose

## Arquitectura
[DESCRIPCIÓN: qué hace esta API, quién la consume, si es microservicio o monolito]

## Convenciones
- Commits: Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`)
- Tests obligatorios: mínimo 80% cobertura
- ViewSets/routers delgados — lógica en Services
- Type hints obligatorios en todo código nuevo
- Validación en serializers/schemas, nunca en vistas

## Comandos críticos
- `/plan` — Antes de implementar cualquier feature o endpoint
- `/jedi-review` — Para código crítico
- `/tdd` — Ciclo RED-GREEN-REFACTOR
- `/security-scan` — Antes de cada release

## Estructura del proyecto
```
config/
├── settings/           ← base.py, development.py, production.py
└── urls.py

apps/
└── mi_app/
    ├── models.py
    ├── serializers.py
    ├── views.py        ← ViewSets delgados
    ├── services.py     ← Lógica de negocio
    └── tests/
```

## Variables de entorno necesarias
- `DATABASE_URL` — Conexión PostgreSQL
- `SECRET_KEY` — Django secret key
- `DEBUG` — False en producción
- `ALLOWED_HOSTS` — Lista de hosts permitidos

## Notas del proyecto
[PLACEHOLDER: autenticación usada (JWT/Session/OAuth), rate limiting, versionado de API]
