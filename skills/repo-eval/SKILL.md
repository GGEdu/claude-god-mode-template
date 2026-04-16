---
name: repo-eval
description: "Evalúa repositorios GitHub para determinar si aportan valor al sistema (skills, agents, rules, stacks). Produce score 0-100 y propuesta de extracción estructurada."
origin: ECC
tools: Read, Bash, Glob, Grep
---

# Repo Eval

Rubrica para evaluar repos externos y decidir si deben integrarse como skills, agents
o patterns en este sistema. Opera en dos fases para minimizar el coste en tokens.

## Cuándo activar

- Antes de reimplementar funcionalidad que podría existir como skill/agent reutilizable
- Cuando el agente `repo-reviewer` procesa una URL
- En el trigger semanal `weekly-repo-discovery`

---

## Fase 1 — Screening rápido (modelo: Haiku, ~500 tokens)

**Input:** URL del repositorio
**Objetivo:** Score 0-100 en ≤ 500 tokens. Gate: si score < 50, parar aquí.

```bash
# Metadata del repo
gh repo view <owner/repo> --json name,description,stargazerCount,updatedAt,primaryLanguage,topics,licenseInfo

# Árbol de archivos (top level)
gh api repos/<owner>/<repo>/git/trees/HEAD --jq '.tree[] | select(.type=="tree" or (.type=="blob" and (.path | test("README|CLAUDE|SKILL|agent")))) | .path'

# README (base64 decode)
gh api repos/<owner>/<repo>/readme --jq '.content' | base64 -d | head -100
```

**Output esperado de Fase 1:**
```json
{
  "phase": 1,
  "url": "https://github.com/owner/repo",
  "scores": {
    "relevance": 0,
    "quality": 0,
    "extractability": 0,
    "integration_cost": 0,
    "total": 0
  },
  "tier": "INCLUDE|REVIEW|WATCH|SKIP",
  "proceed_to_phase2": true,
  "reason": "Una línea explicando el score"
}
```

---

## Fase 2 — Deep-dive (modelo: Sonnet, ~2500 tokens)

**Ejecutar solo si Fase 1 score ≥ 50**

```bash
# Estructura completa (limitada a paths relevantes)
gh api repos/<owner>/<repo>/git/trees/HEAD?recursive=1 \
  --jq '.tree[] | select(.path | test("skill|agent|rule|ops|hook|\.md$|\.yaml$|\.sh$")) | .path' \
  | head -50

# Leer archivos clave (máximo 5, priorizar: README, ejemplos de skills/agents, scripts)
gh api repos/<owner>/<repo>/contents/<path> --jq '.content' | base64 -d
```

**Analizar:**
- Patrones que mapean a `SKILL.md` (best practices, guidelines, workflows)
- Patrones que mapean a `agent.md` (roles especializados con herramientas)
- Reglas que mapean a `rules/*.md` (convenciones de código, seguridad, testing)
- Scripts que mapean a `ops/*.py` o `hooks/*.sh`
- Conflictos con los 130 skills existentes (`ls skills/` para verificar nombres)

**Output esperado de Fase 2:**
```json
{
  "phase": 2,
  "url": "https://github.com/owner/repo",
  "scores": {
    "relevance": 0,
    "quality": 0,
    "extractability": 0,
    "integration_cost": 0,
    "total": 0
  },
  "tier": "INCLUDE|REVIEW|WATCH|SKIP",
  "extracted": {
    "skills": [
      { "name": "slug-del-skill", "description": "una línea", "source_files": ["path/en/repo"] }
    ],
    "agents": [
      { "name": "slug-del-agent", "description": "una línea", "model": "haiku|sonnet|opus" }
    ],
    "rules": [
      { "name": "topic.md", "description": "una línea" }
    ],
    "patterns": ["descripción de patrón reutilizable"]
  },
  "risks": ["riesgo 1", "riesgo 2"],
  "license": "MIT|Apache-2.0|GPL-3.0|unknown",
  "integration_steps": [
    "Crear skills/<name>/SKILL.md con contenido extraído de <source_file>",
    "Añadir '<name>' a stacks/<stack>/stack.yaml bajo agents.<agent>.skills"
  ]
}
```

---

## Dimensiones de scoring (100 puntos total)

### 1. Relevancia (25 pts)
¿Cubre un gap real en los 130 skills existentes?

| Puntos | Criterio |
|--------|----------|
| 25 | Área no cubierta (0-1 skills relacionados) |
| 18 | Extiende área existente (2-4 skills relacionados) |
| 12 | Complemento no crítico |
| 6  | Nicho/muy específico |
| 0  | Duplicado exacto o fuera de scope |

