---
name: workflow-runner
description: >-
  Execute predefined agent workflows from .claude/pipeline.yaml.
  Use when: the developer says /workflow <name>, "run workflow", "execute pipeline",
  or when starting a feature, hotfix, or refactor that has a defined pipeline.
  DO NOT USE when: the developer wants to run a single agent directly.
origin: ECC
---

# Workflow Runner

Execute multi-agent workflows defined in `.claude/pipeline.yaml`.

## Activation

Triggered by:
- `/workflow <name>` (e.g., `/workflow feature`, `/workflow hotfix`)
- `/workflow` or `/workflow --list` — lists available workflows from `.claude/pipeline.yaml`
- Auto-detection when the user says "implementa X", "add feature X", "crea X" without specifying a workflow

## List mode (`/workflow` or `/workflow --list`)

When invoked without a workflow name (or with `--list`), the runner prints a menu:

```
Workflows disponibles en .claude/pipeline.yaml:

  feature           Feature completa con planificación, TDD y revisión
  hotfix            Fix rápido con revisión mínima
  refactor          Mejora de código sin cambio de comportamiento
  security-audit    Auditoría de seguridad exhaustiva
  documentation    Actualización de documentación del proyecto
  review            Revisión profunda de código existente

Uso: /workflow <nombre>     (ej: /workflow feature)
     /workflow --list       (este menú)
     /workflow --describe <nombre>   (detalle de pasos)
```

**Implementación:** parsear `workflows:` keys del pipeline.yaml y mostrar nombre + description. No ejecutar ningún agente — solo descubrimiento.

## Describe mode (`/workflow --describe <name>`)

Imprime los steps del workflow nombrado para que el usuario sepa qué pasa al ejecutarlo:

```
Workflow: feature

Pasos:
  1. docs-lookup        Explorar codebase y documentación relevante
                        (continue_on_failure: true)
  2. planner            Crear plan de implementación
  3. tdd-guide          Escribir tests primero, luego implementar
  4. code-reviewer      Revisar calidad del código
  5. security-reviewer  Verificar vulnerabilidades
                        (parallel_with: code-reviewer)
  6. [audit]            Ejecutar verificaciones automáticas
  7. memory-consolidator Guardar decisiones en memoria
                        (always: true)

Total: 7 steps. Estimación: 15-30 min.
```

## Workflow Routing (FAST_PATH Integration)

When the user requests implementation without specifying a workflow, evaluate trivialidad before selecting:

**Trivial (FAST_PATH) criteria — ALL must be true:**
- Estimated files affected: 3 or fewer
- Estimated lines changed: 50 or fewer
- Does NOT involve auth, security, or payments
- Does NOT create a new module or service

**Routing decision:**
- If trivial -> use `hotfix` workflow (no plan, just TDD + review)
- If not trivial -> use `feature` workflow (full cycle with exploration and plan)

**Notification requirement:** ALWAYS announce the selected workflow before executing:
```
▶ Workflow seleccionado: {name} — {description}.
  Archivos estimados: ~N. Continuar? [Enter/n]
```

In autonomous mode (routines): the workflow MUST be declared explicitly in the routine prompt. Auto-detection is disabled — routines require deterministic prompts.

## Protocol

### 1. Load Pipeline

```bash
# Read the pipeline file
cat .claude/pipeline.yaml
```

If `.claude/pipeline.yaml` doesn't exist, inform the user:
> No pipeline.yaml found. Create one with workflow definitions, or use `make init-project` to generate defaults.

### 2. List Workflows (if no name given)

Display available workflows with descriptions:
```
Available workflows:
  feature  — Full feature implementation with TDD and review
  hotfix   — Quick fix with minimal review
  refactor — Code improvement without behavior changes
```

### 3. Execute Workflow

For the selected workflow, execute steps in order:

**Sequential steps** — run one after another, passing context forward.
**Parallel steps** — use `parallel_with` to run simultaneously (launch subagents in parallel).
**Audit steps** — run `ops/audit-task.sh` for automated checks.
**Memory steps** — trigger memory consolidation via memory-consolidator agent.

### Step Execution Protocol

