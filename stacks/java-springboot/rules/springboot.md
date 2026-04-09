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
