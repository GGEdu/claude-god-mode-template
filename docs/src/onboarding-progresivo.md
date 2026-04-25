# Onboarding progresivo del enforcement

Sintesis.md describe un sistema de **enforcement determinista** mediante hooks programáticos. Activarlo todo de golpe en un equipo o proyecto que no lo conoce produce frustración: workflows familiares fallan, productividad cae temporalmente.

Esta guía propone una **curva de adopción gradual** que permite asimilar el sistema sin bloquear el trabajo.

## Resumen visual

```
Semana 1     Semana 2-3       Semana 4-6        Semana 6+
[FAMILIARIZACIÓN]  [CALIBRACIÓN]    [ENFORCEMENT]     [OPTIMIZACIÓN]
mode: off          mode: warn       mode: block       custom rules
ningún hook       hooks logging    hooks blocking    fine-tuning
```

## Fase 1 — Familiarización (semana 1)

**Objetivo:** ver cómo trabaja Claude con el template SIN gates ni interrupciones.

### Configuración inicial

`.claude/settings.json` con tdd-gate desactivado:

```json
{
  "hooks": {
    "tdd-gate": { "mode": "off" }
  }
}
```

Los hooks `commit-checklist`, `non-goal-guard`, `plan-gate` siguen activos pero en su modo más permisivo (sin PLAN.md, todo es allow).

### Qué hacer

- Ejecutar 5-10 features pequeñas usando `/workflow-runner feature` y `/workflow-runner hotfix`.
- Observar qué archivos se generan: `.claude/state.yaml`, `.claude/memory/`, `PLAN.md`, lessons.
- Familiarizarse con los slash commands: `/plan`, `/tdd`, `/jedi-review`, `/security-scan`.

### Señales de éxito

- El equipo sabe qué hacen los hooks (sin necesidad de leer el código).
- Saben qué es `PLAN.md` y cuándo se crea.
- Saben dónde está `.claude/memory/` y qué contiene.

## Fase 2 — Calibración (semanas 2-3)

**Objetivo:** que el sistema empiece a observar y avisar, sin bloquear.

### Configuración

```json
{
  "hooks": {
    "tdd-gate": {
      "mode": "warn",
      "allowNewModules": true
    }
  }
}
```

`mode: warn` hace que tdd-gate emita warnings en consola cuando detecta código sin tests, pero no bloquea.

### Qué observar

- ¿Cuántos warnings genera al día?
- ¿Cuáles son falsos positivos? (ej: hooks de tests detectan archivos generados como código)
- ¿Qué `excludePatterns` necesitas añadir a `tdd-gate` config?

### Tunear `tdd-gate.excludePatterns`

Si tu proyecto tiene archivos auto-generados (migrations, factories, snapshots), añádelos:

```json
{
  "hooks": {
    "tdd-gate": {
      "mode": "warn",
      "excludePatterns": [
        "src/generated/**",
        "src/migrations/**",
        "*.config.*",
        "*.d.ts",
        "tests/__snapshots__/**",
        "src/proto/generated/**"
      ]
    }
  }
}
```

### Señales de listo para Fase 3

- < 5% warnings/día son falsos positivos.
- El equipo no ignora los warnings (los ve y actúa).
- TDD se ha vuelto hábito en al menos 50% de los commits.

## Fase 3 — Enforcement (semanas 4-6)

**Objetivo:** los gates bloquean violaciones reales.

### Configuración

```json
{
  "hooks": {
    "tdd-gate": {
      "mode": "block",
      "allowNewModules": false,
      "excludePatterns": ["..."]
    }
  }
}
```

`mode: block` con `allowNewModules: false` exige tests para CADA archivo de código nuevo o modificado.

### Qué pasa ahora

- `Write`/`Edit` sobre código sin test → **bloqueado**.
- Commit sin tests con assertions → **bloqueado** por `commit-checklist`.
- Archivos en `non_goals` del PLAN → **bloqueados + rollback automático** por `non-goal-guard`.

### Cómo "salir de un atasco"

Si te bloquean legítimamente (ej. estás haciendo un proof-of-concept):

1. Bypass temporal: `git commit --no-verify` (se loguea en `.claude/memory/commit-bypass.log`).
2. Audit trail: cada bypass debe tener razón documentada en el log.
3. Si bypassas más de 3 veces/semana → revisar config de `excludePatterns`.

### Señales de éxito

- Coverage del proyecto sube a 80%+.
- Tests escritos en RED→GREEN, no después.
- Bugs en producción bajan (correlación, no causa).

## Fase 4 — Optimización (semana 6+)

**Objetivo:** rules personalizadas + automatización avanzada.

### Crear rules específicas del proyecto

Lessons aprendidas en sesiones se promueven a rules:

```bash
# Lessons con sessions_without_repeat >= 5 se auto-promueven.
# Para promover manualmente:
/promote lesson-2026-04-25-001
```

### Tunear pipeline.yaml

Customizar workflows para tu equipo:

```yaml
# .claude/pipeline.yaml
workflows:
  feature:
    steps:
      - agent: docs-lookup
      - agent: planner
      - agent: architect           # añadido — review arquitectónico antes de code
        parallel_with: planner
      - agent: tdd-guide
      - agent: code-reviewer
      - agent: security-reviewer
        parallel_with: code-reviewer
      - agent: pr-test-analyzer    # añadido — análisis de coverage
      - audit: true
      - agent: memory-consolidator
        always: true
```

### Activar Antigravity triggers

Tareas programadas (auditorías semanales, consolidación de memoria):

```bash
make triggers-setup   # genera comandos /schedule
make triggers-list    # ver definidas
```

## Anti-patterns a evitar

❌ **Saltar a Fase 3 sin pasar por 1-2.** El equipo rechaza el sistema y desactiva todo.

❌ **Usar `--no-verify` rutinariamente.** El log se llena y la disciplina se pierde.

❌ **No revisar `.claude/memory/commit-bypass.log`.** Sin observación del log, los bypasses se vuelven normalidad.

❌ **Añadir `excludePatterns` para evitar escribir tests.** El sistema dejó de ser útil.

✅ **Hacer review semanal del log** los primeros 2 meses. Identifica patterns de fricción real vs disciplina pendiente.

## FAQ

### ¿Y si solo soy yo trabajando?

La progresión sigue siendo válida. Te ahorra el coste cognitivo de aprender 8 hooks de golpe.

### ¿Puedo saltarme Fase 1 si ya conozco TDD?

Sí, pero al menos ejecuta 1-2 features para ver `state.yaml` evolucionar y entender el flujo.

### ¿Qué pasa si Claude bloquea algo que YO sé que es correcto?

Reportar al hook `commit-bypass.log` con razón clara. Después analizar:
- ¿El hook está mal? → fix del hook.
- ¿El proyecto tiene caso edge? → añadir a `excludePatterns`.
- ¿Es disciplina pendiente? → escribir el test.

### ¿Cuándo es seguro `mode: block` en CI?

Cuando los falsos positivos son < 1% y el equipo no se queja durante 2 semanas seguidas en `mode: warn`.
