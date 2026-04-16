# Stack: Flutter

**Versiones:** Flutter 3 · Dart 3 · Material/Cupertino · flutter_test

## Inicializar

```bash
make dev-stack STACK=flutter
```

Activa: reglas Flutter, slash commands, CLAUDE.md con plantilla.

---

## Slash commands activados

| Comando | Cuándo usarlo |
| --- | --- |
| `/jedi-review` | Para código crítico (3 expertos: Beck, Fowler, Acton) |
| `/git-workflow` | Workflow de commits y PRs |
| `/workflow-runner <nombre>` | Ejecutar pipelines (`feature`, `hotfix`, `refactor`) |
| `/canary-watch URL` | Monitoreo post-deploy en staging/producción |
| `/security-scan` | Auditoría de seguridad de configuración y `.claude/` |
| `/design-md` | Aplicar dirección visual (Material 3 o Cupertino guidelines) |
| `/codebase-onboarding` | Generar guía de onboarding del repo |

Las prácticas `flutter-patterns`, `dart-style`, `widget-architecture`, `state-management` y `performance-optimization` se aplican como skills embebidas en los agentes del stack.

---

## Convenciones clave

### Arquitectura — Separación UI / Lógica

```text
lib/
├── main.dart                ← Entrypoint
├── config/
│   ├── theme.dart          ← Configuración Material/Cupertino
│   └── routes.dart         ← Rutas nombradas
├── features/
│   ├── users/
│   │   ├── presentation/
│   │   │   ├── pages/      ← Pantallas (full-screen widgets)
│   │   │   ├── widgets/    ← Componentes reutilizables
│   │   │   └── bloc/       ← State management (BLoC o Riverpod)
│   │   ├── data/
│   │   │   ├── models/     ← Data transfer objects (DTOs)
│   │   │   ├── datasources/ ← API / local storage
│   │   │   └── repositories/ ← Interfaz unificada
│   │   └── domain/
│   │       ├── entities/   ← Objetos de negocio puros
│   │       ├── repositories/ ← Interfaces
│   │       └── usecases/   ← Lógica de negocio
└── shared/
    ├── widgets/            ← Componentes globales
    ├── services/           ← Services de app
    └── utils/              ← Helpers
test/
└── features/               ← Tests paralelo a lib/
```

### Widget — Ejemplo correcto (Stateless + BLoC)

```dart
// CORRECTO: separación clara UI / lógica
import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../bloc/user_bloc.dart';

class UserListPage extends StatelessWidget {
  const UserListPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Users')),
      body: BlocBuilder<UserBloc, UserState>(
        builder: (context, state) {
          if (state is UserLoading) {
            return const Center(child: CircularProgressIndicator());
          } else if (state is UserLoaded) {
            return ListView.builder(
              itemCount: state.users.length,
              itemBuilder: (context, index) {
                final user = state.users[index];
                return ListTile(
                  title: Text(user.name),
                  subtitle: Text(user.email),
                );
              },
            );
          } else if (state is UserError) {
            return Center(child: Text('Error: ${state.message}'));
          }
          return Container();
        },
      ),
    );
  }
}

// INCORRECTO: setState en árbol profundo, lógica en widget
class BadUserList extends StatefulWidget {
  @override
  State<BadUserList> createState() => _BadUserListState();
}

class _BadUserListState extends State<BadUserList> {
  List<User> users = [];

  @override
  void initState() {
    super.initState();
    // Lógica de API aquí → MOVER A REPOSITORY + BLOC
    fetchUsers();
  }

  void fetchUsers() async {
    // ...
    setState(() { users = ...; });
  }

  @override
  Widget build(BuildContext context) {
    return ListView.builder(
      itemBuilder: (context, index) => setState(() { /* inline */ }),
    );
  }
}
```

### State Management — BLoC

