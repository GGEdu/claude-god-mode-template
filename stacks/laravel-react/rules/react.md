# React — Reglas del stack

## Arquitectura de componentes

- Componentes en `src/components/` — un archivo por componente
- Hooks customizados en `src/hooks/` — extraer toda lógica de estado fuera del JSX
- Contextos en `src/contexts/` — solo para estado verdaderamente global (auth, theme)
- Lógica de API en `src/services/` o `src/hooks/use*.ts` — nunca fetch directo en componentes

## Data fetching

- Usar SWR o React Query para todos los fetches — nunca `useEffect` + `useState` + `fetch`
- SWR deduplica requests automáticamente — aprovechar `mutate()` para actualizaciones optimistas
- Obtener CSRF cookie de Sanctum ANTES del primer POST: `await api.get('/sanctum/csrf-cookie')`
- Interceptor de Axios para manejar 401 globalmente y redirigir al login

## Performance

- Evitar waterfalls: cargar datos en paralelo con `Promise.all()` o `useSWR` múltiple
- `React.memo` solo cuando el profiler muestra re-renders innecesarios — no por defecto
- Importaciones dinámicas para rutas: `const Dashboard = lazy(() => import('./Dashboard'))`
- No usar barrel files (`index.ts` que re-exporta todo) — impide tree-shaking

## Formularios y validación

- React Hook Form para todos los formularios — evitar estado controlado manual
- Validación con Zod en el cliente + FormRequest en Laravel (validación doble)
- Mostrar errores de validación del backend inline en los campos correspondientes

## Rutas protegidas

- `PrivateRoute` wrapper que comprueba el estado de auth antes de renderizar
- Usar Suspense con fallback para estados de carga
- Redirigir al login con `state={{ from: location }}` para volver después del auth

## Testing (Vitest + Testing Library)

- Tests de componentes en `src/__tests__/` o junto al componente (`Component.test.tsx`)
- Usar `@testing-library/react` — nunca Enzyme
- Mockear las llamadas API con MSW (Mock Service Worker)
- Cada componente crítico tiene test de render, interacción y estado de error

## Anti-patrones a evitar

- `useEffect` para sincronizar estado derivado — calcular directamente en el render
- Prop drilling más de 2 niveles — usar Context o composición
- `any` en TypeScript — siempre tipos explícitos
- `console.log` en el código — usar el debugger o herramientas de desarrollo
