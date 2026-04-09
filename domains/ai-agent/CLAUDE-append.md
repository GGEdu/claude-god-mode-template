
## Dominio: AI Agent Engineering

### Principios
- **Eval-driven**: métricas (pass rate, costo, latencia) antes de features
- **Cost-aware**: model routing por complejidad (Haiku → Sonnet → Opus)
- **Safety gates**: quality checks entre pasos de agentes
- **Decomposition**: tareas complejas → subtareas paralelas

### Patterns
- Orchestrator → Workers (fan-out/fan-in)
- Pipeline secuencial con quality gates
- DAG con dependencias explícitas
- Adversarial verification: 2 agentes independientes deben coincidir
