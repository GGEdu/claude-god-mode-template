# Tutorial guiado: Task Manager con Laravel 13 + React 19

> **Nivel:** Principiante — no necesitas experiencia previa con Claude Code
> **Tiempo estimado:** 2–3 horas siguiendo cada paso
> **Lo que construirás:** Una API REST de gestión de tareas con autenticación, y su frontend en React

Este tutorial te lleva paso a paso por el workflow real de desarrollo usando el template. Verás exactamente qué escribir, qué responde Claude, y qué salida aparece en pantalla para cada comando.

::: info Prerequisitos
Antes de empezar, asegúrate de haber completado la [instalación completa](/instalacion) y de haber inicializado el stack:

```bash
make init-project STACK=laravel LAYERS=react PROJECT=/ruta/al/proyecto
```

Si `make check` muestra todo en verde, estás listo.
:::

---

## El proyecto: Task Manager

Vas a construir **TaskFlow**, una aplicación de gestión de tareas para equipos:

- **API Laravel 13** con autenticación Sanctum, CRUD de tareas con asignación a usuarios
- **SPA React 19** con login, dashboard de tareas, y rutas protegidas

Cada sección del tutorial cubre un comando diferente. Puedes seguirlo completo de una vez o usarlo como referencia cuando necesites un comando concreto.

---

## Sección 1 — Planificar con el agente `planner`

> **Cuándo:** Antes de implementar cualquier feature nueva. Siempre.

```text
"Planifica: Implementa el módulo de tareas: CRUD completo con asignación a usuarios,
prioridades (alta/media/baja) y filtrado por estado"
```

El agente `planner` se lanza como subproceso, lee el estado actual del proyecto y devuelve:

**Output del agente planner:**

```markdown
## Plan: Módulo de Tareas — TaskFlow

### Análisis del Estado Actual
- ✅ Autenticación Sanctum implementada
- ✅ Modelo User con factory
- ⬜ Modelo Task — no existe

### Fase 1 — Backend: Modelo y Migraciones
- [ ] Migración `create_tasks_table` (id, title, description, status, priority, user_id, assigned_to, timestamps)
- [ ] Modelo Task con relaciones (belongsTo User × 2), fillable, casts
- [ ] Factory TaskFactory para tests

### Fase 2 — Backend: API REST
- [ ] TaskController (index, store, show, update, destroy) — thin controller
- [ ] TaskService con la lógica de negocio
- [ ] StoreTaskRequest, UpdateTaskRequest (FormRequest con validación)
- [ ] TaskResource para las respuestas API
- [ ] Rutas en api.php con middleware auth:sanctum

### Fase 3 — Backend: Tests
- [ ] TaskTest::test_authenticated_user_can_list_tasks
- [ ] TaskTest::test_user_can_create_task_with_valid_data
- [ ] TaskTest::test_user_cannot_update_task_of_another_user (autorización)
- [ ] TaskTest::test_task_list_filters_by_status
- [ ] Cobertura objetivo: ≥ 80%

### Fase 4 — Frontend: Integración
- [ ] Hook useTasks() con SWR
- [ ] Componente TaskList con filtros
- [ ] Componente TaskForm (crear/editar)
- [ ] Ruta /dashboard protegida con PrivateRoute

### Dependencias Identificadas
- Fase 2 depende de Fase 1 (migración debe existir antes)
- Fase 4 depende de Fase 2 (endpoints API deben estar listos)

### Riesgos
- **MEDIO:** Autorización granular (¿puede un usuario editar tareas asignadas a él aunque no las haya creado?)
  → Decisión requerida antes de implementar la política
- **BAJO:** Paginación en el listado — usar ->paginate(15) obligatorio según las reglas del stack
```

Claude muestra el plan y espera tu aprobación. Responde:

```text
perfecto, empezamos con la Fase 1
```

---

## Sección 2 — Liberar contexto con `/compact`

> **Cuándo:** Después de explorar código existente, antes de ponerte a implementar

Si has estado leyendo varios archivos o haciendo preguntas sobre el proyecto, el historial de la sesión empieza a llenarse. Antes de empezar la implementación:

