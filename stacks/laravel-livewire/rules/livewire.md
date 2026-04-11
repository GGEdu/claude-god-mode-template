# Livewire — Reglas del stack

## Cuándo usar Livewire vs controlador clásico

| Escenario | Usar |
|---|---|
| Tabla con filtros/búsqueda reactiva | Livewire component |
| Formulario con validación en tiempo real | Livewire component |
| Página estática o datos que no cambian sin recarga | Blade + controlador clásico |
| Operación única (crear y redirigir) | Controlador + `redirect()` |
| Actualización periódica en tiempo real | Livewire + `wire:poll` |

## Estructura de componentes

- Componentes en `app/Livewire/` organizados por dominio: `app/Livewire/Logs/LogList.php`
- Views en `resources/views/livewire/` con la misma jerarquía: `resources/views/livewire/logs/log-list.blade.php`
- Un componente = una responsabilidad clara. Si supera 200 líneas de PHP, extraer sub-componentes
- Nunca lógica de negocio en el componente — delegar a Services

## Propiedades y estado

- Las propiedades `public` son el estado visible del componente (se sincronizan cliente-servidor)
- NO poner datos sensibles como propiedades `public` — van en propiedades `protected` o se cargan en `render()`
- Usar `#[Computed]` para valores derivados que se calculan una vez por request
- Usar `wire:model.lazy` o `.debounce` en inputs para reducir requests al servidor

## Validación

- Usar atributos `#[Validate]` en Livewire 4 para validación reactiva
- Para reglas complejas, delegar a un FormRequest o a una Rule class
- Llamar `$this->validate()` en la action antes de persistir

## Eventos

- Usar `$this->dispatch('event-name', ...data)` para comunicación componente → JavaScript/Alpine
- Usar `#[On('event-name')]` para escuchar eventos de otros componentes
- Preferir eventos Livewire sobre JavaScript puro para mantener el estado en el servidor

## Integración Alpine.js

- Alpine gestiona estado de UI local (modals, dropdowns, toggles) — no estado de negocio
- Livewire gestiona estado del servidor (filtros, datos, paginación)
- Usar `x-data` para UI state y `wire:model`/`wire:click` para server state
- No duplicar estado entre Alpine y Livewire

## Performance

- `wire:loading` para feedback visual en acciones lentas — siempre incluirlo
- `wire:poll` solo cuando sea imprescindible — tiene coste de un request HTTP por intervalo
- Eager loading en `render()` — nunca lazy loading en Livewire (N+1 silencioso)
- Para tablas grandes: paginación con `WithPagination` trait, nunca cargar todos los registros

## Testing

- Testear con `Livewire::test(ComponentClass::class, ['prop' => $value])`
- Métodos: `->set()`, `->call()`, `->assertSee()`, `->assertHasErrors()`, `->assertDispatched()`
- Cada componente crítico: test de render inicial, test de interacción principal, test de validación

## Anti-patrones a evitar

- Queries en el constructor o `mount()` sin paginación
- Propiedades `public` con modelos Eloquent completos (serialización peligrosa)
- Componentes con múltiples responsabilidades mezcladas
- Lógica de negocio directamente en `render()` — extraer a computed properties o services
- `wire:poll` en componentes que no necesitan actualización en tiempo real
