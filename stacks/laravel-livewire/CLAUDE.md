# [NOMBRE DEL PROYECTO]

## Stack
- **Backend**: Laravel 12 (monolito, server-side rendering)
- **Frontend**: Livewire 4 + Alpine.js + TailwindCSS (sin React/TypeScript)
- **Base de datos**: PostgreSQL 17
- **Auth**: Laravel Auth (Breeze/Jetstream o manual)
- **Tests**: Pest
- **Linter**: Pint

## Arquitectura
[DESCRIPCIÓN BREVE: qué hace este proyecto y cómo se organiza]

Usa el patrón **Repository** para acceso a datos y **Services** para lógica de negocio. Los controladores son delgados. Los componentes Livewire orquestan la UI reactiva sin necesitar JavaScript manual.

## Modelos principales
[LISTA DE MODELOS: Ej. User, Article, Comment...]

## Convenciones
- Commits: Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`)
- Tests obligatorios: mínimo 80% cobertura con Pest
- Controladores delgados — lógica en Services (`app/Services/`)
- Acceso a datos en Repositories (`app/Repositories/`) — opcional según complejidad
- Livewire components en `app/Livewire/` para la UI reactiva
- **No hay frontend React ni TypeScript** — ignorar reglas de typescript-reviewer

## Comandos críticos
- `/plan` — Antes de implementar cualquier feature
- `/jedi-review` — Para código que importa
- `/tdd` — Ciclo RED-GREEN-REFACTOR con Pest
- `/security-scan` — Antes de cada release
- `/workflow feature` — Pipeline completo de desarrollo

## Estructura del proyecto
```
app/
├── Http/
│   ├── Controllers/    ← Delgados, solo routing (cuando no se usa Livewire)
│   ├── Middleware/     ← Middleware personalizado
│   └── Livewire/       ← Componentes Livewire (alias de app/Livewire/)
├── Livewire/           ← Componentes Livewire
├── Models/             ← Modelos Eloquent
├── Services/           ← Lógica de negocio
├── Repositories/       ← Acceso a datos (si se usa Repository pattern)
├── Policies/           ← Autorización
└── Rules/              ← Validaciones custom

resources/views/
├── components/         ← Blade components reutilizables
├── layouts/            ← Layouts de la app
└── livewire/           ← Views de componentes Livewire

routes/web.php          ← Solo rutas web
```

## Variables de entorno necesarias
- `APP_URL` — URL local de la app
- `DB_*` — Credenciales de PostgreSQL
- Ver `.env.example` para lista completa
