# Odoo 19 — Convenciones de desarrollo

Versiones: **Odoo 19** · **Python 3.12+** · **PostgreSQL 17**

Aplica siempre estas convenciones al trabajar en módulos Odoo.

## Versión de módulo en __manifest__.py

```python
# CORRECTO: versión siempre en formato Odoo.mayor.menor.parche
{
    'name': 'Mi Módulo',
    'version': '19.0.1.0.0',   # ← SIEMPRE prefijo 19.0
    'depends': ['base'],
    'author': '[TU EMPRESA]',
    'license': 'LGPL-3',
}
```

## Python 3.12 — cambios relevantes

```python
# CORRECTO en Python 3.12: usar type hints modernos (sin imports de typing)
def get_partners(self) -> list[dict]:
    ...

# Union types con | (no Optional ni Union de typing)
def find_user(self, ref: str) -> 'res.users | None':
    ...

# f-strings anidados ya están soportados
name = f"{'hola':>10}"
```

## Estructura de un módulo

```
mi_modulo/
├── __manifest__.py         ← Metadatos: version '19.0.x.y.z', license, author
├── __init__.py
├── models/
│   ├── __init__.py
│   └── mi_modelo.py
├── views/
│   └── mi_modelo_views.xml
├── security/
│   ├── ir.model.access.csv ← Permisos por modelo
│   └── security.xml        ← ir.rules (permisos a nivel de registro)
├── data/
│   └── datos_iniciales.xml
├── static/
│   └── src/
│       └── js/             ← Componentes OWL
└── tests/
    └── test_mi_modulo.py
```

## Modelos Python (ORM de Odoo)

```python
# CORRECTO: herencia clara, campos con descripción, _sql_constraints
class MiModelo(models.Model):
    _name = 'mi.modulo.modelo'
    _description = 'Descripción legible del modelo'
    _order = 'name asc'

    name = fields.Char(string='Nombre', required=True, index=True)
    active = fields.Boolean(default=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    _sql_constraints = [
        ('name_company_unique', 'unique(name, company_id)', 'El nombre debe ser único por empresa.')
    ]
```

## Anti-patrones a evitar

- **NO** usar `browse()` dentro de bucles — usar `search()` o relaciones ORM directamente
- **NO** olvidar `sudo()` con criterio — usarlo solo cuando es necesario, documentar por qué
- **NO** hardcodear IDs de registros (usar `ref()` o `env.ref()`)
- **NO** modificar `base` directamente — usar herencia (`_inherit`)
- **NO** mezclar lógica de negocio en las vistas XML — la lógica va en Python

## Herencia correcta

```python
# Extender modelo existente (sin crear nueva tabla)
class ResPartner(models.Model):
    _inherit = 'res.partner'
    campo_custom = fields.Char(string='Campo Custom')

# Herencia delegada (crea tabla propia con FK al padre)
class MiContacto(models.Model):
    _inherits = {'res.partner': 'partner_id'}
    _name = 'mi.contacto'
    partner_id = fields.Many2one('res.partner', required=True, ondelete='cascade')
```

## Vistas XML

```xml
<!-- CORRECTO: usar external_id para todos los records -->
<record id="view_mi_modelo_form" model="ir.ui.view">
    <field name="name">mi.modulo.modelo.form</field>
    <field name="model">mi.modulo.modelo</field>
    <field name="arch" type="xml">
        <form string="Mi Modelo">
            <sheet>
                <group>
                    <field name="name"/>
                </group>
            </sheet>
        </form>
    </field>
</record>
```

## Seguridad

- **Siempre** incluir `ir.model.access.csv` para cada modelo nuevo
- Usar `ir.rules` para permisos a nivel de registro (multi-company, multi-usuario)
- Nunca dar acceso CRUD completo al grupo `base.group_user` sin revisión

