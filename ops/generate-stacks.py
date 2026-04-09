#!/usr/bin/env python3
"""Genera los 13 nuevos stacks con estructura consistente."""

import os
import textwrap

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ─── Pipeline template (idéntico para todos) ─────────────────────────────────

PIPELINE = textwrap.dedent("""\
workflows:
  feature:
    description: "Feature completa con planificación, TDD y revisión"
    steps:
      - agent: planner
        description: "Crear plan de implementación"
      - agent: tdd-guide
        description: "Escribir tests primero, luego implementar"
      - agent: code-reviewer
        description: "Revisar calidad del código"
      - agent: security-reviewer
        description: "Verificar vulnerabilidades"
        parallel_with: code-reviewer
      - audit: true
        description: "Ejecutar verificaciones automáticas"
      - agent: memory-consolidator
        description: "Guardar decisiones en memoria"
        always: true

  hotfix:
    description: "Fix rápido con revisión mínima"
    steps:
      - agent: tdd-guide
        description: "Escribir test para el fix, luego implementar"
      - agent: code-reviewer
        description: "Revisar el fix"
      - audit: true
      - agent: memory-consolidator
        description: "Guardar decisiones"
        always: true

  refactor:
    description: "Mejora de código sin cambio de comportamiento"
    steps:
      - agent: planner
        description: "Planificar el refactoring"
      - agent: code-simplifier
        description: "Simplificar código"
      - agent: code-reviewer
        description: "Revisar cambios"
      - audit: true
      - agent: memory-consolidator
        description: "Guardar decisiones"
        always: true
""")

# ─── Command templates ────────────────────────────────────────────────────────

COMMANDS_COMMON = {
    "jedi-review": 'Para código crítico — review de 3 expertos en paralelo',
    "git-workflow": 'Si necesitas recordar el workflow de commits y PRs',
    "workflow-runner": 'Para ejecutar un pipeline completo: /workflow feature, /workflow hotfix',
    "canary-watch": 'Post-deploy — monitoreo con Playwright en URLs live',
    "codebase-onboarding": 'Al entrar en un repo nuevo — genera guía de onboarding',
    "benchmark": 'Medir rendimiento antes/después de un PR o cambio',
}

# ─── Agent builder (21 agents, language-specific ones vary) ───────────────────

def build_agents(
    *,
    architect_skills=None,
    planner_skills=None,
    tdd_skills=None,
    code_reviewer_skills=None,
    lang_reviewer=None,  # tuple (name, skills) e.g. ("python-reviewer", ["python-patterns"])
    security_skills=None,
    db_skills=None,
    e2e_skills=None,
):
    """Returns YAML string for agents section."""
    architect_skills = architect_skills or []
    planner_skills = planner_skills or []
    tdd_skills = tdd_skills or []
    code_reviewer_skills = code_reviewer_skills or []
    security_skills = security_skills or []
    db_skills = db_skills or []
    e2e_skills = e2e_skills or []

    # Universal embeds
    architect_all = ["api-design", "architecture-decision-records", "deployment-patterns", "docker-patterns"] + architect_skills
    planner_all = planner_skills + ["search-first"]
    tdd_all = ["tdd-workflow"] + tdd_skills
    cr_all = code_reviewer_skills + ["verification-loop"]
    sec_all = ["security-review"] + security_skills
    db_all = ["database-migrations"] + db_skills

    lines = []
    def agent(name, skills):
        s = ", ".join(skills) if skills else ""
        lines.append(f"  {name}:")
        lines.append(f"    skills: [{s}]")

    agent("architect", architect_all)
    agent("planner", planner_all)
    agent("tdd-guide", tdd_all)
    agent("code-reviewer", cr_all)

    # Language-specific reviewer
    if lang_reviewer:
        agent(lang_reviewer[0], lang_reviewer[1])

    agent("security-reviewer", sec_all)
    agent("database-reviewer", db_all)
    agent("performance-optimizer", [])
    agent("refactor-cleaner", [])
    agent("e2e-runner", e2e_skills)
    agent("doc-updater", [])
    agent("memory-consolidator", [])
    agent("build-error-resolver", [])
    agent("loop-operator", ["safety-guard"])
    agent("code-simplifier", [])
    agent("silent-failure-hunter", [])
    agent("comment-analyzer", [])
    agent("conversation-analyzer", [])
    agent("docs-lookup", ["documentation-lookup"])
    agent("pr-test-analyzer", [])

    return "\n".join(lines)


def build_commands(extra=None):
    """Returns YAML string for commands section."""
    cmds = {**COMMANDS_COMMON}
    if extra:
        cmds.update(extra)
    lines = []
    for name, when in cmds.items():
        lines.append(f'  {name}:')
        lines.append(f'    when: "{when}"')
    return "\n".join(lines)


def build_stack_yaml(*, name, description, meta, rules, agents_str, commands_str, mcps=None):
    """Build full stack.yaml content."""
    parts = [f'name: {name}', f'description: "{description}"', '']

    # Meta fields
    for k, v in meta.items():
        parts.append(f'{k}: {v}')
    parts.append('')

    # Rules
    parts.append('rules:')
    for r in rules:
        parts.append(f'  - {r}')
    parts.append('')

    # Agents
    parts.append('# Agentes con skills embebidas')
    parts.append('agents:')
    parts.append(agents_str)
    parts.append('')

    # Commands
    parts.append('# Comandos standalone')
    parts.append('commands:')
    parts.append(commands_str)
    parts.append('')

    # MCPs
    parts.append('mcps:')
    if mcps:
        for k, v in mcps.items():
            parts.append(f'  {k}: {"true" if v else "false"}')
    else:
        parts.append('  notebooklm: false')
        parts.append('  n8n: false')
    parts.append('')

    return "\n".join(parts) + "\n"


