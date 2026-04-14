# [NOMBRE DEL PROYECTO]

## Stack
- **Backend**: Laravel 13 (API REST)
- **Base de datos**: MySQL 8
- **Auth**: Sanctum (tokens SPA)
- **Tests**: Pest
- **Linter**: Pint

## Arquitectura
[DESCRIPCIÓN BREVE: qué hace este proyecto y cómo se organiza]

## Convenciones
- Commits: Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`)
- Tests obligatorios: mínimo 80% cobertura
- Controladores delgados — lógica en Services
- API Resources para todas las respuestas

## Comandos críticos
- `/plan` — Antes de implementar cualquier feature
- `/jedi-review` — Para código que importa
- `/tdd` — Ciclo RED-GREEN-REFACTOR
- `/security-scan` — Antes de cada release

## Estructura del proyecto
```
app/
├── Http/
│   ├── Controllers/    ← Delgados, solo routing
│   ├── Requests/       ← Validación (FormRequest)
│   └── Resources/      ← Formato de respuestas API
├── Services/           ← Lógica de negocio
└── Models/
```

## Variables de entorno necesarias
- `APP_URL` — URL del backend
- `DB_*` — Credenciales de base de datos