```text
/compact
```

**Qué hace:**
- Comprime el historial anterior en un resumen denso
- **Guarda:** el plan acordado, las decisiones, el estado actual del código
- **Descarta:** las idas y venidas de exploración, los mensajes intermedios

**Output:**

```
Compactando historial de sesión...

Resumen guardado:
• Plan de implementación del módulo de tareas (4 fases)
• Decisión: los usuarios asignados pueden editar sus propias tareas
• Estado: autenticación implementada, módulo de tareas por empezar

Contexto liberado: ~8,400 tokens → ~1,200 tokens de resumen
```

::: warning Solo Claude Code
`/compact` es exclusivo de Claude Code. La gestión de contexto es automática en otras plataformas.
:::

---

## Sección 3 — Desarrollar con TDD: agente `tdd-guide`

> **Cuándo:** Antes de escribir cualquier línea de código de producción

Las reglas de Laravel TDD (`laravel-tdd`) van embebidas en el agente `tdd-guide`
del stack `laravel`. Al pedir "Implementa con TDD: ...", Claude aplica ese contexto
automáticamente.

**Output — Claude confirma las reglas activas:**

```
✅ Reglas Laravel TDD cargadas en el contexto:

Ciclo obligatorio:
  1. Escribe el test PRIMERO (estado RED)
  2. Ejecuta: php artisan test → debe fallar
  3. Implementa lo mínimo para que pase (estado GREEN)
  4. Refactoriza sin romper los tests (IMPROVE)

Convenciones Pest para este stack:
  • Tests de endpoints en tests/Feature/ con RefreshDatabase
  • Tests de servicios en tests/Unit/
  • Usar factories para datos de prueba, nunca datos literales
  • Cada endpoint debe tener: test de éxito, validación y auth
  • Cobertura mínima: 80%
```

### Paso 3a — Iniciar el ciclo TDD: agente `tdd-guide`

```text
"Implementa con TDD: módulo de tareas — CRUD con asignación y prioridades"
```

Claude lanza el agente `tdd-guide` para guiarte por el ciclo:

**FASE RED — Claude escribe los tests primero:**

```php
// tests/Feature/TaskTest.php  (Claude genera este archivo)

class TaskTest extends TestCase
{
    use RefreshDatabase;

    public function test_authenticated_user_can_list_tasks(): void
    {
        $user = User::factory()->create();
        Task::factory()->count(3)->create(['user_id' => $user->id]);

        $response = $this->actingAs($user)
                         ->getJson('/api/tasks');

        $response->assertOk()
                 ->assertJsonCount(3, 'data')
                 ->assertJsonStructure(['data' => [['id', 'title', 'status', 'priority']]]);
    }

    public function test_user_can_create_task_with_valid_data(): void
    {
        $user = User::factory()->create();

        $response = $this->actingAs($user)
                         ->postJson('/api/tasks', [
                             'title'    => 'Revisar PR de autenticación',
                             'priority' => 'alta',
                             'status'   => 'pendiente',
                         ]);

        $response->assertCreated() // 201
                 ->assertJsonPath('data.title', 'Revisar PR de autenticación');

        $this->assertDatabaseHas('tasks', ['title' => 'Revisar PR de autenticación']);
    }

    public function test_user_cannot_update_task_of_another_user(): void
    {
        $owner  = User::factory()->create();
        $other  = User::factory()->create();
        $task   = Task::factory()->create(['user_id' => $owner->id]);

        $response = $this->actingAs($other)
                         ->putJson("/api/tasks/{$task->id}", ['title' => 'Modificado']);

        $response->assertForbidden(); // 403
    }

    public function test_unauthenticated_user_cannot_access_tasks(): void
    {
        $response = $this->getJson('/api/tasks');
        $response->assertUnauthorized(); // 401
    }
}
```

**Ejecuta los tests (deben fallar — estado RED correcto):**

```bash
php artisan test tests/Feature/TaskTest.php
```

**Output de Pest en estado RED:**

