---
name: caveman
description: >-
  Selective output token compression. Forces terse caveman-style output in agents
  whose value is action (code, commits, build fixes), not reasoning. Code, paths,
  URLs, commits, version numbers stay verbatim. Only prose, hedging, and filler
  collapse. Adapted from juliusbrussee/caveman — opt-in per agent, never global.
impact: low
adapted_from: https://github.com/juliusbrussee/caveman
---

# Caveman — Selective Output Compression

> "Why use many token when few token do trick."

A lightweight output style. Cuts ~22–87% of OUTPUT tokens (median ~65%) in prose-heavy
responses by removing filler, articles, and hedging. **Does not touch thinking tokens,
input tokens, code, paths, URLs, or commit messages.**

## When to apply (opt-in per agent)

Activate this skill in agents whose output is **action artifacts**, not human-facing
reasoning:

| Apply | Skip |
|------|------|
| `refactor-cleaner` (output is diffs) | `planner` (output is reasoning) |
| `build-error-resolver` and language variants | `architect` (output justifies trade-offs) |
| `doc-updater` (terse changelog entries) | `security-reviewer` (auditable findings) |
| `e2e-runner` (status reports) | `code-reviewer` (human-facing comments) |
| `memory-consolidator` (compression IS the goal) | `tdd-guide` (explains test rationale) |
| `loop-operator` (operational chatter) | `comment-analyzer` (nuanced quality calls) |

**Rule of thumb:** if the downstream consumer is a human reading prose to make a
judgment call, do NOT apply Caveman. If the consumer is another agent or the user
applying a diff/commit/fix as-is, apply it.

## What is preserved verbatim

- Code blocks (any language, any size)
- File paths, line numbers, function names
- URLs, commit SHAs, version numbers, dates
- Conventional commit messages
- Stack traces, error messages, log lines
- Numeric values, units, percentages
- Quoted strings inside prose

## What is compressed

- Articles ("the", "a", "an") — drop unless ambiguity results
- Hedging ("perhaps", "it seems", "I think", "you might want to")
- Openers ("Sure!", "Of course", "Let me…", "I'll go ahead and…")
- Closers ("Hope this helps", "Let me know if…")
- Restating the user's prompt
- Multi-paragraph explanations of obvious facts

## Activation snippet (paste into agent system prompt)

The exact snippet that activates Caveman is in [`snippet.md`](./snippet.md). To
add Caveman to a new agent, append the contents of `snippet.md` to the agent's
markdown file, **after** the closing `---` of the frontmatter and **before** any
other body content, or as a final `## Output Style` section.

## Verification

To check which agents have Caveman active:

```bash
grep -l "CAVEMAN_ACTIVE" agents/*.md
```

The marker `<!-- CAVEMAN_ACTIVE -->` is included in the snippet so installation
is greppable and auditable.

## What this skill is NOT

- **Not** a global session hook. We deliberately do not install
  `caveman-compress` (rewrites .md files — would degrade rules/CLAUDE.md), nor
  the `SessionStart` auto-activation. Both would break per-agent control.
- **Not** a substitute for prompt engineering. Caveman compresses what the agent
  was already going to say; it does not improve the underlying logic.
- **Not** applied to user-facing reviewers, planners, or architects. Their
  output must remain auditable by humans and other tools.

## Trade-offs

| Win | Cost |
|-----|------|
| 20–35% real cost reduction in implementer/refactorer sessions | Output less polished — fine for action agents, bad for client-facing reports |
| Faster reads for diffs and status updates | Junior devs may find caveman tone confusing; document who uses it |
| No impact on technical correctness | Headline "65% savings" is output-only; thinking tokens unaffected |

## License & attribution

Caveman concept by Julius Brussee — https://github.com/juliusbrussee/caveman (MIT).
This skill is an adaptation: same compression instruction, different deployment
model (selective per-agent, no global hooks, no `.md` compression).
