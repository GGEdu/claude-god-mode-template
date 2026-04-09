# [NOMBRE DEL PROYECTO]

## Stack
- **Frontend**: Nuxt 4 + Vue 3 (Composition API)
- **Backend**: Nitro (server routes)
- **Base de datos**: PostgreSQL
- **Tests**: Vitest + Playwright
- **Linter**: ESLint + Prettier

## Arquitectura
[DESCRIPCIÓN: SaaS, portal, e-commerce, etc.]

## Convenciones
- Commits: Conventional Commits
- Tests: mínimo 80% cobertura
- Composition API con `<script setup>` — no Options API
- `useFetch` / `useAsyncData` para data fetching — no `$fetch` en componentes

## Comandos críticos
- `/plan` — Antes de implementar cualquier feature
- `/tdd` — Ciclo RED-GREEN-REFACTOR
- `/design-md` — Al crear componentes UI

## Estructura del proyecto
```
app/
├── pages/               ← File-based routing
├── components/          ← Vue components
├── composables/         ← Composable functions (use*)
├── layouts/             ← Layout components
└── middleware/          ← Route middleware
server/
├── api/                 ← API routes (Nitro)
├── middleware/          ← Server middleware
└── utils/               ← Server utilities
```

## Variables de entorno necesarias
- `NUXT_PUBLIC_API_BASE` — URL base de API
- `DATABASE_URL` — postgres://...
- `NUXT_SESSION_SECRET` — Secreto de sesión

## Notas del proyecto
[AGREGAR: módulos Nuxt instalados, integraciones, etc.]