```
   FAIL  Tests\Feature\TaskTest
  ✕ authenticated user can list tasks ....................... 12ms
  ✕ user can create task with valid data ................... 8ms
  ✕ user cannot update task of another user ................ 7ms
  ✕ unauthenticated user cannot access tasks ............... 6ms

  Tests:  4 failed
  Failed: Route [api/tasks] not defined.
```

Los tests fallan porque el código aún no existe. Esto es correcto — es el estado RED.

**FASE GREEN — Claude implementa lo mínimo para que pasen:**

Claude genera en orden:
1. La migración
2. El modelo Task
3. El factory
4. El controller + service + FormRequests
5. Las rutas

Una vez escritos, ejecuta:

```bash
php artisan test tests/Feature/TaskTest.php
```

**Output de Pest en estado GREEN:**

```
   PASS  Tests\Feature\TaskTest
  ✓ authenticated user can list tasks ...................... 45ms
  ✓ user can create task with valid data ................... 38ms
  ✓ user cannot update task of another user ................ 32ms
  ✓ unauthenticated user cannot access tasks ............... 18ms

  Tests:  4 passed (14 assertions)
```

**FASE REFACTOR — Claude extrae lógica al TaskService:**

Después de refactorizar, ejecuta de nuevo:

```bash
php artisan test
```

**Output final:**

```
   PASS  Tests\Feature\AuthTest
   PASS  Tests\Feature\TaskTest

  Tests:  7 passed (28 assertions)
  Duration: 1.23s

  Coverage: 87.4% of lines
```

---

## Sección 4 — Patrones de arquitectura Laravel (embebidos)

> **Cuándo:** Al empezar a trabajar en cualquier módulo nuevo de Laravel

**Output — Claude confirma qué patrones tiene activos:**

```
✅ Patrones Laravel activos en el contexto:

Controladores
  • Thin controllers: máximo 5 métodos, sin lógica de negocio
  • Solo reciben la Request, llaman al Service, devuelven el Resource
  • Inyección de dependencias en el constructor

Servicios
  • Lógica de negocio en app/Services/ siempre
  • Un servicio por entidad de dominio (TaskService, UserService...)
  • Los servicios no conocen la Request ni la Response

Validación
  • app/Http/Requests/ para todos los FormRequests
  • Nunca $request->validate() inline en el controller
  • Siempre $request->validated() — nunca $request->all()

Respuestas API
  • app/Http/Resources/ para todas las respuestas
  • Nunca arrays crudos en el return del controller
  • Paginación obligatoria en listados: ->paginate(15)

Autenticación
  • Sanctum para SPA — nunca JWT manual
  • CORS configurado con dominio específico, nunca '*' en producción
```

A partir de este punto, si le pides a Claude que cree un endpoint, generará automáticamente el controlador delgado, el servicio y el resource sin que tengas que recordárselo.

---

## Sección 5 — Seguridad Laravel (embebida en `security-reviewer`)

> **Cuándo:** Al tocar autenticación, inputs de usuario, uploads, o endpoints de API

**Output — Claude activa el checklist de seguridad:**

```
✅ Checklist de seguridad Laravel activado:

Autenticación y autorización
  • Rate limiting en rutas de auth: throttle:5,1
  • Sanctum tokens con nombre descriptivo: createToken('spa-web')
  • Políticas en app/Policies/ — nunca lógica de auth en el controller

Inputs y validación
  • Siempre $request->validated() — nunca $request->all()
  • Validación de tipos estricta en FormRequest
  • Sanitizar antes de almacenar en BBDD

Base de datos
  • Parameterized queries siempre (Eloquent lo hace automáticamente)
  • Mass assignment protegido con $fillable en el modelo
  • Sin exposición de campos sensibles en los Resources

CORS
  • allowed_origins: [env('FRONTEND_URL')] — nunca '*' en producción
  • Configurar en config/cors.php, no inline

Detectando issues en el código actual...
  ⚠️  ALTA: Las rutas /api/tasks no tienen rate limiting
      → Solución: ->middleware('throttle:60,1') en api.php
  ℹ️  BAJA: TaskResource expone user_id directamente
      → Considera exponer solo el nombre del usuario
```

Claude detecta automáticamente issues en el código ya escrito y te propone las correcciones.

