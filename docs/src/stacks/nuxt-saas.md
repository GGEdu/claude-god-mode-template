# Stack: Nuxt SaaS

**Versiones:** Nuxt 4 · Vue 3 · Nitro · PostgreSQL · Vitest · Playwright

## Inicializar

```bash
make dev-stack STACK=nuxt-saas
```

Activa: reglas Nuxt SaaS, slash commands, CLAUDE.md con plantilla.

---

## Slash commands activados

| Comando | Cuándo usarlo |
| --- | --- |
| `/jedi-review` | Para código crítico (3 expertos: Beck, Fowler, Acton) |
| `/git-workflow` | Workflow de commits y PRs |
| `/workflow-runner <nombre>` | Ejecutar pipelines (`feature`, `hotfix`, `refactor`) |
| `/canary-watch URL` | Monitoreo post-deploy en staging/producción |
| `/security-scan` | Auditoría de seguridad de configuración y `.claude/` |
| `/design-md` | Aplicar dirección visual (Tailwind, DaisyUI guidelines) |
| `/codebase-onboarding` | Generar guía de onboarding del repo |

Las prácticas `vue3-patterns`, `nuxt-composables`, `form-handling`, `api-layer` y `performance-optimization` se aplican como skills embebidas en los agentes del stack.

---

## Convenciones clave

### Arquitectura — Pages, Components, Composables

```text
app/
├── app.vue                 ← Componente raíz
├── pages/
│   ├── index.vue          ← / (landing)
│   ├── auth/
│   │   ├── login.vue
│   │   └── signup.vue
│   ├── dashboard/
│   │   └── [[...slug]].vue
│   └── [...].vue          ← Catch-all for 404
├── components/
│   ├── auth/
│   │   ├── LoginForm.vue  ← Form logic en composable
│   │   └── SignupForm.vue
│   ├── ui/
│   │   ├── Button.vue
│   │   ├── Card.vue
│   │   └── Modal.vue
│   └── layout/
│       ├── Header.vue
│       └── Sidebar.vue
├── composables/
│   ├── useAuth.ts         ← Auth state + mutations
│   ├── useForm.ts         ← Form validation + reset
│   ├── usePagination.ts   ← Paginated queries
│   └── useNotification.ts ← Toast/alert management
├── server/
│   ├── api/
│   │   ├── auth/
│   │   │   ├── login.post.ts
│   │   │   └── logout.post.ts
│   │   ├── users/
│   │   │   ├── index.get.ts
│   │   │   └── [id].delete.ts
│   │   └── middleware/
│   │       └── auth.ts
│   └── utils/
│       └── db.ts
├── middleware/
│   └── auth.ts            ← Cliente-side auth guard
├── layouts/
│   ├── default.vue
│   └── auth.vue
└── utils/
    ├── api.ts             ← Axios instance + interceptors
    └── validation.ts      ← Zod schemas
```

### Composable — Lógica reutilizable

```ts
// CORRECTO: composable con ref/reactive reactivos
import { ref, computed, watch } from 'vue'

export const useCounter = () => {
  const count = ref(0)
  const isEven = computed(() => count.value % 2 === 0)
  
  const increment = () => count.value++
  const decrement = () => count.value--
  
  watch(count, (newVal) => {
    console.log(`Count changed to ${newVal}`)
  })
  
  return { count, isEven, increment, decrement }
}

// En componente:
<script setup lang="ts">
const { count, isEven, increment } = useCounter()
</script>

<template>
  <div>
    <p>Count: {{ count }} ({{ isEven ? 'even' : 'odd' }})</p>
    <button @click="increment">Increment</button>
  </div>
</template>

// INCORRECTO: estado global con ref sin cleanup
const globalCount = ref(0)  // ← Memory leak si no se limpia
</script>
```

### API Routes — Nitro handlers

