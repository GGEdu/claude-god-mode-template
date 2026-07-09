# Refactor: integrar `edu-content-forge` como stack `education` (convención god-template)

Estado: PLAN (rama `feat/education-stack`). Ejecución pendiente.

## Convenciones confirmadas
- `ops/update-project.py`: `init-project` copia `stacks/<s>/rules/*.md` → `<proj>/.claude/rules/stack/` (SOLO `.md`). También `layers/<l>/rules`.
- Agentes viven en **core `agents/`**; `stack.yaml` los selecciona y a cada uno le asigna un loadout de skills.
- Skills en **core `skills/`**; commands en **core `commands/`**; overlay vía `stack.yaml`/`domain.yaml`/`layer.yaml`.

## Mapeo de ficheros (fuente: edu-content-forge + vitepress/*)

### → core `agents/` (18; copiar y luego REESCRIBIR refs)
instructional-designer, brainstormer, exercise-progression, redactor-secciones, voice-curator,
humanizador, pulidor-prosa, revisor-didactico, revisor-escritura, revisor-logica, revisor-tecnico,
revisor-coherencia, content-fact-checker, analista-fuentes, didactic-flow-validator, detector-ia, tone-auditor
(slide-builder → `layers/vitepress/`)

### → core `skills/`
humanizar, no-slop, redaccion-academica, metacognition-prompts, motivational-framing,
progressive-examples, tool-introduction-protocol, voice-realistic
- `layers/vitepress/skills/`: vitepress-content-blocks, slide-patterns
- `stacks/laravel` (referenciar): revision-laravel13

### → core `commands/`
create-outline, create-agenda, create-session, create-didactics, create-exercise-progression,
redactar, revisar, humanizar, audit-content, validate-flow, ozymandias
- `layers/vitepress/commands/`: publish-vitepress

### → `stacks/education/rules/*.md`  (RECONCILIAR; nombres que los agentes esperan)
- `principios-redaccion.md`  ← guardrails/voice-guidelines + anti-patterns + .claude/rules/anti-hyperbole.mdc + voice-style.mdc
- `principios-didacticos.md` ← guardrails/didactic-progression + .claude/rules/progressive-examples.mdc
- `patrones-ia.md`           ← guardrails/anti-patterns (léxico IA) + tone-checklist
- `voz-por-defecto.md`       ← personas/*.md (voz) + guardrails/voice-guidelines
- (vitepress-formatting.mdc → `layers/vitepress/rules/`)

### Reescritura de referencias en los 18 agentes
`sed 's#\.claude/principios/#.claude/rules/stack/#g'` — verificar también refs a didactics.yaml, SLIDE-PATTERNS.md, CLAUDE.md.

### `stacks/education/pipeline.yaml`
Convertir edu `pipelines/*.spec.yaml` (outline/session/exercise/didactics/validation) al schema de god (`pipeline.schema.yaml`).

### `stacks/education/templates/`
Desde edu `templates/*.tmpl` (unit-spec, exercise.md, lesson.md, session-skeleton) — referenciados por los `create-*`.

### `stacks/education/stack.yaml` (esqueleto — loadouts a afinar leyendo cada agente)
```yaml
name: education
description: Contenido educativo/didáctico (cursos, VitePress) — ES/EN
rules: [principios-redaccion.md, principios-didacticos.md, patrones-ia.md, voz-por-defecto.md]
agents:
  instructional-designer: { skills: [metacognition-prompts, motivational-framing, progressive-examples] }
  redactor-secciones:     { skills: [redaccion-academica, voice-realistic, no-slop, tool-introduction-protocol] }
  humanizador:            { skills: [humanizar, no-slop, voice-realistic] }
  pulidor-prosa:          { skills: [no-slop, redaccion-academica] }
  revisor-escritura:      { skills: [no-slop, redaccion-academica] }
  revisor-didactico:      { skills: [progressive-examples, metacognition-prompts] }
  # ...resto de revisores + brainstormer/exercise-progression/analista-fuentes/etc.
commands:
  create-outline:  { when: "Genera el outline/arquitectura de una unidad o sesión" }
  redactar:        { when: "Redacta contenido didáctico desde cero (RAFA)" }
  revisar:         { when: "Revisión multidimensional (didáctica/escritura/lógica/técnica)" }
  humanizar:       { when: "Reescribe texto con marcas IA a voz humana" }
  # ...resto
mcps: { notebooklm: true, n8n: false }
```

## Validación
`make init-project STACK=education PROJECT=/tmp/edu-test LAYERS=vitepress`
→ comprobar que los agentes resuelven `.claude/rules/stack/*.md`, y correr el equivalente a `scripts/validate-content.sh`.

## Recomendación de ejecución
Hacerlo en la **VM 109 con Claude Code co-ubicado** (Read/Edit directo sobre los ficheros + `make init-project` para validar en caliente), no por scripts remotos vía guest-agent. Es la primera tarea ideal para el Claude Code de 109.
