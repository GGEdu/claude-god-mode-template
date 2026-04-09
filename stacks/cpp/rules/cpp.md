---
paths:
  - "**/*.cpp"
  - "**/*.hpp"
  - "**/*.h"
  - "**/CMakeLists.txt"
---
# C++ — Reglas del stack

## Modern C++ (20/23)
- RAII obligatorio: recursos gestionados por constructores/destructores
- `std::unique_ptr` por defecto, `std::shared_ptr` solo para ownership compartido
- `std::span` para views de arrays, `std::string_view` para strings
- `auto` donde el tipo es obvio, explícito donde aporta claridad
- `constexpr` para todo lo evaluable en compile-time

## Safety
- NUNCA: `new`/`delete` raw, `malloc`/`free`
- NUNCA: C-style casts — usar `static_cast`, `dynamic_cast`
- Bounds checking: `std::array` sobre C arrays, `.at()` sobre `[]` en debug
- Sanitizers habilitados en CI: ASan, UBSan, TSan

## Testing (GoogleTest)
- `TEST_F` con fixtures para setup/teardown compartido
- `EXPECT_*` para checks no fatales, `ASSERT_*` para precondiciones
- CTest para discovery automático
- Mocks con GoogleMock — interfaces para inyección

## Anti-patrones
- Raw pointers con ownership — usar smart pointers
- `using namespace std;` en headers
- Excepciones en destructores
- Macros donde `constexpr`/templates funcionan
