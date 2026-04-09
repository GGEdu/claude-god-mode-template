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
