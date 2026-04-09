# Orchestration — GitHub Actions & Antigravity

> Extends [agents.md](./agents.md) with rules for running agents outside the local session:
> in GitHub CI/CD pipelines and as scheduled Antigravity remote triggers.

## When to Use Each Execution Mode

| Mode | When | Tool |
|------|------|------|
| **Local agent** | Interactive development, immediate feedback | `Agent` tool in Claude Code |
| **GitHub Action** | On PR/Issue/push events, team-visible output | `.github/workflows/agent-*.yml` |
| **Antigravity trigger** | Scheduled or remote autonomous execution | `CronCreate` / `RemoteTrigger` |

## GitHub Actions — Agent Workflows

Workflows in `.github/workflows/agent-*.yml` run Claude Code agents in CI using `claude -p`.

### Available workflows (added by `make init-project`)

| Workflow | Trigger | Agents |
|----------|---------|--------|
| `agent-pr-review.yml` | PR opened / updated | code-reviewer + security-reviewer (parallel) |
| `agent-issue-triage.yml` | Issue labeled `needs-plan` | planner |
| `agent-scheduled-audit.yml` | Weekly (Mon 09:00 UTC) | security-reviewer + doc-updater |

### Required GitHub repository secrets

Add these in **Settings → Secrets and variables → Actions**:

```text
ANTHROPIC_API_KEY   — Your Anthropic API key
```

`GITHUB_TOKEN` is provided automatically by GitHub Actions.

### Enabling a workflow manually

```bash
# Trigger the audit workflow on demand
gh workflow run agent-scheduled-audit.yml \
  --field scope=security
```

### Adding a new agent workflow

1. Create `stacks/common/workflows/agent-<name>.yml` in the template repo
2. Run `make init-project STACK=<name> PROJECT=/ruta` — all files in `stacks/common/workflows/` are automatically copied to `.github/workflows/`

## Antigravity — Scheduled Remote Triggers

Antigravity triggers run Claude Code agents autonomously on a cron schedule,
without requiring an open local session.

### Trigger definitions

Triggers are defined as YAML files in `ops/triggers/`. Each file describes one scheduled job.

```yaml
# ops/triggers/example.yaml
name: example-trigger
description: "What this trigger does"
schedule: "0 9 * * 1"   # cron expression (UTC)
prompt: |
  Detailed prompt for the agent to execute.
  Be specific about what to read, what to produce, and where to save output.
agent: security-reviewer   # agent from .claude/agents/
model: sonnet
tags: [scheduled, security]
```

### Setting up triggers via Claude Code

After defining a trigger YAML, run inside Claude Code:

```text
make triggers-setup
```

This prints the `/schedule` commands to paste in Claude Code. Example output:

```text
/schedule create weekly-security-audit \
  --cron "0 9 * * 1" \
  --prompt "Run the security-reviewer agent..."
```

### Managing triggers

```text
make triggers-list       # Lists all triggers defined in ops/triggers/
make triggers-status     # Shows which Antigravity triggers are active
```

Or directly in Claude Code:
- `/schedule list` — show all active triggers
- `/schedule delete <name>` — remove a trigger

### Trigger output

By convention, scheduled triggers save their output to `ops/sessions/` with a timestamp:

```text
ops/sessions/security-audit-2026-04-07.md
ops/sessions/memory-consolidation-2026-04-07.md
```

## github-orchestrator Agent

Use the `github-orchestrator` agent when you need to publish agent outputs to GitHub:

```text
"Use the github-orchestrator agent to post this security review to PR #42"
"Use the github-orchestrator agent to create an issue from this audit report"
```

It handles: duplicate detection, label creation, comment formatting, and error reporting.

## Security Considerations

- Never hardcode `ANTHROPIC_API_KEY` in workflow files — always use `${{ secrets.ANTHROPIC_API_KEY }}`
- Limit `--allowedTools` to the minimum needed per workflow
- Review agent output before it reaches a public repo — use `workflow_dispatch` + manual approval for sensitive repos
- Antigravity triggers run with the permissions configured in `.claude/settings.json`
