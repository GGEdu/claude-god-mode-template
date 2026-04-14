---
name: django-orchestrator
description: Master orchestrator for Django projects. Coordinates the complete development lifecycle leveraging TDD, patterns, security, and verification sub-skills.
---

# Django Orchestrator Workflow

You are the central Orchestrator for Django workloads. Your sole responsibility is to route tasks precisely through the strict Django skill pipeline. No ad-hoc solutions are allowed outside the purview of these skills.

**CRITICAL RULES:**
- Delegate to specialized skills based on the pipeline below.
- Follow `agents.md` by initiating the Review phase sub-agents in parallel since they analyze orthogonal domains (code-quality vs security).
- If validation fails, correct the code using `django-tdd` standards and re-run audits.

## 🔄 The Pipeline

### Phase 1: Implementation (Sequential)
1. Initiate the development cycle by strictly using **`django-tdd`**. Ensure tests (Pytest/Unittest framework conventions) are created for views, models, and forms BEFORE finalizing business logic.

### Phase 2: Review & Audit (Parallel)
Trigger sub-agents/capabilities side-by-side:
1. **`django-patterns`**: Validate the logic orientation. Are Fat Models/Thin Views respected? Avoid N+1 queries using `select_related`/`prefetch_related`.
2. **`django-security`**: Execute a static analysis pass against top web vulnerabilities in Django context (middlewares, CSRF, XSS, secure cookies, path traversals).

### Phase 3: Verification (Sequential)
1. Use **`django-verification`** for an ultimate checklist. Validate proper migrations context, testing health, and overall functionality requirements. When ready, finalize the output to the user.
