# Documentación del Claude God Mode Template

Mapa de lectura para entender este template, ordenado por urgencia y profundidad.

## 🚀 Quick Start (5 min)

1. **[`../README.md`](../README.md)** — Visión general, prerequisites, `make install`, `make init-project`.

## 📐 Arquitectura del sistema (30 min)

2. **[`../Sintesis.md`](../Sintesis.md)** — Documento de diseño maestro. La biblia del template.
   - §1: Filosofía central (5 capas + 3 sistemas de enforcement)
   - §2: State machine para operación autónoma (gates obligatorios)
   - §3: Anatomía del repositorio
   - §10: Hooks programáticos
   - §14: Memoria y aprendizaje
   - §17: Adopción progresiva

## 🏛 Decisiones arquitectónicas (15 min)

3. **[`../ORCHESTRATION_DECISIONS.md`](../ORCHESTRATION_DECISIONS.md)** — Histórico de la migración de 9 orchestrators a `pipeline.yaml`. Lecciones aprendidas.

4. **[`audits/Sintesis-errores.md`](audits/Sintesis-errores.md)** — Auditoría conceptual original (2 pasadas). Vulnerabilidades del diseño y cómo se cerraron.

5. **[`audits/plan-de-integracion.md`](audits/plan-de-integracion.md)** — Plan que llevó al estado actual. Útil para entender por qué hay ciertos archivos.

## 🛠 Guías de uso

6. **[`src/instalacion.md`](src/instalacion.md)** — Instalación completa paso a paso.
7. **[`src/primeros-pasos.md`](src/primeros-pasos.md)** — Primera sesión de trabajo.
8. **[`src/inicializar-proyecto.md`](src/inicializar-proyecto.md)** — Inicializar un proyecto desde cero.
9. **[`src/onboarding-progresivo.md`](src/onboarding-progresivo.md)** — Curva de adopción del enforcement (off → warn → block).
10. **[`src/referencia.md`](src/referencia.md)** — Referencia de comandos y estructura.

## 📚 Por stack tecnológico

11. **[`src/stacks/`](src/stacks/)** — Una guía por stack (laravel, python-api, etc.).

## 🔧 Operación y mantenimiento

12. **[`../skills/INDEX.md`](../skills/INDEX.md)** — Índice navegable de las 139 skills.
13. **[`../.claude/pipeline.schema.yaml`](../.claude/pipeline.schema.yaml)** — Gramática formal de workflows.
14. **[`../.claude/memory/lessons/README.md`](../.claude/memory/lessons/README.md)** — Schema y reglas de promoción de lessons.

## 🧹 Histórico

15. **[`audits/`](audits/)** — Auditorías y planes superseded (referencia).
16. **[`history/`](history/)** — Cambios mayores documentados.

---

## Ruta recomendada según rol

### Eres usuario nuevo (instalas y usas)
1 → 6 → 7 → 8 → 9

### Eres mantenedor (modificas el template)
1 → 2 → 3 → 4 → 11 → 12

### Investigas un bug o decisión
3 → 4 → 5 → 15

### Implementas una skill o agent nuevo
2 (§5-7) → 12 → `skills/skill-creator/`
