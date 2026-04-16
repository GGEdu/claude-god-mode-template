# Flujo completo: nueva feature en Laravel + React

> Ejemplo real y paso a paso de qué ocurre cuando pides una nueva característica.
> Stack: Laravel 13 (API) + React 19 (SPA) + Sanctum para autenticación.
> Inicializado con: `make init-project STACK=laravel LAYERS=react PROJECT=/ruta`

---

## El escenario

Tienes un proyecto existente. Abres Claude Code y escribes:

```
/plan "Implementa autenticación con Sanctum para la SPA React: login, logout,
registro, y protección de rutas"
```

Lo que pasa a continuación involucra al menos 6 capas del sistema. Este documento
las recorre en orden.

---

## Capa 0 — Contexto disponible antes de empezar

Antes de que Claude procese tu prompt, ya hay información activa:

**Desde `.claude/CLAUDE.md` (leído al iniciar la sesión):**

```
Stack: Laravel / React
Linter: Biome (JS/TS) / Ruff (Python)
Commits: Conventional Commits
Tests obligatorios: 80% cobertura mínima
```

**Desde `.claude/rules/common/` (cargadas automáticamente):**

- `security.md` → Claude sabe que auth es sensible y activará security-reviewer
- `testing.md` → TDD obligatorio, tests primero
- `development-workflow.md` → orden: plan → tdd → code-review → commit

**Desde skills embebidas en los agentes (compiladas por `ops/compile-agents.py`):**

- `laravel-patterns` → thin controllers, usar Sanctum, FormRequest para validación (embebida en tdd-guide, code-reviewer, architect)
- `laravel-tdd` → ciclo RED-GREEN-REFACTOR con Pest (embebida en tdd-guide)
- `frontend-patterns` → Suspense, evitar waterfalls en data fetching (embebida en typescript-reviewer)

Los agentes ya llevan estas skills compiladas dentro — no necesitas invocarlas manualmente.

Claude tiene todo esto en su contexto activo. No necesita que se lo recuerdes.

---

## Capa 1 — El agente `planner`

Al describir lo que quieres implementar ("Planifica: ..."), Claude Code lanza el agente **planner**.

```
Tu sesión principal
    │
    └── Agent tool: lanza subagente "planner"
            ├── Contexto nuevo (aislado, ~10k tokens vacíos)
            ├── Lee: ~/.claude/agents/planner.md  ← instrucciones del agente
            ├── Recibe: tu prompt + contexto del proyecto actual
            └── NO hereda: historial de sesión completo
```

El agente planner:

1. Lee los archivos del proyecto para entender la estructura existente
2. Identifica dependencias (¿ya existe un modelo User? ¿hay migraciones?)
3. Genera un plan con fases, estimaciones y riesgos

**Salida del planner (ejemplo):**

```markdown
## Plan: Autenticación Sanctum SPA

### Fase 1 — Backend (Laravel)
- [ ] Instalar laravel/sanctum
- [ ] Publicar config y migración de personal_access_tokens
- [ ] Configurar middleware CORS para dominio React
- [ ] AuthController: login(), logout(), register(), me()
- [ ] FormRequest: LoginRequest, RegisterRequest
- [ ] Tests: AuthTest (login correcto, credenciales inválidas, logout)

### Fase 2 — Frontend (React)
- [ ] AuthContext + useAuth hook
- [ ] Componentes: LoginForm, RegisterForm
- [ ] PrivateRoute wrapper para rutas protegidas
- [ ] Cliente API con interceptor para CSRF y 401

### Riesgos identificados
- CORS mal configurado bloquea peticiones desde React (alta probabilidad)
- CSRF token no enviado en primera petición (medio)
- Estado de sesión no sincronizado tras expiración (medio)
```

El subagente devuelve el plan al contexto principal. Claude lo presenta y espera
tu aprobación antes de continuar.

---

## Capa 2 — Apruebas el plan y empieza el desarrollo

Respondes: `"perfecto, empieza"`

Claude sigue el orden del workflow definido en `development-workflow.md`:
**primero los tests, luego la implementación.**

---

## Capa 3 — El agente tdd-guide escribe los tests primero

Claude lanza el agente **tdd-guide** para la Fase 1 (backend).

```
Tu sesión principal
    │
    └── Agent tool: lanza subagente "tdd-guide"
            ├── Lee: ~/.claude/agents/tdd-guide.md
            ├── Recibe: "Escribe tests para AuthController con Sanctum"
            └── Tarea: ciclo RED → GREEN → REFACTOR
```

