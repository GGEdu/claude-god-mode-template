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
