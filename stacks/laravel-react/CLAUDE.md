# [NOMBRE DEL PROYECTO]

## Stack
- **Backend**: Laravel 13 (API REST)
- **Frontend**: React 19 + TypeScript (SPA)
- **Base de datos**: MySQL 8
- **Auth**: Sanctum (tokens SPA)
- **Tests backend**: Pest
- **Tests frontend**: Vitest + Testing Library
- **Linter backend**: Pint
- **Linter frontend**: Biome

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

src/
├── components/         ← Componentes React
├── hooks/              ← Hooks customizados
├── services/           ← Clientes API
└── contexts/           ← Estado global (auth, theme)
```

## Variables de entorno necesarias
- `APP_URL` — URL del backend Laravel
- `VITE_API_URL` — URL para el frontend React
- `DB_*` — Credenciales de base de datos
