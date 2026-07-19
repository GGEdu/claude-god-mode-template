---
name: effort-control
description: Control Claude Code's cost/speed trade-off using /effort levels. Use before starting a workflow or complex task to set the reasoning budget. Levels — standard (default), extra/xhigh (more thorough), max (maximum reasoning, most expensive).
disallowed-tools:
  - Write
  - Edit
  - NotebookEdit
---

# Effort Control

Set the reasoning effort level for the current task using `/effort`. This controls how much extended thinking Claude applies before acting.

## Levels

| Level | Command | Extended Thinking | Best For |
|-------|---------|-----------------|----------|
| Standard | `/effort standard` | Minimal | Most day-to-day tasks |
| Extra | `/effort extra` or `/effort xhigh` | Elevated | Complex features, security review |
| Max | `/effort max` | Maximum budget | Critical decisions, architecture, pre-release |

## When to Use Each Level

### Standard (default)
- Routine code edits, bug fixes, documentation
- Tasks where the path is clear and reversible
- Cost-sensitive batch operations

### Extra
- Complex feature implementation spanning multiple files
- Security audits where missing something is costly
- Refactors with broad side-effect surface
- Debugging hard-to-reproduce issues

### Max
- Architectural decisions (before `/workflow architecture-audit`)
- Pre-release security scan
- Reviewing a PR that touches auth, payments, or core data models
- When a mistake here would be expensive to reverse

## Pairing with Workflow Runner

Set effort before invoking a workflow to amplify the entire pipeline:

```
/effort max
/workflow security-audit
```

```
/effort extra
/workflow feature
```

For routine hotfixes, leave at default — max is expensive and unnecessary for small changes.

## Cost Implications

- `extra` / `xhigh` activates elevated extended thinking — ~2-3x cost of standard for the same task
- `max` uses the maximum reasoning budget — best reserved for high-stakes decisions
- Effort resets to standard at session end

## Decision Matrix

```
Is this reversible in < 5 minutes?
  Yes → standard

Is this a security/auth/payment change?
  Yes → max

Does this span > 5 files or introduce a new architectural layer?
  Yes → extra or max

Is this a routine fix on a well-understood path?
  Yes → standard
```