---

## Sección 6 — Code review: `/jedi-review`

> **Cuándo:** Después de escribir o modificar código, antes de un commit

```text
/jedi-review
```

El agente `code-reviewer` (junto a Kent Beck, Martin Fowler y Mike Acton) analiza los cambios recientes y devuelve:

**Output:**

```
═══════════════════════════════════════════════════════
 Code Review — TaskController + TaskService + TaskPolicy
═══════════════════════════════════════════════════════

 CRITICAL (0) — Sin issues bloqueantes

 HIGH (0) — Sin issues de alta prioridad

 MEDIUM (2)
 ──────────
 ⚠️  TaskService::create() no valida que assigned_to pertenezca
    al mismo equipo que el creador. Un usuario podría asignar
    tareas a cualquier usuario del sistema.
    → Añadir validación: User::where('team_id', $creator->team_id)
                               ->findOrFail($data['assigned_to'])

 ⚠️  TaskResource no implementa el método whenLoaded() para
    relaciones. Cargará el usuario en cada request aunque no
    se necesite.
    → Cambiar: 'assigned_to' => new UserResource($this->whenLoaded('assignedTo'))

 LOW (1)
 ───────
 ℹ️  Falta test para el caso: crear tarea con assigned_to de otro equipo

═══════════════════════════════════════════════════════
 Veredicto: APROBADO CON ADVERTENCIAS
 Los issues MEDIUM deberían corregirse antes del merge
═══════════════════════════════════════════════════════
```

---

## Sección 7 — Revisión profunda: `/jedi-review`

> **Cuándo:** Para código que importa — antes de un PR, después de una feature compleja

`/jedi-review` lanza **tres subagentes en paralelo**, cada uno con una perspectiva distinta:

```text
/jedi-review
```

**Output — Los tres expertos trabajan simultáneamente y devuelven:**

```
═══════════════════════════════════════════════════════
 Jedi Review — TaskService + TaskController
═══════════════════════════════════════════════════════

 ── Kent Beck (Simplicidad y TDD) ──────────────────

 Calificación: A-

 ✅ Tests cubren los casos principales con claridad
 ✅ El código comunica intención — nombres expresivos
 ✅ Sin duplicación obvia
 ⚠️  test_user_cannot_update_task_of_another_user podría
    probar también el caso con assigned_to (no solo owner)
 ⚠️  TaskService::update() hace dos cosas: actualizar datos
    y reasignar. Considerar separar en update() y reassign()

 ── Martin Fowler (Arquitectura y Refactoring) ──────

 Calificación: B+

 ✅ Thin controller correctamente delegando al Service
 ✅ FormRequests separados por acción (Store vs Update)
 ⚠️  TaskService depende directamente de Eloquent.
    Para testabilidad, extraer interfaz TaskRepositoryInterface
    y usar inyección de dependencias en el Service
 ⚠️  La lógica de autorización está duplicada entre
    TaskPolicy y TaskService. Consolidar en la Policy.

 ── Mike Acton (Rendimiento y Datos) ────────────────

 Calificación: B

 ✅ Sin queries N+1 detectadas en el listado (eager loading correcto)
 ✅ Paginación implementada con ->paginate(15)
 ⚠️  Falta índice en tasks.user_id y tasks.assigned_to.
    En producción con muchas tareas, las queries de listado
    serán lentas sin estos índices.
 ℹ️  El filtrado por status hace un full table scan.
    Añadir índice en tasks.status si el volumen crece.

═══════════════════════════════════════════════════════
 VEREDICTO FINAL: B+ (Apto para merge con correcciones)

 Top 3 acciones por impacto:
 1. [ALTO] Añadir índices en tasks.user_id, assigned_to, status
 2. [MEDIO] Eliminar duplicación Policy/Service en autorización
 3. [BAJO] Considerar interfaz TaskRepositoryInterface para tests

 Deuda técnica estimada: ~2h para implementar las 3 acciones
═══════════════════════════════════════════════════════
```

---

## Sección 8 — Auditoría de seguridad: `/security-scan`

> **Cuándo:** Antes de cualquier release, o al implementar código sensible

