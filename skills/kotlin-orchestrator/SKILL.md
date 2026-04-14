---
name: kotlin-orchestrator
description: Specialized orchestrator for Kotlin workflows. Chains robust testing with heavy pattern evaluation (coroutines, web, DBs).
---

# Kotlin Orchestrator Workflow

You act as the primary Orchestrator for all Kotlin changes. Kotlin applications thrive on idiomacy, coroutines conciseness, and robust async testing. To guarantee this, adhere strictly to the following pipeline.

**CRITICAL RULES:**
- Launch sub-skills concurrently for code review to apply multifaceted insights contextually.
- Do not skip the testing phase.

## 🔄 The Pipeline

### Phase 1: Implementation (Sequential)
1. Leverage **`kotlin-testing`**. Draft test structures (Kotest/MockK or JUnit 5) emphasizing edge cases, DSL usage, and immutability before or during implementation.

### Phase 2: Review & Audit (Parallel)
Deploy these skills strategically:
1. **`kotlin-patterns`**: Core language review. Validate scoping functions (let, run, with, apply), immutability vs mutability guidelines, and generic type structures.
2. **`kotlin-coroutines-flows`**: Concurrency audit. Check for proper CoroutineScope usage, Flow flow-control, and structured concurrency patterns. Ensure Dispatchers are injected for testability.
3. **If applicable:** Inject `kotlin-ktor-patterns` or `kotlin-exposed-patterns` simultaneously if the app touches Ktor APIs or the Exposed database library. 

### Phase 3: Verification (Sequential)
1. Verify compilation logic, ensure test coverage integrates cleanly without blocking main threads, and ensure idiomatic formatting before marking complete.
