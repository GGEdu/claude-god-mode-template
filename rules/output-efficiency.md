# Output Efficiency

Reglas de formato de respuesta para reducir tokens de salida sin perder señal. Aplicar en toda sesión y en todos los subagentes.

## Reglas universales

- **Sin openers**: nunca "¡Excelente pregunta!", "Claro que sí", "Entendido", "Por supuesto"
- **Sin closers**: nunca "Espero que esto ayude", "¿Hay algo más en lo que pueda ayudarte?", "No dudes en preguntar"
- **No repetir el prompt** antes de responder — el usuario lo escribió, ya lo sabe
- **Lead with the answer**: código o decisión primero; explicación después, solo si aporta valor
- **Prefer edit over rewrite**: editar archivos existentes en lugar de reescribirlos completos
- **No re-leer archivos** ya leídos en la sesión salvo que hayan cambiado (evita tokens desperdiciados)

## Reglas para subagentes worker (modo automático)

Agentes que procesan output estructurado como parte de un pipeline:

- Output **estructurado únicamente**: JSON, bullets, tablas — sin narrativa
- **Nunca inventar**: file paths, endpoints, function names, API keys no leídos → retornar `null` o `"UNKNOWN"` en lugar de alucinar
- Sin commentary de estado: nada de "Procesando...", "Ahora voy a analizar X..."
- Sin solicitudes de confirmación dentro del output: producir el resultado directamente

## Reglas para agentes de análisis y research (planner, architect)

- **Liderar con hallazgos**, no con metodología — el cómo es secundario al qué
- Todo número o dato debe tener fuente; si falta → indicar "dato no disponible" explícitamente
- **Distinguir datos de interpretación**: "los datos muestran X" vs "interpreto que X podría indicar Y"
- No hacer afirmaciones sin evidencia — preferir "no tengo datos suficientes sobre X" a inventar
- Omitir secciones vacías del plan output (no escribir "## Riesgos\n_Ninguno identificado_")

## Caveman Mode — compresión selectiva por agente

Para una segunda capa de compresión más agresiva en agentes de acción (no de razonamiento) usamos el skill `caveman` (`skills/caveman/SKILL.md`), adaptado de [juliusbrussee/caveman](https://github.com/juliusbrussee/caveman).

### Filosofía

- **Selectivo, nunca global**: nada de `SessionStart` hooks ni `caveman-compress` sobre archivos `.md`. Esos modos romperían la auditabilidad de planner/architect/reviewers.
- **Acción sí, razonamiento no**: lo aplica un agente cuyo output es un diff, un commit o un status. NO lo aplica un agente cuya salida la lee un humano para tomar una decisión.
- **Preserva técnico**: código, paths, URLs, commits, números, stack traces — verbatim siempre.

### Agentes con Caveman activo (acción)

| Agente | Razón |
|--------|-------|
| `refactor-cleaner` | Output = diffs |
| `build-error-resolver` (+ variantes por lenguaje) | Output = fix concreto |
| `doc-updater` | Output = changelog tersos |
| `e2e-runner` | Output = status reports |
| `memory-consolidator` | La compresión ES el objetivo |
| `loop-operator` | Operational chatter |

### Agentes explícitamente SIN Caveman (razonamiento)

`planner`, `architect`, `code-reviewer`, `security-reviewer`, `tdd-guide`, `comment-analyzer`, `conversation-analyzer`, `harness-optimizer`, `performance-optimizer`, `pr-test-analyzer`, `silent-failure-hunter`, `ui-engineer`, `database-reviewer`, `docs-lookup`, `github-orchestrator`, todos los `*-reviewer` por lenguaje, `repo-reviewer`.

### Operación

```bash
bash skills/caveman/install.sh    # idempotente, opt-in por whitelist
bash skills/caveman/uninstall.sh  # reversible bit-perfect
grep -l 'CAVEMAN_ACTIVE' agents/*.md   # auditar cuáles lo llevan
```

El snippet inyectado va delimitado por `<!-- CAVEMAN_ACTIVE -->` … `<!-- /CAVEMAN_ACTIVE -->` para hacer la instalación greppable y reversible.
