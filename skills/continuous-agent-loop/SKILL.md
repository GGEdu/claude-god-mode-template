---
name: continuous-agent-loop
description: Patterns for continuous autonomous agent loops with quality gates, evals, and recovery controls.
origin: ECC
---

# Continuous Agent Loop

This is the v1.8+ canonical loop skill name. It supersedes `autonomous-loops` while keeping compatibility for one release.

## Loop Selection Flow

```text
Start
  |
  +-- Need strict CI/PR control? -- yes --> continuous-pr
  |                                    
  +-- Need RFC decomposition? -- yes --> rfc-dag
  |
  +-- Need exploratory parallel generation? -- yes --> infinite
  |
  +-- default --> sequential
```

## Combined Pattern

Recommended production stack:
1. RFC decomposition (`ralphinho-rfc-pipeline`)
2. quality gates (`plankton-code-quality` + `/quality-gate`)
3. eval loop (`eval-harness`)
4. session persistence (`nanoclaw-repl`)

## Native Dynamic Workflows (Claude Code 2026)

Claude Code's built-in parallel subagent orchestration — distinct from user-built patterns like Ralphinho or Infinite Loop. Announced May 2026.

**Use when**: the operation is uniform across many targets (files, modules, repos) and each unit is independent.

**How it works**: send multiple `Agent` tool calls in a single response. Claude Code runs them truly in parallel, then collects results.

```
# Example: audit all 15 stacks in parallel
Spawn one architecture-auditor subagent per stacks/* directory.
Each writes AUDIT_REPORT.md to its project path.
Collect all reports and consolidate into AUDIT_SUMMARY.md.
```

**Built-in safeguards**: stall detection, escalation gates, checkpoint state.

**Best for**:
- Codebase-wide refactors (50+ files, each independent)
- Mass test generation across modules
- Parallel data migration with isolated units
- Multi-repo security scans

**Contrast with Ralphinho**: Ralphinho handles _interdependent_ units with a merge queue. Dynamic workflows assume each unit is independent — no coordination needed.

**Contrast with Infinite Agentic Loop**: that pattern is spec-driven content generation. Dynamic workflows are operational — they transform existing artifacts.

---

## Failure Modes

- loop churn without measurable progress
- repeated retries with same root cause
- merge queue stalls
- cost drift from unbounded escalation

## Recovery

- freeze loop
- run `/harness-audit`
- reduce scope to failing unit
- replay with explicit acceptance criteria