```dart
// lib/features/users/presentation/bloc/user_bloc.dart
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../domain/usecases/get_users.dart';

abstract class UserEvent {}
class FetchUsers extends UserEvent {}
class CreateUser extends UserEvent {
  final String name;
  CreateUser(this.name);
}

abstract class UserState {}
class UserLoading extends UserState {}
class UserLoaded extends UserState {
  final List<User> users;
  UserLoaded(this.users);
}
class UserError extends UserState {
  final String message;
  UserError(this.message);
}

class UserBloc extends Bloc<UserEvent, UserState> {
  final GetUsers getUsers;

  UserBloc(this.getUsers) : super(UserLoading()) {
    on<FetchUsers>(_onFetchUsers);
    on<CreateUser>(_onCreateUser);
  }

  Future<void> _onFetchUsers(FetchUsers event, Emitter<UserState> emit) async {
    emit(UserLoading());
    try {
      final users = await getUsers();
      emit(UserLoaded(users));
    } catch (e) {
      emit(UserError(e.toString()));
    }
  }

  Future<void> _onCreateUser(CreateUser event, Emitter<UserState> emit) async {
    // Lógica de creación
  }
}
```

### Testing — Widget tests

```dart
// test/features/users/presentation/pages/user_list_test.dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_bloc/flutter_bloc.dart';

void main() {
  group('UserListPage', () {
    testWidgets('displays loading indicator while fetching', (tester) async {
      await tester.pumpWidget(
        MaterialApp(
          home: BlocProvider<UserBloc>(
            create: (_) => MockUserBloc()..add(FetchUsers()),
            child: const UserListPage(),
          ),
        ),
      );

      expect(find.byType(CircularProgressIndicator), findsOneWidget);
    });

    testWidgets('displays users when loaded', (tester) async {
      final mockBloc = MockUserBloc();
      when(() => mockBloc.state).thenReturn(
        UserLoaded([
          User(id: 1, name: 'Alice', email: 'alice@example.com'),
        ]),
      );

      await tester.pumpWidget(
        MaterialApp(
          home: BlocProvider<UserBloc>.value(
            value: mockBloc,
            child: const UserListPage(),
          ),
        ),
      );

      expect(find.text('Alice'), findsOneWidget);
    });
  });
}
```

### Formularios — Validación

```dart
// Form con validación integrada
class UserFormWidget extends StatefulWidget {
  @override
  State<UserFormWidget> createState() => _UserFormWidgetState();
}

class _UserFormWidgetState extends State<UserFormWidget> {
  final _formKey = GlobalKey<FormState>();
  String email = '';
  String name = '';

  @override
  Widget build(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        children: [
          TextFormField(
            validator: (value) {
              if (value?.isEmpty ?? true) return 'Name required';
              return null;
            },
            onSaved: (value) => name = value ?? '',
          ),
          TextFormField(
            validator: (value) {
              if (value?.isEmpty ?? true) return 'Email required';
              if (!value!.contains('@')) return 'Invalid email';
              return null;
            },
            onSaved: (value) => email = value ?? '',
          ),
          ElevatedButton(
            onPressed: () {
              if (_formKey.currentState!.validate()) {
                _formKey.currentState!.save();
                // Enviar al servidor
              }
            },
            child: const Text('Submit'),
          ),
        ],
      ),
    );
  }
}
```

---

## Anti-patrones a evitar

- **Lógica de negocio en widgets** — mover a repositories + usecases
- **`setState` en árbol profundo** — usar BLoC / Riverpod para estado compartido
- **Widgets sin const constructor** — siempre const cuando sea posible (performance)
- **Sin separar presentation / domain** — mantener arquitectura clean
- **API calls directo en widget** — usar repositories y state management
- **Sin manejo de estados de error** — siempre mostrar error state en UI
- **BuildContext propagación manual** — usar Provider o BLoC para inyectar dependencias

---

## Comandos útiles

```bash
# Desarrollo
flutter run
flutter run -d chrome          # Web
flutter run -d all             # Todos los dispositivos

# Tests
flutter test
flutter test --coverage

# Build
flutter build apk              # Android release
flutter build ios              # iOS (macOS only)
flutter build web              # Web

# Análisis
flutter analyze
dart analyze

# Limpieza
flutter clean
flutter pub get
```

## Variables de entorno

```bash
# .env (con flutter_dotenv)
API_BASE_URL=https://api.example.com
API_TIMEOUT=30
DATABASE_ENCRYPTION_KEY=...

# En main.dart:
// await dotenv.load(fileName: ".env");
```

---

## Ejemplo completo

→ [CLAUDE.md para Flutter App](/examples/flutter-app-CLAUDE)
