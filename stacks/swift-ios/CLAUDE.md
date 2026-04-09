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
