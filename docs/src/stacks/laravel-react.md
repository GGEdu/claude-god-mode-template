# Stack: Laravel + React (composición)

> **Nota:** `laravel-react` ya no existe como stack combinado. Fue reemplazado por la composición `STACK=laravel LAYERS=react`, que permite combinar Laravel con cualquier stack frontend de forma independiente.

---

## Inicializar

```bash
# Laravel puro (API backend)
make init-project STACK=laravel PROJECT=/ruta

# Laravel + React SPA
make init-project STACK=laravel LAYERS=react PROJECT=/ruta

# Laravel + React + dominio vertical
make init-project STACK=laravel LAYERS=react DOMAIN=healthcare PROJECT=/ruta
```

---

## ¿Qué cambia con los layers?

- **`STACK=laravel`** activa: reglas Laravel, agentes compilados con skills de backend (laravel-patterns, laravel-tdd, laravel-security, database-migrations)
- **`LAYERS=react`** añade encima: reglas React/TypeScript, agente `typescript-reviewer` con skills frontend (frontend-patterns, coding-standards, design-system), skill `e2e-testing` en e2e-runner, skill `api-design` en architect, comando `/design-md`

La separación en layers permite combinar cualquier backend con React sin crear stacks combinados:

```bash
make init-project STACK=python-api LAYERS=react PROJECT=/ruta
make init-project STACK=go-api LAYERS=react PROJECT=/ruta
```

---

## Slash commands activados (laravel + react)

| Comando | Origen | Cuándo usarlo |
| --- | --- | --- |
| `/jedi-review` | stack | Para código crítico (3 expertos: Beck, Fowler, Acton) |
| `/git-workflow` | stack | Workflow de commits y PRs |
| `/workflow <nombre>` | stack | Ejecutar pipelines (`feature`, `hotfix`, `refactor`) |
| `/canary-watch URL` | stack | Monitoreo post-deploy en staging/producción |
| `/security-scan` | stack | Auditoría de seguridad de configuración y `.claude/` |
| `/laravel-plugin-discovery` | stack | Buscar y evaluar plugins de Laravel |
| `/design-md` | layer react | Aplicar dirección visual al trabajo de UI |
| `/last30days` | stack | Validar cambios recientes antes de planificar |

---

## Convenciones clave

### Backend (Laravel)

- **Controladores delgados**: solo reciben la request, delegan al Service, devuelven Resource
- **Lógica de negocio** → `app/Services/`
- **Validación** → `app/Http/Requests/` (FormRequest), nunca `$request->validate()` inline
- **Respuestas API** → siempre por `app/Http/Resources/`, nunca arrays directos
- **Paginación obligatoria**: `->paginate(15)`, nunca `->get()` sin límite en listados
- **Autenticación**: Sanctum para SPA, nunca JWT manual

### Frontend (React — activo con LAYERS=react)

- **Data fetching**: SWR o React Query, nunca `useEffect + useState + fetch`
- **Formularios**: React Hook Form + Zod (validación doble: cliente + FormRequest)
- **Estado global**: solo para auth y theme; no sobreuso de Context
- **CSRF**: obtener cookie antes del primer POST: `await api.get('/sanctum/csrf-cookie')`

---

## Referencias

- [Documentación del layer React](/estructura/layers)
- [Documentación del stack Laravel](/estructura/stacks)
- [Flujo de una feature completo](/examples/flujo-feature-laravel-react)
- [Tutorial paso a paso](/examples/tutorial-laravel-react)
