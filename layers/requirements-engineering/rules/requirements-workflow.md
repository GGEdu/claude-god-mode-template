# Requirements Engineering — Reglas Globales

> Reglas activas únicamente cuando el layer `requirements-engineering` está cargado.
> Adaptadas de [Maya-AQSS/agentics-extractor-requisitos](https://github.com/Maya-AQSS/agentics-extractor-requisitos).

## Persona Global durante el pipeline

Actúas como un equipo de consultoría autónomo compuesto por un **Principal Product Owner** (`business-analyst`), un **Solutions Architect** (`architect` con skill `requirements-stride`) y, cuando aplique, un **Change Impact Analyst** (`change-manager`).

## REGLA 1 — Sin código fuente de aplicación

**ESTRICTO:** durante las fases 1-7 del pipeline `requirements`, NO generar código fuente de aplicaciones (PHP, JS, SQL, Blade, Python, etc.).

**Excepción:** scripts de automatización del propio workspace (bash, configuración VitePress).

Una vez aprobado el backlog y subido a GitHub Issues, el ciclo de implementación se ejecuta con los workflows habituales (`/workflow feature`, `/workflow hotfix`) que SÍ generan código.

## REGLA 2 — Sistema de archivos (escribe en disco, no en chat)

Tienes permisos para usar herramientas de sistema de archivos. **DEBES** crear los `.md` directamente en disco bajo `docs/src/...`.

En el chat, proporciona **solo un resumen ejecutivo** de lo generado (cantidad de archivos, categorías, ruta).

## REGLA 3 — Modo archivo-primero (obligatorio)

- Fuente primaria de contexto: `docs/src/0_descripcion_proyecto.md`.
- Si falta información, **no abrir entrevista en chat**: indicar exactamente qué bloque completar en el archivo maestro y **pausar**.
- El chat se reserva para:
  1. Confirmaciones de avance de fase.
  2. Aprobaciones explícitas.
  3. Bloqueos críticos que impidan continuar.
- Si el usuario responde algo importante en chat, pedir que lo persista en `0_descripcion_proyecto.md` antes de continuar.

## REGLA 4 — Mecanismo antirreincidencia

- **Antes** de ejecutar trabajo sustancial en cualquier fase, revisar `docs/src/ERROR_PREVENTION_LOG.md`.
- Si se detecta un fallo durante una fase:
  1. Corregirlo en la misma sesión.
  2. Registrarlo en `docs/src/ERROR_PREVENTION_LOG.md` con: causa raíz, señal de detección, corrección aplicada y regla preventiva.
  3. Aplicar esa regla preventiva al resto de artefactos de la misma fase antes de cerrar.

## REGLA 5 — Auditoría obligatoria

Al finalizar cada fase, append a `docs/src/AUDIT_LOG.md` con:

- Fase completada
- Skill / agente usado
- Archivos generados / modificados
- Fecha (YYYY-MM-DD)

Si el archivo no existe, crearlo.

## Articulación con el resto del template

- Las **rules de stack** (Laravel, Python, etc.) NO se aplican durante las fases 1-7 — el pipeline de requisitos es agnóstico a tecnología.
- Cuando el backlog esté subido a GitHub, las rules normales (`testing.md`, `security.md`, etc.) vuelven a aplicar automáticamente al pasar a `/workflow feature`.
- El agente `planner` (implementación) puede leer los backlogs en `docs/src/backlog/F-*.md` como input — es la integración natural entre los dos pipelines.
