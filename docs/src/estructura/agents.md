# Directorio: `agents/`

Fuente de verdad de los **22 agentes** del template. `make install` los compila (con skills embebidas) y los copia a `~/.claude/agents/`.

> Los archivos en `agents/` son la base. **Nunca editar directamente** `.claude/agents/` — esos son artefactos compilados por `ops/compile-agents.py`.

---

## Cómo funciona la compilación

```
agents/architect.md  +  skills/api-design/SKILL.md
                     +  skills/architecture-decision-records/SKILL.md
                     +  skills/deployment-patterns/SKILL.md
                        ↓
        ops/compile-agents.py
                        ↓
    .claude/agents/architect.md   (agent + skills incrustados)
```

El desarrollador **no invoca skills manualmente** — los agentes ya conocen sus skills.

---

## Inventario de los 22 agentes

### Planificación

| Agente | Descripción | Modelo | Herramientas |
|--------|-------------|--------|--------------|
| **architect** | Diseño de arquitectura de sistemas, escalabilidad y decisiones técnicas. Usar PROACTIVAMENTE al planificar features, refactorizar sistemas grandes o tomar decisiones arquitectónicas. | opus | Read, Grep, Glob |
| **planner** | Especialista en planificación para features complejas y refactoring. Usar PROACTIVAMENTE cuando el usuario pide implementar features, cambios arquitectónicos o refactoring complejo. | opus | Read, Grep, Glob |

### Revisión de código

| Agente | Descripción | Modelo | Herramientas |
|--------|-------------|--------|--------------|
| **code-reviewer** | Revisión experta de código para calidad, seguridad y mantenibilidad. Usar INMEDIATAMENTE después de escribir o modificar código. OBLIGATORIO para todos los cambios. | sonnet | Read, Grep, Glob, Bash |
| **code-simplifier** | Refactoriza código para reducir carga cognitiva. Aplica early returns, async/await, extracción de lógica anidada. Preserva comportamiento exactamente. Usar después de que una feature funciona y tiene tests. | sonnet | Read, Grep, Glob, Bash, Edit |
| **comment-analyzer** | Evalúa calidad de comentarios en 4 dimensiones: precisión, completitud, valor a largo plazo, elementos engañosos. Usar en PRs con cambios de comentarios o periódicamente en lógica de negocio. | sonnet | Read, Grep, Glob, Bash |
| **typescript-reviewer** | Revisor experto de TypeScript/JavaScript. Especializado en type safety, async correctness, seguridad Node/web, patrones idiomáticos. OBLIGATORIO para proyectos TS/JS. | sonnet | Read, Grep, Glob, Bash |
| **python-reviewer** | Revisor experto de Python. PEP 8, idiomas Pythónicos, type hints, seguridad, rendimiento. OBLIGATORIO para proyectos Python. | sonnet | Read, Grep, Glob, Bash |

### Testing

| Agente | Descripción | Modelo | Herramientas |
|--------|-------------|--------|--------------|
| **tdd-guide** | Especialista TDD. Enforce metodología test-first. Usar PROACTIVAMENTE al escribir features, corregir bugs o refactorizar. Asegura 80%+ de cobertura. | sonnet | Read, Write, Edit, Bash, Grep |
| **e2e-runner** | Especialista en testing E2E con Vercel Agent Browser (preferido) y Playwright como fallback. Gestiona journeys de test, cuarentena de tests frágiles, artefactos. | sonnet | Read, Write, Edit, Bash, Grep, Glob |
| **pr-test-analyzer** | Análisis de cobertura conductual para PRs. Mapea código cambiado a tests, identifica caminos sin tests, evalúa gaps por impacto. Diferente de tdd-guide (que guía RED-GREEN-REFACTOR). | sonnet | Read, Grep, Glob, Bash |

### Seguridad y base de datos

| Agente | Descripción | Modelo | Herramientas |
|--------|-------------|--------|--------------|
| **security-reviewer** | Detección y remediación de vulnerabilidades. Usar PROACTIVAMENTE después de escribir código que maneja input de usuario, auth, APIs o datos sensibles. Detecta OWASP Top 10. | sonnet | Read, Write, Edit, Bash, Grep, Glob |
| **database-reviewer** | Especialista PostgreSQL para optimización de queries, diseño de esquemas, seguridad y rendimiento. Usar PROACTIVAMENTE al escribir SQL, migraciones o diseñar esquemas. Incluye mejores prácticas Supabase. | sonnet | Read, Write, Edit, Bash, Grep, Glob |

