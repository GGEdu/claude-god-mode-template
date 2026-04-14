---
name: golang-orchestrator
description: Efficient orchestration layer for Go (Golang) codebases, chaining test-driven flows to pattern consistency algorithms.
---

# Golang Orchestrator Workflow

You supervise the creation of Go applications. Go focuses on simplicity, fast compilation, and explicit concurrency. As the orchestrator, you ensure these tenets are respected by invoking specialized skills.

**CRITICAL RULES:**
- Follow table-driven testing. 
- Ensure review logic covers concurrency anomalies.

## 🔄 The Pipeline

### Phase 1: Implementation (Sequential)
1. Activate the **`golang-testing`** skill. Every struct/function logic must have an accompanying `_test.go` file. Implement Table-Driven Tests with Subtests (`t.Run`) as the core standard. Ensure base compliance before passing to Phase 2.

### Phase 2: Review & Audit
1. Apply **`golang-patterns`** to evaluate structural integrity. Watch for channel leaks, improper goroutine synchronization (`sync.WaitGroup`/`Mutex`), overly nesting logic, and explicit error handling (`if err != nil`). Validate package interfaces and separation of concerns.

### Phase 3: Verification (Sequential)
1. Conclude the workflow by evaluating if `go test`, `go vet`, and `go fmt` will succeed cleanly. Fix any hanging elements, verify concurrency is race-free, and mark as delivered.
