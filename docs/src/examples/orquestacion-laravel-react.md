# Orquestación avanzada: GitHub Actions + Antigravity con Laravel + React

> **Prerequisito:** Haber completado el [tutorial TaskFlow](/examples/tutorial-laravel-react) o tener un proyecto inicializado con `make init-project STACK=laravel LAYERS=react PROJECT=/ruta`.
>
> Este tutorial cubre lo que ocurre **fuera de tu sesión local**: cómo Claude Code sigue trabajando en CI/CD, en cron, y publicando resultados a GitHub — sin que tú hagas nada.

---

## Los tres modos de ejecución

Hasta ahora has visto agentes locales (dentro de Claude Code en tu terminal). Hay dos modos más:

| Modo | Cuándo se ejecuta | Quién lo ve | Herramienta |
|------|-------------------|-------------|-------------|
| **Local** | Cuando tú lo pides en la sesión | Solo tú | `Agent` tool en Claude Code |
| **GitHub Actions** | En cada PR, push, o cron de CI | Todo el equipo (comentarios en PR/Issues) | `.github/workflows/agent-*.yml` |
| **Antigravity** | Cron autónomo (sin CI, sin sesión abierta) | Tú (archivo en `ops/sessions/`) | `CronCreate` / `RemoteTrigger` en Claude Code |

La diferencia clave: GitHub Actions requiere un repositorio con CI. Antigravity no — funciona incluso en repos privados sin Actions configurado.

---

## Parte 1 — GitHub Actions: el equipo también tiene agentes

### Qué instala `make init-project`

Al inicializar el proyecto, se copian 3 workflows en `.github/workflows/`:

```
.github/workflows/
├── agent-pr-review.yml       ← Se activa en cada PR abierto o actualizado
├── agent-issue-triage.yml    ← Se activa cuando un issue recibe el label "needs-plan"
└── agent-scheduled-audit.yml ← Lunes 09:00 UTC — auditoría automática
```

### Setup inicial (una sola vez)

Antes de que funcionen, necesitas añadir tu API key como secret en GitHub:

```
GitHub repo → Settings → Secrets and variables → Actions → New repository secret

Nombre: ANTHROPIC_API_KEY
Valor:  sk-ant-...
```

`GITHUB_TOKEN` lo proporciona GitHub automáticamente — no necesitas configurarlo.

### Escenario: abrir un PR en TaskFlow

Tu compañero abre un PR que añade el endpoint `PATCH /api/tasks/{id}/complete`:

```bash
git checkout -b feat/complete-task
# ... escribe código ...
git push -u origin feat/complete-task
gh pr create --title "feat: mark task as complete"
```

**Qué ocurre automáticamente:**

El workflow `agent-pr-review.yml` se dispara. En CI, Claude Code ejecuta dos agentes con `claude -p`:

```yaml
# Fragment de agent-pr-review.yml
- name: Code review (code-reviewer agent)
  run: |
    BASE=${{ github.event.pull_request.base.sha }}
    HEAD=${{ github.event.pull_request.head.sha }}

    claude -p \
      --allowedTools "Bash(git diff*),Bash(git log*),Read,Grep,Glob" \
      --model sonnet \
      "You are the code-reviewer agent. Review the changes in this PR.
      Run: git diff ${BASE}...${HEAD}
      Apply the full review checklist: CRITICAL/HIGH/MEDIUM/LOW.
      Output the complete review in markdown. Be concise — skip LOW issues."
    > /tmp/code-review.md

- name: Security review (security-reviewer agent)
  run: |
    claude -p \
      --allowedTools "Bash(git diff*),Bash(git log*),Read,Grep,Glob" \
      --model sonnet \
      "You are the security-reviewer agent. Analyze the PR changes.
      Focus on OWASP Top 10: injection, auth bypasses, XSS, exposed secrets.
      Only report real findings. Output as markdown with severity labels."
    > /tmp/security-review.md
```

Primero corre `code-reviewer`, luego `security-reviewer`, y el resultado combinado se publica como comentario en el PR:

```
## Code Review — Claude Code Agents

✅ TaskController correctamente delgado — lógica en TaskService
✅ FormRequest valida el ID antes del handler
⚠️  HIGH: El método complete() no verifica si la tarea ya está completada
           → Añadir guard: if ($task->isComplete()) throw new TaskAlreadyCompleteException()
⚠️  MEDIUM: TaskCompletedEvent no se dispara — otros módulos no se enteran del cambio

---

## Security Review — Claude Code Agents

✅ Sanctum protege el endpoint (middleware auth:sanctum activo)
✅ Policy TaskPolicy@complete verifica ownership
⚠️  HIGH: Sin rate limiting en el endpoint — un usuario puede completar 1000 tareas/seg
          → Añadir throttle:60,1 en la ruta
```

