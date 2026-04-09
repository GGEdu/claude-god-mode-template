# Next.js 15 — Reglas del stack

## App Router

- Usar **App Router** por defecto — no Pages Router
- Server Components por defecto; Client Components (`'use client'`) solo cuando se necesita interactividad o hooks del navegador
- Layouts en `app/layout.tsx`, páginas en `app/[ruta]/page.tsx`
- Metadata con `export const metadata` o `generateMetadata()` — no `<Head>`

## Data Fetching

- **Server Components** para fetching inicial de datos — `async/await` directamente en el componente
- **React Query / SWR** para datos en Client Components que requieren revalidación o mutaciones
- **Server Actions** para mutaciones: formularios, operaciones CRUD
- Nunca `useEffect` + `fetch` para data fetching inicial — usar Server Components

```typescript
// CORRECTO: fetch en Server Component
async function ProductPage({ params }: { params: { id: string } }) {
  const product = await getProduct(params.id); // función con cache de Next.js
  return <ProductDetail product={product} />;
}

// CORRECTO: Server Action para mutación
'use server'
async function createProduct(formData: FormData) {
  const product = await db.product.create({ data: { name: formData.get('name') } });
  revalidatePath('/products');
}
```

## Rendering y Performance

- `React.cache()` para deduplicar requests en el mismo render
- `unstable_cache` para caché persistente entre requests
- `next/image` obligatorio para todas las imágenes — nunca `<img>` directa
- `next/font` para fuentes — evita layout shift
- Route groups `(group)/` para organizar sin afectar la URL
- Parallel Routes `@slot` para layouts complejos (dashboards)
- `loading.tsx` para Suspense boundaries en cada ruta

## TypeScript

- `strict: true` en `tsconfig.json`
- Nunca `any` — usar `unknown` cuando el tipo es genuinamente desconocido
- Tipos para params de rutas: `{ params: { id: string } }`
- `zod` para validación de inputs en Server Actions y API Routes

## API Routes

- Usar solo para webhooks, callbacks OAuth, y endpoints que requieren lógica específica de API
- Para la mayoría de operaciones, preferir Server Actions sobre API Routes
- Validación con zod en el body de la request antes de procesar

## Anti-patrones a evitar

- `'use client'` en un componente padre que envuelve toda la página
- Fetch de datos en `useEffect` cuando se puede hacer en Server Component
- `router.refresh()` como sustituto de `revalidatePath()` en Server Actions
- Usar `process.env` directamente en Client Components — expone variables al cliente
- Importar librerías pesadas en Client Components sin `dynamic()` con `ssr: false`
