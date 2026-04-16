# Stack: Kotlin Multiplatform

**Versiones:** Kotlin 2.0 · Ktor 3 · Compose Multiplatform · Android · PostgreSQL · Kotest · Detekt

## Inicializar

```bash
make dev-stack STACK=kotlin-multiplatform
```

Activa: reglas Kotlin multiplatforma, slash commands, CLAUDE.md con plantilla.

---

## Slash commands activados

| Comando | Cuándo usarlo |
| --- | --- |
| `/jedi-review` | Para código crítico (3 expertos: Beck, Fowler, Acton) |
| `/git-workflow` | Workflow de commits y PRs |
| `/workflow-runner <nombre>` | Ejecutar pipelines (`feature`, `hotfix`, `refactor`) |
| `/canary-watch URL` | Monitoreo post-deploy en staging/producción |
| `/security-scan` | Auditoría de seguridad de configuración y `.claude/` |
| `/benchmark` | Medir regresiones de rendimiento en mobile/JVM |
| `/codebase-onboarding` | Generar guía de onboarding del repo |

Las prácticas `kotlin-patterns`, `multiplatform-architecture`, `coroutine-management`, `testing-kotest` y `performance-optimization` se aplican como skills embebidas en los agentes del stack.

---

## Convenciones clave

### Arquitectura — Shared + Platform-Specific

```text
shared/
├── src/commonMain/kotlin/       ← Código compartido (no acceso a APIs específicas)
│   ├── domain/                  ← Entidades de negocio
│   ├── usecase/                 ← Casos de uso puros
│   ├── repository/              ← Interfaces (implementadas per-platform)
│   └── model/                   ← DTOs y tipos comunes
├── src/androidMain/kotlin/      ← Android-specific (Room, DataStore)
├── src/iosMain/kotlin/          ← iOS-specific (SQLite, UserDefaults)
├── src/jvmMain/kotlin/          ← JVM-specific (Spring Boot, JDBC)
└── src/commonTest/              ← Tests compartidos
composeApp/                       ← Compose Multiplatform UI
├── src/commonMain/
│   └── kotlin/com/example/
│       ├── screens/             ← Pages
│       ├── viewmodels/          ← State management (Compose)
│       └── components/          ← Reusable widgets
└── src/[platform]Main/          ← Platform-specific UI
```

### Sealed Classes — Type-safe state

```kotlin
// CORRECTO: sealed class para casos de uso
sealed class UserState {
    object Loading : UserState()
    data class Success(val users: List<User>) : UserState()
    data class Error(val message: String) : UserState()
}

// Usar con when (exhaustive)
when (state) {
    is UserState.Loading -> showLoadingSpinner()
    is UserState.Success -> displayUsers(state.users)
    is UserState.Error -> showError(state.message)
}

// INCORRECTO: strings o enums sin type safety
enum class UserStateEnum { LOADING, SUCCESS, ERROR }
var message: String? = null  // Error message si SUCCESS? ¿Dónde?
```

### Coroutines — Lifecycle management

```kotlin
// CORRECTO: viewModelScope para lifecycle-aware cancellation
class UserViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UserState>(UserState.Loading)
    val uiState: StateFlow<UserState> = _uiState.asStateFlow()
    
    fun loadUsers() {
        viewModelScope.launch {
            try {
                _uiState.value = UserState.Loading
                val users = userRepository.getUsers()
                _uiState.value = UserState.Success(users)
            } catch (e: Exception) {
                _uiState.value = UserState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

// INCORRECTO: launch sin scope (memory leak)
fun loadUsers() {
    GlobalScope.launch {  // ← Nunca usar, no se cancela
        val users = userRepository.getUsers()
        updateUI(users)
    }
}

// INCORRECTO: blocking calls en coroutine
val user = userRepository.getUser(id)  // ← Blocking, usa delay
val user = withContext(Dispatchers.IO) {
    userRepository.getUser(id)  // ← Mejor si es blocking
}
```

### Repository — Platform-specific implementation

```kotlin
// shared/src/commonMain/kotlin/com/example/repository/UserRepository.kt
interface UserRepository {
    suspend fun getUsers(): List<User>
    suspend fun getUserById(id: String): User
}

// shared/src/androidMain/kotlin/com/example/repository/AndroidUserRepository.kt
class AndroidUserRepository(private val db: UserDatabase) : UserRepository {
    override suspend fun getUsers(): List<User> = withContext(Dispatchers.IO) {
        db.userDao().getAllUsers().map { it.toDomain() }
    }
    
    override suspend fun getUserById(id: String): User = withContext(Dispatchers.IO) {
        db.userDao().getById(id).toDomain()
    }
}

// shared/src/jvmMain/kotlin/com/example/repository/JvmUserRepository.kt
class JvmUserRepository(private val dataSource: DataSource) : UserRepository {
    override suspend fun getUsers(): List<User> = withContext(Dispatchers.IO) {
        dataSource.connection.use { conn ->
            conn.prepareStatement("SELECT * FROM users").use { stmt ->
                stmt.executeQuery().use { rs ->
                    generateSequence {
                        if (rs.next()) User(rs.getString("id"), rs.getString("name"))
                        else null
                    }.toList()
                }
            }
        }
    }
    
    override suspend fun getUserById(id: String): User {
        // ...
    }
}
```

