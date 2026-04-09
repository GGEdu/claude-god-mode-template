# [NOMBRE DEL PROYECTO]

## Stack
- **Framework**: Next.js 15 (App Router)
- **Backend**: API Routes + Server Actions
- **Base de datos**: PostgreSQL (Supabase)
- **Auth**: Supabase Auth
- **Pagos**: Stripe
- **Tests**: Vitest (unitarios) + Playwright (E2E)
- **Linter**: Biome

## Arquitectura
[DESCRIPCIÓN: qué hace este SaaS, quiénes son los usuarios y cuál es el flujo principal]

## Estructura del proyecto
```
app/
├── (auth)/             ← Rutas de login/signup (sin layout compartido)
├── (dashboard)/        ← Rutas protegidas para usuarios autenticados
│   ├── layout.tsx      ← Layout con sidebar/nav
│   └── [feature]/      ← Páginas por feature
├── api/                ← API Routes (webhooks, etc.)
└── layout.tsx          ← Root layout (providers)

components/
├── ui/                 ← Componentes genéricos (shadcn/ui)
└── [feature]/          ← Componentes específicos por feature

lib/
├── supabase/           ← Clientes Supabase (server/client/middleware)
├── stripe/             ← Helpers de Stripe y webhooks
└── utils/              ← Utilidades compartidas

actions/                ← Server Actions organizadas por dominio
```

## Seguridad
- RLS (Row Level Security) habilitado en todas las tablas de Supabase
- Webhooks de Stripe validados con firma (`STRIPE_WEBHOOK_SECRET`)
- Middleware protege todas las rutas de `/dashboard` — verificar sesión con Supabase SSR

## Convenciones
- Commits: Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`)
- Tests obligatorios: mínimo 80% cobertura en Server Actions y utilidades
- Server Components por defecto — usar `"use client"` solo cuando sea necesario
- Datos desde Supabase en Server Components; mutaciones via Server Actions

## Comandos críticos
- `/plan` — Antes de implementar cualquier feature
- `/tdd` — Ciclo RED-GREEN-REFACTOR
- `/jedi-review` — Para código crítico (auth, pagos, RLS)
- `/security-scan` — Antes de cada release (especialmente Stripe webhooks)

## Variables de entorno necesarias
- `NEXT_PUBLIC_SUPABASE_URL` — URL del proyecto Supabase
- `NEXT_PUBLIC_SUPABASE_ANON_KEY` — Clave anónima Supabase (pública)
- `SUPABASE_SERVICE_ROLE_KEY` — Clave de servicio Supabase (solo servidor)
- `STRIPE_SECRET_KEY` — Clave secreta de Stripe
- `STRIPE_WEBHOOK_SECRET` — Secreto para validar webhooks de Stripe
- `NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY` — Clave publicable de Stripe (frontend)