**Check rápido:** `ls skills/ | grep -i <topic>` para ver cobertura actual.

### 2. Calidad (35 pts)

**Stars y madurez (10 pts):**
- ≥500 stars → 10 | 100-499 → 7 | 10-99 → 4 | <10 → 0

**Actividad reciente (10 pts):**
- Actualizado en últimos 30 días → 10
- 1-3 meses → 7 | 3-6 meses → 4 | >6 meses → 0

**Documentación (10 pts):**
- README excelente + ejemplos + tests → 10
- README bueno + ejemplos básicos → 7
- README mínimo → 4 | Sin README → 0

**Tests y CI (5 pts):**
- CI passing + cobertura >80% → 5
- CI presente → 3 | Tests sin CI → 1 | Sin tests → 0

### 3. Extractabilidad (20 pts)

**Claridad de patrones (10 pts):**
- Patrones claros y bien documentados → 10
- Algunos patrones, docs moderadas → 7
- Patrones implícitos, docs pobres → 3
- Caótico → 0

**Dependencias (5 pts):**
- Sin deps o deps estándar → 5
- Pocas deps conocidas → 3
- Muchas deps de nicho → 1
- Deps pesadas/complejas → 0

**Licencia (5 pts):**
- MIT, Apache 2.0, BSD → 5
- CC BY, ISC → 4
- GPL (verificar compatibilidad) → 2
- Propietaria/restrictiva → 0

### 4. Coste de integración (20 pts)

**Esfuerzo de adaptación (10 pts):**
- Drop-in: README → markdown directo → 10
- Adaptación ligera: renombrar, reestructurar → 7
- Refactor moderado: extraer snippets, reescribir parcialmente → 4
- Refactor pesado → 1 | Inviable → 0

**Carga de mantenimiento (5 pts):**
- Autocontenido, sin actualizaciones necesarias → 5
- Estable, actualizaciones ocasionales → 3
- En desarrollo activo con breaking changes → 1

**Riesgo de conflicto (5 pts):**
- Sin colisiones de nombre o concepto → 5
- Solapamientos menores manejables → 3
- Solapamientos significativos → 1
- Conflictos mayores → 0

---

## Tiers de decisión

### INCLUDE (score ≥ 80)
Generar template completo de SKILL.md/agent.md listo para copiar.
Incluir instrucciones exactas de dónde colocar cada archivo.

### REVIEW (score 50-79)
Generar propuesta parcial con elementos extractables identificados.
Marcar riesgos claramente. El usuario decide si vale el esfuerzo.

### WATCH (score 30-49)
Loguear en `ops/sessions/repo-evaluations.md` con tier WATCH.
No generar propuesta. Re-evaluar en 6 meses si el proyecto madura.

### SKIP (score < 30)
Loguear con razón. No re-evaluar. Blacklisted.

---

## Reglas de memoria

1. **Siempre leer primero** `ops/sessions/repo-evaluations.md` antes de evaluar
2. **Si URL ya existe** en el log: retornar resultado cacheado, no re-evaluar
3. **Exception:** forzar re-evaluación si el repo tiene >90 días desde la evaluación
   Y el usuario lo pide explícitamente
4. **Siempre actualizar** el log tras cada evaluación (incluso SKIP)

---

## Template de SKILL.md generado (output de Fase 2)

```markdown
---
name: <slug-extraído>
description: "<descripción de una línea extraída del repo>"
origin: "<owner>/<repo>"
tools: Read, Bash
---

# <Título del Skill>

> Extraído de: <URL>
> Licencia: <licencia>
> Integrado: <fecha>

## Cuándo usar

[Extraído del README / docs del repo]

## Patrones principales

[Contenido adaptado al formato del sistema]

## Ejemplos

[Ejemplos clave del repo, adaptados]
```

---

## Template de agent.md generado (output de Fase 2)

```markdown
---
name: <slug-extraído>
description: "<descripción con trigger claro de cuándo usarlo>"
tools: [Read, Bash, Grep, Glob]
model: sonnet
---

# <Nombre del Agente>

> Adaptado de: <URL>
> Licencia: <licencia>

## Rol

[Descripción del rol extraída/adaptada]

## Proceso

1. [Paso 1]
2. [Paso 2]
3. [Paso 3]

## Criterios de éxito

- [ ] Criterio 1
- [ ] Criterio 2
```
