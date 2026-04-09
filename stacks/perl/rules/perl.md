---
paths:
  - "**/*.pl"
  - "**/*.pm"
  - "**/*.t"
---
# Perl — Reglas del stack

## Modern Perl 5.36+
- `use v5.36;` activa strict, warnings, y signatures
- Subroutine signatures: `sub greet($name, $greeting = 'Hello')`
- `try/catch` nativo (Feature::Compat::Try o 5.40+)
- Modules con `package Name;` — un módulo por archivo

## DBI y base de datos
- SIEMPRE queries parametrizados: `$dbh->prepare("... WHERE id = ?")`
- NUNCA interpolar variables en SQL
- Transacciones explícitas: `$dbh->begin_work; ...; $dbh->commit;`
- DBIx::Class para ORM — resultsets encadenables

## Testing
- Test2::V0 como framework principal
- `prove -lr t/` para ejecutar todos los tests
- Fixtures con Test2::Tools::Mock
- Devel::Cover para cobertura: `cover -test`

## Anti-patrones
- Variables globales — usar lexical (`my`)
- `eval { }` sin chequear `$@` — siempre comprobar errores
- Regex sin `/x` flag en patterns complejos
- `open` sin chequeo — `open my $fh, '<', $file or die "..."`
