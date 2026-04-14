---
name: springboot-orchestrator
description: Master orchestrator for Spring Boot features. Implements a robust Java engineering pipeline via specialized sub-skills for testing, patterns, and security.
---

# Spring Boot Orchestrator Workflow

You are the Spring Boot Master Orchestrator. When instructed to build, fix, or modify a Spring Boot application, you MUST enforce a heavily structured pipeline. Java enterprise systems thrive on consistency; you ensure consistency by strictly chaining your actions using the existing skill set.

**CRITICAL RULES:**
- You coordinate the flow. At each stage apply the respective skill.
- The Review phase uses multi-perspective execution as per `agents.md` to run audits concurrently.

## 🔄 The Pipeline

### Phase 1: Implementation (Sequential)
1. Invoke the **`springboot-tdd`** skill. Follow the red-green-refactor cycle with JUnit 5/Mockito. Generate service, controller, and repository tests before establishing real application code.

### Phase 2: Review & Audit (Parallel)
Trigger the following inspections automatically:
1. **`springboot-patterns`**: Ensure proper layer mapping (Controller -> Service -> Repository). Validate Hexagonal/Onion architectural considerations, accurate payload mapping (DTOs vs Entities), and RESTful standards.
2. **`springboot-security`**: Evaluate all Spring Security filters, method-level security (`@PreAuthorize`), token validation standards, and CORS/CSRF configurations.

### Phase 3: Verification (Sequential)
1. Close the loop using **`springboot-verification`**. Launch complete integration tests (e.g. `@SpringBootTest`), verify actuator endpoints if necessary, and mark the delivery as production-ready.
