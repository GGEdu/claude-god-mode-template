# Stack: Laravel 13 + React 19

**Versiones:** Laravel 13 · React 19 · TypeScript · MySQL 8 · Sanctum

## Inicializar

```bash
make dev-stack STACK=laravel-react
```

Activa: reglas Laravel + React, slash commands, CLAUDE.md con plantilla.

---

## Slash commands activados

| Comando | Cuándo usarlo |
| --- | --- |
| `/jedi-review` | Para código crítico (3 expertos: Beck, Fowler, Acton) |
| `/git-workflow` | Workflow de commits y PRs |
| `/workflow <nombre>` | Ejecutar pipelines (`feature`, `hotfix`, `refactor`) |
| `/canary-watch URL` | Monitoreo post-deploy en staging/producción |
| `/security-scan` | Auditoría de seguridad de configuración y `.claude/` |
| `/laravel-plugin-discovery` | Buscar y evaluar plugins de Laravel |
| `/design-md` | Aplicar dirección visual al trabajo de UI |
| `/last30days` | Validar cambios recientes antes de planificar |

Además de los comandos anteriores, este stack incluye los comandos universales (`/ck`, `/plankton-code-quality`, `/context-budget`, etc.) definidos en `commands:` del stack.

Las prácticas como `laravel-patterns`, `laravel-tdd`, `laravel-security`, `frontend-patterns` y `database-migrations` están embebidas en agentes y se aplican automáticamente durante ejecución de `planner`, `tdd-guide`, `security-reviewer`, `typescript-reviewer` y `database-reviewer`.

---

## Convenciones clave

### Backend (Laravel)

- **Controladores delgados**: solo reciben la request, delegan al Service, devuelven Resource
- **Lógica de negocio** → `app/Services/`
- **Validación** → `app/Http/Requests/` (FormRequest), nunca `$request->validate()` inline
- **Respuestas API** → siempre por `app/Http/Resources/`, nunca arrays directos
- **Paginación obligatoria**: `->paginate(15)`, nunca `->get()` sin límite en listados
- **Autenticación**: Sanctum para SPA, nunca JWT manual

### Frontend (React)

- **Data fetching**: SWR o React Query, nunca `useEffect + useState + fetch`
- **Formularios**: React Hook Form + Zod (validación doble: cliente + FormRequest)
- **Estado global**: solo para auth y theme; no sobreuso de Context
- **CSRF**: obtener cookie antes del primer POST: `await api.get('/sanctum/csrf-cookie')`

### Tests

- **Pest** en backend: `tests/Feature/` para endpoints, `tests/Unit/` para Services
- **Vitest + Testing Library** en frontend; mocks de API con MSW
- Cada endpoint: test de éxito, test de validación, test de auth

---

## Anti-patrones a evitar

- `$request->all()` — siempre `$request->validated()`
- Fat controllers (más de 5 métodos o lógica de negocio)
- Queries dentro de bucles — siempre eager loading
- `env()` fuera de archivos de config — usar `config('app.key')`
- `useEffect` para sincronizar estado derivado (calcularlo en render)
- `any` en TypeScript

---

## Comandos útiles

```bash
# Backend
php artisan serve
php artisan test
php artisan migrate
php artisan route:list

# Frontend
npm run dev
npm run test
npm run build
```

---

## Ejemplo completo

→ [Flujo de una feature en Laravel + React](/examples/flujo-feature-laravel-react)