```text
/security-scan
```

El agente `security-reviewer` hace una auditoría OWASP completa:

**Output:**

```
═══════════════════════════════════════════════════════
 Security Review — TaskFlow API
 OWASP Top 10 Checklist
═══════════════════════════════════════════════════════

 A01 — Broken Access Control
 ✅ TaskPolicy implementada y registrada
 ✅ Middleware auth:sanctum en todas las rutas API
 ⚠️  HIGH: El endpoint GET /api/tasks devuelve TODAS las tareas
    del usuario. Si el rol "admin" puede ver tareas de otros
    equipos, necesita scope adicional.

 A02 — Cryptographic Failures
 ✅ Passwords hasheadas con bcrypt (Laravel por defecto)
 ✅ Tokens Sanctum son opacos (no JWT expuesto)

 A03 — Injection
 ✅ Eloquent ORM previene SQL injection automáticamente
 ✅ Validación de inputs en FormRequests

 A05 — Security Misconfiguration
 ⚠️  HIGH: config/cors.php tiene 'allowed_origins' => ['*']
    Cambiar a: env('FRONTEND_URL', 'http://localhost:3000')
 ✅ APP_DEBUG=false en .env.example

 A07 — Identification and Authentication Failures
 ⚠️  HIGH: Endpoint /api/auth/login sin rate limiting
    → Añadir throttle:5,1 en la ruta
 ✅ Tokens de Sanctum tienen expiración configurable

 A09 — Security Logging and Monitoring Failures
 ℹ️  LOW: Sin logging de intentos de login fallidos.
    Considerar: Log::warning('Failed login attempt', [...])

═══════════════════════════════════════════════════════
 ISSUES CRÍTICOS: 0
 ISSUES ALTOS: 3 → Deben corregirse antes del deploy
 ISSUES BAJOS: 1 → Recomendable
═══════════════════════════════════════════════════════
```

Claude aplica automáticamente los fixes para los issues ALTOS.

---

## Sección 9 — Diseñar endpoints con `api-design` (skill embebida)

> **Cuándo:** Al diseñar nuevos endpoints REST o revisar los existentes

**Output — Claude activa las reglas de diseño de API:**

```
✅ Principios de API Design activados:

Naming
  • Sustantivos en plural para recursos: /tasks, /users
  • Relaciones anidadas cuando tiene sentido: /tasks/{id}/comments
  • Sin verbos en las rutas: NO /getTasks, SÍ GET /tasks

Códigos HTTP correctos
  • 200 OK — operación exitosa (GET, PUT)
  • 201 Created — recurso creado (POST)
  • 204 No Content — eliminado exitosamente (DELETE)
  • 422 Unprocessable — error de validación
  • 403 Forbidden — sin autorización
  • 404 Not Found — recurso no existe

Respuestas consistentes
  • Siempre usar API Resources de Laravel
  • Paginación en listados: { data: [...], meta: { total, per_page, current_page } }
  • Errores con estructura: { message: "...", errors: { field: ["..."] } }

Revisando rutas actuales...
  ✅ GET /api/tasks — correcto
  ✅ POST /api/tasks — correcto, devuelve 201
  ⚠️  DELETE /api/tasks/{id} devuelve 200 con { message: "Deleted" }
      → Cambiar a 204 sin cuerpo de respuesta
```

---

## Sección 10 — Migraciones con `database-migrations` (skill embebida)

> **Cuándo:** Al crear o modificar migraciones de base de datos

**Output — Claude activa las buenas prácticas de migraciones:**

```
✅ Patrones de migraciones activados:

Índices
  • Añadir índice en foreign keys siempre
  • Añadir índice en campos de filtrado frecuente (status, priority)
  • Índice compuesto cuando se filtra por múltiples campos juntos

Estructura
  • Usar unsignedBigInteger para foreign keys (o foreignId())
  • Timestamps obligatorios en todas las tablas ($table->timestamps())
  • SoftDeletes si el modelo debe ser recuperable ($table->softDeletes())

Reversibilidad
  • El método down() debe deshacer exactamente lo que hace up()
  • Sin pérdida de datos en down() si es posible

Generando migración para tasks con las mejores prácticas...
```

