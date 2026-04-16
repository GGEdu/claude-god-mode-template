# Laravel — Reglas del stack

## Arquitectura

- Controladores DELGADOS: solo reciben la request, delegan a un Service, devuelven la response
- Lógica de negocio en `app/Services/` — nunca en el controlador
- Validación en `app/Http/Requests/` (FormRequest) — nunca inline con `$request->validate()`
- Políticas de autorización en `app/Policies/` — nunca lógica de auth en el controlador

## Eloquent y base de datos

- SIEMPRE eager loading para relaciones: `User::with('roles')->get()`, nunca lazy
- Usar query scopes para condiciones reutilizables: `User::active()->recent()->get()`
- Transacciones para operaciones que modifican múltiples tablas: `DB::transaction()`
- Factories para todos los modelos — los tests los requieren

## API REST

- Respuestas siempre a través de API Resources (`app/Http/Resources/`)
- Paginación obligatoria en listados: `->paginate(15)`, nunca `->get()` sin límite
- Códigos HTTP correctos: 201 para create, 422 para validación, 404 para not found
- Rate limiting en rutas de auth: `throttle:5,1`

## Autenticación

- Usar Sanctum para SPA — nunca JWT manual
- CORS configurado con `allowed_origins` específico, nunca `'*'` en producción
- Tokens de API con nombres descriptivos: `$user->createToken('spa-web')`

## Testing (Pest)

- Tests en `tests/Feature/` para endpoints completos (con base de datos real)
- Tests en `tests/Unit/` para Services y helpers aislados
- Usar `RefreshDatabase` en Feature tests
- Cada endpoint tiene al menos: test de éxito, test de validación, test de auth

## Anti-patrones a evitar

- Fat controllers (más de 5 métodos o lógica de negocio)
- `$request->all()` — siempre `$request->validated()`
- Queries dentro de bucles — siempre eager loading o colecciones
- `env()` fuera de archivos de config — usar `config('app.key')` en el código