def write_file(path, content):
    """Write file, creating directories."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    print(f"  ✅ {os.path.relpath(path, BASE)}")


# ═══════════════════════════════════════════════════════════════════════════════
# STACK DEFINITIONS
# ═══════════════════════════════════════════════════════════════════════════════

STACKS = {}

# ─── 1. java-springboot ──────────────────────────────────────────────────────

STACKS["java-springboot"] = {
    "description": "Java — Spring Boot 3 + PostgreSQL + Maven/Gradle",
    "meta": {
        "backend": "java",
        "backend_framework": "springboot",
        "database": "postgresql",
        "tests_backend": "junit5",
        "linter_backend": "checkstyle",
    },
    "rules": ["springboot.md"],
    "agents": lambda: build_agents(
        architect_skills=["springboot-patterns", "jpa-patterns"],
        planner_skills=["springboot-patterns"],
        tdd_skills=["springboot-tdd"],
        code_reviewer_skills=["java-coding-standards", "springboot-verification"],
        security_skills=["springboot-security"],
        db_skills=["jpa-patterns"],
    ),
    "commands": lambda: build_commands(),
    "claude_md": textwrap.dedent("""\
        # [NOMBRE DEL PROYECTO]

        ## Stack
        - **Backend**: Java 21+ / Spring Boot 3
        - **Base de datos**: PostgreSQL 17
        - **Build**: Maven o Gradle
        - **Tests**: JUnit 5 + Mockito + Testcontainers
        - **Linter**: Checkstyle / SpotBugs

        ## Arquitectura
        [DESCRIPCIÓN: qué hace este servicio, si es API REST, microservicio, etc.]

        ## Convenciones
        - Commits: Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`)
        - Tests obligatorios: mínimo 80% cobertura (JaCoCo)
        - Inmutabilidad preferida: records para DTOs, final en campos
        - Inyección por constructor, nunca por campo

        ## Comandos críticos
        - `/plan` — Antes de implementar cualquier feature
        - `/jedi-review` — Para código crítico
        - `/tdd` — Ciclo RED-GREEN-REFACTOR
        - `/security-scan` — Antes de cada release

        ## Estructura del proyecto
        ```
        src/main/java/com/example/
        ├── config/              ← Configuración Spring
        ├── controller/          ← REST controllers (delgados)
        ├── service/             ← Lógica de negocio
        ├── repository/          ← JPA repositories
        ├── model/               ← Entities + DTOs (records)
        ├── security/            ← Auth config
        └── exception/           ← Global exception handler
        src/test/java/
        └── ...                  ← Tests mirror de src/main
        ```

        ## Variables de entorno necesarias
        - `SPRING_DATASOURCE_URL` — jdbc:postgresql://...
        - `SPRING_DATASOURCE_USERNAME` / `PASSWORD`
        - `JWT_SECRET` — Para auth JWT
        - `SERVER_PORT` — Puerto (default 8080)

        ## Notas del proyecto
        [AGREGAR: decisiones de diseño, integraciones externas, etc.]
    """),
    "rule_files": {
        "springboot.md": textwrap.dedent("""\
            ---
            paths:
              - "**/*.java"
            ---
            # Spring Boot — Reglas del stack

            ## Arquitectura
            - Controllers DELGADOS: reciben request, delegan a Service, devuelven response
            - Lógica de negocio en `@Service` — nunca en el controlador
            - Validación con `@Valid` + DTOs (records) — nunca inline
            - Excepciones centralizadas con `@ControllerAdvice`

            ## JPA y base de datos
            - SIEMPRE usar `@Transactional` en servicios que modifican datos
            - Consultas N+1: usar `@EntityGraph` o `JOIN FETCH`
            - DTOs para respuestas — nunca exponer entidades JPA directamente
            - Migraciones con Flyway o Liquibase — nunca auto-ddl en producción

            ## Testing
            - `@SpringBootTest` para integration tests con `@Testcontainers`
            - `@WebMvcTest` para controller tests aislados con `MockMvc`
            - `@DataJpaTest` para repository tests
            - Mínimo 80% cobertura (JaCoCo)

            ## Anti-patrones a evitar
            - Inyección por campo (`@Autowired` en campos) — usar constructor
            - `Optional.get()` sin `isPresent()` — usar `orElseThrow()`
            - Lógica en controllers — siempre delegar a services
            - Strings mágicos — usar constantes o enums
        """),
    },
}

# ─── 2. kotlin-multiplatform ─────────────────────────────────────────────────

STACKS["kotlin-multiplatform"] = {
    "description": "Kotlin — Ktor backend + Compose Multiplatform + Android",
    "meta": {
        "backend": "kotlin",
        "backend_framework": "ktor",
        "frontend": "kotlin",
        "frontend_framework": "compose-multiplatform",
        "database": "postgresql",
        "tests_backend": "kotest",
        "linter_backend": "detekt",
    },
    "rules": ["kotlin.md", "android.md"],
    "agents": lambda: build_agents(
        architect_skills=["kotlin-patterns", "kotlin-ktor-patterns", "android-clean-architecture"],
        planner_skills=["kotlin-patterns"],
        tdd_skills=["kotlin-testing"],
        code_reviewer_skills=["kotlin-patterns", "kotlin-coroutines-flows"],
        security_skills=[],
        db_skills=["kotlin-exposed-patterns"],
        e2e_skills=[],
    ),
    "commands": lambda: build_commands(),
    "claude_md": textwrap.dedent("""\
        # [NOMBRE DEL PROYECTO]

        ## Stack
        - **Backend**: Kotlin + Ktor
        - **Frontend**: Compose Multiplatform (Android + Desktop + iOS)
        - **Base de datos**: PostgreSQL + Exposed ORM
        - **DI**: Koin
        - **Tests**: Kotest + MockK
        - **Linter**: Detekt

        ## Arquitectura
        [DESCRIPCIÓN: KMP app, backend API, módulos compartidos, etc.]

        ## Convenciones
        - Commits: Conventional Commits (`feat:`, `fix:`)
        - Tests: mínimo 80% cobertura (Kover)
        - Structured concurrency: CoroutineScope controlado, nunca GlobalScope
        - Null safety estricto: evitar `!!`, preferir `?.let {}` o `requireNotNull()`

        ## Comandos críticos
        - `/plan` — Antes de implementar cualquier feature
        - `/tdd` — Ciclo RED-GREEN-REFACTOR
        - `/jedi-review` — Para código crítico

        ## Estructura del proyecto
        ```
        shared/
        ├── commonMain/          ← Código compartido (expect/actual)
        ├── androidMain/         ← Implementaciones Android
        └── iosMain/             ← Implementaciones iOS
        backend/
        ├── src/main/kotlin/
        │   ├── routes/          ← Ktor routing
        │   ├── services/        ← Lógica de negocio
        │   └── repositories/    ← Exposed DAOs
        android/
        └── app/src/main/
            ├── ui/              ← Compose screens
            └── di/              ← Koin modules
        ```

        ## Variables de entorno necesarias
        - `DATABASE_URL` — jdbc:postgresql://...
        - `JWT_SECRET` — Para auth
        - `PORT` — Puerto del backend

        ## Notas del proyecto
        [AGREGAR: módulos compartidos, targets KMP activos, etc.]
    """),
    "rule_files": {
        "kotlin.md": textwrap.dedent("""\
            ---
            paths:
              - "**/*.kt"
              - "**/*.kts"
            ---
            # Kotlin — Reglas del stack

            ## Idioms
            - Data classes para DTOs, sealed classes para estados
            - Extension functions para utilidades — no utility classes
            - `when` exhaustivo: siempre cubrir todos los casos (sealed)
            - Scope functions: `let` para null check, `apply` para builder, `also` para side effects

            ## Coroutines
            - NUNCA `GlobalScope` — usar structured concurrency con CoroutineScope
            - `Flow` para streams de datos — `StateFlow` para estado en UI
            - `withContext(Dispatchers.IO)` para I/O, nunca bloquear el Main
            - `supervisorScope` cuando los hijos pueden fallar independientemente

            ## Ktor (backend)
            - Routing DSL con `route {}` — handlers delgados, delegar a services
            - Serialización con `kotlinx.serialization` — no Jackson
            - Content negotiation configurado globalmente
            - Auth con plugins de Ktor — no middlewares manuales

            ## Anti-patrones
            - `var` donde `val` basta — preferir inmutabilidad
            - `!!` (non-null assertion) — usar `?.let {}` o `requireNotNull()`
            - Callbacks anidados — usar coroutines/Flow
            - Platform types sin anotación — anotar nullability en boundaries Java
        """),
        "android.md": textwrap.dedent("""\
            ---
            paths:
              - "**/*.kt"
              - "**/AndroidManifest.xml"
            ---
            # Android + Compose — Reglas

            ## Clean Architecture
            - Capa de dominio sin dependencias Android (pure Kotlin)
            - UseCases como clases con `operator fun invoke()`
            - Repository interfaz en dominio, implementación en data
            - ViewModels en presentation — nunca acceden a data layer directamente

            ## Compose
            - State hoisting: estado sube, eventos bajan
            - `remember` + `mutableStateOf` para estado local
            - `collectAsStateWithLifecycle()` para StateFlow en Compose
            - Previews con `@Preview` para cada componente significativo
            - `LazyColumn` / `LazyRow` para listas — nunca Column con forEach

            ## Compose Multiplatform
            - `expect`/`actual` para APIs de plataforma
            - Resources compartidos via `commonMain/composeResources`
            - Navigation con Voyager o Decompose — no Navigation Component
        """),
    },
}

# ─── 3. swift-ios ─────────────────────────────────────────────────────────────

STACKS["swift-ios"] = {
    "description": "Swift — SwiftUI + iOS/macOS/visionOS",
    "meta": {
        "mobile": "swift",
        "mobile_framework": "swiftui",
        "tests_mobile": "swift-testing",
        "linter_mobile": "swiftlint",
    },
    "rules": ["swift.md"],
    "agents": lambda: build_agents(
        architect_skills=["swiftui-patterns", "swift-actor-persistence"],
        planner_skills=["swiftui-patterns"],
        tdd_skills=["swift-protocol-di-testing"],
        code_reviewer_skills=["swift-concurrency-6-2", "swiftui-patterns"],
        security_skills=[],
        db_skills=[],
        e2e_skills=[],
    ),
    "commands": lambda: build_commands({
        "design-md": "Al crear componentes o vistas — aplica sistema de diseño",
    }),
    "claude_md": textwrap.dedent("""\
        # [NOMBRE DEL PROYECTO]

        ## Stack
        - **Plataforma**: iOS 18+ / macOS 15+ / visionOS 2+
        - **UI**: SwiftUI (Liquid Glass en iOS 26+)
        - **Lenguaje**: Swift 6.2+
        - **Tests**: Swift Testing + XCTest
        - **Linter**: SwiftLint

        ## Arquitectura
        [DESCRIPCIÓN: app iOS, macOS, visionOS, widget, etc.]

        ## Convenciones
        - Commits: Conventional Commits
        - Tests: mínimo 80% cobertura
        - Concurrency: `@MainActor` por defecto, `@concurrent` para background
        - State: `@Observable` macro, nunca `ObservableObject` (legacy)

        ## Comandos críticos
        - `/plan` — Antes de implementar cualquier feature
        - `/tdd` — Ciclo RED-GREEN-REFACTOR
        - `/jedi-review` — Para código crítico

        ## Estructura del proyecto
        ```
        App/
        ├── Sources/
        │   ├── App/             ← Entry point (@main)
        │   ├── Features/
        │   │   ├── Home/        ← HomeView + HomeViewModel
        │   │   └── Settings/    ← SettingsView + SettingsViewModel
        │   ├── Core/
        │   │   ├── Models/      ← Domain models
        │   │   ├── Services/    ← Business logic + networking
        │   │   └── Persistence/ ← Actor-based storage
        │   └── UI/
        │       ├── Components/  ← Reusable views
        │       └── Theme/       ← Colors, fonts, spacing
        ├── Tests/               ← Swift Testing
        └── Previews/            ← Preview providers
        ```

        ## Notas del proyecto
        [AGREGAR: targets, entitlements, capabilities, etc.]
    """),
    "rule_files": {
        "swift.md": textwrap.dedent("""\
            ---
            paths:
              - "**/*.swift"
            ---
            # Swift / SwiftUI — Reglas del stack

            ## Swift 6.2 Concurrency
            - Single-threaded por defecto — todo código es `@MainActor` implícito
            - `@concurrent` explícito SOLO para trabajo en background (I/O, cómputo)
            - Actors para estado compartido thread-safe
            - `async let` para paralelismo, `TaskGroup` para N dinámico

            ## SwiftUI
            - `@Observable` macro (no `ObservableObject`) para ViewModels
            - State hoisting: `@Binding` sube estado, closures bajan eventos
            - `NavigationStack` con `navigationDestination(for:)` — no NavigationView
            - `task {}` para async work en views — se cancela automáticamente
            - Lists con `ForEach` + `Identifiable` — no indices manuales

            ## Persistencia
            - SwiftData para modelos locales (reemplaza Core Data)
            - Actor-based persistence para thread safety
            - `@Query` en views para datos reactivos

            ## Testing
            - Swift Testing framework (`@Test`, `#expect`) — no XCTest para tests nuevos
            - Protocol-based DI: definir protocolos para servicios, inyectar mocks
            - `@MainActor` en tests que acceden UI state

            ## Anti-patrones
            - Force unwrap (`!`) — usar `guard let` o `if let`
            - `DispatchQueue.main.async` — usar `@MainActor`
            - Massive ViewModels — extraer lógica a Services
            - `AnyView` type erasure — usar `@ViewBuilder` o `some View`
        """),
    },
}

# ─── 4. rust-api ──────────────────────────────────────────────────────────────

STACKS["rust-api"] = {
    "description": "Rust — Axum/Actix Web + PostgreSQL",
    "meta": {
        "backend": "rust",
        "backend_framework": "axum",
        "database": "postgresql",
        "tests_backend": "cargo-test",
        "linter_backend": "clippy",
    },
    "rules": ["rust.md"],
    "agents": lambda: build_agents(
        architect_skills=["rust-patterns"],
        planner_skills=["rust-patterns"],
        tdd_skills=["rust-testing"],
        code_reviewer_skills=["rust-patterns"],
        security_skills=[],
        db_skills=[],
    ),
    "commands": lambda: build_commands(),
    "claude_md": textwrap.dedent("""\
        # [NOMBRE DEL PROYECTO]

        ## Stack
        - **Backend**: Rust (stable)
        - **Framework**: Axum (o Actix Web)
        - **Base de datos**: PostgreSQL + SQLx
        - **Tests**: cargo test
        - **Linter**: Clippy + rustfmt

        ## Arquitectura
        [DESCRIPCIÓN: API REST, microservicio, CLI, etc.]

        ## Convenciones
        - Commits: Conventional Commits
        - Tests: mínimo 80% cobertura (cargo-tarpaulin)
        - Error handling: `thiserror` para librería, `anyhow` para app
        - Ownership: prefer borrowing, clone solo cuando es necesario

        ## Comandos críticos
        - `/plan` — Antes de implementar cualquier feature
        - `/tdd` — Ciclo RED-GREEN-REFACTOR
        - `/jedi-review` — Para código crítico

        ## Estructura del proyecto
        ```
        src/
        ├── main.rs              ← Entry point + router setup
        ├── config.rs            ← Environment config
        ├── routes/              ← Handler functions
        ├── services/            ← Business logic
        ├── models/              ← Domain types + DB models
        ├── repositories/        ← SQLx queries
        └── error.rs             ← Error types (thiserror)
        tests/
        └── integration/         ← Integration tests
        migrations/              ← SQLx migrations
        ```

        ## Variables de entorno necesarias
        - `DATABASE_URL` — postgres://...
        - `RUST_LOG` — Nivel de logging (info, debug)
        - `PORT` — Puerto del servidor

        ## Notas del proyecto
        [AGREGAR: crates clave, features flags, etc.]
    """),
    "rule_files": {
        "rust.md": textwrap.dedent("""\
            ---
            paths:
              - "**/*.rs"
              - "**/Cargo.toml"
            ---
            # Rust — Reglas del stack

            ## Ownership y borrowing
            - Prefer `&self` y `&str` sobre owned types en parámetros
            - `Clone` solo cuando hay razón clara — documentar por qué
            - `Cow<'_, str>` cuando el caller puede dar owned o borrowed
            - Lifetime elision: no anotar lifetimes innecesarios

            ## Error handling
            - `thiserror` para error types en librerías
            - `anyhow::Result` para application-level errors
            - `?` operator — nunca `.unwrap()` en producción
            - Errores con contexto: `.context("descripción")` (anyhow)

            ## Async
            - Tokio como runtime estándar
            - `#[tokio::main]` en main, `#[tokio::test]` en tests
            - `Send + Sync` bounds explícitos en traits async
            - Evitar `.await` en loops — usar `futures::stream` o `join_all`

            ## Testing
            - `#[cfg(test)]` para unit tests en el mismo archivo
            - `tests/` para integration tests
            - `proptest` o `quickcheck` para property-based testing
            - Mocks con `mockall` — traits para inyección de dependencias

            ## Anti-patrones
            - `.unwrap()` / `.expect()` en prod — usar `?`
            - `unsafe` sin documentar invariantes
            - `String` donde `&str` basta
            - `Arc<Mutex<>>` donde un channel sería más claro
        """),
    },
}

# ─── 5. cpp ───────────────────────────────────────────────────────────────────

STACKS["cpp"] = {
    "description": "C++20 — CMake + GoogleTest",
    "meta": {
        "backend": "cpp",
        "build_system": "cmake",
        "tests_backend": "googletest",
        "linter_backend": "clang-tidy",
    },
    "rules": ["cpp.md"],
    "agents": lambda: build_agents(
        architect_skills=["cpp-coding-standards"],
        planner_skills=[],
        tdd_skills=["cpp-testing"],
        code_reviewer_skills=["cpp-coding-standards"],
        security_skills=[],
        db_skills=[],
    ),
    "commands": lambda: build_commands(),
    "claude_md": textwrap.dedent("""\
        # [NOMBRE DEL PROYECTO]

        ## Stack
        - **Lenguaje**: C++20 (o C++23)
        - **Build**: CMake 3.25+
        - **Tests**: GoogleTest + CTest
        - **Linter**: clang-tidy + clang-format
        - **Sanitizers**: ASan, UBSan, TSan

        ## Arquitectura
        [DESCRIPCIÓN: librería, servicio, aplicación, embedded, etc.]

        ## Convenciones
        - Commits: Conventional Commits
        - Tests: mínimo 80% cobertura (lcov/gcov)
        - RAII para gestión de recursos — no new/delete explícito
        - Smart pointers: `unique_ptr` por defecto, `shared_ptr` solo cuando se comparte

        ## Comandos críticos
        - `/plan` — Antes de implementar cualquier feature
        - `/tdd` — Ciclo RED-GREEN-REFACTOR
        - `/jedi-review` — Para código crítico

        ## Estructura del proyecto
        ```
        src/
        ├── main.cpp             ← Entry point
        ├── core/                ← Lógica central
        └── utils/               ← Utilidades
        include/
        └── project/             ← Headers públicos
        tests/
        ├── unit/                ← Unit tests (GoogleTest)
        └── integration/         ← Integration tests
        cmake/                   ← CMake modules
        CMakeLists.txt
        ```

        ## Notas del proyecto
        [AGREGAR: dependencias, targets, plataformas soportadas, etc.]
    """),
    "rule_files": {
        "cpp.md": textwrap.dedent("""\
            ---
            paths:
              - "**/*.cpp"
              - "**/*.hpp"
              - "**/*.h"
              - "**/CMakeLists.txt"
            ---
            # C++ — Reglas del stack

            ## Modern C++ (20/23)
            - RAII obligatorio: recursos gestionados por constructores/destructores
            - `std::unique_ptr` por defecto, `std::shared_ptr` solo para ownership compartido
            - `std::span` para views de arrays, `std::string_view` para strings
            - `auto` donde el tipo es obvio, explícito donde aporta claridad
            - `constexpr` para todo lo evaluable en compile-time

            ## Safety
            - NUNCA: `new`/`delete` raw, `malloc`/`free`
            - NUNCA: C-style casts — usar `static_cast`, `dynamic_cast`
            - Bounds checking: `std::array` sobre C arrays, `.at()` sobre `[]` en debug
            - Sanitizers habilitados en CI: ASan, UBSan, TSan

            ## Testing (GoogleTest)
            - `TEST_F` con fixtures para setup/teardown compartido
            - `EXPECT_*` para checks no fatales, `ASSERT_*` para precondiciones
            - CTest para discovery automático
            - Mocks con GoogleMock — interfaces para inyección

            ## Anti-patrones
            - Raw pointers con ownership — usar smart pointers
            - `using namespace std;` en headers
            - Excepciones en destructores
            - Macros donde `constexpr`/templates funcionan
        """),
    },
}

# ─── 6. perl ──────────────────────────────────────────────────────────────────

STACKS["perl"] = {
    "description": "Perl 5.36+ — Mojolicious/Dancer2 + PostgreSQL",
    "meta": {
        "backend": "perl",
        "backend_framework": "mojolicious",
        "database": "postgresql",
        "tests_backend": "Test2",
        "linter_backend": "perlcritic",
    },
    "rules": ["perl.md"],
    "agents": lambda: build_agents(
        architect_skills=["perl-patterns"],
        planner_skills=["perl-patterns"],
        tdd_skills=["perl-testing"],
        code_reviewer_skills=["perl-patterns"],
        security_skills=["perl-security"],
        db_skills=[],
    ),
    "commands": lambda: build_commands(),
    "claude_md": textwrap.dedent("""\
        # [NOMBRE DEL PROYECTO]

        ## Stack
        - **Lenguaje**: Perl 5.36+
        - **Framework**: Mojolicious (o Dancer2)
        - **Base de datos**: PostgreSQL + DBI
        - **Tests**: Test2::V0 + prove
        - **Linter**: Perl::Critic

        ## Arquitectura
        [DESCRIPCIÓN: web app, API, CLI tool, etc.]

        ## Convenciones
        - Commits: Conventional Commits
        - Tests: mínimo 80% cobertura (Devel::Cover)
        - `use strict; use warnings;` siempre (implícito en 5.36+)
        - Subroutine signatures habilitadas

        ## Comandos críticos
        - `/plan` — Antes de implementar cualquier feature
        - `/tdd` — Ciclo RED-GREEN-REFACTOR

        ## Estructura del proyecto
        ```
        lib/
        └── MyApp/
            ├── Controller/      ← Route handlers
            ├── Model/           ← Business logic
            └── Schema/          ← DBIx::Class schemas
        t/
        ├── unit/               ← Unit tests
        └── integration/        ← Integration tests
        script/                 ← Entry points
        ```

        ## Notas del proyecto
        [AGREGAR: módulos CPAN clave, configuración, etc.]
    """),
    "rule_files": {
        "perl.md": textwrap.dedent("""\
            ---
            paths:
              - "**/*.pl"
              - "**/*.pm"
              - "**/*.t"
            ---
            # Perl — Reglas del stack

            ## Modern Perl 5.36+
            - `use v5.36;` activa strict, warnings, y signatures
            - Subroutine signatures: `sub greet($name, $greeting = 'Hello')`
            - `try/catch` nativo (Feature::Compat::Try o 5.40+)
            - Modules con `package Name;` — un módulo por archivo

            ## DBI y base de datos
            - SIEMPRE queries parametrizados: `$dbh->prepare("... WHERE id = ?")`
            - NUNCA interpolar variables en SQL
            - Transacciones explícitas: `$dbh->begin_work; ...; $dbh->commit;`
            - DBIx::Class para ORM — resultsets encadenables

            ## Testing
            - Test2::V0 como framework principal
            - `prove -lr t/` para ejecutar todos los tests
            - Fixtures con Test2::Tools::Mock
            - Devel::Cover para cobertura: `cover -test`

            ## Anti-patrones
            - Variables globales — usar lexical (`my`)
            - `eval { }` sin chequear `$@` — siempre comprobar errores
            - Regex sin `/x` flag en patterns complejos
            - `open` sin chequeo — `open my $fh, '<', $file or die "..."`
        """),
    },
}

# ─── 7. nuxt-saas ────────────────────────────────────────────────────────────

STACKS["nuxt-saas"] = {
    "description": "Nuxt 4 — Vue 3 + Nitro + PostgreSQL",
    "meta": {
        "backend": "typescript",
        "backend_framework": "nitro",
        "frontend": "typescript",
        "frontend_framework": "nuxt",
        "database": "postgresql",
        "tests_backend": "vitest",
        "tests_frontend": "playwright",
        "linter_backend": "eslint",
    },
    "rules": ["nuxt.md"],
    "agents": lambda: build_agents(
        architect_skills=["nuxt4-patterns"],
        planner_skills=["frontend-patterns"],
        tdd_skills=[],
        code_reviewer_skills=["nuxt4-patterns"],
        lang_reviewer=("typescript-reviewer", ["frontend-patterns", "nuxt4-patterns", "coding-standards"]),
        security_skills=[],
        db_skills=[],
        e2e_skills=["e2e-testing"],
    ),
    "commands": lambda: build_commands({
        "design-md": "Al crear componentes o páginas — aplica sistema de diseño",
    }),
    "claude_md": textwrap.dedent("""\
        # [NOMBRE DEL PROYECTO]

        ## Stack
        - **Frontend**: Nuxt 4 + Vue 3 (Composition API)
        - **Backend**: Nitro (server routes)
        - **Base de datos**: PostgreSQL
        - **Tests**: Vitest + Playwright
        - **Linter**: ESLint + Prettier

        ## Arquitectura
        [DESCRIPCIÓN: SaaS, portal, e-commerce, etc.]

        ## Convenciones
        - Commits: Conventional Commits
        - Tests: mínimo 80% cobertura
        - Composition API con `<script setup>` — no Options API
        - `useFetch` / `useAsyncData` para data fetching — no `$fetch` en componentes

        ## Comandos críticos
        - `/plan` — Antes de implementar cualquier feature
        - `/tdd` — Ciclo RED-GREEN-REFACTOR
        - `/design-md` — Al crear componentes UI

        ## Estructura del proyecto
        ```
        app/
        ├── pages/               ← File-based routing
        ├── components/          ← Vue components
        ├── composables/         ← Composable functions (use*)
        ├── layouts/             ← Layout components
        └── middleware/          ← Route middleware
        server/
        ├── api/                 ← API routes (Nitro)
        ├── middleware/          ← Server middleware
        └── utils/               ← Server utilities
        ```

        ## Variables de entorno necesarias
        - `NUXT_PUBLIC_API_BASE` — URL base de API
        - `DATABASE_URL` — postgres://...
        - `NUXT_SESSION_SECRET` — Secreto de sesión

        ## Notas del proyecto
        [AGREGAR: módulos Nuxt instalados, integraciones, etc.]
    """),
    "rule_files": {
        "nuxt.md": textwrap.dedent("""\
            ---
            paths:
              - "**/*.vue"
              - "**/*.ts"
              - "**/*.js"
            ---
            # Nuxt 4 — Reglas del stack

            ## Componentes
            - `<script setup lang="ts">` obligatorio — no Options API
            - Props con `defineProps<{}>()` tipado — no runtime validation
            - Emits con `defineEmits<{}>()` tipado
            - `defineModel()` para v-model bidireccional

            ## Data Fetching
            - `useFetch()` para requests SSR-safe con caching automático
            - `useAsyncData()` para transformaciones complejas
            - NUNCA `$fetch` en componentes — causa doble fetch (SSR + client)
            - `useLazyFetch()` para datos no críticos (carga sin bloquear)

            ## Hydration Safety
            - Sin `Date.now()`, `Math.random()` en setup — causan mismatch
            - `<ClientOnly>` para contenido browser-only
            - `useId()` para IDs estables entre SSR y client

            ## Performance
            - Route rules para ISR/SWR: `routeRules: { '/api/**': { swr: 60 } }`
            - `<NuxtLink>` con prefetch automático — no `<a>` para rutas internas
            - Lazy components: `<LazyComponent>` para below-the-fold
            - `definePageMeta({ middleware: [...] })` — no middleware global innecesario

            ## Anti-patrones
            - `$fetch` en componentes (doble fetch en SSR)
            - `onMounted` para datos que se pueden obtener en SSR
            - Store global para estado de un solo componente
            - Auto-imports sin awareness — conocer qué se importa
        """),
    },
}

# ─── 8. flutter ───────────────────────────────────────────────────────────────

STACKS["flutter"] = {
    "description": "Flutter 3 — Dart + Material/Cupertino",
    "meta": {
        "mobile": "dart",
        "mobile_framework": "flutter",
        "tests_mobile": "flutter_test",
        "linter_mobile": "dart-analyze",
    },
    "rules": ["flutter.md"],
    "agents": lambda: build_agents(
        architect_skills=["flutter-dart-code-review"],
        planner_skills=[],
        tdd_skills=[],
        code_reviewer_skills=["flutter-dart-code-review"],
        security_skills=[],
        db_skills=[],
        e2e_skills=[],
    ),
    "commands": lambda: build_commands({
        "design-md": "Al crear widgets o screens — aplica sistema de diseño",
    }),
    "claude_md": textwrap.dedent("""\
        # [NOMBRE DEL PROYECTO]

        ## Stack
        - **Framework**: Flutter 3 (Material 3)
        - **Lenguaje**: Dart 3
        - **State**: BLoC / Riverpod / Provider
        - **Tests**: flutter_test + integration_test
        - **Linter**: dart analyze + custom lint rules

        ## Arquitectura
        [DESCRIPCIÓN: app móvil, web, desktop, multiplataforma, etc.]

        ## Convenciones
        - Commits: Conventional Commits
        - Tests: mínimo 80% cobertura
        - Clean Architecture: presentation / domain / data
        - Widgets pequeños y reutilizables — extraer a archivos separados

        ## Comandos críticos
        - `/plan` — Antes de implementar cualquier feature
        - `/tdd` — Ciclo RED-GREEN-REFACTOR
        - `/design-md` — Al crear widgets UI

        ## Estructura del proyecto
        ```
        lib/
        ├── main.dart            ← Entry point
        ├── app/                 ← App widget, router, theme
        ├── features/
        │   └── feature_name/
        │       ├── presentation/  ← Screens, widgets, BLoC/providers
        │       ├── domain/        ← Entities, use cases, repos (interfaces)
        │       └── data/          ← Models, data sources, repo implementations
        ├── core/                ← Shared utilities, constants, theme
        └── l10n/                ← Localization
        test/
        └── features/            ← Tests mirror
        integration_test/        ← E2E tests
        ```

        ## Notas del proyecto
        [AGREGAR: state management elegido, packages clave, targets, etc.]
    """),
    "rule_files": {
        "flutter.md": textwrap.dedent("""\
            ---
            paths:
              - "**/*.dart"
              - "**/pubspec.yaml"
            ---
            # Flutter / Dart — Reglas del stack

            ## Widgets
            - Widgets PEQUEÑOS: max 80-100 líneas de build method
            - `const` constructors donde sea posible — mejor performance
            - Composición sobre herencia: `Column([WidgetA(), WidgetB()])` > un mega-widget
            - Keys solo cuando Flutter no puede diferenciar widgets (listas dinámicas)

            ## State Management
            - Elegir UNO: BLoC, Riverpod, Provider, GetX — no mezclar
            - BLoC: Events → Bloc → States. Never emit states from UI
            - Riverpod: `ref.watch()` en build, `ref.read()` en callbacks
            - Provider: `context.watch()` en build, `context.read()` en callbacks

            ## Performance
            - `const` widgets para evitar rebuilds innecesarios
            - `RepaintBoundary` para aislar rebuilds costosos
            - `ListView.builder` para listas largas — nunca `ListView(children:)`
            - DevTools performance overlay para detectar jank

            ## Testing
            - `testWidgets()` para widget tests con `WidgetTester`
            - `blocTest()` para unit tests de BLoCs
            - `pumpAndSettle()` para esperar animaciones
            - Golden tests para regresión visual

            ## Anti-patrones
            - `setState` en widgets complejos — usar state management
            - Business logic en widgets — mover a use cases/services
            - `BuildContext` pasado a funciones async — puede ser invalid
            - `late` variables sin guarantee de inicialización
        """),
    },
}

# ─── 9. ml-pytorch ────────────────────────────────────────────────────────────

STACKS["ml-pytorch"] = {
    "description": "Machine Learning — PyTorch + Python + CUDA",
    "meta": {
        "backend": "python",
        "backend_framework": "pytorch",
        "tests_backend": "pytest",
        "linter_backend": "ruff",
    },
    "rules": ["pytorch.md"],
    "agents": lambda: build_agents(
        architect_skills=["pytorch-patterns"],
        planner_skills=["python-patterns"],
        tdd_skills=["python-testing"],
        code_reviewer_skills=["pytorch-patterns", "python-patterns"],
        lang_reviewer=("python-reviewer", ["python-patterns"]),
        security_skills=[],
        db_skills=[],
    ),
    "commands": lambda: build_commands(),
    "claude_md": textwrap.dedent("""\
        # [NOMBRE DEL PROYECTO]

        ## Stack
        - **Framework ML**: PyTorch 2+
        - **Lenguaje**: Python 3.12+
        - **GPU**: CUDA 12+ / MPS (Apple Silicon)
        - **Tests**: pytest
        - **Linter**: Ruff

        ## Arquitectura
        [DESCRIPCIÓN: modelo de clasificación, generativo, RL, etc.]

        ## Convenciones
        - Commits: Conventional Commits
        - Reproducibilidad: seeds fijos, configs versionadas
        - Type hints obligatorios (mypy strict mode)
        - Experimentos tracked con wandb o mlflow

        ## Comandos críticos
        - `/plan` — Antes de implementar cualquier feature
        - `/tdd` — Ciclo RED-GREEN-REFACTOR
        - `/benchmark` — Medir performance de modelo

        ## Estructura del proyecto
        ```
        src/
        ├── data/                ← Datasets, dataloaders, transforms
        ├── models/              ← Arquitecturas (nn.Module)
        ├── training/            ← Training loops, optimizers
        ├── evaluation/          ← Métricas, inference
        ├── config/              ← Hydra/YAML configs
        └── utils/               ← Logging, reproducibility
        notebooks/               ← Exploración (no producción)
        scripts/                 ← Entry points (train, eval, export)
        tests/                   ← pytest
        ```

        ## Variables de entorno necesarias
        - `CUDA_VISIBLE_DEVICES` — GPUs disponibles
        - `WANDB_API_KEY` — Tracking de experimentos
        - `DATA_DIR` — Directorio de datasets

        ## Notas del proyecto
        [AGREGAR: modelo base, dataset, métricas target, etc.]
    """),
    "rule_files": {
        "pytorch.md": textwrap.dedent("""\
            ---
            paths:
              - "**/*.py"
            ---
            # PyTorch — Reglas del stack

            ## Modelos
            - Herencia de `nn.Module` — implementar `forward()` y `__init__()`
            - `@torch.no_grad()` en inference — nunca olvidar
            - `model.eval()` antes de inference, `model.train()` antes de training
            - Inicialización explícita de pesos cuando el default no es adecuado

            ## Training
            - Training loop explícito (no frameworks mágicos)
            - `optimizer.zero_grad()` → `loss.backward()` → `optimizer.step()`
            - Gradient clipping: `torch.nn.utils.clip_grad_norm_`
            - Mixed precision: `torch.amp.autocast` + `GradScaler`
            - Checkpoints periódicos: `torch.save(model.state_dict(), path)`

            ## Data
            - `Dataset` + `DataLoader` con `num_workers > 0`
            - `pin_memory=True` para transferencia GPU más rápida
            - Transforms como pipeline: `Compose([...])` reproducible
            - Validación split fija — nunca random por epoch

            ## Reproducibilidad
            - Seeds al inicio: `torch.manual_seed()`, `np.random.seed()`, `random.seed()`
            - `torch.use_deterministic_algorithms(True)` cuando sea posible
            - Config files (YAML/Hydra) para hiperparámetros — no hardcoded

            ## Anti-patrones
            - `.cuda()` hardcoded — usar `device = torch.device('cuda' if...)`
            - Datos en GPU que no se necesitan — `.cpu()` para métricas
            - Training sin validation — siempre monitorear overfitting
            - Notebooks como producción — extraer a scripts reproducibles
        """),
    },
}

# ─── 10. healthcare ───────────────────────────────────────────────────────────

STACKS["healthcare"] = {
    "description": "Healthcare — EMR/CDSS + HIPAA compliance (stack-agnostic)",
    "meta": {
        "domain": "healthcare",
        "compliance": "hipaa",
    },
    "rules": ["healthcare.md"],
    "agents": lambda: build_agents(
        architect_skills=["healthcare-emr-patterns", "healthcare-cdss-patterns"],
        planner_skills=[],
        tdd_skills=["healthcare-eval-harness"],
        code_reviewer_skills=["healthcare-phi-compliance"],
        security_skills=["healthcare-phi-compliance"],
        db_skills=[],
    ),
    "commands": lambda: build_commands(),
    "claude_md": textwrap.dedent("""\
        # [NOMBRE DEL PROYECTO]

        ## Stack
        - **Dominio**: Healthcare / Clinical
        - **Compliance**: HIPAA, HL7 FHIR
        - **Lenguaje**: [DEFINIR]
        - **Base de datos**: [DEFINIR] (con encryption at rest)
        - **Tests**: [DEFINIR] + healthcare eval harness

        ## Arquitectura
        [DESCRIPCIÓN: EMR, CDSS, patient portal, telemedicine, etc.]

        ## Requisitos de compliance
        - PHI (Protected Health Information) cifrado en tránsito y reposo
        - Audit trail completo para todo acceso a datos clínicos
        - Role-Based Access Control (RBAC) con principio de mínimo privilegio
        - BAA (Business Associate Agreement) con todos los vendors

        ## Convenciones
        - Commits: Conventional Commits
        - Tests: mínimo 80% cobertura + safety eval harness
        - CERO tolerancia a exposición de PHI en logs, errores, o URLs
        - Clinical scoring validado contra literatura médica

        ## Comandos críticos
        - `/plan` — Antes de implementar cualquier feature
        - `/tdd` — Ciclo RED-GREEN-REFACTOR (con eval harness)
        - `/security-scan` — OBLIGATORIO antes de cada release

        ## Estructura del proyecto
        ```
        src/
        ├── clinical/            ← Lógica clínica (CDSS, scoring)
        ├── emr/                 ← Flujos de registro médico
        ├── compliance/          ← PHI handlers, audit, encryption
        ├── integrations/        ← HL7 FHIR, lab systems
        └── api/                 ← Endpoints (con auth + audit)
        ```

        ## Notas del proyecto
        [AGREGAR: normativa específica, integraciones clínicas, etc.]
    """),
    "rule_files": {
        "healthcare.md": textwrap.dedent("""\
            ---
            description: "Healthcare compliance and clinical safety rules"
            ---
            # Healthcare — Reglas del dominio

            ## PHI (Protected Health Information)
            - NUNCA loguear PHI — sanitizar antes de cualquier output
            - Campos PHI: nombre, DOB, SSN, MRN, direcciones, teléfonos, emails, fotos
            - Encryption at rest obligatorio para toda tabla con PHI
            - Access control: cada query de PHI debe pasar por authorization layer

            ## Audit Trail
            - TODO acceso a datos clínicos debe generar audit log
            - Audit log inmutable: append-only, nunca borrar
            - Campos: who, what, when, from_where, why (clinical justification)
            - Retención mínima: 6 años (HIPAA) — verificar regulación local

            ## Clinical Decision Support (CDSS)
            - Scores clínicos (NEWS2, qSOFA, etc.) validados contra fuentes médicas
            - Drug interaction checks con base de datos actualizada (MEDI, RxNorm)
            - Alert fatigue: clasificar severidad (critical/warning/info)
            - Override logging: registrar cuando el clínico ignora una alerta

            ## Testing (Patient Safety)
            - Eval harness obligatorio: test suite de seguridad del paciente
            - Boundary testing para dosis (mínima, máxima, pediátrica, geriátrica)
            - Integration tests con datos clínicos de prueba (NEVER real PHI)
            - Deployment bloqueado si eval harness falla

            ## Anti-patrones
            - PHI en URLs, query params, o error messages
            - Datos clínicos sin audit trail
            - Scoring sin validación contra literatura
            - Deploy sin pasar eval harness de seguridad del paciente
        """),
    },
}

# ─── 11. supply-chain ────────────────────────────────────────────────────────

STACKS["supply-chain"] = {
    "description": "Supply Chain — Logistics, procurement, inventory (stack-agnostic)",
    "meta": {
        "domain": "supply-chain",
    },
    "rules": ["supply-chain.md"],
    "agents": lambda: build_agents(
        architect_skills=["carrier-relationship-management", "inventory-demand-planning"],
        planner_skills=["production-scheduling"],
        tdd_skills=[],
        code_reviewer_skills=["logistics-exception-management", "quality-nonconformance"],
        security_skills=["customs-trade-compliance"],
        db_skills=[],
    ),
    "commands": lambda: build_commands(),
    "claude_md": textwrap.dedent("""\
        # [NOMBRE DEL PROYECTO]

        ## Stack
        - **Dominio**: Supply Chain / Logistics
        - **Lenguaje**: [DEFINIR]
        - **Base de datos**: [DEFINIR]
        - **Integraciones**: ERP, TMS, WMS

        ## Arquitectura
        [DESCRIPCIÓN: TMS, WMS, demand planning, procurement, etc.]

        ## Dominios cubiertos
        - **Carrier management**: scorecards, RFP, rate negotiation
        - **Inventory**: demand forecasting, safety stock, replenishment
        - **Logistics exceptions**: delays, damages, claims
        - **Customs/trade**: HS classification, duties, FTA
        - **Production**: scheduling, changeover, bottleneck resolution
        - **Quality**: NCR lifecycle, CAPA, SPC
        - **Returns**: RMA, grading, disposition, vendor recovery
        - **Energy procurement**: tariffs, PPAs, demand charges

        ## Convenciones
        - Commits: Conventional Commits
        - Tests obligatorios para cálculos financieros y forecasting
        - Datos de prueba realistas (pero anonimizados)

        ## Comandos críticos
        - `/plan` — Antes de implementar cualquier módulo
        - `/tdd` — Ciclo RED-GREEN-REFACTOR

        ## Notas del proyecto
        [AGREGAR: ERPs conectados, carriers, regiones, etc.]
    """),
    "rule_files": {
        "supply-chain.md": textwrap.dedent("""\
            ---
            description: "Supply chain domain rules and patterns"
            ---
            # Supply Chain — Reglas del dominio

            ## Carrier Management
            - Carrier scorecards: on-time %, damage rate, cost per unit, responsiveness
            - RFP process: lane analysis → bid solicitation → award → monitoring
            - Rate validation: compare against market indices + historical
            - Contingency carriers para cada lane crítica

            ## Inventory & Demand
            - ABC/XYZ classification para priorizar atención
            - Safety stock = f(demand variability, lead time variability, service level)
            - Forecast accuracy medida con MAPE/MAD — track por SKU
            - Seasonal transitions: phase-in/phase-out con markdown strategy

            ## Logistics Exceptions
            - Escalation tiers: L1 (auto-resolve), L2 (analyst), L3 (manager), L4 (VP)
            - Claims: documentation → filing → follow-up → recovery tracking
            - Root cause categories: carrier, weather, customs, warehouse, supplier

            ## Customs & Trade
            - HS Code: clasificar al nivel de 6+ dígitos con ruling references
            - Incoterms: documentar responsibilities en cada shipment
            - FTA utilization: verify rules of origin antes de reclamar preferencia
            - Denied party screening obligatorio antes de cada shipment

            ## Anti-patrones
            - Forecasts sin medición de accuracy — siempre track MAPE
            - Safety stock estático — recalcular periódicamente
            - Claims sin documentación fotográfica
            - HS classification sin verificar contra rulings previos
        """),
    },
}

# ─── 12. content-creator ─────────────────────────────────────────────────────

STACKS["content-creator"] = {
    "description": "Content Creation — Articles, social media, video, presentations",
    "meta": {
        "domain": "content",
    },
    "rules": ["content.md"],
    "agents": lambda: build_agents(
        architect_skills=["content-engine", "article-writing"],
        planner_skills=["content-engine"],
        tdd_skills=[],
        code_reviewer_skills=[],
        security_skills=[],
        db_skills=[],
    ),
    "commands": lambda: build_commands({
        "crosspost": "Distribuir contenido a múltiples plataformas (X, LinkedIn, Threads)",
        "x-api": "Publicar o leer de X/Twitter programáticamente",
        "frontend-slides": "Crear presentaciones HTML con animaciones",
        "fal-ai-media": "Generar imágenes, video o audio con IA",
        "video-editing": "Editar video con FFmpeg, Remotion, CapCut",
        "videodb": "Indexar, buscar y editar video con VideoDB",
    }),
    "claude_md": textwrap.dedent("""\
        # [NOMBRE DEL PROYECTO]

        ## Stack
        - **Dominio**: Content Creation & Distribution
        - **Plataformas**: X, LinkedIn, Threads, YouTube, Newsletter
        - **Herramientas**: FFmpeg, Remotion, fal.ai, ElevenLabs
        - **CMS**: [DEFINIR si aplica]

        ## Arquitectura
        [DESCRIPCIÓN: blog, social presence, video channel, newsletter, etc.]

        ## Flujos de contenido
        1. **Investigación**: deep-research → outline → draft
        2. **Escritura**: article-writing con voice consistency
        3. **Distribución**: content-engine → crosspost (adaptado por plataforma)
        4. **Media**: fal-ai-media para imágenes, video-editing para video
        5. **Presentaciones**: frontend-slides para talks/pitches

        ## Convenciones
        - Voz consistente: definir en DESIGN.md o style guide
        - NUNCA contenido idéntico cross-platform — adaptar por formato
        - Atribución de fuentes obligatoria
        - Calendario de contenido en Notion/Sheets

        ## Comandos disponibles
        - `/crosspost` — Adaptar y distribuir a múltiples plataformas
        - `/x-api` — Publicar en X/Twitter
        - `/frontend-slides` — Crear presentación HTML
        - `/fal-ai-media` — Generar media con IA
        - `/video-editing` — Editar video
        - `/videodb` — Indexar y buscar en videos

        ## Notas del proyecto
        [AGREGAR: plataformas activas, tono de voz, audiencia target, etc.]
    """),
    "rule_files": {
        "content.md": textwrap.dedent("""\
            ---
            description: "Content creation and distribution rules"
            ---
            # Content Creation — Reglas del dominio

            ## Principios de escritura
            - Lead with value — la primera línea debe enganchar
            - Una idea por pieza — no mezclar temas inconexos
            - Estructura escaneable: headers, bullets, párrafos cortos
            - Voz activa preferida — evitar pasiva innecesaria

            ## Distribución multi-plataforma
            - NUNCA copiar/pegar idéntico entre plataformas
            - X: conciso, hooks fuertes, threads para profundidad
            - LinkedIn: profesional, datos/stats, CTA claro
            - YouTube: SEO en título y descripción, timestamps
            - Newsletter: personal, exclusividad, no spam

            ## Media
            - Imágenes: resolver sin texto superpuesto (accesibilidad)
            - Video: primeros 3 segundos son hook — no intros largas
            - Presentaciones: máx 6 palabras por slide, visual > texto

            ## Calidad
            - Fact-check: todo dato debe tener fuente verificable
            - Proofread: sin typos, gramática correcta
            - Atribución: citar fuentes siempre
            - A/B testing: probar variaciones de headlines/hooks
        """),
    },
}

# ─── 13. ai-agent ────────────────────────────────────────────────────────────

STACKS["ai-agent"] = {
    "description": "AI Agent Engineering — Multi-agent systems, evals, LLM pipelines",
    "meta": {
        "domain": "ai-engineering",
        "backend": "python",  # or typescript
        "tests_backend": "pytest",
        "linter_backend": "ruff",
    },
    "rules": ["ai-agent.md"],
    "agents": lambda: build_agents(
        architect_skills=["agentic-engineering", "autonomous-loops", "agent-harness-construction"],
        planner_skills=["agentic-engineering", "cost-aware-llm-pipeline"],
        tdd_skills=["eval-harness", "ai-regression-testing"],
        code_reviewer_skills=["agentic-engineering", "continuous-agent-loop"],
        lang_reviewer=("python-reviewer", ["python-patterns"]),
        security_skills=["agent-payment-x402"],
        db_skills=[],
    ),
    "commands": lambda: build_commands({
        "agent-eval": "Comparar agentes head-to-head (pass rate, costo, tiempo)",
        "claude-devfleet": "Orquestar multi-agente con DevFleet",
    }),
    "claude_md": textwrap.dedent("""\
        # [NOMBRE DEL PROYECTO]

        ## Stack
        - **Dominio**: AI Agent Engineering
        - **Lenguaje**: Python / TypeScript
        - **LLM**: Claude API (Anthropic SDK)
        - **Framework**: Claude Code / Agent SDK / LangGraph
        - **Tests**: pytest + eval harness
        - **Linter**: Ruff

        ## Arquitectura
        [DESCRIPCIÓN: single agent, multi-agent DAG, autonomous loop, etc.]

        ## Principios
        - Eval-driven development: métricas antes de features
        - Cost-aware: model routing por complejidad de tarea
        - Decomposition: tareas complejas → subtareas paralelas
        - Safety gates: quality checks entre pasos

        ## Convenciones
        - Commits: Conventional Commits
        - Evals obligatorios: pass rate, costo, latencia, consistencia
        - Prompts versionados como código
        - Budget tracking por sesión/tarea

        ## Comandos críticos
        - `/plan` — Antes de implementar cualquier feature
        - `/tdd` — Ciclo RED-GREEN-REFACTOR con eval harness
        - `/agent-eval` — Comparar agentes head-to-head
        - `/benchmark` — Medir performance de pipeline

        ## Estructura del proyecto
        ```
        src/
        ├── agents/              ← Agent definitions + system prompts
        ├── tools/               ← Tool implementations (MCP servers)
        ├── evals/               ← Evaluation harnesses + datasets
        ├── pipelines/           ← Multi-step workflows / DAGs
        ├── prompts/             ← Versioned prompt templates
        └── utils/               ← Cost tracking, model routing
        tests/
        ├── unit/                ← Unit tests
        └── evals/               ← Eval results + baselines
        ```

        ## Variables de entorno necesarias
        - `ANTHROPIC_API_KEY` — Claude API
        - `OPENAI_API_KEY` — (si se usa para comparar)
        - `MODEL_BUDGET_USD` — Presupuesto máximo por sesión

        ## Notas del proyecto
        [AGREGAR: modelos usados, pipelines activos, eval baselines, etc.]
    """),
    "rule_files": {
        "ai-agent.md": textwrap.dedent("""\
            ---
            paths:
              - "**/*.py"
              - "**/*.ts"
              - "**/prompts/**"
            ---
            # AI Agent Engineering — Reglas del stack

            ## Eval-Driven Development
            - SIEMPRE definir eval antes de implementar feature
            - Métricas obligatorias: pass rate, costo, latencia, consistencia
            - Baseline documentado — cada cambio debe medirse contra baseline
            - Evals automatizados en CI — no deploy sin pasar umbral

            ## Model Routing
            - Haiku para tareas simples y agentes worker (90% capacidad, 3x ahorro)
            - Sonnet para desarrollo principal y orquestación
            - Opus para razonamiento complejo y decisiones arquitectónicas
            - Routing dinámico: empezar con modelo barato, escalar si falla

            ## Multi-Agent Patterns
            - Orchestrator → Workers (fan-out/fan-in)
            - Pipeline secuencial con quality gates entre pasos
            - DAG con dependencias explícitas
            - Adversarial verification: 2 agentes independientes deben coincidir

            ## Prompts
            - Prompts son código: versionados, testeados, revisados
            - Separar instrucciones de datos de contexto
            - Few-shot examples > descripciones abstractas
            - Prompt injection defense: sanitizar inputs de usuarios

            ## Cost Control
            - Budget por sesión/tarea — abort si se excede
            - Token counting proactivo: estimar antes de enviar
            - Caching de respuestas frecuentes (prompt caching)
            - Batch API para tareas no interactivas (50% descuento)

            ## Anti-patrones
            - Deploy sin eval — siempre medir impacto
            - Modelo más caro "por si acaso" — routing por complejidad
            - Prompts hardcodeados sin versionado
            - Agentes sin límite de iteraciones — siempre max_turns
        """),
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# GENERATOR
# ═══════════════════════════════════════════════════════════════════════════════

def generate_all():
    print(f"Generando {len(STACKS)} stacks...\n")

    for name, cfg in sorted(STACKS.items()):
        stack_dir = os.path.join(BASE, "stacks", name)
        print(f"📦 {name}")

        # stack.yaml
        agents_str = cfg["agents"]()
        commands_str = cfg["commands"]()
        content = build_stack_yaml(
            name=name,
            description=cfg["description"],
            meta=cfg["meta"],
            rules=cfg["rules"],
            agents_str=agents_str,
            commands_str=commands_str,
        )
        write_file(os.path.join(stack_dir, "stack.yaml"), content)

        # CLAUDE.md
        write_file(os.path.join(stack_dir, "CLAUDE.md"), cfg["claude_md"])

        # pipeline.yaml (same for all)
        write_file(os.path.join(stack_dir, "pipeline.yaml"), PIPELINE)

        # Rule files
        rules_dir = os.path.join(stack_dir, "rules")
        for rule_name, rule_content in cfg["rule_files"].items():
            write_file(os.path.join(rules_dir, rule_name), rule_content)

        print()

    print(f"✅ {len(STACKS)} stacks generados")


if __name__ == "__main__":
    generate_all()