**Migración generada:**

```php
// database/migrations/2026_04_01_create_tasks_table.php
public function up(): void
{
    Schema::create('tasks', function (Blueprint $table) {
        $table->id();
        $table->string('title');
        $table->text('description')->nullable();
        $table->enum('status', ['pendiente', 'en_progreso', 'completada'])->default('pendiente');
        $table->enum('priority', ['baja', 'media', 'alta'])->default('media');
        $table->foreignId('user_id')->constrained()->cascadeOnDelete();
        $table->foreignId('assigned_to')->nullable()->constrained('users')->nullOnDelete();
        $table->timestamps();

        // Índices para queries frecuentes
        $table->index('status');
        $table->index('priority');
        $table->index(['user_id', 'status']); // índice compuesto para filtrado
    });
}
```

---

## Sección 11 — Frontend React con `frontend-patterns` (skill embebida)

> **Cuándo:** Al empezar el desarrollo frontend o crear componentes nuevos

**Output — Claude activa las reglas de React:**

```
✅ Patrones React activados:

Data fetching
  • SWR o React Query para todos los fetches
  • Nunca useEffect + useState + fetch manual
  • CSRF cookie de Sanctum ANTES del primer POST

Formularios
  • React Hook Form + Zod para todos los formularios
  • Validación en el cliente (Zod) + en el servidor (FormRequest)
  • Mostrar errores del backend inline en los campos

Estado global
  • Solo para auth y theme — no sobreuso de Context
  • El estado derivado se calcula en el render, no con useEffect

Performance
  • Importaciones dinámicas para rutas grandes
  • React.memo solo cuando el profiler muestra re-renders innecesarios
  • Sin barrel files (index.ts que re-exporta todo)

TypeScript
  • Sin any — siempre tipos explícitos
  • Tipos para todas las respuestas de la API
```

**Código generado para el hook de tareas:**

```typescript
// src/hooks/useTasks.ts
import useSWR, { mutate } from 'swr';
import { api } from '@/lib/api';

interface Task {
  id: number;
  title: string;
  status: 'pendiente' | 'en_progreso' | 'completada';
  priority: 'baja' | 'media' | 'alta';
  assigned_to: number | null;
}

interface TasksResponse {
  data: Task[];
  meta: { total: number; per_page: number; current_page: number };
}

export function useTasks(filters?: { status?: string }) {
  const params = new URLSearchParams(filters as Record<string, string>).toString();
  const key = `/api/tasks${params ? `?${params}` : ''}`;

  const { data, error, isLoading } = useSWR<TasksResponse>(key, api.get);

  const createTask = async (taskData: Omit<Task, 'id'>) => {
    await api.post('/api/tasks', taskData);
    mutate(key); // revalida la lista automáticamente
  };

  return { tasks: data?.data ?? [], meta: data?.meta, isLoading, error, createTask };
}
```

---

## Sección 12 — Tests E2E con `e2e-testing` (skill embebida en `e2e-runner`)

> **Cuándo:** Al implementar o revisar flujos críticos del usuario

**Output — Claude activa las reglas de tests E2E con Playwright:**

```
✅ Reglas E2E activadas (Playwright):

Setup
  • Arrancar la app completa antes de los tests
  • Crear datos de prueba via API, no directamente en BBDD
  • Un usuario de prueba por test (no compartir estado)

Assertions
  • Esperar elementos visibles antes de interactuar
  • Usar locators semánticos: getByRole, getByLabel, getByText
  • Capturar screenshots en fallos automáticamente

Casos críticos a cubrir siempre
  • Flujo de login completo (happy path)
  • Flujo de login fallido (credenciales incorrectas)
  • Acceso a ruta protegida sin autenticación → redirect a login
  • Crear/editar/borrar el recurso principal
```

**Test E2E generado para el flujo de login:**

