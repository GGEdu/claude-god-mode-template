# Antigravity Triggers

Triggers define scheduled autonomous agent executions via Antigravity (Claude Code's remote trigger system).

Each `.yaml` file in this directory describes one scheduled job. They do **not** run by themselves — they are declarations. You activate them by running `make triggers-setup` inside Claude Code, which generates the `/schedule` commands.

## YAML format

```yaml
name: <slug>                      # Unique identifier, used as trigger name
description: "Human description"
schedule: "0 9 * * 1"            # Standard cron expression (UTC)
prompt: |                         # Full prompt for the agent
  Multi-line prompt here.
  Be specific: what to read, what to produce, where to save.
agent: <agent-name>               # Agent from .claude/agents/ (optional hint)
model: sonnet                     # sonnet | opus | haiku
output: ops/sessions/<name>-$(date +%Y%m%d).md   # Where to save output
tags: [tag1, tag2]
```

## Cron expression reference

```text
┌─────── minute (0-59)
│ ┌───── hour (0-23 UTC)
│ │ ┌─── day of month (1-31)
│ │ │ ┌─ month (1-12)
│ │ │ │ ┌ day of week (0-7, 0=Sunday)
│ │ │ │ │
0 9 * * 1   → Every Monday at 09:00 UTC
0 18 * * *  → Every day at 18:00 UTC
0 9 * * 0   → Every Sunday at 09:00 UTC
0 9 1 * *   → First day of every month at 09:00 UTC
```

## Activating triggers

Inside Claude Code, run:

```text
make triggers-setup
```

This reads all `.yaml` files and prints the `/schedule` commands to execute.
Paste each command in the Claude Code prompt to register the trigger.

## Managing active triggers

```text
/schedule list                    # Show all active triggers
/schedule delete <name>           # Remove a specific trigger
/schedule run <name>              # Execute a trigger immediately (test)
```

## Output convention

Trigger outputs are saved in `ops/sessions/` with a timestamp suffix.
They are gitignored by default (add `ops/sessions/` to `.gitignore`).
