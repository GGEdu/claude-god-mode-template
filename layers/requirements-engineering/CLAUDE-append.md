## Layer activa: Ingeniería de Requisitos

Este proyecto incluye el layer `requirements-engineering` adaptado de [Maya-AQSS/agentics-extractor-requisitos](https://github.com/Maya-AQSS/agentics-extractor-requisitos).

### Pipeline de 7 fases

| Fase | Agente / Skill | Disparador | Output |
|------|----------------|------------|--------|
| 1. Descubrimiento | `business-analyst` | `/iniciar-requisitos` | `docs/src/1_epics_and_features.md` |
| 2. Arquitectura | `architect` + `requirements-stride` | aprobación humana | `docs/src/2_architecture_risks.md` |
| 3. Backlog | `business-analyst` | aprobación | N archivos en `docs/src/backlog/F-XX.Y_*.md` |
| 4. Diagramas | `architect` + `requirements-stride` | aprobación | `docs/src/3_c4_diagrams.md` |
| 5. Publicación VitePress | (ambos agentes) | aprobación | `docs/.vitepress/config.mts` |
| 6. Subida a GitHub | (script bash) | confirmación | Issues + Project + milestones |
| 7. Gestión de cambios | `change-manager` | `/revisar-cambios` (re-entrante) | `AUDIT_LOG.md` actualizado |

### Reglas operativas críticas

- **NO se genera código fuente de aplicación** durante este pipeline. Solo artefactos `.md` de requisitos.
- **Modo archivo-primero:** la fuente de verdad es `docs/src/0_descripcion_proyecto.md`. Si falta info, devolver checklist y pausar — no abrir entrevista en chat.
- **Compuertas de aprobación humana** entre fases 1↔2↔3↔4↔5. La Fase 7 es re-entrante.
- **Auditoría obligatoria:** cada fase escribe append a `docs/src/AUDIT_LOG.md`.

### Archivos canónicos del workspace

| Archivo | Tipo | Propósito |
|---------|------|-----------|
| `docs/src/0_descripcion_proyecto.md` | input maestro | Contexto bruto del proyecto (rellenar ANTES) |
| `docs/src/0_cambios_requisitos.md` | input | Cambios solicitados (alimenta Fase 7) |
| `docs/src/AUDIT_LOG.md` | output append-only | Registro de fases ejecutadas |
| `docs/src/ERROR_PREVENTION_LOG.md` | output append-only | Lecciones aprendidas / reglas anti-reincidencia |
| `docs/src/backlog/F-*.md` | outputs | Una Feature por archivo, formato `F-XX.Y_titulo.md` |

### Atajos

```bash
# Fases 1-5 secuenciales con compuertas:
/workflow requirements

# Fase 7 (re-entrante, cada vez que entran cambios):
/workflow change-review

# Subida manual a GitHub Issues (Fase 6):
REPO=owner/repo ORG=org PROJECT_NUMBER=N \
  bash layers/requirements-engineering/scripts/upload_backlog_to_github.sh --dry-run
```
