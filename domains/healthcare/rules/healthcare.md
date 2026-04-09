---
description: "Healthcare compliance and clinical safety rules"
---
# Healthcare — Reglas del dominio

## PHI (Protected Health Information)
- NUNCA loguear PHI — sanitizar antes de cualquier output
- Campos PHI: nombre, DOB, SSN, MRN, direcciones, teléfonos, emails, fotos
- Encryption at rest obligatorio para toda tabla con PHI
- Access control: cada query de PHI debe pasar por authorization layer

## Audit Trail
- TODO acceso a datos clínicos debe generar audit log
- Audit log inmutable: append-only, nunca borrar
- Campos: who, what, when, from_where, why (clinical justification)
- Retención mínima: 6 años (HIPAA) — verificar regulación local

## Clinical Decision Support (CDSS)
- Scores clínicos (NEWS2, qSOFA, etc.) validados contra fuentes médicas
- Drug interaction checks con base de datos actualizada (MEDI, RxNorm)
- Alert fatigue: clasificar severidad (critical/warning/info)
- Override logging: registrar cuando el clínico ignora una alerta

## Testing (Patient Safety)
- Eval harness obligatorio: test suite de seguridad del paciente
- Boundary testing para dosis (mínima, máxima, pediátrica, geriátrica)
- Integration tests con datos clínicos de prueba (NEVER real PHI)
- Deployment bloqueado si eval harness falla

## Anti-patrones
- PHI en URLs, query params, o error messages
- Datos clínicos sin audit trail
- Scoring sin validación contra literatura
- Deploy sin pasar eval harness de seguridad del paciente