### Rendimiento y análisis

| Agente | Descripción | Modelo | Herramientas |
|--------|-------------|--------|--------------|
| **performance-optimizer** | Análisis y optimización de rendimiento. Identifica bottlenecks, optimiza bundles, mejora rendimiento en runtime. Profiling, memory leaks, optimización de renders. | sonnet | Read, Write, Edit, Bash, Grep, Glob |
| **silent-failure-hunter** | Detección de fallos silenciosos e inadecuado manejo de errores. Encuentra empty catch blocks, fallbacks peligrosos, stack traces perdidos. Complementa code-reviewer con análisis de propagación de errores. | sonnet | Read, Grep, Glob, Bash |
| **conversation-analyzer** | Analiza transcripts de sesión para detectar patrones de fricción: frustración, correcciones repetidas, trabajo revertido, intención malinterpretada. Usar cuando una sesión se atasca o tras correcciones repetidas. | sonnet | Read, Grep, Glob, Bash |

### Infraestructura y automatización

| Agente | Descripción | Modelo | Herramientas |
|--------|-------------|--------|--------------|
| **build-error-resolver** | Especialista en resolución de errores de build y TypeScript. Usar PROACTIVAMENTE cuando el build falla. Solo corrige errores con diffs mínimos — sin ediciones arquitectónicas. | sonnet | Read, Write, Edit, Bash, Grep, Glob |
| **refactor-cleaner** | Especialista en limpieza y consolidación de código muerto. Ejecuta knip, depcheck, ts-prune para identificar código sin usar y lo elimina de forma segura. | sonnet | Read, Write, Edit, Bash, Grep, Glob |
| **doc-updater** | Especialista en documentación y codemaps. Actualiza READMEs, guías, genera docs/CODEMAPS/*. | haiku | Read, Write, Edit, Bash, Grep, Glob |
| **loop-operator** | Ejecuta loops de tareas autónomas multi-paso de forma segura. Para tareas que requieren 5+ pasos secuenciales. Incluye detección de stalls, checkpoints y escalation gates. Diferente de planner (que crea planes). | sonnet | Read, Grep, Glob, Bash, Edit, Write |
| **memory-consolidator** | Consolida y comprime archivos en `.claude/memory/` cuando crecen demasiado. Invocar cuando un archivo supere 150 líneas o el directorio supere 600 líneas totales. | sonnet | Read, Write, Bash |
| **docs-lookup** | Busca documentación actualizada de librerías, frameworks y APIs usando Context7 MCP. Usar cuando el usuario pregunta cómo usar una librería o necesita ejemplos de código actualizados. | sonnet | Read, Grep, mcp__context7__ |
| **github-orchestrator** | Publica resultados de agentes en GitHub: comenta reviews en PRs, crea issues desde reportes de auditoría. Detecta duplicados y gestiona etiquetas. Usar cuando necesites que la salida de un agente sea visible en el repo remoto. | sonnet | Read, Bash |

---

## Activación por stack

Los stacks activan 20 agentes comunes, más 2 agentes dependientes del lenguaje:

| Agente | Stacks donde se incluye |
| --- | --- |
| **typescript-reviewer** | laravel (con `LAYERS=react`), nextjs-saas, nuxt-saas — stacks con frontend TypeScript, o cualquier stack con `LAYERS=react` |
| **python-reviewer** | odoo, python-api, ml-pytorch (stacks Python) |
| Resto (20) | Todos los 15 stacks |

---

## Añadir un agente nuevo

1. Crear `agents/<nombre>.md` con frontmatter `name`, `description`, `tools`, `model`
2. Añadirlo en los `stacks/*/stack.yaml` donde aplique (sección `agents:` con `skills:` asignadas)
3. Ejecutar `make dev-stack STACK=<stack>` para recompilar
4. Ejecutar `make install` para instalar globalmente
