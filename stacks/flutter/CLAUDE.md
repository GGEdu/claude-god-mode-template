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