### Ktor Server — Routing y handlers

```kotlin
// jvm/src/jvmMain/kotlin/com/example/Application.kt
fun Application.configureRouting(userService: UserService) {
    routing {
        get("/api/users") {
            try {
                val users = userService.getUsers()
                call.respond(HttpStatusCode.OK, users)
            } catch (e: Exception) {
                call.respond(HttpStatusCode.InternalServerError, 
                    mapOf("error" to e.message))
            }
        }
        
        post("/api/users") {
            try {
                val request = call.receive<CreateUserRequest>()
                val user = userService.createUser(request.name, request.email)
                call.respond(HttpStatusCode.Created, user)
            } catch (e: ValidationException) {
                call.respond(HttpStatusCode.BadRequest, 
                    mapOf("error" to e.message))
            }
        }
    }
}
```

### Testing — Kotest

```kotlin
// shared/src/commonTest/kotlin/UserRepositoryTest.kt
class UserRepositoryTest : StringSpec({
    val repository = FakeUserRepository()
    
    "should return all users" {
        val users = repository.getUsers()
        users shouldHaveSize 0
    }
    
    "should save and retrieve user" {
        val user = User("1", "Alice")
        repository.saveUser(user)
        
        val retrieved = repository.getUserById("1")
        retrieved.shouldNotBeNull()
        retrieved.name shouldBe "Alice"
    }
    
    "should throw on invalid id" {
        shouldThrow<UserNotFoundException> {
            repository.getUserById("invalid-id")
        }
    }
})

// Parametrized tests
class UserValidationTest : StringSpec({
    val testCases = listOf(
        "" to "Name required",
        "A".repeat(256) to "Name too long",
        "valid" to null,
    )
    
    testCases.forEach { (name, expectedError) ->
        "validate name '$name'" {
            if (expectedError != null) {
                shouldThrow<ValidationException> {
                    User.validate(name)
                }
            } else {
                User.validate(name) shouldNotThrow
            }
        }
    }
})
```

### Compose Multiplatform — State management

```kotlin
// composeApp/src/commonMain/kotlin/App.kt
@Composable
fun App(userViewModel: UserViewModel = UserViewModel()) {
    val uiState by userViewModel.uiState.collectAsState()
    
    when (val state = uiState) {
        is UserState.Loading -> {
            Box(modifier = Modifier.fillMaxSize()) {
                CircularProgressIndicator(Modifier.align(Alignment.Center))
            }
        }
        is UserState.Success -> {
            LazyColumn {
                items(state.users) { user ->
                    UserCard(user)
                }
            }
        }
        is UserState.Error -> {
            Box(modifier = Modifier.fillMaxSize()) {
                Text(state.message, Modifier.align(Alignment.Center))
            }
        }
    }
}

@Composable
fun UserCard(user: User) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(user.name, style = MaterialTheme.typography.headlineSmall)
            Text(user.email, style = MaterialTheme.typography.bodySmall)
        }
    }
}
```

---

## Anti-patrones a evitar

- **Código específico de plataforma en commonMain** — usar expect/actual
- **Blocking calls sin `withContext(Dispatchers.IO)`** — causas ANR en Android
- **GlobalScope.launch** — siempre usar `viewModelScope`, `lifecycleScope`, o constructores
- **Sin sealed classes para estados** — usar `Any` / `String` es type-unsafe
- **Mutación directa de state** — siempre usar `StateFlow` / `MutableStateFlow`
- **Excepciones en suspendfun sin try/catch** — manejar siempre errores en coroutines
- **No cancelar resources** — usar `useContext` para AutoCloseable

---

## Comandos útiles

```bash
# Desarrollo
./gradlew run                   # JVM

# Android
./gradlew installDebug
./gradlew connectedAndroidTest

# Tests
./gradlew allTests
./gradlew testDebugUnitTest

# Lint
./gradlew detekt

# Build
./gradlew build
./gradlew assembleDebug         # APK
```

## Variables de entorno

```bash
JDBC_URL=jdbc:postgresql://localhost:5432/kotlin_mp
JDBC_USER=postgres
JDBC_PASSWORD=

PORT=8080
DATABASE_POOL_SIZE=10
```

---

## Ejemplo completo

→ [CLAUDE.md para Kotlin Multiplatform](/examples/kotlin-mp-CLAUDE)
