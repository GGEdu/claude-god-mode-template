---
paths:
  - "**/*.vue"
  - "**/*.ts"
  - "**/*.js"
---
# Nuxt 4 — Reglas del stack

## Componentes
- `<script setup lang="ts">` obligatorio — no Options API
- Props con `defineProps<{}>()` tipado — no runtime validation
- Emits con `defineEmits<{}>()` tipado
- `defineModel()` para v-model bidireccional

## Data Fetching
- `useFetch()` para requests SSR-safe con caching automático
- `useAsyncData()` para transformaciones complejas
- NUNCA `$fetch` en componentes — causa doble fetch (SSR + client)
- `useLazyFetch()` para datos no críticos (carga sin bloquear)

## Hydration Safety
- Sin `Date.now()`, `Math.random()` en setup — causan mismatch
- `<ClientOnly>` para contenido browser-only
- `useId()` para IDs estables entre SSR y client

## Performance
- Route rules para ISR/SWR: `routeRules: { '/api/**': { swr: 60 } }`
- `<NuxtLink>` con prefetch automático — no `<a>` para rutas internas
- Lazy components: `<LazyComponent>` para below-the-fold
- `definePageMeta({ middleware: [...] })` — no middleware global innecesario

## Anti-patrones
- `$fetch` en componentes (doble fetch en SSR)
- `onMounted` para datos que se pueden obtener en SSR
- Store global para estado de un solo componente
- Auto-imports sin awareness — conocer qué se importa
