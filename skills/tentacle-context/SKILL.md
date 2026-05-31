---
name: tentacle-context
description: Isolated per-area context files for multi-agent coordination. Agents read and update .tentacles/<area>/CONTEXT.md before and after working, providing scoped persistent context that survives session restarts.
origin: internal
---

# Tentacle Context — Scoped Work Areas

**Problema que resuelve:** `.claude/memory/` es un pool global. Cuando múltiples agentes trabajan en paralelo en áreas distintas (auth, database, frontend), el contexto se mezcla. Los tentacles aislan el contexto por área de trabajo.

## Estructura de directorios

```
.tentacles/
├── auth-refactor/
│   ├── CONTEXT.md      ← contexto arquitectural (commiteado)
│   └── todo.md         ← estado de tareas (gitignored, local)
├── database-schema/
│   ├── CONTEXT.md
│   └── todo.md
└── archive/            ← áreas >30 días inactivas (auto-archivadas)
    └── old-feature/
        └── CONTEXT.md
```

## Protocolo para agentes

### Al comenzar a trabajar en un área

1. Determinar el área de trabajo. Si no está claro, inferirla del nombre de la feature o preguntarla.
2. Comprobar si existe contexto previo:
   ```bash
   cat .tentacles/<area>/CONTEXT.md 2>/dev/null
   ```
3. Si existe → leerlo completo antes de hacer cualquier otra cosa.
4. Si no existe → crearlo (ver formato abajo) antes de empezar.

### Al terminar de trabajar

Actualizar `.tentacles/<area>/CONTEXT.md` con:
- Decisiones tomadas en esta sesión
- Estado actual del área
- Dependencias detectadas con otras áreas
- Tareas pendientes para la próxima sesión

### Cuándo NO usar tentacles

- Tareas triviales de 1-2 archivos (hotfix workflow)
- Cambios que afectan el proyecto entero (usar `.claude/memory/` directamente)
- Cuando ya existe un CONTEXT.md global suficientemente específico

## Formato de CONTEXT.md

```markdown
---
area: <nombre del área>
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: active | paused | done
---

# <Nombre del Área>

## Estado actual
[Una línea: qué está hecho, qué está en progreso]

## Decisiones tomadas
- [YYYY-MM-DD] <decisión> — <razón>
- ...

## Arquitectura local
[Diagram o descripción de cómo funciona este área específicamente]

## Dependencias con otras áreas
- Depende de: [área] para [motivo]
- Provee a: [área] el [qué]

## Sesión anterior terminó en
[Punto exacto donde se paró — para que la próxima sesión retome rápidamente]

## Tareas pendientes
- [ ] [tarea específica]
- [ ] ...
```

## todo.md — superficie de delegación

El `todo.md` es el estado de las tareas locales del área. A diferencia de TaskCreate (efímero), survives between sessions.

```markdown
# Todo: <área>

## En progreso
- [ ] [tarea] — @agente-responsable

## Pendiente
- [ ] [tarea]

## Completado
- [x] [tarea] — [fecha]
```

**Regla:** `todo.md` es gitignored (estado local). `CONTEXT.md` se commitea (conocimiento arquitectural).

## Coordinación entre áreas paralelas

Cuando múltiples agentes trabajan simultáneamente:

1. Cada agente lee su `CONTEXT.md` de área al inicio.
2. Las dependencias cross-área se documentan en `Dependencias con otras áreas`.
3. Al detectar un conflicto o bloqueo → escribir en `CONTEXT.md` de la propia área y notificar al agente coordinador.
4. El agente coordinador (planner/architect) puede leer múltiples CONTEXT.md para tener una vista global:
   ```bash
   for f in .tentacles/*/CONTEXT.md; do echo "=== $f ==="; head -15 "$f"; done
   ```

## Worktree por área (opcional)

Para features de alto riesgo, cada tentacle puede tener su propio worktree git:

```bash
# Crear worktree para un área
git worktree add .tentacles/<area>/worktree -b feature/<area>

# Trabajar en el área (agente usa este path como CWD)
# Al terminar, merging al branch principal
git worktree remove .tentacles/<area>/worktree
```

Usar worktrees cuando:
- El área toca archivos que otro área también modifica
- Se necesita CI independiente por área
- Los cambios son experimentales y podrían revertirse
