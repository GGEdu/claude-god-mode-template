---
paths:
  - "**/*.py"
  - "**/*.ts"
  - "**/prompts/**"
---
# AI Agent Engineering — Reglas del stack

## Eval-Driven Development
- SIEMPRE definir eval antes de implementar feature
- Métricas obligatorias: pass rate, costo, latencia, consistencia
- Baseline documentado — cada cambio debe medirse contra baseline
- Evals automatizados en CI — no deploy sin pasar umbral

## Model Routing
- Haiku para tareas simples y agentes worker (90% capacidad, 3x ahorro)
- Sonnet para desarrollo principal y orquestación
- Opus para razonamiento complejo y decisiones arquitectónicas
- Routing dinámico: empezar con modelo barato, escalar si falla

## Multi-Agent Patterns
- Orchestrator → Workers (fan-out/fan-in)
- Pipeline secuencial con quality gates entre pasos
- DAG con dependencias explícitas
- Adversarial verification: 2 agentes independientes deben coincidir

## Prompts
- Prompts son código: versionados, testeados, revisados
- Separar instrucciones de datos de contexto
- Few-shot examples > descripciones abstractas
- Prompt injection defense: sanitizar inputs de usuarios

## Cost Control
- Budget por sesión/tarea — abort si se excede
- Token counting proactivo: estimar antes de enviar
- Caching de respuestas frecuentes (prompt caching)
- Batch API para tareas no interactivas (50% descuento)

## Anti-patrones
- Deploy sin eval — siempre medir impacto
- Modelo más caro "por si acaso" — routing por complejidad
- Prompts hardcodeados sin versionado
- Agentes sin límite de iteraciones — siempre max_turns
