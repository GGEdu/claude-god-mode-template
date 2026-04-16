# Stack: C++

**Versiones:** C++20 · CMake 3.25+ · GoogleTest · clang-tidy

## Inicializar

```bash
make dev-stack STACK=cpp
```

Activa: reglas C++, slash commands, CLAUDE.md con plantilla.

---

## Slash commands activados

| Comando | Cuándo usarlo |
| --- | --- |
| `/jedi-review` | Para código crítico (3 expertos: Beck, Fowler, Acton) |
| `/git-workflow` | Workflow de commits y PRs |
| `/workflow-runner <nombre>` | Ejecutar pipelines (`feature`, `hotfix`, `refactor`) |
| `/canary-watch URL` | Monitoreo post-deploy en staging/producción |
| `/security-scan` | Auditoría de seguridad de configuración y `.claude/` |
| `/benchmark` | Medir regresiones de rendimiento con microbenchmarks |
| `/codebase-onboarding` | Generar guía de onboarding del repo |

Las prácticas `cpp-patterns`, `raii-memory-management`, `testing-googletest`, `security-review` y `performance-optimization` se aplican como skills embebidas en los agentes del stack.

---

## Convenciones clave

### Arquitectura — Headers y CMakeLists modular

```text
include/
├── myproject/
│   ├── User.hpp             ← Definición de clase
│   ├── UserRepository.hpp   ← Interfaz/abstracción
│   └── service/
│       └── UserService.hpp
src/
├── User.cpp
├── UserRepository.cpp
└── service/
    └── UserService.cpp
tests/
├── CMakeLists.txt
├── UserTest.cpp
└── UserServiceTest.cpp
CMakeLists.txt              ← Build configuration
```

### RAII — Resource Acquisition Is Initialization

```cpp
// CORRECTO: RAII con std::unique_ptr
class DatabasePool {
private:
    std::vector<std::unique_ptr<Connection>> connections;

public:
    void addConnection() {
        connections.push_back(std::make_unique<Connection>());
        // Destructor automático al salir del scope
    }
};

// INCORRECTO: manual new/delete
class BadPool {
private:
    Connection* conn;

public:
    BadPool() { conn = new Connection(); }
    ~BadPool() { delete conn; } // Fácil olvidarse, memory leak
};
```

### Clases con parámetros — Separar headers de implementación

```cpp
// include/myproject/User.hpp
#pragma once
#include <string>

namespace myproject {

class User {
private:
    int id_;
    std::string email_;

public:
    User(int id, const std::string& email);
    
    int getId() const;
    const std::string& getEmail() const;
    
    void setEmail(const std::string& email);
};

}  // namespace myproject

// src/User.cpp
#include "myproject/User.hpp"

namespace myproject {

User::User(int id, const std::string& email)
    : id_(id), email_(email) {}

int User::getId() const { return id_; }
const std::string& User::getEmail() const { return email_; }

void User::setEmail(const std::string& email) {
    email_ = email;
}

}  // namespace myproject
```

### Table-driven tests con GoogleTest

```cpp
// tests/UserTest.cpp
#include <gtest/gtest.h>
#include "myproject/User.hpp"

using namespace myproject;

struct UserTestCase {
    int id;
    std::string email;
    int expectedId;
};

class UserTest : public ::testing::TestWithParam<UserTestCase> {};

TEST_P(UserTest, ConstructorInitializesFields) {
    const auto& param = GetParam();
    User user(param.id, param.email);

    EXPECT_EQ(user.getId(), param.expectedId);
    EXPECT_EQ(user.getEmail(), param.email);
}

INSTANTIATE_TEST_SUITE_P(
    UserTests,
    UserTest,
    ::testing::Values(
        UserTestCase{1, "alice@example.com", 1},
        UserTestCase{2, "bob@example.com", 2},
        UserTestCase{999, "invalid", 999}
    )
);
```

### Error handling — std::optional y std::variant

```cpp
// Retornar valor opcional
std::optional<User> findUser(int id) {
    if (id < 0) return std::nullopt;
    return User(id, "user@example.com");
}

// Usar:
if (auto user = findUser(1)) {
    std::cout << user->getEmail();
} else {
    std::cout << "Not found";
}

// Para errores con contexto: std::variant
std::variant<User, std::string> createUser(const std::string& email) {
    if (email.empty()) return "Email required";
    return User(1, email);
}

// Usar:
if (std::holds_alternative<std::string>(result)) {
    std::cout << "Error: " << std::get<std::string>(result);
}
```

### CMakeLists.txt — Ejemplo mínimo

```cmake
cmake_minimum_required(VERSION 3.25)
project(myproject CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Librería principal
add_library(myproject_lib
    src/User.cpp
    src/UserRepository.cpp
)

target_include_directories(myproject_lib PUBLIC include)

# Tests
enable_testing()
find_package(GTest REQUIRED)

add_executable(myproject_tests
    tests/UserTest.cpp
)

target_link_libraries(myproject_tests myproject_lib GTest::gtest_main)
add_test(NAME MyProjectTests COMMAND myproject_tests)
```

---

## Anti-patrones a evitar

- **Raw pointers para ownership** — usar `std::unique_ptr` / `std::shared_ptr`
- **`new` / `delete` manual** — eso es lo que smart pointers resuelven
- **Sin constructor / destructor definidos** — especialmente en RAII
- **`using namespace std;` en headers** — solo en `.cpp`, nunca en `hpp`
- **Ignorar warnings de compilador** — compilar con `-Wall -Wextra -Werror`
- **Threads sin sincronización clara** — usar `std::mutex` y RAII para locks
- **Copias innecesarias** — pasar por const ref cuando sea posible

---

## Comandos útiles

```bash
# Build
cmake -B build -DCMAKE_BUILD_TYPE=Debug
cmake --build build

# Tests
./build/myproject_tests

# Lint
clang-tidy src/*.cpp -checks=*

# Release build
cmake -B build-release -DCMAKE_BUILD_TYPE=Release
cmake --build build-release

# Code coverage (si usar gcov)
cmake -B build -DCMAKE_BUILD_TYPE=Debug -DCOVERAGE=ON
cmake --build build
ctest
```

## Variables de entorno

```bash
CMAKE_BUILD_TYPE=Debug          # Debug o Release
CMAKE_CXX_COMPILER=clang++      # Compilador
CXXFLAGS=-Wall -Wextra -Werror  # Flags adicionales
```

---

## Ejemplo completo

→ [CLAUDE.md para C++ Microservicio](/examples/cpp-microservice-CLAUDE)