```typescript
// e2e/auth.spec.ts
import { test, expect } from '@playwright/test';

test('usuario puede iniciar sesión y ver el dashboard', async ({ page }) => {
  // Arrange: crear usuario via API
  const user = await createTestUser({ email: 'test@taskflow.com', password: 'password' });

  // Act: navegar y hacer login
  await page.goto('/login');
  await page.getByLabel('Email').fill(user.email);
  await page.getByLabel('Contraseña').fill('password');
  await page.getByRole('button', { name: 'Iniciar sesión' }).click();

  // Assert: redirige al dashboard con las tareas
  await expect(page).toHaveURL('/dashboard');
  await expect(page.getByRole('heading', { name: 'Mis Tareas' })).toBeVisible();
});

test('usuario sin autenticar es redirigido al login', async ({ page }) => {
  await page.goto('/dashboard');
  await expect(page).toHaveURL('/login');
});
```

---

## Sección 13 — Commit y hooks defensivos

> **Cuándo:** Cada vez que quieras guardar tu trabajo en git

Los hooks del template actúan automáticamente — no tienes que hacer nada especial.

```bash
git add -p                          # revisa los cambios interactivamente
git commit -m "feat: add task CRUD with authorization"
```

**Output del pre-commit hook (automático):**

```
[pre-commit] Ejecutando Biome en archivos TypeScript/JavaScript...
  ✅ src/hooks/useTasks.ts — OK
  ✅ src/components/TaskList.tsx — OK
  ✅ src/components/TaskForm.tsx — OK

[pre-commit] Detectando secrets en el diff...
  ✅ Sin secrets detectados

[pre-commit] Todo correcto. Procediendo con el commit.
```

Si hay errores de linting, el commit se bloquea:

```
[pre-commit] Ejecutando Biome...
  ✖ src/components/TaskForm.tsx:
    [error] Unexpected any. Specify a different type. (line 12)

[pre-commit] ❌ Linting fallido. El commit ha sido bloqueado.
Corrige los errores y vuelve a intentarlo.
```

Claude ve el error y lo corrige antes de que tengas que volver a ejecutar el commit.

```bash
git push
```

**Output del pre-push hook (automático):**

```
[pre-push] Ejecutando tests PHP...

   PASS  Tests\Feature\AuthTest (3 tests, 9 assertions)
   PASS  Tests\Feature\TaskTest (4 tests, 14 assertions)
   PASS  Tests\Unit\TaskServiceTest (5 tests, 12 assertions)

   Tests: 12 passed (35 assertions)
   Duration: 2.1s
   Coverage: 87.4%

[pre-push] ✅ Tests pasados. Procediendo con el push.
```

Si algún test falla, el push se bloquea. Claude diagnostica el fallo automáticamente.

::: tip El workflow de git completo: `/git-workflow`
```text
/git-workflow
```
Carga las reglas de Conventional Commits y el workflow de PRs. Útil cuando no recuerdas el formato exacto de los mensajes de commit o los pasos para crear un PR.
:::

---

## Sección 14 — Gestión de tokens y coste

> **Cuándo:** Para monitorear el gasto, optimizar costes o cambiar el modelo

::: warning Solo Claude Code
`/cost`, `/model`, y `/compact` son exclusivos de Claude Code.
:::

### Ver el coste de la sesión: `/cost`

```text
/cost
```

**Output:**

```
═══════════════════════════════════════════════════════════
 Resumen de Tokens — Sesión Actual
═══════════════════════════════════════════════════════════

 Uso total: 68,400 tokens de entrada + 21,200 de salida
 Coste estimado: ~$1.74 USD

 Desglose por actividad:
 ├─ Planificación (/plan)          14,200 tokens (21%)
 ├─ TDD y tests                    22,600 tokens (33%)
 ├─ Code review (/jedi-review)     18,400 tokens (27%)
 └─ Frontend React                 13,400 tokens (19%)

 ─────────────────────────────────────────────────────────
 Comparativa con configuración por defecto:
 ├─ Default (Opus + sin límites):   ~$6.20 USD
 ├─ Esta sesión (Sonnet + compact): ~$1.74 USD
 └─ Ahorro: 72% ✓

 Variables activas que reducen el coste:
 • Modelo: sonnet (en lugar de opus por defecto)
 • MAX_THINKING_TOKENS=10000 (en lugar de 31,999)
 • CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50 (compacta antes)
 • CLAUDE_CODE_SUBAGENT_MODEL=haiku (agentes con haiku)
═══════════════════════════════════════════════════════════
```

