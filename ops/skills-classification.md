# Skills Without Pipeline Integration — Classification Report

Generated after global audit + fix cycle (2026-05-31). 
**105/143 skills are referenced** by at least one stack or pipeline.yaml.

The 38 remaining skills are classified below. None represent functional gaps — 
each has a justified reason for existing outside the pipeline system.

---

## Category A — Domain Stacks Not Yet Created (20 skills)

These skills exist for specific industry verticals. They will be integrated when 
a dedicated stack for that domain is created. In the meantime they are available 
as slash commands for teams that work in those domains.

| Skill | Domain | Needs Stack |
|-------|--------|-------------|
| `healthcare-cdss-patterns` | Healthcare | `stacks/healthcare/` |
| `healthcare-emr-patterns` | Healthcare | `stacks/healthcare/` |
| `healthcare-eval-harness` | Healthcare | `stacks/healthcare/` |
| `healthcare-phi-compliance` | Healthcare | `stacks/healthcare/` |
| `carrier-relationship-management` | Logistics | `stacks/logistics/` |
| `logistics-exception-management` | Logistics | `stacks/logistics/` |
| `returns-reverse-logistics` | Logistics | `stacks/logistics/` |
| `customs-trade-compliance` | Logistics | `stacks/logistics/` |
| `production-scheduling` | Manufacturing | `stacks/manufacturing/` |
| `quality-nonconformance` | Manufacturing | `stacks/manufacturing/` |
| `inventory-demand-planning` | Manufacturing | `stacks/manufacturing/` |
| `energy-procurement` | Energy | `stacks/energy/` |
| `investor-materials` | Finance/Startup | `stacks/fintech/` |
| `investor-outreach` | Finance/Startup | `stacks/fintech/` |
| `videodb` | Media | `stacks/media/` |
| `video-editing` | Media | `stacks/media/` |
| `fal-ai-media` | Media | `stacks/media/` |
| `crosspost` | Content/Social | `stacks/media/` |
| `x-api` | Social/Marketing | `stacks/media/` |
| `content-engine` | Content Creation | `stacks/media/` |

**Action**: Create dedicated stacks when first project of that domain is initialized.

---

## Category B — Claude Code Meta-Tools (10 skills)

These skills are about building and operating Claude Code systems (harnesses, 
agents, loops). They are developer tools for the meta-layer, not for application 
projects. Adding them to project stacks would be misleading.

| Skill | Purpose |
|-------|---------|
| `agent-harness-construction` | Build Claude Code harness configurations |
| `agentic-engineering` | Engineering patterns for Claude agents |
| `agent-eval` | Evaluate and compare agent performance |
| `ai-first-engineering` | AI-first development methodology |
| `ai-regression-testing` | Regression testing for AI systems |
| `autonomous-loops` | Loop architecture patterns for `/loop` usage |
| `claude-devfleet` | Multi-agent fleet orchestration |
| `continuous-agent-loop` | Reference for choosing loop patterns |
| `dmux-workflows` | Terminal multiplexer orchestration (tmux/zellij) |
| `enterprise-agent-ops` | Enterprise-scale agent operations |
| `effort-control` | `/effort` levels — set cost/reasoning budget before a workflow |

**Action**: Document in `docs/` as harness-building tools. No stack integration needed.

---

## Category C — Developer Slash Commands (8 skills)

These are utility tools a developer invokes on demand. They have no automation 
use case — their value is interactive, one-shot invocation.

| Skill | Invocation Pattern |
|-------|-------------------|
| `exa-search` | `/exa-search <query>` — web search with Exa |
| `data-scraper-agent` | `/data-scraper-agent` — build scraping automations |
| `caveman` | `/caveman` — compress agent output style |
| `article-writing` | `/article-writing` — draft technical articles |
| `frontend-slides` | `/frontend-slides` — generate presentation decks |
| `ralphinho-rfc-pipeline` | `/ralphinho-rfc-pipeline` — RFC-driven large-feature orchestration |
| `repo-eval` | `/repo-eval` — evaluate external repos for adoption |
| `agent-payment-x402` | `/agent-payment-x402` — add X402 payment capability to agents |

**Action**: None. Already accessible as slash commands in any project.

---

## Summary

| Category | Count | Status |
|----------|-------|--------|
| Domain stacks not yet created | 20 | Waiting for domain-specific stacks |
| Claude Code meta-tools | 11 | Intentionally standalone |
| Developer slash commands | 8 | Intentionally standalone |
| **Referenced (stack or pipeline)** | **105** | **Integrated** |
| **Total** | **143** | |

**No skill is dead code.** All 38 have a clear purpose; integration is blocked 
by missing domain stacks (Category A) or intentionally absent (B, C).
