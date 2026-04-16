# Stack: Laravel

**Versiones:** Laravel 13 · PHP 8.3 · MySQL 8 · Sanctum · Pest

## Inicializar

```bash
make dev-stack STACK=laravel
```

Para proyectos full-stack con React:

```bash
make dev-stack STACK=laravel LAYERS=react
```

Activa: reglas Laravel, slash commands, CLAUDE.md con plantilla.

---

## Slash commands activados

| Comando | Cuándo usarlo |
| --- | --- |
| `/jedi-review` | Para código crítico (3 expertos: Beck, Fowler, Acton) |
| `/git-workflow` | Workflow de commits y PRs |
| `/workflow-runner <nombre>` | Ejecutar pipelines (`feature`, `hotfix`, `refactor`) |
| `/canary-watch URL` | Monitoreo post-deploy en staging/producción |
| `/security-scan` | Auditoría de seguridad de configuración y `.claude/` |
| `/laravel-plugin-discovery` | Buscar y evaluar paquetes Laravel vía LaraPlugins.io |
| `/last30days` | Validar conocimiento reciente sobre librerías antes de planificar |
| `/codebase-onboarding` | Generar guía de onboarding del repo |

Las prácticas `laravel-patterns`, `laravel-testing`, `api-design`, `security-review` y `database-migrations` se aplican como skills embebidas en los agentes del stack.

---

## Convenciones clave

### Arquitectura — Controladores delgados

```text
app/
├── Http/
│   ├── Controllers/         ← Delgados: solo reciben request, delegan, retornan response
│   ├── Requests/            ← Validación con FormRequest
│   └── Resources/           ← Transformación de respuestas API
├── Services/                ← Lógica de negocio
├── Models/                  ← Eloquent models con relaciones
├── Policies/                ← Autorización (Laravel Gate/Policy)
├── Jobs/                    ← Tareas asincrónicas (colas)
├── Exceptions/              ← Excepciones custom
└── Providers/               ← Service providers (IoC container)
routes/
├── api.php                  ← Rutas REST con middleware
└── web.php                  ← Rutas web (si aplica)
tests/
├── Feature/                 ← Tests de endpoints (con base de datos real)
└── Unit/                    ← Tests de Services/helpers aislados
```

### Controlador — Ejemplo correcto

```php
// CORRECTO: controlador delgado
class UserController extends Controller
{
    public function __construct(private UserService $service) {}

    public function store(CreateUserRequest $request)
    {
        $user = $this->service->createUser($request->validated());
        return new UserResource($user);
    }
}

// INCORRECTO: lógica de negocio en el controlador
class UserController extends Controller
{
    public function store(Request $request)
    {
        $validated = $request->validate([...]);
        // Lógica de negocio aquí → MOVER A SERVICE
        $user = User::create($validated);
        return response()->json($user);
    }
}
```

### Validación — FormRequest

```php
// app/Http/Requests/CreateUserRequest.php
class CreateUserRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'email' => 'required|email|unique:users',
            'name' => 'required|string|max:255',
            'role' => 'required|in:user,admin',
        ];
    }
}

// En el controlador: $validated = $request->validated();
// NUNCA: $request->all()
```

### Service — Lógica de negocio

```php
// app/Services/UserService.php
class UserService
{
    public function __construct(private UserRepository $repo) {}

    public function createUser(array $data): User
    {
        // Validar reglas de negocio
        if ($this->emailBlacklisted($data['email'])) {
            throw new DomainException('Email no permitido');
        }

        // Transacción si múltiples tablas
        return DB::transaction(fn() => 
            $this->repo->create($data)
        );
    }
}
```

### Eloquent — Eager loading obligatorio

```php
// CORRECTO: eager loading
$users = User::with('roles', 'permissions')->get();

// INCORRECTO: N+1 queries (lazy loading)
$users = User::all();
foreach ($users as $user) {
    echo $user->roles; // Query por cada usuario
}

// Scopes para condiciones reutilizables
class User extends Model
{
    public function scopeActive($query)
    {
        return $query->where('active', true);
    }

    public function scopeRecent($query)
    {
        return $query->orderBy('created_at', 'desc');
    }
}

// Uso: User::active()->recent()->get();
```

### API REST — Códigos HTTP y paginación

```php
// Creación → 201
return response()->json($resource, 201);

// Validación fallida → 422
return response()->json(['errors' => ...], 422);

// No encontrado → 404
return response()->json(['message' => 'Not found'], 404);

// Paginación obligatoria en listados
public function index()
{
    $users = User::with('roles')
        ->paginate(15); // NUNCA ->get()
    return UserResource::collection($users);
}
```

### Testing — Pest con RefreshDatabase

```php
// tests/Feature/UserControllerTest.php
use Pest\Laravel\RefreshDatabase;

beforeEach(fn() => $this->user = User::factory()->create());

test('create user returns 201', function () {
    $response = $this->post('/api/users', [
        'email' => 'test@example.com',
        'name' => 'Test User',
    ]);

    $response->assertStatus(201);
    $this->assertDatabaseHas('users', ['email' => 'test@example.com']);
});

test('create user with invalid email returns 422', function () {
    $response = $this->post('/api/users', [
        'email' => 'invalid',
    ]);

    $response->assertStatus(422);
});
```

---

## Anti-patrones a evitar

- **Fat controllers** — más de 5 métodos o lógica de negocio dentro
- **`$request->all()`** — siempre `$request->validated()`
- **Queries dentro de bucles** — siempre eager loading con `with()`
- **`env()` fuera de config** — usar `config('app.key')` en el código
- **Lógica de auth en controlador** — mover a Policy o Gate
- **Middleware de autenticación missing** — siempre `auth:sanctum` en rutas protegidas
- **Sin transacciones en operaciones multi-tabla** — usar `DB::transaction()`

---

## Comandos útiles

```bash
# Desarrollo
php artisan serve

# Tests
php artisan test --coverage
php artisan test tests/Feature/UserControllerTest.php

# Linting y formato
./vendor/bin/pint

# Migraciones
php artisan migrate
php artisan migrate:rollback
php artisan tinker

# Generar código
php artisan make:model User -mcr  # Model + migration + controller
php artisan make:request CreateUserRequest
php artisan make:resource UserResource
php artisan make:policy UserPolicy
```

## Variables de entorno

```bash
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=laravel_db
DB_USERNAME=root
DB_PASSWORD=

APP_KEY=base64:...
APP_URL=http://localhost:8000

SANCTUM_STATEFUL_DOMAINS=localhost:3000,localhost:8000
SESSION_DOMAIN=localhost
```

---

## Ejemplo completo

→ [CLAUDE.md para Laravel API](/examples/laravel-api-CLAUDE)
