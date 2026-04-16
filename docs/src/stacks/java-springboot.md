# Stack: Java Spring Boot

**Versiones:** Java 21 · Spring Boot 3 · PostgreSQL · JUnit 5 · Maven/Gradle · Checkstyle

## Inicializar

```bash
make dev-stack STACK=java-springboot
```

Activa: reglas Spring Boot, slash commands, CLAUDE.md con plantilla.

---

## Slash commands activados

| Comando | Cuándo usarlo |
| --- | --- |
| `/jedi-review` | Para código crítico (3 expertos: Beck, Fowler, Acton) |
| `/git-workflow` | Workflow de commits y PRs |
| `/workflow-runner <nombre>` | Ejecutar pipelines (`feature`, `hotfix`, `refactor`) |
| `/canary-watch URL` | Monitoreo post-deploy en staging/producción |
| `/security-scan` | Auditoría de seguridad de configuración y `.claude/` |
| `/benchmark` | Medir regresiones de rendimiento en endpoints |
| `/codebase-onboarding` | Generar guía de onboarding del repo |

Las prácticas `spring-patterns`, `spring-testing`, `database-transactions`, `api-design` y `security-review` se aplican como skills embebidas en los agentes del stack.

---

## Convenciones clave

### Arquitectura — Layered

```text
src/main/java/com/example/
├── DemoApplication.java      ← @SpringBootApplication entrypoint
├── controller/               ← @RestController (thin: parse → service → response)
├── service/                  ← @Service (business logic)
├── repository/               ← JpaRepository (data access)
├── entity/                   ← @Entity JPA models
├── dto/                      ← Data transfer objects (request/response)
├── config/                   ← @Configuration beans
├── exception/                ← Custom exceptions
└── security/                 ← Security config
src/test/java/               ← Test paralelo a src/main/java
```

### Controller — Thin, delegating

```java
// CORRECTO: controlador delgado
@RestController
@RequestMapping("/api/users")
public class UserController {
    
    private final UserService userService;
    
    public UserController(UserService userService) {
        this.userService = userService;
    }
    
    @PostMapping
    public ResponseEntity<UserResponse> createUser(@Valid @RequestBody CreateUserRequest request) {
        User user = userService.createUser(request.getEmail(), request.getName());
        return ResponseEntity.status(201).body(new UserResponse(user));
    }
    
    @GetMapping("/{id}")
    public ResponseEntity<UserResponse> getUser(@PathVariable Long id) {
        return userService.findById(id)
            .map(user -> ResponseEntity.ok(new UserResponse(user)))
            .orElse(ResponseEntity.notFound().build());
    }
}

// INCORRECTO: lógica de negocio en el controller
@PostMapping
public User createUser(@RequestBody User user) {
    // Validación, lógica de negocio aquí → MOVER A SERVICE
    if (user.getEmail().isEmpty()) throw new Exception();
    userRepository.save(user);
    return user;
}
```

### Service — Transaccional

```java
// CORRECTO: lógica de negocio con @Transactional
@Service
public class UserService {
    
    private final UserRepository userRepository;
    private final EmailService emailService;
    
    public UserService(UserRepository userRepository, EmailService emailService) {
        this.userRepository = userRepository;
        this.emailService = emailService;
    }
    
    @Transactional
    public User createUser(String email, String name) {
        // Validación de reglas de negocio
        if (userRepository.existsByEmail(email)) {
            throw new DuplicateEmailException("Email already exists");
        }
        
        User user = new User();
        user.setEmail(email);
        user.setName(name);
        
        User saved = userRepository.save(user);
        
        // Send welcome email (si falla, todo rollback)
        emailService.sendWelcome(saved);
        
        return saved;
    }
    
    public Optional<User> findById(Long id) {
        return userRepository.findById(id);
    }
}
```

### Entity — JPA con lazy loading

