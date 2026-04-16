# Stack: Laravel + Livewire

**Versiones:** Laravel 12 · PHP 8.2 · Livewire 4 · Alpine.js · TailwindCSS · PostgreSQL

## Inicializar

```bash
make dev-stack STACK=laravel-livewire
```

Activa: reglas Livewire, slash commands, CLAUDE.md con plantilla.

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

Las prácticas `livewire-patterns`, `blade-conventions`, `alpine-reactivity`, `security-review` y `database-migrations` se aplican como skills embebidas en los agentes del stack.

---

## Convenciones clave

### Arquitectura — Monolito Blade + Livewire

Sin SPA separada. Todo vive en Laravel:

```text
app/
├── Livewire/                ← Componentes Livewire (interactividad)
│   ├── UserList.php         ← Componente con estado reactivo
│   ├── UserForm.php         ← Formulario con validación en vivo
│   └── Modals/              ← Modales interactivos
├── Http/Controllers/        ← Controllers solo para rutas no-Livewire
├── Services/                ← Lógica de negocio
├── Models/                  ← Eloquent models
└── Providers/
resources/views/
├── components/              ← Componentes Blade reutilizables
├── livewire/                ← Vistas Blade para componentes Livewire
└── layouts/                 ← Layouts base
```

### Componente Livewire — Ejemplo

```php
// app/Livewire/UserList.php
use Livewire\Component;
use Livewire\Attributes\Validate;
use App\Models\User;

class UserList extends Component
{
    #[Validate('required|email|unique:users,email')]
    public string $email = '';

    #[Validate('required|string|max:255')]
    public string $name = '';

    public function save()
    {
        $this->validate();

        User::create([
            'email' => $this->email,
            'name' => $this->name,
        ]);

        // Reset después de crear
        $this->reset('email', 'name');
        $this->dispatch('user-created');
    }

    public function render()
    {
        $users = User::all();
        return view('livewire.user-list', ['users' => $users]);
    }
}
```

### Vista Blade para Livewire

```blade
<!-- resources/views/livewire/user-list.blade.php -->
<div class="space-y-4">
    <form wire:submit.prevent="save" class="bg-white p-6 rounded">
        <div>
            <label>Email</label>
            <input type="email" wire:model="email" class="form-input" />
            @error('email') <span class="error">{{ $message }}</span> @enderror
        </div>

        <div>
            <label>Name</label>
            <input type="text" wire:model="name" class="form-input" />
            @error('name') <span class="error">{{ $message }}</span> @enderror
        </div>

        <button type="submit" class="btn-primary">Create User</button>
    </form>

    <div class="space-y-2">
        @foreach ($users as $user)
            <div class="p-4 bg-gray-50 rounded">
                {{ $user->name }} ({{ $user->email }})
            </div>
        @endforeach
    </div>
</div>
```

### Reactividad con wire:model y debounce

```blade
<!-- Sin debounce: query en cada keystroke (caro) -->
<input type="text" wire:model="search" />

<!-- Con debounce: espera 500ms sin cambios antes de actualizar -->
<input type="text" wire:model.debounce-500ms="search" />

<!-- Lazy: solo actualiza cuando pierda el foco -->
<input type="text" wire:model.lazy="search" />
```

### Alpine.js para interacciones ligeras

```blade
<!-- Alpine es suficiente para UI local; Livewire para estado global -->
<div x-data="{ open: false }">
    <button @click="open = !open">Toggle</button>
    
    <div x-show="open" class="mt-4">
        Contenido visible solo localmente
    </div>
</div>
```

### Testing Livewire

```php
// tests/Livewire/UserListTest.php
use Livewire\Livewire;
use Tests\TestCase;

class UserListTest extends TestCase
{
    use RefreshDatabase;

    test('can create user from livewire component', function () {
        Livewire::test(UserList::class)
            ->set('email', 'test@example.com')
            ->set('name', 'Test User')
            ->call('save')
            ->assertDispached('user-created');

        $this->assertDatabaseHas('users', [
            'email' => 'test@example.com',
        ]);
    });

    test('validation errors show inline', function () {
        Livewire::test(UserList::class)
            ->set('email', 'invalid')
            ->call('save')
            ->assertHasErrors('email');
    });
}
```

---

## Anti-patrones a evitar

- **Lógica de UI pesada en JavaScript** — Alpine es suficiente, si necesitas más, reconsidera la arquitectura
- **`wire:model` sin debounce en búsquedas** — resultará en queries por cada keystroke
- **Componentes Livewire anidados sin separación clara** — mantener jerarquía simple
- **Lógica de negocio en componente Livewire** — mover a Service
- **Estado global compartido entre componentes** — usar eventos Livewire (`dispatch`)
- **Validación solo en formulario HTML** — siempre en FormRequest o componente Livewire
- **Sin transacciones en operaciones multi-tabla** — usar `DB::transaction()`

---

## Comandos útiles

```bash
# Desarrollo
php artisan serve
npm run dev        # Vite para TailwindCSS

# Tests
php artisan test --coverage

# Generar componentes Livewire
php artisan make:livewire UserList
php artisan make:livewire Modals/ConfirmDelete

# Linting
./vendor/bin/pint
npm run lint       # ESLint para Alpine/TailwindCSS

# Migraciones
php artisan migrate
```

## Variables de entorno

```bash
DB_CONNECTION=pgsql
DB_HOST=127.0.0.1
DB_PORT=5432
DB_DATABASE=laravel_livewire
DB_USERNAME=postgres
DB_PASSWORD=

APP_KEY=base64:...
APP_URL=http://localhost:8000
```

---

## Ejemplo completo

→ [CLAUDE.md para Laravel + Livewire](/examples/laravel-livewire-CLAUDE)