Tu compañero recibe el review en el PR sin haber pedido nada. Antes de que hagas tu code review manual, los issues críticos ya están identificados.

### Triaje de issues con el agente planner

Cuando alguien crea un issue con el label `needs-plan`, el workflow `agent-issue-triage.yml` lanza el agente `planner` automáticamente:

```
Issue: "feat: exportar tareas a CSV"
Label: needs-plan
```

El agente lee el issue, analiza el codebase, y comenta en el issue con un plan de implementación completo: fases, archivos a modificar, riesgos, estimaciones. El desarrollador que lo vaya a implementar ya tiene el plan listo antes de abrir una sesión.

---

## Parte 2 — Antigravity: Claude trabaja mientras duermes

### Qué es Antigravity

Antigravity ejecuta prompts de Claude Code en un cron, sin que tengas una sesión abierta y sin necesitar GitHub Actions. Es útil para proyectos personales, repos privados, o cuando quieres que los resultados vayan a `ops/sessions/` en lugar de a GitHub.

Los triggers se definen como archivos YAML en `ops/triggers/`.

### El trigger de auditoría semanal (ya incluido)

El template incluye `ops/triggers/weekly-security-audit.yaml`:

```yaml
name: weekly-security-audit
description: "Auditoría de seguridad semanal sobre archivos modificados en los últimos 7 días"
schedule: "0 9 * * 1"   # Lunes 09:00 UTC
model: sonnet
output: "ops/sessions/security-audit-$(date +%Y%m%d).md"
tags: [security, audit, weekly]

prompt: |
  You are the security-reviewer agent. Conduct a weekly security audit.

  Step 1 — Identify files changed in the last 7 days:
    Run: git log --since="7 days ago" --name-only --pretty=format: | sort -u | grep -v '^$'

  Step 2 — Review each relevant file for:
    - Hardcoded secrets, API keys, or credentials
    - Missing authentication or authorization checks
    - Input validation gaps (SQL injection, XSS, path traversal)
    - Insecure dependencies (check package.json / composer.json if modified)
    - CSRF vulnerabilities on state-changing endpoints

  Step 3 — Produce a markdown security audit report with:
    1. Executive summary (2-3 sentences)
    2. Findings table: File | Severity | Issue | Recommendation
    3. Action items (prioritized by severity)
    4. Files audited (count + list)

  Step 4 — Save the report to: ops/sessions/security-audit-YYYYMMDD.md

  If no critical or high findings: end with "✅ No critical findings this week."
```

### Añadir un trigger específico para Laravel

Para TaskFlow, quizás quieras auditar específicamente el código de autenticación y las rutas de API. Crea `ops/triggers/laravel-auth-audit.yaml`:

```yaml
name: laravel-auth-audit
description: "Auditoría semanal de autenticación y rutas API en el stack Laravel"
schedule: "0 10 * * 3"   # Miércoles 10:00 UTC
model: sonnet
output: "ops/sessions/laravel-auth-audit-$(date +%Y%m%d).md"
tags: [security, laravel, auth, weekly]

prompt: |
  You are the security-reviewer agent specialized in Laravel.
  
  Audit the following files:
  - app/Http/Controllers/AuthController.php
  - app/Services/AuthService.php
  - app/Http/Requests/ (all FormRequest files)
  - routes/api.php
  - config/cors.php
  - config/sanctum.php
  
  For each file, check:
  1. **Auth endpoints**: Are all state-changing routes protected by auth:sanctum?
  2. **Rate limiting**: Do login/register/password-reset routes have throttle middleware?
  3. **CORS**: Is allowed_origins set to a specific domain, not '*'?
  4. **Token scope**: Are Sanctum tokens created with descriptive names and limited abilities?
  5. **FormRequests**: Do all requests use ->validated() not ->all()?
  6. **Mass assignment**: Are $fillable arrays defined and not using $guarded = []?
  
  Produce findings as: File | Issue | Severity | Fix
  Save to: ops/sessions/laravel-auth-audit-YYYYMMDD.md
```

### Activar los triggers

Dentro de Claude Code, ejecuta:

```
make triggers-setup
```

Esto imprime los comandos `/schedule create` listos para pegar:

```
Paste these commands in Claude Code:

/schedule create weekly-security-audit \
  --cron "0 9 * * 1" \
  --prompt-file ops/triggers/weekly-security-audit.yaml

/schedule create laravel-auth-audit \
  --cron "0 10 * * 3" \
  --prompt-file ops/triggers/laravel-auth-audit.yaml
```