```java
// CORRECTO: lazy loading por defecto, eager cuando necesario
@Entity
@Table(name = "users")
public class User {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, unique = true)
    private String email;
    
    @Column(nullable = false)
    private String name;
    
    @OneToMany(mappedBy = "user", fetch = FetchType.LAZY)
    private Set<Order> orders = new HashSet<>();
    
    // Constructors, getters, setters
    public User() {}
    
    public User(String email, String name) {
        this.email = email;
        this.name = name;
    }
}
```

### Repository — JPA custom queries

```java
// CORRECTO: Query personalizado con eager loading
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    
    // Query simple
    Optional<User> findByEmail(String email);
    
    // Query con FETCH JOIN para evitar N+1
    @Query("SELECT u FROM User u LEFT JOIN FETCH u.orders WHERE u.id = ?1")
    Optional<User> findByIdWithOrders(Long id);
    
    // Paginación
    Page<User> findByActiveTrue(Pageable pageable);
}
```

### Testing — JUnit 5 + MockMvc

```java
// tests/java/com/example/UserControllerTest.java
@SpringBootTest
@AutoConfigureMockMvc
class UserControllerTest {
    
    @Autowired
    private MockMvc mockMvc;
    
    @MockBean
    private UserService userService;
    
    @Test
    void testCreateUserReturns201() throws Exception {
        User user = new User("test@example.com", "Test User");
        when(userService.createUser("test@example.com", "Test User"))
            .thenReturn(user);
        
        mockMvc.perform(post("/api/users")
            .contentType(MediaType.APPLICATION_JSON)
            .content("""
                {
                    "email": "test@example.com",
                    "name": "Test User"
                }
                """))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.email").value("test@example.com"));
    }
    
    @Test
    void testGetUserNotFoundReturns404() throws Exception {
        when(userService.findById(999L))
            .thenReturn(Optional.empty());
        
        mockMvc.perform(get("/api/users/999"))
            .andExpect(status().isNotFound());
    }
}

// Repository test con @DataJpaTest (solo DB layer)
@DataJpaTest
class UserRepositoryTest {
    
    @Autowired
    private UserRepository userRepository;
    
    @Test
    void testSaveAndFindByEmail() {
        User user = new User("alice@example.com", "Alice");
        userRepository.save(user);
        
        Optional<User> found = userRepository.findByEmail("alice@example.com");
        assertThat(found).isPresent();
        assertThat(found.get().getName()).isEqualTo("Alice");
    }
}
```

---

## Anti-patrones a evitar

- **Lógica de negocio en @Controller** — mover a @Service
- **@Transactional en @Repository** — poner en @Service donde se necesita rollback de múltiples tablas
- **N+1 queries sin @Query FETCH JOIN** — siempre eager load relaciones si las usas
- **Sin paginación en listados** — retornar `Page` con límite
- **Raw exceptions sin custom types** — crear excepciones custom que extienda `RuntimeException`
- **Inyección global de ApplicationContext** — usar constructor injection siempre
- **Sin validación en @RequestBody** — usar `@Valid` + anotaciones `@NotNull`, `@Email`, etc.

---

## Comandos útiles

```bash
# Desarrollo (Maven)
mvn spring-boot:run

# Tests
mvn test
mvn test -DargLine="-Dspring.profiles.active=test"
mvn clean verify     # incluye integration tests

# Build
mvn clean package
java -jar target/demo-0.0.1-SNAPSHOT.jar

# Lint / Format
mvn checkstyle:check
mvn spotbugs:check

# Gradle alternative
./gradlew bootRun
./gradlew test
./gradlew build
```

## Variables de entorno

```bash
SPRING_DATASOURCE_URL=jdbc:postgresql://localhost:5432/springboot_db
SPRING_DATASOURCE_USERNAME=postgres
SPRING_DATASOURCE_PASSWORD=

SPRING_JPA_HIBERNATE_DDL_AUTO=update
SPRING_JPA_SHOW_SQL=false

SERVER_PORT=8080
SPRING_PROFILES_ACTIVE=development
```

---

## Ejemplo completo

→ [CLAUDE.md para Spring Boot API](/examples/springboot-api-CLAUDE)
