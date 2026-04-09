# [NOMBRE DEL PROYECTO]

## Stack
- **Framework**: Odoo 19 (Community / Enterprise)
- **Backend**: Python 3.12+
- **Frontend**: OWL 2 (Odoo Web Library)
- **Base de datos**: PostgreSQL 17
- **Tests**: unittest (TransactionCase / SavepointCase)
- **Linter**: Ruff

## Arquitectura
[DESCRIPCIÓN: qué módulos Odoo se desarrollan, si es SaaS/On-Premise, qué módulos base se extienden]

## Convenciones
- Commits: Conventional Commits (`feat:`, `fix:`, `refactor:`, `docs:`)
- Cada módulo tiene su propio `security/ir.model.access.csv`
- Lógica de negocio en modelos Python, no en controladores ni vistas
- Herencia de módulos base preferida sobre modificación directa

## Comandos críticos
- `/plan` — Antes de implementar cualquier módulo o feature
- `/jedi-review` — Para código crítico
- `/tdd` — Ciclo RED-GREEN-REFACTOR para tests TransactionCase
- `/security-scan` — Antes de cada release (access rules, ir.rules)

## Módulos desarrollados en este proyecto
[LISTA: mi_modulo_1, mi_modulo_2, ...]

## Addons path
```
[RUTA]/addons/          ← módulos custom
[RUTA]/odoo/addons/     ← módulos Odoo base (no modificar)
```

## Variables de entorno necesarias
- `ODOO_DB` — Nombre de la base de datos
- `ODOO_MASTER_PASSWORD` — Master password de admin
- `DATABASE_URL` — Conexión PostgreSQL

## Notas del proyecto
[PLACEHOLDER: arquitectura multi-empresa, versión exacta de Odoo, módulos enterprise usados]
