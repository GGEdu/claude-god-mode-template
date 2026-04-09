# Stack: Next.js 15 SaaS

**Versiones:** Next.js 15 (App Router) · TypeScript · Supabase · Stripe

## Inicializar

```bash
make dev-stack STACK=nextjs-saas
```

Activa: reglas Next.js 15 + Supabase, slash commands, CLAUDE.md con plantilla.

---

## Slash commands activados

| Comando | Cuándo usarlo |
| --- | --- |
| `/jedi-review` | Para código crítico (3 expertos: Beck, Fowler, Acton) |
| `/git-workflow` | Workflow de commits y PRs |
| `/workflow <nombre>` | Ejecutar pipelines (`feature`, `hotfix`, `refactor`) |
| `/canary-watch URL` | Monitoreo post-deploy en staging/producción |
| `/security-scan` | Auditoría de seguridad de configuración y `.claude/` |
| `/design-md` | Aplicar dirección visual en componentes/páginas |
| `/last30days` | Validar cambios recientes antes de planificar |

Además de los comandos anteriores, este stack incluye comandos universales (`/ck`, `/plankton-code-quality`, `/context-budget`, etc.).

Las prácticas como `frontend-patterns`, `nextjs-turbopack`, `api-design`, `database-migrations`, `security-review` y `e2e-testing` van embebidas en agentes y se aplican automáticamente cuando esos agentes se ejecutan.

---

## Convenciones clave

### App Router — principios

- **Server Components por defecto** — `'use client'` solo para interactividad real
- **Server Actions** para mutaciones: formularios, CRUD, operaciones críticas
- `async/await` directamente en Server Components para fetching inicial
- React Query / SWR solo en Client Components que requieren revalidación

### Supabase — seguridad

- **Siempre RLS habilitado** en todas las tablas
- `auth.uid()` como filtro base: `USING (auth.uid() = user_id)`
- `createServerClient` (del paquete `@supabase/ssr`) en Server Components
- `createBrowserClient` en Client Components
- Verificar sesión con `supabase.auth.getUser()` — nunca `getSession()` (no verifica el JWT)
- `SUPABASE_SERVICE_ROLE_KEY` **nunca** en el cliente frontend

### TypeScript

- `strict: true` en `tsconfig.json`
- Nunca `any` — usar `unknown` cuando el tipo es genuinamente desconocido
- Zod para validación en Server Actions y API Routes

---

## Anti-patrones a evitar

- `'use client'` en componentes wrapper que envuelven toda la página
- `useEffect + fetch` cuando se puede hacer en Server Component
- `router.refresh()` como sustituto de `revalidatePath()` en Server Actions
- `process.env.SECRET` directamente en Client Components
- Importar librerías pesadas en Client Components sin `dynamic()` con `ssr: false`
- Olvidar `revalidatePath()` o `revalidateTag()` después de una mutación

---

## Comandos útiles

```bash
# Desarrollo
npm run dev

# Build y análisis
npm run build
ANALYZE=true npm run build  # bundle analyzer

# Tests E2E
npx playwright test
npx playwright test --ui

# Supabase local
supabase start
supabase db diff --use-migra  # ver diff de schema
supabase migration new nombre_migracion
```

---

## Variables de entorno necesarias

```bash
NEXT_PUBLIC_SUPABASE_URL=https://xxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...   # Solo servidor, NUNCA al cliente
STRIPE_SECRET_KEY=sk_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

---

## Ejemplo completo

→ [CLAUDE.md para Next.js SaaS](/examples/saas-nextjs-CLAUDE)