```csv
# ir.model.access.csv
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_mi_modelo_user,mi.modulo.modelo user,model_mi_modulo_modelo,base.group_user,1,0,0,0
access_mi_modelo_manager,mi.modulo.modelo manager,model_mi_modulo_modelo,base.group_system,1,1,1,1
```

## Tests con TransactionCase

```python
from odoo.tests.common import TransactionCase

class TestMiModelo(TransactionCase):
    def setUp(self):
        super().setUp()
        self.modelo = self.env['mi.modulo.modelo'].create({'name': 'Test'})

    def test_nombre_requerido(self):
        with self.assertRaises(Exception):
            self.env['mi.modulo.modelo'].create({'name': False})
```

## Componentes OWL 2 (Odoo 19)

```javascript
/** @odoo-module **/
import { Component, useState, onWillStart } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";

export class MiComponente extends Component {
    static template = "mi_modulo.MiComponente";
    static props = {
        recordId: { type: Number },
    };

    setup() {
        this.state = useState({ loading: false, data: null });
        this.orm = useService("orm");

        onWillStart(async () => {
            this.state.data = await this.orm.read(
                "mi.modulo.modelo",
                [this.props.recordId],
                ["name", "active"]
            );
        });
    }
}
```

**Reglas OWL en Odoo 19:**
- Siempre declarar `static props = {}` — mejora el rendimiento del renderer
- Usar `useService("orm")` en lugar de `this.env.services.rpc` (deprecado)
- Preferir `onWillStart` sobre `willStart` del ciclo de vida antiguo
- `/** @odoo-module **/` sigue siendo requerido como primera línea

## PostgreSQL 17 — consideraciones específicas

```python
# CORRECTO: usar índices parciales para campos con muchos NULL (PG17 los optimiza mejor)
# En el modelo, añadir índice en campo opcionales con alta selectividad:
class MiModelo(models.Model):
    _name = 'mi.modulo.modelo'

    # Para queries frecuentes sobre registros activos:
    _sql_constraints = [...]

    def init(self):
        # Índice parcial — solo indexa registros activos (PG17 feature)
        tools.create_index(
            self._cr,
            'mi_modulo_modelo_active_idx',
            self._table,
            ['name'],
            where='active = true'
        )
```

**Notas de compatibilidad PG17:**
- Autenticación por defecto: `scram-sha-256` (configurar en `pg_hba.conf`)
- `VACUUM` más eficiente en tablas grandes — relevante para `mail.message`, `ir.attachment`
- Sin cambios en sintaxis SQL usada por el ORM de Odoo
- Backup con `pg_dump --format=custom` sigue siendo la opción recomendada

## Migraciones de esquema

- Usar `pre-migration.py` y `post-migration.py` en carpeta `migrations/X.Y.Z/`
- No renombrar columnas directamente — usar scripts de migración
- Probar migraciones en copia de base de datos antes de producción
- Para migrar desde Odoo 17/18: usar herramienta oficial `openupgradelib`

## Comandos de desarrollo frecuentes

```bash
# Actualizar módulo
python odoo-bin -c odoo.conf -u mi_modulo -d mi_db

# Ejecutar tests del módulo
python odoo-bin -c odoo.conf --test-enable -u mi_modulo -d mi_db --stop-after-init

# Ejecutar solo una clase de test
python odoo-bin -c odoo.conf --test-tags /mi_modulo:TestMiModelo -d mi_db --stop-after-init

# Scaffold (crear módulo nuevo)
python odoo-bin scaffold mi_modulo addons/

# Conectar a PostgreSQL 17
psql -U odoo -h localhost -p 5432 mi_db
```

## odoo.conf mínimo para desarrollo

```ini
[options]
addons_path = addons,odoo/addons
db_host = localhost
db_port = 5432
db_user = odoo
db_password = odoo
db_name = False
; PostgreSQL 17 usa scram-sha-256 por defecto
; asegúrate de que pg_hba.conf tenga: host all odoo 127.0.0.1/32 scram-sha-256
http_port = 8069
workers = 0
log_level = info
```
