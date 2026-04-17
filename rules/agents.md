# Agent Orchestration

## Available Agents

Located in `~/.claude/agents/`:

| Agent | Purpose | When to Use |
|-------|---------|-------------|
| planner | Implementation planning | Complex features, refactoring |
| architect | System design | Architectural decisions |
| tdd-guide | Test-driven development | New features, bug fixes |
| code-reviewer | Code review | After writing code |
| security-reviewer | Security analysis | Before commits |
| build-error-resolver | Fix build errors (generic) | When build fails (no stack-specific resolver) |
| e2e-runner | E2E testing | Critical user flows |
| refactor-cleaner | Dead code cleanup | Code maintenance |
| ui-engineer | Build new UI features + refactor existing ones with design rules | Creating or improving UI components |
| doc-updater | Documentation | Updating docs |
| repo-reviewer | Evaluate GitHub repos for reuse | Before reimplementing existing patterns |
| harness-optimizer | Analyze and improve agent harness config | Cuando el sistema muestra baja calidad, alto coste o comportamiento inesperado |
| **Language Reviewers** | | |
| go-reviewer | Go idiomatic review, concurrency, security | After writing Go code |
| java-reviewer | Java/Spring Boot layered arch, JPA, security | After writing Java code |
| kotlin-reviewer | Kotlin/Android/KMP coroutines, Compose, clean arch | After writing Kotlin code |
| python-reviewer | Python PEP8, type hints, security | After writing Python code |
| cpp-reviewer | C++ memory safety, modern C++20 idioms | After writing C++ code |
| csharp-reviewer | C# .NET async patterns, nullable types | After writing C# code |
| flutter-reviewer | Flutter/Dart widgets, state management | After writing Flutter code |
| **Build Resolvers** | | |
| go-build-resolver | Go build, vet, module errors | When Go build fails |
| java-build-resolver | Java/Maven/Gradle compilation errors | When Java build fails |
| kotlin-build-resolver | Kotlin/Gradle build errors | When Kotlin build fails |
| cpp-build-resolver | C++ CMake, linker, template errors | When C++ build fails |
| dart-build-resolver | Dart/Flutter build, pub, build_runner | When Flutter/Dart build fails |

## Immediate Agent Usage

No user prompt needed:
1. Complex feature requests - Use **planner** agent
2. Code just written/modified - Use **code-reviewer** agent
3. Bug fix or new feature - Use **tdd-guide** agent
4. Architectural decision - Use **architect** agent

## Stack Orchestrators (Pipeline Managers)

For end-to-end task execution within a specific ecosystem, invoke its Stack Orchestrator. These skills enforce a strict execution pipeline (`Test -> Audit in Parallel -> Verify`) and automatically route sub-tasks to specialized domain skills. Available orchestrators:
- `/laravel-orchestrator`
- `/django-orchestrator`
- `/springboot-orchestrator`
- `/python-orchestrator`
- `/rust-orchestrator`
- `/golang-orchestrator`
- `/cpp-orchestrator`
- `/kotlin-orchestrator`
- `/perl-orchestrator`

## Parallel Task Execution

ALWAYS use parallel Task execution for independent operations:

```markdown
# GOOD: Parallel execution
Launch 3 agents in parallel:
1. Agent 1: Security analysis of auth module
2. Agent 2: Performance review of cache system
3. Agent 3: Type checking of utilities

# BAD: Sequential when unnecessary
First agent 1, then agent 2, then agent 3
```

## Multi-Perspective Analysis

For complex problems, use split role sub-agents:
- Factual reviewer
- Senior engineer
- Security expert
- Consistency reviewer
- Redundancy checker
