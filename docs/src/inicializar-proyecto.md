# Inicializar un proyecto

::: info Prerequisito
`make install` ejecutado en esta máquina ([ver instalación](/instalacion)).
:::

Funciona igual para proyectos nuevos y proyectos existentes. El comando copia la configuración de Claude Code dentro del proyecto sin modificar el código.

---

## Stacks disponibles

```bash
make list-stacks
```

```text
Stacks disponibles:

  cpp                  C++20 — CMake + GoogleTest
  flutter              Flutter 3 — Dart + Material/Cupertino
  go-api               Go — API REST o microservicio + PostgreSQL
  java-springboot      Java — Spring Boot 3 + PostgreSQL + Maven/Gradle
  kotlin-multiplatform Kotlin — Ktor backend + Compose Multiplatform + Android
  laravel              Laravel 13 (API REST) + MySQL + Sanctum + Pest
  ml-pytorch           Machine Learning — PyTorch + Python + CUDA
  nextjs-saas          Next.js 15 (App Router) + Supabase + Stripe
  nuxt-saas            Nuxt 4 — Vue 3 + Nitro + PostgreSQL
  odoo                 Odoo 19 — módulos Python + XML + OWL frontend + PostgreSQL 17
  perl                 Perl 5.36+ — Mojolicious/Dancer2 + PostgreSQL
  python-api           Python API — Django REST Framework o FastAPI + PostgreSQL
  rust-api             Rust — Axum/Actix Web + PostgreSQL
  swift-ios            Swift — SwiftUI + iOS/macOS/visionOS
```

---

## Inicializar el proyecto

```bash
make init-project STACK=laravel LAYERS=react PROJECT=/ruta/al/proyecto
```

Con domain overlay (opcional):

```bash
make init-project STACK=laravel LAYERS=react DOMAIN=healthcare PROJECT=/ruta/al/proyecto
```

Domains disponibles: `healthcare`, `ai-agent`, `content-creator`, `supply-chain`. Un domain añade skills especializadas a los agentes del tech stack (merge, no reemplazo).

Salida:

```text
Inicializando stack 'laravel' + layer 'react' + domain 'healthcare' en /ruta/al/proyecto...
  ✅ Stack rules copiadas a /ruta/al/proyecto/.claude/rules/stack/
  ✅ Domain rules copiadas a /ruta/al/proyecto/.claude/rules/stack/
  Compilando agentes con skills embebidas...
  ✅ Agentes compilados (22 agentes con skills del stack + domain)
  ✅ Comandos: /jedi-review, /git-workflow, /design-md, ...
  ✅ CLAUDE.md creado — edita los [PLACEHOLDER] con el contexto del proyecto
  ✅ Domain context appended to CLAUDE.md
```

Crea en el proyecto:

- `.claude/rules/stack/` — reglas del stack (+ domain si se indicó), activas en cada sesión automáticamente
- `.claude/commands/` — comandos standalone del stack como slash commands (`/jedi-review`, `/git-workflow`...)
- `.claude/agents/` — agentes **compilados** con skills embebidas del stack (y domain si aplica)
- `.claude/memory/` — directorio de memoria persistente
- `.claude/CLAUDE.md` — plantilla con `[PLACEHOLDER]` a rellenar
- `.claude/pipeline.yaml` — workflows orquestables (`/workflow feature`, `/workflow hotfix`)

Los agentes globales adicionales y el hook de memoria vienen de `~/.claude/` (instalados con `make install`).

---

## Rellenar el CLAUDE.md

Abre `.claude/CLAUDE.md` y reemplaza cada `[PLACEHOLDER]`:

```markdown
# Blog API

## Stack
- Backend: Laravel 13 + PHP 8.3
- Frontend: React 19 + TypeScript + Vite
- Base de datos: PostgreSQL 17
- Auth: Sanctum (SPA)
- Tests: Pest + Vitest
- Linters: Pint + Biome

## Arquitectura
API REST Laravel + SPA React. Autenticación por cookie Sanctum.
Posts, comentarios y usuarios. Panel admin en /admin.

## Decisiones de seguridad críticas
- CORS: solo blog.tudominio.com en producción
- Tokens Sanctum nombrados 'spa-web' para identificar origen
- Rate limiting: 5 intentos/minuto en /api/login

## Convenciones del equipo
- Commits: Conventional Commits (feat:, fix:, refactor:)
- Tests: mínimo 80% cobertura, Pest para Feature + Unit
- Fat controllers prohibidos: lógica en Services/

## Estructura
app/
  Http/Controllers/   ← controladores delgados
  Services/           ← lógica de negocio
  Http/Requests/      ← validación (FormRequest)
resources/js/         ← React SPA
tests/Feature/        ← tests de endpoints completos
tests/Unit/           ← tests de Services
```

**El CLAUDE.md es el contexto que Claude lee en cada sesión. Sin él, no tiene información del proyecto.**

---

## Configurar token de GitHub

```bash
echo "GITHUB_TOKEN=ghp_tu_token_aqui" > .env
echo ".env" >> .gitignore
```

---

## Verificar y hacer primer commit

```bash
# Verificar configuración
cd ~/ruta/al/template && make check

# Primer commit en el proyecto
cd /ruta/al/proyecto
git add .claude/
git commit -m "feat: inicializar proyecto con god-mode (stack: laravel, layer: react)"
```

---

## Primer arranque

```bash
cd /ruta/al/proyecto
claude
```

Claude lee `.claude/CLAUDE.md` automáticamente al arrancar. Si lo describe correctamente, todo está configurado.

Continúa en [Primeros pasos](/primeros-pasos) para el flujo de trabajo diario.

---

## Estructura del proyecto tras la inicialización

```text
blog-api/
├── .claude/
│   ├── CLAUDE.md              ← Contexto del proyecto (rellenar con datos reales)
│   ├── memory/                ← Memoria de sesiones (versionada en git)
│   ├── agents/                ← Agentes compilados con skills embebidas
│   ├── commands/              ← Slash commands standalone
│   ├── pipeline.yaml          ← Workflows orquestables
│   └── rules/
│       └── stack/             ← Reglas del stack + domain elegidos
│           ├── laravel.md
│           └── react.md
├── app/                       ← Código Laravel
├── resources/js/              ← React SPA
├── tests/
└── .env                       ← Secretos locales (en .gitignore)
```

Los agentes, comandos y reglas comunes viven en `~/.claude/` — aplican globalmente.

---

## MCPs opcionales

Activa solo lo que vayas a usar — cada MCP consume herramientas del contexto.

```bash
# Para investigar documentación externa con NotebookLM
make activate-notebooklm
# Reinicia Claude Code después

# Para automatizaciones con n8n
make activate-n8n
# Reinicia Claude Code después
```

Para desactivar y recuperar contexto:

```bash
make deactivate-notebooklm
make deactivate-n8n
```
