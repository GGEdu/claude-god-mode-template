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