```ts
// server/api/users/index.get.ts
export default defineEventHandler(async (event) => {
  // Middleware de autenticación ejecutado automáticamente
  const user = await requireAuth(event)
  
  const { page = 1, limit = 20 } = getQuery(event)
  
  try {
    const users = await db.user.findMany({
      skip: (parseInt(page as string) - 1) * parseInt(limit as string),
      take: parseInt(limit as string),
    })
    
    const total = await db.user.count()
    
    return {
      success: true,
      data: users,
      meta: { page, limit, total }
    }
  } catch (err) {
    throw createError({
      statusCode: 500,
      message: 'Failed to fetch users'
    })
  }
})

// server/api/users/[id].delete.ts
export default defineEventHandler(async (event) => {
  const user = await requireAuth(event)
  const id = getRouterParam(event, 'id')
  
  if (!id) {
    throw createError({ statusCode: 400, message: 'ID required' })
  }
  
  // Verificar autorización
  const targetUser = await db.user.findUnique({ where: { id } })
  if (!targetUser || (user.id !== id && user.role !== 'admin')) {
    throw createError({ statusCode: 403, message: 'Forbidden' })
  }
  
  await db.user.delete({ where: { id } })
  
  return { success: true }
})

// INCORRECTO: sin validación de entrada
export default defineEventHandler(async (event) => {
  const body = await readBody(event)  // ← Sin validación
  await db.user.create({ data: body })  // ← SQL injection risk
})
```

### Forms — Validación con Zod

```vue
<script setup lang="ts">
import { z } from 'zod'
import { useAsyncData } from '#app'

const loginSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(8, 'Mínimo 8 caracteres')
})

type LoginForm = z.infer<typeof loginSchema>

const form = reactive<LoginForm>({
  email: '',
  password: ''
})

const errors = reactive<Partial<Record<keyof LoginForm, string>>>({})
const loading = ref(false)

const validateField = (field: keyof LoginForm) => {
  const fieldSchema = z.object({ [field]: loginSchema.shape[field] })
  const result = fieldSchema.safeParse({ [field]: form[field] })
  
  if (!result.success) {
    errors[field] = result.error.issues[0].message
  } else {
    delete errors[field]
  }
}

const handleSubmit = async () => {
  // Validar todo
  const result = loginSchema.safeParse(form)
  if (!result.success) {
    result.error.issues.forEach(issue => {
      const field = issue.path[0] as keyof LoginForm
      errors[field] = issue.message
    })
    return
  }
  
  loading.value = true
  try {
    await $fetch('/api/auth/login', {
      method: 'POST',
      body: form
    })
    navigateTo('/dashboard')
  } catch (err) {
    // Handle error
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <form @submit.prevent="handleSubmit">
    <div class="form-group">
      <label>Email</label>
      <input 
        v-model="form.email"
        type="email"
        @blur="validateField('email')"
        :class="{ 'error': errors.email }"
      />
      <span v-if="errors.email" class="error-text">{{ errors.email }}</span>
    </div>
    
    <div class="form-group">
      <label>Password</label>
      <input 
        v-model="form.password"
        type="password"
        @blur="validateField('password')"
        :class="{ 'error': errors.password }"
      />
      <span v-if="errors.password" class="error-text">{{ errors.password }}</span>
    </div>
    
    <button type="submit" :disabled="loading">
      {{ loading ? 'Logging in...' : 'Login' }}
    </button>
  </form>
</template>

// INCORRECTO: sin validación de entrada
<template>
  <form @submit.prevent="submitForm">
    <input v-model="email" placeholder="Email" />
    <input v-model="password" type="password" placeholder="Password" />
    <button type="submit">Login</button>
  </form>
</template>

<script>
const submitForm = async () => {
  await $fetch('/api/auth/login', { method: 'POST', body: { email, password } })
  // ← Sin validación, sin manejo de errores, email puede ser cualquier cosa
}
</script>
```

### useAuth — Composable de autenticación

