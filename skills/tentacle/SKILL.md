---
name: tentacle
description: Manage scoped work areas (.tentacles/) for multi-agent coordination. Create, list, and hand off context-isolated work areas that survive session restarts.
origin: internal
---

# /tentacle

Gestiona áreas de trabajo aisladas en `.tentacles/`. Cada área tiene su propio `CONTEXT.md` (contexto arquitectural persistente) y `todo.md` (estado de tareas local).

## Comandos

### `/tentacle create <nombre>`

Crea un nuevo área de trabajo con scaffold completo.

**Proceso:**
1. Verificar que `.tentacles/<nombre>/` no existe ya (si existe, informar y parar).
2. Crear la estructura:
   ```
   .tentacles/<nombre>/
   ├── CONTEXT.md    ← template pre-rellenado
   └── todo.md       ← vacío
   ```
3. Rellenar `CONTEXT.md` con el nombre del área, fecha actual, y preguntar al usuario:
   - ¿Cuál es el objetivo principal de esta área?
   - ¿De qué otras áreas depende?
4. Informar que `todo.md` es gitignored y `CONTEXT.md` se puede commitear.

**Template CONTEXT.md generado:**
```markdown
---
area: <nombre>
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: active
---

# <nombre>

## Estado actual
Área recién creada — sin progreso todavía.

## Decisiones tomadas
_Ninguna aún._

## Arquitectura local
_Por definir._

## Dependencias con otras áreas
_Por identificar._

## Sesión anterior terminó en
_Primera sesión — sin historial._

## Tareas pendientes
- [ ] Definir scope y acceptance criteria
```

---

### `/tentacle list`

Lista todas las áreas activas con su estado.

**Proceso:**
1. `ls .tentacles/` para descubrir áreas.
2. Para cada área (excepto `archive/`):
   - Leer el frontmatter de `CONTEXT.md` (status, updated)
   - Contar tareas pendientes en `todo.md` si existe
3. Mostrar tabla:

```
Área                  Estado    Última actualización   Tareas pendientes
──────────────────────────────────────────────────────────────────────
auth-refactor         active    2026-05-10             3
database-schema       paused    2026-04-28             7
frontend-components   done      2026-05-09             0
```

4. Si `.tentacles/` no existe → informar que no hay áreas y sugerir `/tentacle create <nombre>`.

---

### `/tentacle handoff <nombre>`

Prepara notas de handoff para que otro agente (o sesión) retome el área sin pérdida de contexto.

**Proceso:**
1. Leer `.tentacles/<nombre>/CONTEXT.md` completo.
2. Leer `.tentacles/<nombre>/todo.md` si existe.
3. Generar un resumen de handoff que incluya:
   - Estado actual en 2-3 frases
   - Última tarea completada
   - Próxima tarea a hacer (específica, con detalle suficiente para retomar sin contexto adicional)
   - Decisiones clave que el próximo agente debe conocer
   - Archivos tocados recientemente: `git log --oneline -10 -- $(git diff --name-only HEAD~10 HEAD 2>/dev/null | grep -v "^$")`
4. Escribir el resumen en `.tentacles/<nombre>/CONTEXT.md` bajo la sección `## Sesión anterior terminó en`.
5. Actualizar `updated:` en el frontmatter.

---

### `/tentacle archive <nombre>`

Archiva un área completada.

**Proceso:**
1. Verificar que `status: done` en `CONTEXT.md` (advertir si no).
2. Mover `.tentacles/<nombre>/` a `.tentacles/archive/<nombre>/`.
3. Agregar una línea de resumen al final de `.tentacles/archive/<nombre>/CONTEXT.md`:
   ```
   <!-- ARCHIVADO: YYYY-MM-DD — [resumen en 1 línea del trabajo realizado] -->
   ```
4. Verificar si el conocimiento de esta área debería promoverse al wiki del proyecto (`docs/src/wiki/`) — preguntar al usuario.

---

## Relación con otros sistemas

| Sistema | Propósito | Alcance |
|---------|-----------|---------|
| `.tentacles/<area>/CONTEXT.md` | Contexto scoped por área | Persistente, commiteado |
| `.tentacles/<area>/todo.md` | Estado de tareas del área | Local, gitignored |
| `.claude/memory/*.md` | Decisiones globales del proyecto | Persistente, comprimible |
| `docs/src/wiki/` | Conocimiento permanente del equipo | Permanente, commiteado |
| `TaskCreate` | Seguimiento in-session | Efímero, desaparece al cerrar |

## Cuándo usar tentacles vs memoria global

Usar **tentacles** cuando:
- La feature toca múltiples archivos en un área coherente
- Se espera trabajar en >1 sesión
- Hay otros agentes trabajando en paralelo en otras áreas
- Se necesita aislamiento de contexto para no contaminar otras áreas

Usar **`.claude/memory/`** cuando:
- La decisión afecta a todo el proyecto
- Es una regla de arquitectura global
- Es un constraint de negocio o compliance que aplica a todas las áreas
