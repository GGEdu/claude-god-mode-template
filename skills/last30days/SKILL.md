---
name: last30days
description: Investiga un tema en Reddit, HN, X y YouTube limitado a los últimos 30 días. Supera el knowledge cutoff del modelo con datos reales y actuales de la comunidad.
when: "Antes de /plan cuando la decisión implique elegir tecnología, librería o patrón — y siempre que quieras saber el estado actual de algo en el ecosistema"
---

Investiga **"$ARGUMENTS"** en fuentes actuales (últimos 30 días).

## Modo completo (si last30days-skill está instalado en `~/.claude/skills/last30days/`)

```bash
python ~/.claude/skills/last30days/scripts/run.py "$ARGUMENTS"
```

Presenta: top hallazgos ordenados por relevancia+recencia, con fuente y fecha.

## Modo degradado (sin instalación — funciona siempre vía WebSearch)

Realizar las siguientes búsquedas en paralelo:

1. `"$ARGUMENTS" site:reddit.com after:2025-01-01`
2. `"$ARGUMENTS" site:news.ycombinator.com after:2025-01-01`
3. `"$ARGUMENTS" best practices 2025`
4. `"$ARGUMENTS" site:github.com discussions after:2025-01-01`

## Output requerido

```markdown
## Estado actual: [tema]
Fecha de research: YYYY-MM-DD

### Consenso de la comunidad
1. [hallazgo principal con fuente y fecha]
2. [hallazgo secundario con fuente y fecha]
3. [hallazgo tercero con fuente y fecha]

### Cambios recientes o controversias
- [si aplica: cambio relevante, deprecación, nueva versión, debate activo]

### Fuentes
- [URL o referencia] — [fecha]
```

**Importante**: si no se encuentran datos suficientes (<2 fuentes relevantes), indicarlo explícitamente en lugar de rellenar con conocimiento del modelo.