### Cambiar de modelo según la tarea

```text
/model opus
```

Úsalo para decisiones de arquitectura complejas que requieren el mayor razonamiento. Es 3-5× más caro que Sonnet.

**¿Cuándo usar cada modelo?**

| Modelo | Cuándo usarlo | Coste relativo |
|---|---|---|
| `haiku` | Preguntas simples, exploración rápida, tareas repetitivas | × 1 (más barato) |
| `sonnet` | Desarrollo general — el 95% del trabajo | × 4 |
| `opus` | Decisiones arquitectónicas complejas, análisis profundo | × 15 |

Volver al modelo estándar:

```text
/model sonnet
```

### Configuración de ahorro en `settings.json`

Estas variables están configuradas en `.claude/settings.json`:

```json
{
  "model": "sonnet",
  "env": {
    "MAX_THINKING_TOKENS": "10000",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "50",
    "CLAUDE_CODE_SUBAGENT_MODEL": "haiku"
  }
}
```

| Variable | Valor configurado | Qué hace |
|---|---|---|
| `MAX_THINKING_TOKENS` | `10000` | Limita el razonamiento interno (por defecto 31,999) |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE` | `50` | Compacta al 50% del contexto (por defecto 80%) |
| `CLAUDE_CODE_SUBAGENT_MODEL` | `haiku` | Los subagentes usan haiku (más barato) |

---

## Apéndice — Problemas frecuentes

### Los agentes no aparecen tras `make init-project`

**Síntoma:** `/jedi-review` devuelve "Comando no encontrado" o los agentes no se ejecutan.

**Solución:**

```bash
# Verifica que los agentes se copiaron
ls .claude/agents/

# Si está vacío, vuelve a ejecutar:
make init-project STACK=laravel LAYERS=react PROJECT=/ruta/al/proyecto

# Luego reinicia Claude Code completamente (no solo /reset)
# Cierra la sesión y vuelve a abrir con: claude
```

### El pre-commit hook falla con errores de Biome

**Síntoma:** El commit se bloquea con errores de linting.

**Diagnóstico:**

```bash
# Ver exactamente qué falla
npx biome check src/

# Corregir automáticamente lo que sea seguro
npx biome check --apply src/
```

### El contexto se llena antes de terminar la tarea

**Síntoma:** Claude empieza a olvidar cosas de antes en la conversación.

**Solución:**

```text
/compact
```

Si ya está muy lleno, considera cambiar a Haiku para exploración y volver a Sonnet para implementar:

```text
/model haiku
[hace la exploración o análisis de la estructura]

/model sonnet
[vuelve a implementar]
```

### `make check` muestra `❌ Sin agentes`

**Síntoma:**

```
Agentes (.claude/agents/):
  ❌ Sin agentes — ejecuta: make init-project STACK=<nombre>
```

**Solución:**

```bash
make init-project STACK=laravel LAYERS=react PROJECT=/ruta/al/proyecto
# Reiniciar Claude Code después
```

### Error CORS al hacer peticiones desde React

**Síntoma:** Las peticiones desde React al API de Laravel fallan con "CORS policy".

**Solución en Laravel:**

```php
// config/cors.php
'allowed_origins' => [env('FRONTEND_URL', 'http://localhost:5173')],
```

```bash
# .env
FRONTEND_URL=http://localhost:5173
```

---

## ¿Qué sigue?

Has completado el tutorial básico. Para continuar:

- **[Referencia completa de comandos](/referencia)** — Todos los comandos disponibles en una tabla
- **[Flujo completo de una feature](/examples/flujo-feature-laravel-react)** — Cómo funcionan internamente las capas del sistema
- **[Stack Laravel + React](/stacks/laravel-react)** — Cómo inicializar con `STACK=laravel LAYERS=react`
- **[Analizar proyectos externos](/analizar-proyecto-externo)** — Usa el template para auditar código existente
