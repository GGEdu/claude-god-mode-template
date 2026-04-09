
## Dominio: Healthcare

### Compliance
- **HIPAA**: PHI cifrado en tránsito y reposo, audit trail completo
- **BAA**: Business Associate Agreement con todos los vendors
- **RBAC**: Principio de mínimo privilegio para acceso a datos clínicos

### Requisitos de dominio
- Eval harness de seguridad del paciente obligatorio antes de deploy
- Drug interaction checks con base de datos actualizada
- Clinical scoring validado contra literatura médica
- NUNCA loguear PHI — sanitizar antes de cualquier output
