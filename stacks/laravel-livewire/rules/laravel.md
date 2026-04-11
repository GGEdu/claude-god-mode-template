# Laravel — Reglas del stack

## Arquitectura

- Controladores DELGADOS: solo reciben la request, delegan a un Service, devuelven la response
- Lógica de negocio en `app/Services/` — nunca en el controlador ni en el componente Livewire
- Validación en `app/Http/Requests/` (FormRequest) para controladores, o `#[Validate]` para Livewire
- Políticas de autorización en `app/Policies/` — nunca lógica de auth en el controlador

## Eloquent y base de datos

- SIEMPRE eager loading para relaciones: `User::with('roles')->get()`, nunca lazy
- Usar query scopes para condiciones reutilizables: `Log::active()->bySeverity('critical')->get()`
- Transacciones para operaciones que modifican múltiples tablas: `DB::transaction()`
- Factories para todos los modelos — los tests los requieren

## Respuestas web (monolito Livewire)

- No se usan API Resources — las responses son Blade views o datos pasados a `render()`
- Paginación obligatoria en listados: `->paginate(25)`, nunca `->get()` sin límite
- Redirecciones con `redirect()->route()` desde controladores; en Livewire usar `$this->redirectRoute()`

## Autenticación

- Laravel Auth integrado (sesión + cookies) — no Sanctum salvo que se añada una API REST
- Gates y Policies para autorización: `$this->authorize('update', $log)` en el componente Livewire
- Middleware `auth` en rutas protegidas

## Testing (Pest)

- Tests en `tests/Feature/` para flujos completos (con base de datos real)
- Tests en `tests/Unit/` para Services y helpers aislados
- Componentes Livewire se testean con `Livewire::test()` — ver skill `livewire-patterns`
- Usar `RefreshDatabase` en Feature tests
- Cada componente crítico tiene al menos: test de render, test de interacción, test de validación

## Anti-patrones a evitar

- Fat controllers o fat Livewire components (lógica de negocio en ellos)
- `$request->all()` — siempre `$request->validated()`
- Queries dentro de bucles — siempre eager loading o colecciones
- `env()` fuera de archivos de config — usar `config('app.key')` en el código
- Propiedades Livewire con datos sensibles (son serializadas al cliente)