For each step:

1. **Announce**: `"▶ Step N: {agent} — {description}"`
2. **Execute**: Invoke the agent as a subagent with the task context
3. **Capture**: Note key outputs/decisions from the agent
4. **Update memory**: Write a brief entry to `.claude/memory/` with what was done
5. **Check**: If step failed, STOP and report (unless `continue_on_failure: true`)

### 4. Audit Gate

If the workflow has `audit: true` steps:
```bash
bash ops/audit-task.sh . "workflow: {workflow_name}"
```

Report results. If audit FAILS:
- Show findings
- Ask developer: "Audit failed. Fix issues and retry? [y/n]"
- Do NOT proceed to next steps until audit passes

### 5. Summary

After all steps complete:
```
── Workflow Complete: {name} ──
  Steps executed: N/N
  Duration: ~Xm
  Audit: PASS/FAIL
  Memory: Updated
```

## Pipeline YAML Schema

```yaml
workflows:
  feature:
    description: "Full feature implementation with TDD and review"
    steps:
      - agent: planner
        description: "Create implementation plan"
      - agent: tdd-guide
        description: "Write tests first, then implement"
      - agent: code-reviewer
        description: "Review code quality"
      - agent: security-reviewer
        description: "Check for vulnerabilities"
        parallel_with: code-reviewer    # Runs at the same time as code-reviewer
      - audit: true
        description: "Run verification checks"
      - agent: memory-consolidator
        description: "Save learnings"
        always: true                    # Runs even if previous steps had issues
```

### Step Properties

| Property | Type | Description |
|----------|------|-------------|
| `agent` | string | Agent name to invoke |
| `audit` | bool | Run ops/audit-task.sh |
| `description` | string | What this step does |
| `parallel_with` | string | Run in parallel with named agent (one) |
| `parallel_with_agent` | string | Alias of `parallel_with`; use when fan-out is by agent name |
| `always` | bool | Run even if previous steps failed |
| `continue_on_failure` | bool | Don't stop pipeline if this step fails |
| `skill` | string | Activate this skill on the agent for this step (e.g. `requirements-stride`) |
| `outputs` | array<string> | File paths or directories the step is expected to produce |
| `approval_gate` | object | Pause after step until user confirms (see below) |

### Workflow-Level Properties

| Property | Type | Description |
|----------|------|-------------|
| `description` | string | Human-readable summary |
| `layer` | string | Layer that owns this workflow (e.g. `requirements-engineering`); only available when that layer is active |
| `re_entrant` | bool | Workflow may be invoked multiple times in the same project; each run logs as a separate entry |
| `steps` | array | Steps as documented above |

### `approval_gate` Object

```yaml
approval_gate:
  message: "Plan ready. Approve to proceed to TDD?"
  blocking: true   # default true; set false to allow auto-approval in autonomous mode
  on_reject: stop  # stop | retry | skip   (default: stop)
```

**Behavior:**

1. After the step finishes, print the `message` to chat.
2. Wait for user input. Accept `y` / `yes` / Enter to approve, `n` / `no` to reject.
3. If approved → continue to next step.
4. If rejected → apply `on_reject` (default: halt the workflow with a saved cursor in `.claude/state/<workflow>.yaml` for resumption).
5. In autonomous mode (`/loop` or scheduled triggers): if `blocking: true`, abort and notify; if `blocking: false`, auto-approve and log.

**Outputs verification:** if a step declares `outputs:`, verify each path exists after execution. If a declared output is missing and `continue_on_failure` is not true, mark the step as `incomplete` and trigger `on_reject`.

## Task-Level Memory

After each agent step completes, append to `.claude/memory/`:
```markdown
### {timestamp} — {workflow}/{step}
- Agent: {agent_name}
- Task: {description}
- Key decisions: {brief summary}
- Files modified: {list}
```

This ensures every task is captured individually, not just at session end.

## Error Handling

- If an agent fails or stalls: log the error, mark step as FAILED
- If audit fails: block subsequent steps, show developer findings
- If developer cancels: save progress to memory, note steps remaining
- Always run `always: true` steps regardless of failures
