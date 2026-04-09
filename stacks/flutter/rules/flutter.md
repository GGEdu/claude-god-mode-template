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
