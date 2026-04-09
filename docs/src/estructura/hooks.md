# Directorio: `hooks/`

El directorio contiene **1 hook de Claude Code**: `session-consolidate.sh`, que se ejecuta automáticamente al final de cada sesión (evento `Stop`).

---

## `session-consolidate.sh`

**Propósito:** Al finalizar una sesión de Claude Code, analiza la actividad git del proyecto y genera/actualiza archivos de memoria en `.claude/memory/` con los hallazgos clave.

### Cuándo se ejecuta

Configurado como hook `Stop` en `~/.claude/settings.json`:

```json
{
  "hooks": {
    "Stop": [{
      "hooks": [{
        "type": "command",
        "command": "$HOME/.claude/hooks/session-consolidate.sh"
      }]
    }]
  }
}
```

Se dispara cuando Claude Code termina una respuesta completa (no en mid-stream).

### Flujo completo

```
sesión termina
      ↓
Stop hook dispara session-consolidate.sh
      ↓
¿CLAUDE_CONSOLIDATION_RUNNING=1? → salir (anti-recursión)
      ↓
¿Existe .claude/ en el directorio actual? → si no, salir
      ↓
Recopilar contexto git:
  - git log (últimos commits)
  - git diff HEAD~1 (cambios recientes)
  - git status (estado actual)
      ↓
Llamar al modelo Haiku con max 5 turns
(prompt: analiza actividad + genera/actualiza memoria)
      ↓
Escribir hasta 4 archivos .md en .claude/memory/
      ↓
Rotar log si >200 líneas → ~/.claude/hooks/session-consolidate.log
```

### Guard de anti-recursión

```bash
export CLAUDE_CONSOLIDATION_RUNNING=1
```

La variable de entorno previene que el propio Claude Code (invocado por el hook) dispare otro hook `Stop`, creando un bucle infinito.

### Condiciones de ejecución

El hook solo actúa si el directorio de trabajo tiene un subdirectorio `.claude/`. Esto lo limita a proyectos con Claude Code configurado, evitando generar memoria en directorios arbitrarios.

### Formato de los archivos de memoria generados

El hook instruye a Haiku a escribir archivos con este frontmatter YAML:

```markdown
---
name: <título descriptivo>
description: <una línea — para decidir relevancia futura>
type: <user | feedback | project | reference>
updated: <YYYY-MM-DD>
---

[contenido de la memoria]
```

### Límites de uso

| Parámetro | Valor |
|-----------|-------|
| Modelo | `claude-haiku-4-5` |
| Max turns | 5 |
| Max archivos por sesión | 4 |
| Log path | `~/.claude/hooks/session-consolidate.log` |
| Rotación del log | >200 líneas → conservar últimas 100 |

### Log de ejecución

Cada invocación escribe en `~/.claude/hooks/session-consolidate.log`:

```
[2026-04-08 15:42] session-consolidate: iniciando en /home/user/my-project
[2026-04-08 15:42] session-consolidate: memoria generada — 2 archivos escritos
```

### Archivos de memoria típicos generados

| Archivo | Tipo | Contenido |
|---------|------|-----------|
| `project_overview.md` | project | Estado actual del proyecto, decisiones recientes |
| `agents.md` | reference | Inventario de agentes activos y sus skills |
| `skills.md` | reference | Skills activas en el stack actual |
| `improvement-plan.md` | project | Hoja de ruta y mejoras identificadas |

> **Nota:** Estos archivos son gitignored (`.claude/memory/*.md`). Son contexto volátil de sesión. El contenido estable debe documentarse en `docs/src/estructura/`.

### Instalación

El hook se instala globalmente con `make install`:

```bash
cp hooks/session-consolidate.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/session-consolidate.sh
```

Y se registra en `~/.claude/settings.json` (también instalado por `make install`).
