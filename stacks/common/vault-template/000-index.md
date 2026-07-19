# __PROJECT_NAME__ — vault de memoria

Memoria del proyecto, curada y legible. Complementa (no duplica) a:
- **Graphify** — grafo de código estructural, autoactualizado en cada commit (`git log --oneline -1 --grep=graphify` para ver rebuilds)
- **MemPalace** — búsqueda semántica/verbatim sobre archivos y conversaciones, se alimenta solo al final de cada sesión

Ver decisión: `memory/decisions/2026-07-14-memoria-vault-graphify-mempalace-default.md` en `claude-god-mode-template` para el porqué de esta arquitectura de 3 capas (sin MCP `memory`).

## Estructura

- `memory/conversations/` — qué se hizo en cada sesión (resumen)
- `memory/decisions/` — decisiones de arquitectura/diseño tomadas y por qué
- `memory/research/` — hallazgos de investigación por tema (evaluación de repos, resultados de auditorías)

## Cómo se llena

**Automático:** al final de cada sesión de Claude Code en este proyecto, el hook de `Stop` (`session-consolidate.sh`) vuelca aquí lo relevante y ejecuta `mempalace mine` para indexarlo semánticamente. No hace falta pedirlo.

**Manual (si quieres forzar algo ahora mismo, sin esperar a que acabe la sesión):**
- Pide explícitamente "guarda esto en el vault" / "documenta esta decisión" — se escribe directo a `memory/decisions/` o `memory/research/` según aplique.
- `mempalace mine .` desde la raíz del proyecto — reindexa semánticamente sin esperar al cierre de sesión.
- `graphify update .` — reconstruye el grafo de código sin necesidad de hacer commit.
