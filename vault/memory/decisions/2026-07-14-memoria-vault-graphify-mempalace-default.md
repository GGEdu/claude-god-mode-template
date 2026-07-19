---
name: memoria-vault-graphify-mempalace-default
description: MCP `memory` eliminado del sistema; vault+Graphify+MemPalace pasa a ser el default de todo proyecto nuevo
updated: 2026-07-14
---

**Qué:** MCP `memory` (server-memory, grafo de entidades manual) eliminado de `~/.mcp.json`, `~/.config/opencode/opencode.json`, `.mcp.json` y `.mcp-servers-reference.json` de este repo. `make init-project` ahora crea `vault/` + instala el git hook de Graphify + inicializa MemPalace por defecto en todo proyecto nuevo, sin flag ni LAYERS= — no es opcional.

**Por qué:** council unánime (Skeptic/Pragmatist/Critic, ver transcript de sesión) — MCP `memory` nunca se usó en ningún proyecto pese a estar disponible; requiere población manual explícita (`create_entities`/`create_relations`), lo contrario de lo que se pidió (sincronización automática). Graphify (grafo de código, hook post-commit) y MemPalace (semántico/verbatim, hook de Stop) cubren el espacio real de necesidad sin intervención manual.

**Mecanismo (`hooks/session-consolidate.sh`, Stop hook, ya global en `~/.claude/hooks/` y por-proyecto vía template):**
- Si el proyecto tiene `vault/` → consolida ahí (`vault/memory/{conversations,decisions,research}`); si no, cae a `.claude/memory/` (proyectos sin vault todavía).
- Graphify: instala su git hook de forma perezosa si no está (`graphify hook status` → `graphify hook install`), idempotente.
- MemPalace: inicializa (`mempalace init . --yes --no-llm`, heurísticas only, nunca manda contenido a un LLM externo) y mina (`mempalace mine`) al final de cada sesión.
- Consulta en vivo (search/wake-up) idéntica en ambas herramientas: mismo MCP server `mempalace-mcp` registrado globalmente en `~/.mcp.json` (Claude Code) y `~/.config/opencode/opencode.json` (OpenCode), ambas contra el mismo `~/.mempalace/palace`.
- Auto-consolidación al terminar sesión: Claude Code vía Stop hook nativo (settings.json). OpenCode no tiene Stop hook nativo — se añadió `~/.config/opencode/plugin/memory-consolidate.js`, que escucha el evento `session.idle` (equivalente real, confirmado en `@opencode-ai/plugin` types) y lanza el mismo `session-consolidate.sh`. Registrado en `opencode.json` → `"plugin": [...]`. Probado: `opencode run` carga el plugin sin error (ver log de sesión).
- Graphify no necesita puente: su hook vive en `.git/hooks/post-commit`, dispara igual sin importar qué herramienta hizo el commit.

**Aclaración importante:** "terminar sesión" no es cerrar la terminal — el Stop hook (Claude Code) y `session.idle` (OpenCode) disparan al final de CADA turno (cuando el agente termina de responder y espera el siguiente mensaje), no solo al cerrar el proceso. En una conversación larga puede dispararse muchas veces; es barato (local, idempotente) así que no es un problema.

**Corrección aplicada tras esta decisión:** `mempalace.yaml` no se debe commitear (issue #185 upstream de MemPalace — contiene paths/config específicos de la máquina). Añadido a `.gitignore` del propio template y al bloque de `.gitignore` que `init-project` genera para cada proyecto nuevo. `vault/` sí se commitea (es contenido curado, no config de la herramienta).

**Cuándo revisar:** si aparece una necesidad real (no hipotética) de grafo de entidades cross-proyecto que ni el vault ni Graphify ni MemPalace cubran — reintroducir entonces como layer opt-in, nunca como default.
