---
name: revisar-cambios
description: >-
  Ejecuta la **Fase 7: Gestión de Cambios y Revisión de Backlog** del pipeline
  de ingeniería de requisitos. Lee `docs/src/0_cambios_requisitos.md` y aplica
  análisis de impacto sobre el backlog existente. No modifica nada sin
  aprobación explícita del usuario.
---

# /revisar-cambios — Fase 7 (re-entrante)

Activa el agente **`change-manager`** para la **Fase 7: Gestión de Cambios y Revisión de Backlog** del pipeline de ingeniería de requisitos.

Esta fase **es re-entrante**: cada ejecución se registra como `CHANGE-XX` independiente en `AUDIT_LOG.md`. Puedes ejecutarla N veces a lo largo del proyecto cada vez que entren nuevos cambios.

## Pasos obligatorios (delegados al agente)

1. Revisar `docs/src/ERROR_PREVENTION_LOG.md` antes de actuar.
2. Leer `docs/src/0_cambios_requisitos.md` — fuente de los cambios solicitados.
3. Leer todos los archivos en `docs/src/backlog/` — estado actual del backlog.
4. Leer `docs/src/1_epics_and_features.md` — mapa de Epics y Features.
5. Ejecutar análisis de impacto: catalogar cambios, mapear impacto, construir matriz.
6. Mostrar matriz de impacto en chat y **esperar confirmación explícita** antes de modificar nada.
7. Aplicar solo los cambios aprobados explícitamente por el usuario.
8. Verificar coherencia de dependencias: sin ciclos, prioridades consistentes.
9. Actualizar `docs/src/AUDIT_LOG.md` con registro `CHANGE-XX`.

## Cuándo invocar

- Tras una reunión con cliente/stakeholders que introduzca nuevos requisitos.
- Cuando se detecta que un requisito previo era incorrecto o incompleto.
- Tras un cambio de prioridades de negocio que afecte al alcance.
- Cuando el equipo descubre una restricción técnica que invalida un backlog.

## Atajo equivalente

`/workflow change-review` ejecuta este mismo flujo desde `pipeline.yaml`.
