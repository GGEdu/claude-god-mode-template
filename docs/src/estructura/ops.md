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

- `make install` → compila los 38 agentes sin skills (instalación global)
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

## `generate-stacks.py`

**Propósito:** Genera los stacks con estructura consistente usando templates internos. Produce `stack.yaml` y `pipeline.yaml` para todos los stacks a partir de definiciones centralizadas en el script.

### Uso

```bash
python3 ops/generate-stacks.py
```

> **Nota:** Solo ejecutar si se necesita regenerar todos los stacks desde cero. Normalmente los stacks se editan directamente.

---

## `copy-commands.py`

**Propósito:** Copia los comandos slash (`.claude/commands/`) del stack activo al proyecto destino, aplicando overlays de layers y domains en orden.

### Uso

```bash
python3 ops/copy-commands.py <project_path> <stack_yaml> [overlay.yaml...]
```

Envuelto por `make init-project` — raramente se invoca directamente.

---

## `distribute-agents.py`

**Propósito:** Distribuye los agentes compilados a formatos alternativos: Antigravity (`.agent/skills/`) y GitHub Copilot (`.github/prompts/`). Excluye agentes que requieren MCP (solo funcionan en Claude Code).

### Uso

```bash
python3 ops/distribute-agents.py <stack.yaml> <agents_dir> <project_dir>
```

---

## `install-global.py`

**Propósito:** Instala en `~/.claude/` solo los agentes y skills que realmente se usan (referenciados en algún `stack.yaml` o `domain.yaml`). Evita instalar assets huérfanos globalmente.

### Uso

```bash
python3 ops/install-global.py ~/.claude
```

Envuelto por `make install`.

---

## `test-suite.py`

**Propósito:** Suite de tests integral. Inicializa cada stack en `proyectos/<stack>/`, verifica todos los archivos generados, testea cada skill embebida, y persiste el progreso en `.claude/memory/` para sobrevivir crashes.

### Uso

```bash
python3 ops/test-suite.py [--stack STACK] [--resume] [--domain DOMAIN] [--no-invoke] [--keep] [--verbose]
```

| Flag | Descripción |
|------|-------------|
| `--stack STACK` | Ejecutar solo ese stack |
| `--resume` | Reanudar desde el último checkpoint |
| `--domain DOMAIN` | Probar también un domain overlay |
| `--no-invoke` | Solo estructura + embed, sin invocaciones `claude --print` |
| `--keep` | Mantener directorios `proyectos/` tras los tests |
| `--verbose` | Mostrar detalles en fallos |

Envuelto por `make test-suite`.

---

## `cron/`

Scripts para auditorías periódicas ejecutadas vía cron en el servidor. Alternativa a los triggers de Antigravity cuando el servidor ya tiene LiteLLM local y se quiere prescindir de APIs externas.

### `weekly-audit.py`

**Propósito:** Auditoría semanal de seguridad vía LiteLLM. Lee los archivos críticos del repo y envía el contexto al modelo. Guarda el resultado en `ops/sessions/audit-YYYY-MM-DD.md`.

### Uso

```bash
# Ejecutar manualmente
python3 ops/cron/weekly-audit.py

# Con servidor LiteLLM alternativo
LITELLM_URL=http://192.168.1.19:4000 python3 ops/cron/weekly-audit.py
```

### Variables de entorno

| Variable | Default | Descripción |
|----------|---------|-------------|
| `LITELLM_URL` | `http://localhost:4000` | URL del servidor LiteLLM |
| `LITELLM_MODEL` | `cerebro-lite` | Alias del modelo |

### Archivos que audita

El script lee hasta 4 000 chars de cada archivo. Adaptar `AUDIT_FILES` al proyecto:

```python
AUDIT_FILES = [
    "src/api/main.py",
    "src/api/auth.py",
    "src/ingestion/main.py",
    "src/scraper/worker.py",
]
```

Los archivos no encontrados se documentan como `*archivo no encontrado*` en el reporte — no produce error.

### Output

Crea `ops/sessions/audit-YYYY-MM-DD.md` con formato markdown estructurado:

```markdown
# Auditoría semanal — 2026-05-19

## Resumen Ejecutivo
...

## Hallazgos (CRITICAL/HIGH/MEDIUM)
...

## Acciones recomendadas
...
```

### Instalación como cron

```bash
crontab -e
# Añadir (o copiar desde ops/cron/weekly-audit.cron):
0 9 * * 1 cd /root/myproject && python3 ops/cron/weekly-audit.py >> /var/log/audit.log 2>&1
```

El archivo `ops/cron/weekly-audit.cron` contiene el snippet listo para pegar.

### Cron vs Antigravity triggers

| Criterio | Cron en servidor | Antigravity trigger |
|----------|-----------------|---------------------|
| LiteLLM local disponible | ✅ Ideal — sin API keys externas | ❌ Runner externo no alcanza la LAN |
| Sin servidor propio | ❌ Requiere servidor | ✅ Solo necesita `ANTHROPIC_API_KEY` |
| Independencia de proveedor LLM | ✅ Cualquier modelo vía LiteLLM | ❌ Requiere Claude Code |
| Output local | ✅ Archivo en `ops/sessions/` | ✅ Igual |

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
| `weekly-repo-discovery.yaml` | Domingos 09:00 UTC | Descubre repos de GitHub con potencial para integración; screening Haiku de 12-15 candidatos; genera lista para deep-dive manual |

### Activación

```bash
make triggers-setup
# Imprime los comandos /schedule create para pegar en Claude Code
```

Los outputs se guardan en `ops/sessions/` con timestamp (gitignored por defecto).
