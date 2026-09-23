---
name: effort-control
description: Control Claude Code's cost/speed trade-off using /effort levels. Use before starting a workflow or complex task to set the reasoning budget. Levels — low, medium, high, xhigh, max (from cheapest/fastest to deepest/most expensive).
disallowed-tools:
  - Write
  - Edit
  - NotebookEdit
---

# Effort Control

Set the reasoning effort level for the current task using `/effort`. This controls how much extended thinking Claude applies before acting.

## Levels

Real levels (`claude --help` → `--effort <level>`): `low`, `medium`, `high`, `xhigh`, `max`.
Set them with `/effort <level>` in a session or `claude --effort <level>` at launch.

| Level | Best For |
|-------|----------|
| `low` | Mechanical edits, renames, formatting, quick lookups |
| `medium` | Routine fixes and documentation on a clear, reversible path |
| `high` | Everyday feature work spanning a few files |
| `xhigh` | Complex features, security review, hard-to-reproduce bugs, refactors with broad side effects |
| `max` | Architecture decisions, pre-release security scan, auth/payments/core-data PRs; mistakes expensive to reverse |

## Pairing with Workflow Runner

Set effort before invoking a workflow to amplify the entire pipeline:

```
/effort max
/workflow security-audit
```

```
/effort xhigh
/workflow feature
```

For routine hotfixes, leave at default — max is expensive and unnecessary for small changes.

## Cost Implications

- `xhigh` spends noticeably more reasoning than `high` for the same task
- `max` uses the maximum reasoning budget — best reserved for high-stakes decisions
- `/effort` applies to the current session only

## Decision Matrix

```
Is this reversible in < 5 minutes?
  Yes → low or medium

Is this a security/auth/payment change?
  Yes → max

Does this span > 5 files or introduce a new architectural layer?
  Yes → xhigh or max

Is this a routine fix on a well-understood path?
  Yes → low or medium
```
