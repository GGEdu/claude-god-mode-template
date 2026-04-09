---
name: design-md
description: Carga el sistema de diseño de una empresa como contexto visual para generar UI consistente con identidad profesional. Evita componentes genéricos sin personalidad.
when: "Al crear o refactorizar componentes UI, páginas, o sistemas de diseño — especialmente al inicio de un proyecto frontend"
---

Carga y aplica el sistema de diseño de **"$ARGUMENTS"** (ej: `linear`, `stripe`, `vercel`, `supabase`).

## Paso 1 — Buscar DESIGN.md local

```bash
# Buscar en el stack activo
find stacks/*/design/ -name "$ARGUMENTS.md" 2>/dev/null
# Buscar en memoria de sesión
ls .claude/memory/design-*.md 2>/dev/null
```

Si existe → leerlo directamente.

## Paso 2 — Si no existe localmente, obtener del repo remoto

Fetch desde:
```
https://raw.githubusercontent.com/VoltAgent/awesome-design-md/main/design-md/$ARGUMENTS/DESIGN.md
```

Guardar en `.claude/memory/design-$ARGUMENTS.md` para reusar durante la sesión.

## Paso 3 — Aplicar el sistema de diseño

Extraer y presentar los tokens clave:

```markdown
## Sistema de diseño: [empresa]

### Colores
- Primary: #hex — [uso]
- Background: #hex — [contexto]
- Text: #hex / #hex (dark)
- Accent: #hex — [cuándo usar]

### Tipografía
- Headings: [font-family, weight, size]
- Body: [font-family, weight, line-height]
- Code: [font-family]

### Espaciado y forma
- Border radius: [valores]
- Shadows: [valores]
- Spacing scale: [base unit]

### Principios de diseño
- [1-3 principios clave que guían las decisiones visuales]
```

Al generar componentes: aplicar estos tokens explícitamente. Indicar qué token se usa en cada decisión de diseño.

## Empresas disponibles (selección curada)

**Herramientas SaaS**: linear, stripe, vercel, supabase, figma, notion, raycast, cursor
**Big Tech**: apple, github, airbnb, spotify, uber
**Design-first**: tailwind, shadcn, radix

Para ver todas: `https://github.com/VoltAgent/awesome-design-md/tree/main/design-md`
