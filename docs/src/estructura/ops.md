# Directorio: `ops/`

Los **scripts y herramientas operacionales** del template. Son herramientas de build, integración y automatización programada — el usuario raramente los invoca directamente (el `Makefile` los envuelve).

---

## `compile-agents.py`

**Propósito:** Lee `stack.yaml`, incrusta las skills asignadas en cada agente y escribe los agentes compilados al directorio destino.

### Uso

```bash
python3 ops/compile-agents.py <stack.yaml> <skills_dir> <agents_dir> <output_dir> [overlay.yaml...]
```

| Argumento | Descripción |
|-----------|-------------|
| `stack.yaml` | Declaración del stack (sección `agents:` con skills) |
| `skills_dir` | Directorio base de skills (normalmente `skills/`) |
| `agents_dir` | Directorio fuente de agentes (normalmente `agents/`) |
| `output_dir` | Destino de los agentes compilados (`.claude/agents/`) |
| `overlay.yaml...` | _(Opcional, múltiples)_ Layers o domains — se aplican en orden (layers primero, domain último) |

### Cómo funciona internamente

1. Lee la sección `agents:` de `stack.yaml` (formato dict con skills por agente)
2. Para cada overlay (layers + domain), llama a `merge_domain_skills()` — añade skills sin reemplazar las del stack
   - Si el overlay referencia un agente que no existe en el stack (ej. `typescript-reviewer` en `python-api`), lo **crea** con las skills del overlay
3. Para cada agente: lee `agents/<nombre>.md` + skills asignadas
4. Strips YAML frontmatter de cada `SKILL.md` antes de incrustar
5. Añade un bloque `# Embedded Skills Reference` al final del agente
6. Escribe el archivo compilado en `output_dir/<nombre>.md`

### Formato del bloque incrustado

```markdown
---

# Embedded Skills Reference

> These skills are loaded automatically as part of your expertise.
> Use this knowledge directly — the developer does NOT need to invoke them.

## Skill: laravel-tdd

[contenido de skills/laravel-tdd/SKILL.md]

## Skill: tdd-workflow

[contenido de skills/tdd-workflow/SKILL.md]
```

### Cuándo se ejecuta

- `make install` → compila los 22 agentes sin skills (instalación global)
- `make dev-stack STACK=x` → compila agentes con skills del stack para este repo
- `make dev-stack STACK=x LAYERS=react` → stack + layer técnico
- `make dev-stack STACK=x DOMAIN=y` → stack + domain overlay
- `make dev-stack STACK=x LAYERS=react DOMAIN=healthcare` → stack + layer + domain (triple composición)
- `make init-project STACK=x PROJECT=/ruta [LAYERS=...] [DOMAIN=...]` → compila en el proyecto destino

### Formatos soportados

```yaml
# Formato legacy (lista) — solo copia, sin skills
agents:
  - architect
  - planner

# Formato actual (dict) — con skills por agente
agents:
  architect:
    skills:
      - api-design
      - deployment-patterns
  planner:
    skills: []
```

---

## `detect-stack.py`

**Propósito:** Escanea un proyecto y detecta automáticamente cuál de los 15 stacks encaja mejor, usando un sistema de puntuación por marcadores. También detecta layers técnicos (ej. React) y los sugiere como `LAYERS=`.

### Uso

```bash
python3 ops/detect-stack.py <project_path> [stacks_dir]
python3 ops/detect-stack.py <project_path> --json   # salida JSON para pipes
```

| Exit code | Significado |
|-----------|-------------|
| `0` | Stack detectado — nombre impreso en stdout |
| `1` | Sin match o error |

### Sistema de marcadores

El script puntúa cada stack buscando archivos o contenido específico:

| Marcador | Contenido | Stack beneficiado | Puntos |
|----------|-----------|-------------------|--------|
| `go.mod` | — | go-api | +10 |
| `composer.json` | `laravel/framework` | laravel | +10 |
| `artisan` | — | laravel | +8 |
| `__manifest__.py` | — | odoo | +15 |
| `manage.py` | — | python-api | +8 |
| `requirements.txt` | `django` | python-api | +10 |
| `requirements.txt` | `fastapi` | python-api | +10 |
| `package.json` | `"next"` | nextjs-saas | +10 |
| `supabase/` | — | nextjs-saas | +5 |
| `.env` | `STRIPE` | nextjs-saas | +3 |