Pega cada línea en Claude Code para activarlos. Puedes verificar cuáles están activos:

```
/schedule list
```

```
Active schedules:
  weekly-security-audit    — cron: 0 9 * * 1  (next: Mon 2026-04-20 09:00 UTC)
  laravel-auth-audit       — cron: 0 10 * * 3 (next: Wed 2026-04-22 10:00 UTC)
```

### Output esperado

El lunes siguiente aparece en tu repo:

```
ops/sessions/security-audit-20260420.md
```

```markdown
# Security Audit — 2026-04-20

## Executive summary
3 archivos modificados esta semana. Se encontraron 2 issues de severidad HIGH
en la lógica de autenticación y configuración de CORS.

## Findings

| File | Severity | Issue | Recommendation |
|------|----------|-------|----------------|
| config/cors.php | HIGH | `allowed_origins` = `['*']` en producción | Cambiar a `[env('FRONTEND_URL')]` |
| app/Http/Controllers/AuthController.php | HIGH | Endpoint /login sin rate limiting | Añadir `throttle:5,1` |
| app/Services/TokenService.php | MEDIUM | Token creado sin abilities | Definir `->createToken('spa', ['tasks:read', 'tasks:write'])` |

## Action items
1. [URGENT] Restringir CORS en config/cors.php
2. [URGENT] Añadir throttle:5,1 a rutas /login y /register
3. [MEDIUM] Añadir token abilities a Sanctum

## Files audited (3)
- app/Http/Controllers/AuthController.php
- app/Services/TokenService.php  
- config/cors.php

✅ No hardcoded secrets found.
```

---

## Parte 3 — github-orchestrator: publicar a GitHub

Si quieres que el output de Antigravity llegue al equipo como GitHub Issue (no solo como archivo local), usas el agente `github-orchestrator`.

### Escenario: convertir el audit en un issue

Después de ver `ops/sessions/security-audit-20260420.md`, le pides a Claude:

```
Usa el agente github-orchestrator para crear un issue con los hallazgos de
ops/sessions/security-audit-20260420.md. Label: "security-audit". 
Asigna a @ggarrido.
```

El agente lee el archivo, comprueba que no existe ya un issue con el mismo título de esta semana (previene duplicados), y crea el issue:

```
✅ Issue creado: #47 "Security Audit — 2026-04-20"
   Labels: security-audit, high-priority
   Assignee: @ggarrido
   URL: https://github.com/miorg/taskflow/issues/47
```

También puedes automatizarlo desde el trigger YAML añadiendo un paso final al prompt:

```yaml
prompt: |
  # ... (pasos de auditoría anteriores) ...
  
  Step 5 — If findings include CRITICAL or HIGH severity:
    Use the github-orchestrator agent to create a GitHub Issue with:
    - Title: "Security Audit — YYYY-MM-DD"
    - Label: security-audit
    - Body: the full findings table + action items
    - Skip if an issue with this exact title already exists this week
```

---

## Flujo completo integrado

```
Developer hace push → abre PR
    │
    └── GitHub Actions: agent-pr-review.yml
            ├── code-reviewer (code quality)
            └── security-reviewer (OWASP)
                    │
                    └── Comentario automático en el PR
                            (team lo ve antes del merge)

Lunes 09:00 UTC (sin nadie conectado)
    │
    └── Antigravity: weekly-security-audit
            └── security-reviewer analiza últimos 7 días
                    │
                    └── ops/sessions/security-audit-YYYYMMDD.md

Miércoles 10:00 UTC (sin nadie conectado)
    │
    └── Antigravity: laravel-auth-audit
            └── security-reviewer audita auth + rutas API
                    │
                    └── ops/sessions/laravel-auth-audit-YYYYMMDD.md
                                │
                                └── github-orchestrator → Issue en GitHub
                                        (si hay hallazgos HIGH/CRITICAL)
```

---

## Qué no necesitaste hacer manualmente

- Recordar hacer code review en cada PR del equipo
- Ejecutar auditorías de seguridad semanales
- Crear issues de seguimiento de vulnerabilidades
- Leer logs de CI para ver si el PR pasó los checks de calidad
- Acordarte de revisar la configuración de CORS o rate limiting

Todo esto ocurre porque los tres modos de ejecución están configurados en capas:
el equipo tiene cobertura en CI (GitHub Actions), el repo tiene vigilancia autónoma
(Antigravity), y los resultados fluyen al backlog del equipo (github-orchestrator).
