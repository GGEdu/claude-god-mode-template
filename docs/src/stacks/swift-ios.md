# Stack: Swift / iOS

**Versiones:** Swift 6.2+ · SwiftUI · iOS 18+ / macOS 15+ / visionOS 2+ · Swift Testing · SwiftLint

## Inicializar

```bash
make dev-stack STACK=swift-ios
```

Activa: reglas Swift, slash commands, CLAUDE.md con plantilla.

---

## Slash commands activados

| Comando | Cuándo usarlo |
| --- | --- |
| `/jedi-review` | Para código crítico — review de 3 expertos en paralelo |
| `/git-workflow` | Si necesitas recordar el workflow de commits y PRs |
| `/workflow-runner <nombre>` | Para ejecutar un pipeline completo: `feature`, `hotfix`, `refactor` |
| `/canary-watch URL` | Post-deploy — monitoreo con Playwright en URLs live |
| `/codebase-onboarding` | Al entrar en un repo nuevo — genera guía de onboarding |
| `/benchmark` | Medir rendimiento antes/después de un PR o cambio |
| `/design-md` | Al crear componentes o vistas — aplica sistema de diseño |
| `/security-scan` | Escanea `.claude/` por vulnerabilidades |

Las skills `swiftui-patterns`, `swift-concurrency-6-2`, `swift-protocol-di-testing`, `swift-actor-persistence` y `liquid-glass-design` se aplican como skills embebidas en los agentes del stack.

---

## Convenciones clave

### Arquitectura — Feature-based

```text
App/
├── Sources/
│   ├── App/             ← Entry point (@main)
│   ├── Features/
│   │   ├── Home/        ← HomeView + HomeViewModel
│   │   └── Settings/    ← SettingsView + SettingsViewModel
│   ├── Core/
│   │   ├── Models/      ← Domain models
│   │   ├── Services/    ← Business logic + networking
│   │   └── Persistence/ ← Actor-based storage (SwiftData)
│   └── UI/
│       ├── Components/  ← Reusable views
│       └── Theme/       ← Colors, fonts, spacing
├── Tests/               ← Swift Testing
└── Previews/            ← Preview providers
```

### Swift 6.2 Concurrency

```swift
// Swift 6.2: @MainActor es el default implícito en toda la app
// No necesitas anotarlo — el código es single-threaded por defecto

// CORRECTO: @concurrent explícito solo para trabajo en background
@concurrent
func fetchUserData(id: UUID) async throws -> User {
    // Este código corre fuera del main actor
    let data = try await URLSession.shared.data(from: apiURL(id))
    return try JSONDecoder().decode(User.self, from: data.0)
}

// INCORRECTO: DispatchQueue.main.async — legacy
// DispatchQueue.main.async { self.users = result }  // ← no usar

// CORRECTO: async let para paralelismo
func loadDashboard() async throws {
    async let users = fetchUsers()
    async let stats = fetchStats()
    (self.users, self.stats) = try await (users, stats)
}
```

### ViewModel con @Observable

```swift
// CORRECTO: @Observable macro (Swift 5.9+)
@Observable
final class UserListViewModel {
    var users: [User] = []
    var isLoading = false
    var error: String?

    private let service: UserServiceProtocol

    init(service: UserServiceProtocol = UserService()) {
        self.service = service
    }

    func loadUsers() async {
        isLoading = true
        defer { isLoading = false }

        do {
            users = try await service.fetchUsers()
        } catch {
            self.error = error.localizedDescription
        }
    }
}

// INCORRECTO: ObservableObject (legacy)
// class UserListViewModel: ObservableObject {
//     @Published var users: [User] = []  // ← evitar
// }
```

### Vista SwiftUI con NavigationStack

