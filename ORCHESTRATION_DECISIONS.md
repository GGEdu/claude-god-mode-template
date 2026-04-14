# Orchestration Decisions & Architecture

## Contexto
Durante la refactorización arquitectónica basada en los principios definidos en `rules/agents.md`, se tomó la decisión de crear perfiles **Orquestadores** ("Orchestrators") para cada stack significativo del repositorio `claude-god-mode-template`. 

El objetivo es abstraer la invocación secuencial de las directivas (ej. lanzar TDD, luego Patterns, luego Seguridad) en un flujo único ("Flow") liderado por la inteligencia de orquestación.

## Decisiones Arquitectónicas (Decisions Records)

### 1. El Patrón del Pipeline: `Test > Audit > Verify`
Se unificó estructuralmente que TODOS los orquestadores deben seguir de forma **estricta** un ciclo de 3 fases.
**Decisión Estratégica:** Ninguna implementación debe comenzar con la resolución lógica. El orquestador DEBE garantizar que la primera capa siempre sea la invocación de testing (`*-tdd` o `*-testing`). Esto previene vulnerabilidades de regresión por diseño.

### 2. Uso del Principio de "Multi-Perspective Analysis"
**Decisión Estratégica:** Las fases de revisión (Stage 2) NUNCA son monolíticas. Las lógicas de Arquitectura/Patrones (`*-patterns`) y Seguridad (`*-security`) abordan problemas completamente ortogonales. Atendiendo al archivo `.rules/agents.md`, el orquestador simulará la concurrencia delegando roles de "Security engineer" y "Architect" al mismo momento durante el análisis, garantizando un cruce seguro y evitando cuellos de botella secuenciales.

### 3. Exclusión de Ecosistemas Fragmentados
**Decisión Estratégica:** No se crearon orquestadores para habilidades ultra-específicas (como scripts bash genéricos `frontend-slides` o aislados). Un Orquestador de Stack justifica su existencia si ese ecosistema (ej. Laravel, Django, Kotlin) requiere adherencia a marcos robustos de validación, compilación y seguridad empresarial. Hemos seleccionado 9 pilas backend críticas.

### 4. Bucle Estricto de Regresión (Feedback Loop)
**Decisión Estratégica:** Las skills actúan como compuertas lógicas (Gates). Si la fase de `*-security` detecta vulnerabilidades, la directiva del Orchestrator dictamina una revocación del código al "Implementation Phase" y forzosamente actualiza los tests (`*-tdd`) para capturar la inyección/vulnerabilidad antes de reintentar.

### 5. Configuración y Nombrado
Todos los Orquestadores adoptaron la convención `<stack>-orchestrator/SKILL.md` para ser nativamente detectables por el autocompletado en el comando `/`.

## Stack Configurations Enforced
- **Laravel:** `laravel-tdd` -> (`laravel-patterns` & `laravel-security`) -> `laravel-verification`
- **Django:** `django-tdd` -> (`django-patterns` & `django-security`) -> `django-verification`
- **Spring Boot:** `springboot-tdd` -> (`springboot-patterns` & `springboot-security`) -> `springboot-verification`
- **Kotlin:** `kotlin-testing` -> (`kotlin-patterns` & `kotlin-coroutines-flows`)
- **Python:** `python-testing` -> `python-patterns`
- **Go/Golang:** `golang-testing` -> `golang-patterns`
- **Rust:** `rust-testing` -> `rust-patterns`
- **C++:** `cpp-testing` -> `cpp-coding-standards`
- **Perl:** `perl-testing` -> (`perl-patterns` & `perl-security`)
