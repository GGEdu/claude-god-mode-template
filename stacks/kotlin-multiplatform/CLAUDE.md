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
