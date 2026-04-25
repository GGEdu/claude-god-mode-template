---
name: iniciar-requisitos
description: >-
  Ejecuta la **Fase 1: Descubrimiento y Desglose** del pipeline de ingeniería
  de requisitos. Lee `docs/src/0_descripcion_proyecto.md` como contexto bruto
  y produce `docs/src/1_epics_and_features.md`. Usar cuando se inicia un
  proyecto greenfield o se necesita derivar Epics+Features desde notas/
  conversaciones de negocio.
---

# /iniciar-requisitos — Fase 1

Activa el agente **`business-analyst`** para la **Fase 1: Descubrimiento y Desglose** del pipeline de ingeniería de requisitos.

> Este comando pertenece al layer `requirements-engineering`. Para que esté
> disponible, el proyecto debe haberse inicializado con `make init-project ... LAYERS=requirements-engineering`.

## Pasos obligatorios (delegados al agente)

1. Revisar `docs/src/ERROR_PREVENTION_LOG.md` antes de actuar.
2. Leer `docs/src/0_descripcion_proyecto.md` como fuente única de contexto.
3. Validar completitud mínima en bloques 0, 2, 3, 4, 5, 6, 7 y semáforo de 9.
4. Si faltan datos: devolver checklist de secciones a completar y pausar.
5. Extraer Epics y Features desde bloques 2, 3, 4, 5, 6, 7.
6. Crear `docs/src/1_epics_and_features.md` en disco.
7. Actualizar `docs/src/AUDIT_LOG.md`.
8. Mostrar resumen ejecutivo en chat y esperar aprobación.

## Después de Fase 1

Cuando el usuario apruebe los Epics, ejecutar **Fase 2: Arquitectura y Riesgos** con el agente `architect` (skill `requirements-stride`).

Ver el pipeline completo en `layers/requirements-engineering/docs/pipeline.md` o ejecutar `/workflow requirements` para correr todas las fases secuencialmente con compuertas de aprobación.
