# Livewire Patterns

## Ciclo de vida de un componente

Un componente Livewire es una clase PHP que renderiza una Blade view. El ciclo es:

1. **`mount()`** — se llama una vez al instanciar el componente (como un constructor HTTP). Ideal para inicializar propiedades desde parámetros de ruta o del padre.
2. **`hydrate()` / `dehydrate()`** — se llaman en cada request antes/después de la acción. Útiles para reconstruir objetos no serializables.
3. **`updated($property, $value)`** — se llama después de que una propiedad cambia vía `wire:model`. Usa `updatedSearch()` para escuchar propiedades específicas.
4. **`render()`** — devuelve la Blade view. Se llama al final de cada request.

```php
class LogList extends Component
{
    public string $search = '';
    public string $severity = 'all';

    public function mount(Application $app): void
    {
        $this->application = $app;
    }

    public function updatedSearch(): void
    {
        $this->resetPage(); // built-in pagination reset
    }

    public function render(): View
    {
        return view('livewire.log-list', [
            'logs' => Log::search($this->search)
                ->bySeverity($this->severity)
                ->paginate(25),
        ]);
    }
}
```

## Wire Directives esenciales

```blade
{{-- Binding bidireccional — actualiza la propiedad en cada keystroke --}}
<input wire:model="search" type="text">

{{-- Lazy binding — actualiza al perder el foco (más eficiente) --}}
<input wire:model.lazy="search" type="text">

{{-- Debounced — espera 500ms de inactividad antes de actualizar --}}
<input wire:model.debounce.500ms="search" type="text">

{{-- Acciones --}}
<button wire:click="archive({{ $log->id }})">Archivar</button>
<form wire:submit.prevent="save">...</form>

{{-- Loading states --}}
<span wire:loading wire:target="save">Guardando...</span>
<button wire:loading.attr="disabled" wire:target="save">Guardar</button>

{{-- Confirmación antes de acción destructiva --}}
<button wire:click="delete({{ $log->id }})"
        wire:confirm="¿Eliminar este log?">Eliminar</button>

{{-- Polling automático --}}
<div wire:poll.5s>{{ $this->activeCount }}</div>
```

## Propiedades computadas (Computed Properties)

```php
use Livewire\Attributes\Computed;

class Dashboard extends Component
{
    // Cached por request — no se recalcula en cada llamada a $this->stats
    #[Computed]
    public function stats(): array
    {
        return [
            'total' => Log::count(),
            'critical' => Log::where('severity', 'critical')->count(),
        ];
    }
}
```

```blade
{{-- En la view se accede como propiedad --}}
<p>Total: {{ $this->stats['total'] }}</p>
```

## Integración con Alpine.js

Livewire y Alpine comparten el DOM. Alpine gestiona interactividad local (UI state), Livewire gestiona estado del servidor.

```blade
{{-- Alpine maneja el toggle local; Livewire dispara acciones del servidor --}}
<div x-data="{ open: false }">
    <button @click="open = !open">Filtros</button>
    <div x-show="open">
        <select wire:model="severity" @change="open = false">
            <option value="all">Todos</option>
            <option value="critical">Crítico</option>
        </select>
    </div>
</div>

{{-- Escuchar eventos de Livewire desde Alpine --}}
<div x-on:log-archived.window="$dispatch('notify', { message: 'Log archivado' })">
```

```php
// Disparar evento de Livewire al frontend
public function archive(int $id): void
{
    Log::findOrFail($id)->archive();
    $this->dispatch('log-archived', id: $id);
}
```

## Validación

```php
use Livewire\Attributes\Validate;

class CommentForm extends Component
{
    // Validación inline con atributo (Livewire 4)
    #[Validate('required|min:10|max:2000')]
    public string $body = '';

    public function save(): void
    {
        $this->validate(); // lanza ValidationException si falla
        Comment::create(['body' => $this->body, 'log_id' => $this->logId]);
        $this->reset('body');
        $this->dispatch('comment-added');
    }
}
```

## Testing con Livewire::test()

```php
use Livewire\Livewire;
use App\Livewire\LogList;

it('filters logs by severity', function () {
    Log::factory()->create(['severity' => 'critical']);
    Log::factory()->create(['severity' => 'info']);

    Livewire::test(LogList::class)
        ->set('severity', 'critical')
        ->assertSee('critical')
        ->assertDontSee('info');
});

it('archives a log and dispatches event', function () {
    $log = Log::factory()->create();

    Livewire::test(LogList::class)
        ->call('archive', $log->id)
        ->assertDispatched('log-archived');

    expect($log->fresh()->archived_at)->not->toBeNull();
});

it('validates comment body', function () {
    Livewire::test(CommentForm::class, ['logId' => 1])
        ->set('body', 'short')
        ->call('save')
        ->assertHasErrors(['body' => 'min']);
});
```

## Cuándo usar Livewire vs controlador clásico

| Escenario | Usar |
|---|---|
| Tabla con filtros/búsqueda en tiempo real | Livewire component |
| Formulario con validación reactiva | Livewire component |
| Página estática o con datos fijos | Blade + controlador clásico |
| Operación de un solo paso (crear, redirigir) | Controlador + redirect() |
| Actualización en tiempo real (SSE/WebSocket) | Livewire + `wire:poll` o `dispatch` |
| Tabla paginada con filtros | Livewire + `WithPagination` |

## Anti-patrones a evitar

- **Fat components**: lógica de negocio en el componente — moverla a Services
- **`wire:model` en objetos Eloquent directamente** — usar propiedades tipadas simples
- **Queries en `render()` sin paginación** — siempre `->paginate()` en listados
- **Propiedades `public` con datos sensibles** — las propiedades Livewire son serializadas al frontend
- **Alpine para estado persistente** — Alpine es UI-only; el estado real va en propiedades Livewire
- **Múltiples componentes anidados cuando uno basta** — la composición tiene coste de hydration

## Estructura de archivos recomendada

```
app/Livewire/
├── Dashboard/
│   ├── Overview.php          ← componente de alto nivel
│   └── StatsCard.php         ← componente reutilizable
├── Logs/
│   ├── LogList.php           ← tabla con filtros
│   ├── LogDetail.php         ← vista detalle
│   └── CommentThread.php     ← hilo de comentarios
└── Settings/
    └── ApplicationForm.php

resources/views/livewire/
├── dashboard/
│   ├── overview.blade.php
│   └── stats-card.blade.php
└── logs/
    ├── log-list.blade.php
    └── comment-thread.blade.php
```
