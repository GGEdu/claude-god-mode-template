# Stack: Odoo 19

**Versiones:** Odoo 19 · Python 3.12+ · PostgreSQL 17 · OWL 2

## Inicializar

```bash
make dev-stack STACK=odoo
```

Activa: reglas Odoo 19, slash commands, CLAUDE.md con plantilla.

---

## Slash commands activados

| Comando | Cuándo usarlo |
| --- | --- |
| `/jedi-review` | Para código crítico (3 expertos: Beck, Fowler, Acton) |
| `/git-workflow` | Workflow de commits y PRs |
| `/workflow-runner <nombre>` | Ejecutar pipelines (`feature`, `hotfix`, `refactor`) |
| `/canary-watch URL` | Monitoreo post-deploy en staging/producción |
| `/security-scan` | Auditoría de seguridad de configuración y `.claude/` |
| `/benchmark` | Medir regresiones de rendimiento |
| `/codebase-onboarding` | Generar guía de onboarding del repo |

Además de los comandos anteriores, este stack incluye comandos universales (`/ck`, `/plankton-code-quality`, `/context-budget`, etc.).

Las prácticas `python-patterns`, `python-testing`, `api-design`, `database-migrations` y `security-review` se aplican como skills embebidas en agentes.

---

## Convenciones clave

### Versión del módulo

Siempre en formato `19.0.mayor.menor.parche`:

```python
{'version': '19.0.1.0.0'}  # en __manifest__.py
```

### Python 3.12 — type hints modernos

```python
# Sin imports de typing
def get_partners(self) -> list[dict]: ...
def find_user(self, ref: str) -> 'res.users | None': ...
```

### Modelos

```python
class MiModelo(models.Model):
    _name = 'mi.modulo.modelo'
    _description = 'Descripción legible'
    _order = 'name asc'

    name = fields.Char(string='Nombre', required=True, index=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
```

### OWL 2

```javascript
/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class MiComponente extends Component {
    static template = "mi_modulo.MiComponente";
    static props = { recordId: { type: Number } };  // ← obligatorio

    setup() {
        this.orm = useService("orm");  // no this.env.services.rpc (deprecado)
        onWillStart(async () => { ... });  // no willStart() antiguo
    }
}
```

### Seguridad

- **Siempre** `security/ir.model.access.csv` por cada modelo nuevo
- Usar `ir.rules` para permisos multi-company / multi-usuario
- `sudo()` con criterio y documentado con un comentario `# sudo: necesario porque X`

---

## Anti-patrones a evitar

- `browse()` dentro de bucles — usar `search()` o relaciones ORM
- Hardcodear IDs de registros — usar `ref()` o `env.ref()`
- Modificar el módulo `base` directamente — usar `_inherit`
- Lógica de negocio en vistas XML
- `this.env.services.rpc` en OWL (deprecado) — usar `useService("orm")`

---

## Comandos útiles

```bash
# Actualizar módulo
python odoo-bin -c odoo.conf -u mi_modulo -d mi_db

# Tests del módulo
python odoo-bin -c odoo.conf --test-enable -u mi_modulo -d mi_db --stop-after-init

# Tests de una clase específica
python odoo-bin -c odoo.conf --test-tags /mi_modulo:TestMiModelo -d mi_db --stop-after-init

# Scaffold (crear módulo nuevo)
python odoo-bin scaffold mi_modulo addons/

# PostgreSQL 17
psql -U odoo -h localhost -p 5432 mi_db
```

---

## PostgreSQL 17 — notas específicas

- Autenticación por defecto: `scram-sha-256` (configurar en `pg_hba.conf`)
- Índices parciales para campos con muchos NULL son más eficientes (PG17 los optimiza mejor)
- `VACUUM` más eficiente en tablas grandes — relevante para `mail.message` y `ir.attachment`