```ts
// composables/useAuth.ts
export const useAuth = () => {
  const user = useState<User | null>('auth.user', () => null)
  const isAuthenticated = computed(() => user.value !== null)
  
  const login = async (email: string, password: string) => {
    try {
      const response = await $fetch('/api/auth/login', {
        method: 'POST',
        body: { email, password }
      })
      user.value = response.user
      return true
    } catch (error) {
      console.error('Login failed:', error)
      return false
    }
  }
  
  const logout = async () => {
    await $fetch('/api/auth/logout', { method: 'POST' })
    user.value = null
  }
  
  // Restaurar sesión en mount
  const restoreSession = async () => {
    try {
      const response = await $fetch('/api/auth/me')
      user.value = response.user
    } catch {
      user.value = null
    }
  }
  
  return { user, isAuthenticated, login, logout, restoreSession }
}

// app.vue
<script setup>
const { restoreSession } = useAuth()

onMounted(() => {
  restoreSession()
})
</script>
```

### Testing — Vitest + Playwright

```ts
// tests/composables/useAuth.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { useAuth } from '~/composables/useAuth'
import { ref } from 'vue'

describe('useAuth', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })
  
  it('should return null user initially', () => {
    const { user } = useAuth()
    expect(user.value).toBeNull()
  })
  
  it('should login successfully', async () => {
    global.$fetch = vi.fn().mockResolvedValue({
      user: { id: '1', email: 'test@example.com' }
    })
    
    const { login, user } = useAuth()
    const result = await login('test@example.com', 'password')
    
    expect(result).toBe(true)
    expect(user.value?.email).toBe('test@example.com')
  })
  
  it('should logout successfully', async () => {
    global.$fetch = vi.fn().mockResolvedValue({})
    
    const { logout, user } = useAuth()
    user.value = { id: '1', email: 'test@example.com' }
    
    await logout()
    expect(user.value).toBeNull()
  })
})

// tests/e2e/login.spec.ts (Playwright)
import { test, expect } from '@playwright/test'

test.describe('Login Flow', () => {
  test('should login with valid credentials', async ({ page }) => {
    await page.goto('http://localhost:3000/auth/login')
    
    await page.fill('input[type="email"]', 'test@example.com')
    await page.fill('input[type="password"]', 'password123')
    await page.click('button[type="submit"]')
    
    await page.waitForURL('**/dashboard')
    expect(await page.url()).toContain('/dashboard')
  })
  
  test('should show validation errors', async ({ page }) => {
    await page.goto('http://localhost:3000/auth/login')
    
    await page.fill('input[type="email"]', 'invalid')
    await page.click('button[type="submit"]')
    
    const errorText = await page.textContent('.error-text')
    expect(errorText).toContain('Email inválido')
  })
})
```

---

## Anti-patrones a evitar

- **Lógica de negocio en componentes** — extraer a composables
- **$fetch directo en componentes** — usar composables o server routes
- **Sin validación de entrada en forms** — siempre Zod + validación server
- **`useState` sin namespace** — usar nombres únicos `useState('key.subkey')`
- **Queries N+1 en server routes** — usar `include` / `select` en Prisma
- **Sin middleware de autenticación** — verificar `requireAuth(event)` en todas las rutas protegidas
- **Paginación sin límite** — siempre `skip` y `take` explícitos
- **Sin manejo de errores en server routes** — usar `createError` con statusCode
- **Componentes sin `<script setup>`** — sintaxis legacy, usar setup script

---

## Comandos útiles

```bash
# Desarrollo
npm run dev                 # Inicia dev server en :3000

# Tests
npm run test               # Vitest
npm run test:coverage      # Con coverage
npm run test:e2e           # Playwright E2E

# Build
npm run build
npm run preview            # Previewear el build

# Lint / Format
npm run lint
npm run format

# Database
npx prisma migrate dev     # Aplicar migraciones
npx prisma studio         # UI para BD
```

## Variables de entorno

```bash
NUXT_PUBLIC_API_BASE=http://localhost:3000
DATABASE_URL=postgresql://user:pass@localhost:5432/saas_db

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=app-password

JWT_SECRET=super-secret-key-change-in-production
SESSION_TIMEOUT=3600

STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
```

---

## Ejemplo completo

→ [CLAUDE.md para Nuxt SaaS](/examples/nuxt-saas-CLAUDE)
