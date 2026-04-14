---
name: cpp-orchestrator
description: C++ central orchestrator routing tasks through strict testing pipelines and cpp-coding-standards verification.
---

# C++ Orchestrator Workflow

C++ operations require extremely strict orchestration to prevent catastrophic memory leaks, segmentation faults, and undefined behavior. You are the Commander of C++ tasks.

**CRITICAL RULES:**
- Always ensure tests are written before deep feature coding.
- Verify modern C++ principles strictly via the pattern audits.

## 🔄 The Pipeline

### Phase 1: Implementation (Sequential)
1. Promptly utilize the **`cpp-testing`** skill. Define tests using the corresponding framework (Catch2, GTest). You must implement features to strictly pass these test suites without side effects.

### Phase 2: Review & Audit
1. Utilize the **`cpp-coding-standards`** skill. Perform an aggressive review focusing on constraints: Memory management (using Smart Pointers `std::unique_ptr`/`std::shared_ptr` over raw pointers), Rule of 5 semantics, modern C++ (C++11/14/17/20) features, and strict `const` correctness.

### Phase 3: Verification (Sequential)
1. Consolidate changes. Ensure it compiles strictly without warnings on major compilers (GCC/Clang/MSVC) and that tools like Valgrind or ASan wouldn't flag the new logic. The code is then delivered.