El agente tdd-guide escribe primero los tests (estado RED — fallan porque no
existe el código):

```php
// tests/Feature/AuthTest.php

class AuthTest extends TestCase
{
    use RefreshDatabase;

    public function test_user_can_login_with_valid_credentials(): void
    {
        $user = User::factory()->create([
            'password' => bcrypt('password123'),
        ]);

        $response = $this->postJson('/api/auth/login', [
            'email' => $user->email,
            'password' => 'password123',
        ]);

        $response->assertOk()
                 ->assertJsonStructure(['token', 'user' => ['id', 'email']]);
    }

    public function test_login_fails_with_invalid_credentials(): void
    {
        $response = $this->postJson('/api/auth/login', [
            'email' => 'fake@example.com',
            'password' => 'wrong',
        ]);

        $response->assertUnprocessable(); // 422
    }

    public function test_authenticated_user_can_logout(): void
    {
        $user = User::factory()->create();
        $token = $user->createToken('test')->plainTextToken;

        $response = $this->withHeader('Authorization', "Bearer $token")
                         ->postJson('/api/auth/logout');

        $response->assertOk();
        $this->assertDatabaseCount('personal_access_tokens', 0);
    }
}
```

Claude ejecuta los tests: **fallan** (correcto, es el estado RED).

---

## Capa 4 — Implementación guiada por skills embebidas del stack

Ahora Claude implementa el código para que los tests pasen. Aquí entra
la combinación de skills embebidas del stack en el contexto principal, no en el
subagente.

Claude sabe (por la skill) que debe:

- Controlador delgado → lógica en un Service
- FormRequest para validación, no validación inline
- Usar Sanctum, no JWT manual

```php
// app/Http/Requests/LoginRequest.php
class LoginRequest extends FormRequest
{
    public function rules(): array
    {
        return [
            'email'    => ['required', 'email'],
            'password' => ['required', 'string'],
        ];
    }
}

// app/Services/AuthService.php
class AuthService
{
    public function login(array $credentials): array
    {
        if (! Auth::attempt($credentials)) {
            throw new AuthenticationException();
        }

        $user = Auth::user();
        $token = $user->createToken('spa')->plainTextToken;

        return ['token' => $token, 'user' => $user];
    }

    public function logout(User $user): void
    {
        $user->currentAccessToken()->delete();
    }
}

// app/Http/Controllers/AuthController.php  ← thin controller
class AuthController extends Controller
{
    public function __construct(private AuthService $auth) {}

    public function login(LoginRequest $request): JsonResponse
    {
        $result = $this->auth->login($request->validated());
        return response()->json($result);
    }

    public function logout(Request $request): JsonResponse
    {
        $this->auth->logout($request->user());
        return response()->json(['message' => 'Logged out']);
    }
}
```

Claude ejecuta los tests: **pasan** (estado GREEN).

---

## Capa 5 — code-reviewer analiza la calidad

Al terminar el código, Claude lanza automáticamente el agente **code-reviewer**
(definido en `rules/common/code-review.md`: "use code-reviewer after writing code").

```
Tu sesión principal
    │
    └── Agent tool: lanza subagente "code-reviewer"
            ├── Lee: ~/.claude/agents/code-reviewer.md
            ├── Recibe: los archivos recién creados + diff
            └── Analiza: calidad, naming, cohesión, cobertura
```

El code-reviewer devuelve:

```
✅ AuthService correctamente desacoplado del controller
✅ FormRequest valida antes de llegar al servicio
⚠️  MEDIUM: AuthService no tiene interfaz — dificulta mocking en tests
⚠️  MEDIUM: logout() elimina solo el token actual, no todos los del usuario
              (puede ser intencional, pero documentar explícitamente)
ℹ️  LOW: Falta test para el endpoint GET /api/auth/me
```

Claude aplica los HIGH/CRITICAL automáticamente y presenta los MEDIUM para que
decidas.

---

## Capa 6 — security-reviewer audita el módulo de auth

Las `rules/common/security.md` dicen: "STOP and use security-reviewer when
authentication code". Claude lanza el agente **security-reviewer** en paralelo
con el code-reviewer.

```
Tu sesión principal
    │
    ├── Agent tool: code-reviewer  ──┐
    └── Agent tool: security-reviewer ┘ (en paralelo)
```