```swift
struct UserListView: View {
    @State private var viewModel = UserListViewModel()

    var body: some View {
        NavigationStack {
            Group {
                if viewModel.isLoading {
                    ProgressView()
                } else {
                    List(viewModel.users) { user in
                        NavigationLink(value: user) {
                            UserRowView(user: user)
                        }
                    }
                }
            }
            .navigationTitle("Usuarios")
            .navigationDestination(for: User.self) { user in
                UserDetailView(user: user)
            }
        }
        .task {
            // task{} se cancela automáticamente al desaparecer la vista
            await viewModel.loadUsers()
        }
        .alert("Error", isPresented: .constant(viewModel.error != nil)) {
            Button("OK") { viewModel.error = nil }
        } message: {
            Text(viewModel.error ?? "")
        }
    }
}
```

### Tests con Swift Testing

```swift
import Testing

@Suite("UserViewModel Tests")
struct UserViewModelTests {

    @Test("Carga usuarios correctamente")
    func loadUsers() async throws {
        let mockService = MockUserService(users: [
            User(id: UUID(), name: "Alice", email: "alice@example.com"),
        ])
        let viewModel = UserListViewModel(service: mockService)

        await viewModel.loadUsers()

        #expect(viewModel.users.count == 1)
        #expect(viewModel.users.first?.name == "Alice")
        #expect(!viewModel.isLoading)
    }

    @Test("Maneja errores de red")
    func handleNetworkError() async throws {
        let mockService = MockUserService(error: URLError(.notConnectedToInternet))
        let viewModel = UserListViewModel(service: mockService)

        await viewModel.loadUsers()

        #expect(viewModel.error != nil)
        #expect(viewModel.users.isEmpty)
    }
}

// Protocol para DI — facilita mocking
protocol UserServiceProtocol {
    func fetchUsers() async throws -> [User]
}
```

### Persistencia con SwiftData

```swift
import SwiftData

@Model
final class CachedUser {
    var id: UUID
    var name: String
    var email: String
    var syncedAt: Date

    init(id: UUID, name: String, email: String) {
        self.id = id
        self.name = name
        self.email = email
        self.syncedAt = .now
    }
}

// CORRECTO: Actor-based persistence para thread safety
actor PersistenceService {
    private let container: ModelContainer

    init() throws {
        container = try ModelContainer(for: CachedUser.self)
    }

    func save(_ user: CachedUser) throws {
        let context = ModelContext(container)
        context.insert(user)
        try context.save()
    }
}
```

### Principios Swift

- **`@Observable` macro**: no `ObservableObject` / `@Published` (legacy)
- **`@concurrent`**: solo para I/O y cómputo pesado — el resto es main actor por defecto
- **Protocols para DI**: definir protocolos para servicios, inyectar mocks en tests
- **`guard let` / `if let`**: nunca force unwrap (`!`) en producción
- **`task {}`**: para async work en views — se cancela al desaparecer la vista
- **`NavigationStack`**: no `NavigationView` (deprecated)

---

## Anti-patrones a evitar

- Force unwrap (`!`) — usar `guard let`, `if let`, o `??`
- `DispatchQueue.main.async` — usar `@MainActor` o `await MainActor.run {}`
- `ObservableObject` / `@Published` — migrar a `@Observable`
- Massive ViewModels con lógica de negocio — extraer a Services
- `AnyView` type erasure — usar `@ViewBuilder` o `some View`
- `NavigationView` — reemplazar por `NavigationStack`
- Estado en singletons globales — usar DI vía inicializador

---

## Comandos útiles

```bash
# Build y tests
xcodebuild test -scheme MyApp -destination 'platform=iOS Simulator,name=iPhone 16'

# Lint
swiftlint lint
swiftlint lint --fix  # autocorrección

# Format
swift-format format --in-place Sources/**/*.swift

# Swift Package Manager
swift build
swift test
swift package resolve

# Dependencias (SPM)
swift package add-dependency https://github.com/apple/swift-collections
```

## Variables de entorno / configuración

```bash
# En Xcode: Edit Scheme → Run → Arguments → Environment Variables
API_BASE_URL=https://api.miapp.com
API_KEY=          # No hardcodear — usar Keychain en producción
ENVIRONMENT=development
FEATURE_FLAGS_ENABLED=true
```
