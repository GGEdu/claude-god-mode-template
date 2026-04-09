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