El security-reviewer evalúa:

```
✅ Sanctum genera tokens opacos (no JWT expuesto)
✅ FormRequest previene mass assignment
✅ bcrypt usado implícitamente por Laravel para passwords
⚠️  HIGH: Endpoint de login sin rate limiting — vulnerable a fuerza bruta
          → Añadir: throttle:5,1 en las rutas de auth
⚠️  HIGH: CORS permite '*' en config/cors.php
          → Cambiar a: 'allowed_origins' => [env('FRONTEND_URL')]
ℹ️  LOW: Considerar invalidar todos los tokens al cambiar password
```

Los issues HIGH se corrigen antes de continuar.

---

## Capa 7 — Frontend React con frontend-patterns activa

Claude repite el ciclo para la Fase 2 (React), ahora con la skill
`frontend-patterns` activa en el contexto principal.

```jsx
// hooks/useAuth.ts
// La skill indica: evitar waterfalls, usar SWR para deduplicación

export function useAuth() {
    const { data: user, mutate } = useSWR('/api/auth/me', fetcher, {
        revalidateOnFocus: false,  // no re-fetch en cada focus de ventana
    });

    const login = async (credentials: LoginCredentials) => {
        // Obtener CSRF token primero (requerimiento de Sanctum SPA)
        await api.get('/sanctum/csrf-cookie');
        const { data } = await api.post('/auth/login', credentials);
        mutate(data.user);          // actualiza cache SWR sin re-fetch
        return data;
    };

    return { user, login, logout, isLoading: !user };
}
```

```jsx
// components/PrivateRoute.tsx
// La skill indica: usar Suspense para estados de carga
export function PrivateRoute({ children }: { children: React.ReactNode }) {
    const { user, isLoading } = useAuth();

    if (isLoading) return <Suspense fallback={<LoadingSpinner />} />;
    if (!user) return <Navigate to="/login" replace />;

    return children;
}
```

---

## Capa 8 — Pre-commit hook valida automáticamente

Al hacer `git commit`, el hook `.githooks/pre-commit` se ejecuta sin que
tengas que hacer nada:

```bash
[pre-commit] Ejecutando Biome en archivos JS/TS...
✅ hooks/useAuth.ts — OK
✅ components/PrivateRoute.tsx — OK
✅ components/LoginForm.tsx — OK

[pre-commit] Detectando secrets...
✅ Sin secrets detectados

[pre-commit] Todo correcto. Procediendo con el commit.
```

Si algo falla, el commit se bloquea y Claude ve el error en la terminal.

---

## Capa 9 — Pre-push hook ejecuta los tests completos

Al hacer `git push`, el hook `.githooks/pre-push` ejecuta:

```bash
[pre-push] Ejecutando tests PHP...
....... (7 tests, 21 assertions)
✅ AuthTest: 7/7 pasando
✅ Cobertura: 84% (supera el mínimo de 80%)

[pre-push] Tests pasados. Procediendo con el push.
```

---

## Resumen del flujo completo

```
Tu prompt: /plan "auth con Sanctum"
    │
    ├── [Contexto activo]  CLAUDE.md + rules/ + skills embebidas del stack
    │
    ├── [Subagente 1]  planner        → plan de fases y riesgos
    │
    ├── [Subagente 2]  tdd-guide      → tests primero (RED)
    │
    ├── [Claude direct] implementación → guiada por laravel-patterns + laravel-tdd (GREEN)
    │
    ├── [Subagente 3]  code-reviewer  ─┐
    ├── [Subagente 4]  security-reviewer ┘ en paralelo
    │
    ├── [Claude direct] frontend React → guiado por frontend-patterns
    │
    ├── [Hook automático] pre-commit  → linting + secrets
    │
    └── [Hook automático] pre-push    → tests completos
```

---

## Qué no necesitaste hacer manualmente

- Recordarle a Claude las convenciones del proyecto
- Indicarle que usara thin controllers o FormRequests
- Pedirle que hiciera code review
- Pedirle que auditara seguridad
- Ejecutar el linter antes del commit
- Acordarte de los tests

Todo esto ocurre automáticamente porque está definido en las capas correctas:
CLAUDE.md para convenciones, rules/ para comportamiento de Claude, skills embebidas en los agentes
para estándares del stack, y githooks para enforcement local.
