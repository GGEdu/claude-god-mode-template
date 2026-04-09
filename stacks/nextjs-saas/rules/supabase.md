# Supabase — Reglas del stack

## Cliente SSR vs Client

- Usar `@supabase/ssr` — no el cliente básico de `@supabase/supabase-js`
- **Server Component / Route Handler**: `createServerClient` con cookies de `next/headers`
- **Client Component**: `createBrowserClient`
- **Middleware**: `createServerClient` con cookies del objeto `request`

```typescript
// Server Component
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'

export async function createClient() {
  const cookieStore = await cookies()
  return createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    { cookies: { getAll: () => cookieStore.getAll(), setAll: (cs) => cs.forEach(({ name, value, options }) => cookieStore.set(name, value, options)) } }
  )
}
```

## Row Level Security (RLS)

- **Siempre** habilitar RLS en todas las tablas — nunca acceso sin RLS en producción
- Policy mínima para usuario autenticado: `auth.uid() = user_id`
- Policies separadas para SELECT, INSERT, UPDATE, DELETE
- Nunca usar `service_role` key en el cliente frontend

```sql
-- CORRECTO: RLS para tabla de proyectos
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;

CREATE POLICY "users_own_projects" ON projects
  FOR ALL USING (auth.uid() = user_id);
```

## Auth con Next.js

- Middleware en `middleware.ts` para proteger rutas y refrescar sesiones
- Verificar sesión en Server Components con `supabase.auth.getUser()` — no `getSession()` (no verifica el JWT)
- Redirigir a `/login` desde middleware si no hay sesión en rutas protegidas
- Callback de OAuth en `app/auth/callback/route.ts`

## Storage

- Nunca subir archivos directamente al bucket `public` para datos de usuario — usar buckets privados con políticas RLS
- Signed URLs para acceso temporal a archivos privados
- Validar tipo MIME y tamaño antes de subir

## Edge Functions

- Para lógica que debe correr cerca del usuario o que necesita secretos del servidor
- No usar `SUPABASE_SERVICE_ROLE_KEY` en el cliente — solo en Edge Functions y Server Components
- Usar `Deno.env.get()` para variables de entorno en Edge Functions

## Variables de entorno obligatorias

```bash
NEXT_PUBLIC_SUPABASE_URL=https://xxxx.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJ...  # Segura para el cliente
SUPABASE_SERVICE_ROLE_KEY=eyJ...      # NUNCA exponer al cliente
```
