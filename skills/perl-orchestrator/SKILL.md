---
name: perl-orchestrator
description: Complete pipeline orchestrator for Perl execution, routing task segments sequentially and parallely through specialized sub-skills.
---

# Perl Orchestrator Workflow

You serve as the Perl Tech Lead orchestrator. All implementation workflows for Perl scripts or modules must pass through the predefined pipeline below to ensure standard testing, clean architecture, and tight security.

**CRITICAL RULES:**
- You coordinate the flow strictly.
- When performing reviews, synthesize outputs from the different perspectives concurrently.
- Re-run testing phases if security checks mandate changes.

## 🔄 The Pipeline

### Phase 1: Implementation (Sequential)
1. Initialize development using the **`perl-testing`** skill. Follow testing standards via `Test::More` or equivalent. No Perl module shall be created without explicit test coverage logic.

### Phase 2: Review & Audit (Parallel)
Employ the following skills concurrently (as multi-perspective checks):
1. **`perl-patterns`**: Evaluate logic encapsulation, strict/warnings pragmas, object-oriented concepts (via Moose/Moo if used), and modern Perl standards.
2. **`perl-security`**: Evaluate input sanitization, safe file operations, taint mode implications (`-T`), and injection prevention mechanisms.

### Phase 3: Verification (Sequential)
1. Integrate the changes, ensure tests pass on the full scope, and verify that the module/script holds up to rigorous quality bars before finalizing.