Además de los marcadores de stack, el script detecta **layer markers**: si encuentra `package.json` con `"react"` (score ≥ 5), sugiere `LAYERS=react` en la salida.

### Salida humana

```
🔍 Stack detectado: laravel
   Laravel 13 (API REST) + MySQL + Sanctum
   Score: 22

   Evidencia:
     +10 composer.json (contains 'laravel/framework')
     +8  artisan
     +4  composer.json (contains 'sanctum')

   Alternativas:
     python-api: score 5

   Layer detectado: react (package.json contains "react", score: 10)

STACK=laravel LAYERS=react
```

### Cuándo usarlo

```bash
# Detectar stack de un proyecto antes de init
python3 ops/detect-stack.py ~/my-project

# En un script (modo JSON)
DETECTED=$(python3 ops/detect-stack.py . --json | jq -r .detected)
```

---

## `audit-task.sh`

**Propósito:** Mini-auditoría post-tarea. Ejecuta 5 checks en <10 segundos y escribe el resultado en `.claude/memory/audit-log.md`.

### Uso

```bash
ops/audit-task.sh [project_path] [task_description]
```

| Argumento | Default |
|-----------|---------|
| `project_path` | `.` (directorio actual) |
| `task_description` | `"tarea sin nombre"` |

### Los 5 checks

| Check | Qué verifica | Resultado si falla |
|-------|-------------|-------------------|
| **Secrets scan** | Busca patrones `sk-*`, `AKIA*`, `ghp_*`, `password=*` en código fuente | ❌ FAIL |
| **Console.log** | >5 `console.log` en archivos TS/JS no-test | ⚠️ WARN |
| **Tests** | Corre `npm test` / `php artisan test` / `go test` / `pytest` según lo que detecte | ⚠️ WARN |
| **Lint** | Corre `npm run lint` si existe | ⚠️ WARN |
| **Git status** | Archivos modificados sin stage | ⚠️ WARN |

### Formato del log

El script añade entradas a `.claude/memory/audit-log.md`:

```markdown
### 2026-04-08 15:42 — implementar login
✅ PASS — 4/5 checks passed (1 warnings, 0 failures)
  ⚠️  GIT: 2 archivos modificados sin stage
```

El log se rota automáticamente a las últimas 100 líneas cuando supera 200 líneas.

### Exit codes

| Código | Condición |
|--------|-----------|
| `0` | Sin FAIL (puede haber warnings) |
| `1` | Al menos un check en FAIL (credenciales detectadas) |

### Cuándo se ejecuta

Se puede invocar manualmente o integrar en el `Stop` hook de Claude Code para que se ejecute al final de cada sesión.

---

## `triggers/`

Directorio con triggers para ejecución autónoma programada vía Antigravity. Cada archivo YAML define un trabajo que Claude Code ejecuta según un cron, sin sesión abierta.

### Formato de un trigger

```yaml
name: weekly-security-audit
description: "Auditoría semanal de seguridad"
schedule: "0 9 * * 1"   # cron UTC — lunes 09:00
model: sonnet
tags: [security, weekly]

prompt: |
  Eres el agente security-reviewer. Audita los archivos modificados
  en los últimos 7 días y guarda el reporte en ops/sessions/...
```

### Triggers incluidos

| Archivo | Schedule | Propósito |
| --- | --- | --- |
| `weekly-security-audit.yaml` | Lunes 09:00 UTC | Auditoría de seguridad de archivos modificados en 7 días |
| `weekly-docs-health.yaml` | Martes 09:00 UTC | Verifica que la documentación esté actualizada |
| `daily-memory-consolidation.yaml` | Diario 07:00 UTC | Consolida `.claude/memory/` si crece demasiado |

### Activación

```bash
make triggers-setup
# Imprime los comandos /schedule create para pegar en Claude Code
```

Los outputs se guardan en `ops/sessions/` con timestamp (gitignored por defecto).
