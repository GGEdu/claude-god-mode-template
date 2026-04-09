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
- `/workflow` (lists available workflows)

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
| `parallel_with` | string | Run in parallel with named agent |
| `always` | bool | Run even if previous steps failed |
| `continue_on_failure` | bool | Don't stop pipeline if this step fails |

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
