# Primeros pasos

::: info Prerequisito
Instalación completada ([ver instalación](/instalacion)). `make install` ejecutado, proyecto inicializado con `make init-project`.
:::

Este tutorial sigue un proyecto real de ejemplo: `blog-api` (Laravel REST API + React SPA).

---

## Abrir el proyecto

```bash
cd ~/proyectos/blog-api
claude
```

Claude lee `.claude/CLAUDE.md` automáticamente al iniciar.

---

## Antes de implementar → agente `planner`

```text
"Planifica: quiero añadir autenticación con Sanctum a la API"
```

El agente `planner` se activa automáticamente y genera un plan con fases, dependencias y riesgos antes de escribir código.

Salida típica:

```text
## Plan: Autenticación Sanctum

Fase 1: Configurar Sanctum (20 min)
  - Instalar laravel/sanctum
  - Publicar config
  - Migrar tabla personal_access_tokens

Fase 2: Endpoints de auth (45 min)
  - POST /api/login → devuelve token
  - POST /api/logout → revoca token
  - GET /api/me → usuario autenticado

Fase 3: Proteger rutas existentes (15 min)
  - Middleware auth:sanctum en rutas protegidas
  - Tests de auth en Feature/AuthTest.php

Riesgos: CORS en SPA, configurar stateful domains para cookies
```

---

## Desarrollar con TDD → agente `tdd-guide`

```text
"Implementa con TDD: endpoint POST /api/login con Sanctum"
```

El agente `tdd-guide` se activa automáticamente y guía el ciclo RED → GREEN → REFACTOR:

1. **RED** — escribe el test primero (debe fallar)
2. **GREEN** — implementa lo mínimo para que pase
3. **REFACTOR** — limpia sin romper los tests

El agente te dice exactamente qué test escribir primero:

```php
// tests/Feature/Auth/LoginTest.php
it('returns token on valid credentials', function () {
    $user = User::factory()->create(['password' => bcrypt('secret')]);

    $response = $this->postJson('/api/login', [
        'email' => $user->email,
        'password' => 'secret',
    ]);

    $response->assertOk()->assertJsonStructure(['token']);
});
```

---

## Revisar el código → `/jedi-review`

Después de escribir código importante:

```text
/jedi-review
```

Lanza 3 subagentes en paralelo (Kent Beck, Martin Fowler, Mike Acton). Cada uno analiza independientemente. Recibes un veredicto consolidado con las 3 acciones prioritarias.

Salida típica:

```text
## Jedi Review — AuthController.php

[KENT BECK] El controlador está limpio. Pero login/logout en el mismo
controlador viola SRP — extraer a AuthService.

[MARTIN FOWLER] $request->all() en línea 23 — siempre usar $request->validated().
El FormRequest LoginRequest no existe todavía.

[MIKE ACTON] Token generado sin nombre descriptivo: createToken('token').
Cambiar a createToken('spa-web') para identificar el origen.

Veredicto: B — funcional pero con 3 correcciones antes de PR.

Top 3 acciones:
1. Crear LoginRequest con validated() — bloquea mass assignment
2. createToken('spa-web') — identificación de token
3. Extraer lógica a AuthService — testeable de forma unitaria
```

---

## Auditoría de seguridad → `/security-scan`

Para código de autenticación, pagos o cualquier lógica crítica:

```text
/security-scan
```

Ejecuta una auditoría enfocada en OWASP Top 10 y configuración de seguridad:

- Revisión de inputs y validación
- Riesgos de auth/autorización
- Hallazgos de secretos o configuraciones peligrosas en `.claude/`
- Recomendaciones priorizadas por severidad

**Úsalo en:** auth, endpoints que manejan datos sensibles, cambios de permisos.

---

## Commit

```bash
git add -p                    # revisa cambios interactivamente
git commit -m "feat(auth): add Sanctum token authentication"
git push
```

---

## Post-deploy → `/canary-watch`

Después de desplegar a producción o staging:

```text
/canary-watch https://blog-api.tu-dominio.com
```

Playwright comprueba automáticamente:

- Errores de consola
- Peticiones de red fallidas
- Tiempos de carga
- Screenshots comparativos

Veredicto: `DEPLOY OK` / `INVESTIGAR` / `ROLLBACK`

---

## Flujo de trabajo completo

```text
Planificar:   "Planifica: [descripción del feature]"   → agente planner
Desarrollar:  "Implementa con TDD: [feature]"          → agente tdd-guide
Revisar:      /jedi-review  + /security-scan para código crítico
Commit:       git add -p && git commit
Post-deploy:  /canary-watch https://url-produccion
Memoria:      automática — el Stop hook actualiza .claude/memory/ al terminar
```

---

## Referencia rápida de comandos

- `"Planifica: [descripción]"` — Antes de implementar cualquier feature (activa agente `planner`)
- `"Implementa con TDD: [feature]"` — Desarrollo con test-driven development (activa agente `tdd-guide`)
- `/jedi-review` — Revisión experta del código escrito
- `/security-scan` — Auditoría de seguridad para código crítico
- `/canary-watch url` — Post-deploy para verificar producción
- `/compact` — Liberar contexto después de explorar
