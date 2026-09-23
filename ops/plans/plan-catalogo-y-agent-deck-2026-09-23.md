---
name: plan-catalogo-y-agent-deck
description: Dónde vive cada pieza de configuración de IA (skills, agentes, reglas, MCP, pipelines), cómo llega a cada repo y a cada harness, y qué construye agent-deck encima
estado: propuesta
creado: 2026-09-23
destinatario: sesión de agent-deck (Fase 4 "MCPs y skills" y Fase 6 "multi-harness")
---

# Catálogo de configuración de IA + agent-deck — plan general

## 0. La decisión, en una frase

**`claude-god-mode-template` es el catálogo** (la fuente de verdad y la copia de
seguridad de toda la configuración de IA). **`agent-deck` es el panel de control**
que lo lee y lo aplica a los repos de `~/development`. agent-deck no guarda
configuraciones propias; el catálogo no sabe nada de sesiones ni de UI.

Por qué así y no todo en agent-deck:
- El `PLAN.md` de agent-deck ya lo presupone: Fase 4, *"Skills por symlink desde
  un repo central"*. Ese repo central existe y está maduro: 146 skills, 38
  agentes, 12 reglas, 16 stacks, layers, domains, `pipeline.yaml`, instalación,
  manifiestos por proyecto y tests.
- La regla no negociable de agent-deck ("si el panel cae, las sesiones siguen")
  se extiende: si agent-deck cae o se reescribe, el catálogo sigue intacto y
  usable con `make`.
- Ya hubo un intento de "otro sitio más" (`agent-os`); no crear un tercero.

## 1. Las piezas y dónde vive cada una

| Pieza | Repo | Ruta | Es la fuente de verdad de… |
|---|---|---|---|
| **Catálogo** | `claude-god-mode-template` | `skills/`, `agents/`, `rules/`, `commands/`, `stacks/`, `layers/`, `domains/`, `hooks/`, `.claude/pipeline.yaml`, `ops/` | Todo contenido de IA reutilizable |
| **Ejecutor** | `agent-deck/exec` | `src/` | Estado de sesiones y de qué está aplicado en cada repo. Único que escribe en los repos |
| **Panel** | `agent-deck/panel` | `app/`, `lib/` | Nada: solo muestra y pide acciones al ejecutor |
| **Secretos** | vault SOPS (`homelab-ops`) | ya existente | Claves, tokens, contraseñas. **Nunca en el catálogo** |
| **Memoria** | MemPalace + `~/.claude/projects/*/memory/` | ya existente | Memoria por proyecto. No es configuración: no va al catálogo |
| **Repos de trabajo** | `~/development/<proyecto>/<repo>` | `.claude/`, `.opencode/`, `.agents/`, `AGENTS.md` | Solo lo que reciben aplicado + su `CLAUDE.md` propio |

## 2. Un original por pieza, adaptadores generados por harness

Verificado el 2026-09-23 leyendo los binarios instalados (opencode 1.18.31,
freebuff 0.0.180, Claude Code 2.1.x):

| Pieza | Claude Code | opencode | freebuff |
|---|---|---|---|
| Skills (`SKILL.md`) | `~/.claude/skills`, `.claude/skills` | **lee** `~/.claude/skills` y `~/.agents/skills` (+ `.opencode/skills`) | **lee** `~/.claude/skills`, `~/.agents/skills`, `.claude/skills`, `.agents/skills` |
| Agentes | `.claude/agents/*.md` | **no los lee** → `.opencode/agents/*.md` (otro frontmatter) | **no** → `.agents/*.ts` |
| Comandos | `.claude/commands/` | `.opencode/commands/` | — |
| Reglas | `CLAUDE.md`, `.claude/rules/` | `AGENTS.md` (fallback `CLAUDE.md`) | `knowledge.md`, `AGENTS.md`, `CLAUDE.md` |
| MCP | `.mcp.json` / settings | `opencode.json` → `mcp` | `mcpServers` por agente |
| Hooks | sí | no (plugins JS) | no |
| Pipelines | `pipeline.yaml` + `workflow-runner` | no | no |

Consecuencias, que son reglas:

1. **Skills: una sola carpeta `skills/`, sin variantes por harness.** ~130 de 146
   son portables tal cual. Las ~15 que usan mecanismos solo de Claude
   (`AskUserQuestion`, subagentes, `claude -p`…) llevan dentro su camino
   alternativo ("si no tienes subagentes, hazlo en secuencia") o se marcan con el
   campo `compatibility` del estándar Agent Skills y no se aplican donde no sirven.
   Duplicar por harness multiplica la deriva: ya hoy había 4 `SKILL.md` distintos
   entre el template y `~/.claude/skills`.
2. **Agentes, comandos, reglas y MCP: original en formato Claude + adaptador
   generado.** Se amplía `ops/distribute-agents.py` (hoy genera Antigravity y
   Copilot) con salidas opencode y freebuff, más un `AGENTS.md` generado desde
   `rules/` y un MCP declarativo único traducido a cada formato.
3. **Lo generado nunca se edita a mano.** Lleva cabecera
   `<!-- generado desde claude-god-mode-template@<sha>:<ruta>; no editar -->`, y un
   test regenera y compara.
4. **Hooks y pipelines son solo de Claude.** No se traducen; el panel lo indica.

## 3. Contrato del catálogo (lo que agent-deck puede dar por hecho)

El ejecutor es Node sin dependencias; el catálogo es Python. El contrato entre
ambos son **comandos del catálogo con salida JSON**, no que agent-deck reimplemente
la lógica (su riesgo 5: "el ejecutor se convierte en un segundo producto").

Todos aceptan `--json` y **ninguno imprime secretos ni contenido de ficheros**. Estado a
2026-09-23 (rama `feat/catalog`, pendiente de fusionar):

| Comando del catálogo | Estado | Salida | Uso desde agent-deck |
|---|---|---|---|
| `ops/catalog.py [--out dist/catalog.json]` · `make catalog` | ✅ | índice de 230 piezas: `{type, name, description, path, sha256, files, bytes, category, harnesses, compatibility, used_by, global_install}` + `commit`, `dirty`, `categories`, `external`, `retired` | Listado del panel |
| `ops/drift.py` · `make drift` | ✅ | `~/.claude` vs catálogo: igual/difiere (con ficheros)/solo-instalada/externa/retirada | Semáforo de `~/.claude` |
| `ops/collect.py <tipo> <nombre> [--overwrite]` · `make collect` | ✅ | recoge al catálogo, commit en rama (nunca `main`) | Botón "recoger" |
| `ops/apply.py <repo> --items t:n,… --harness … --mode auto\|link\|copy [--remove]` · `make apply` | ✅ | por pieza y harness: aplicado / no-aplica / omitido (conflicto) / rechazado; registra en el manifiesto → `items` | Aplicar y quitar piezas |
| `ops/repo-status.py <repo>` · `make repo-status` | ✅ | al-dia / catalogo-mas-nuevo / editado-localmente / enlace-roto / falta | "Este repo va por detrás" |
| `ops/check-skill-integrity.py` · `make check-skills` | ✅ | exit 0/1 + lista | Puerta antes de aplicar (apply.py ya la usa) |
| `ops/adapters.py` · `make adapters` | ✅ opencode · ⏳ freebuff | `dist/opencode/{agents,commands}` | Lo usa apply.py |
| `ops/install-opencode.py [--write]` · `make install-opencode` | ✅ | instala en `~/.config/opencode` + `instructions` | Instalación global opencode |
| `ops/mcp.py import\|render\|diff` · `make mcp-diff` | ✅ | `mcp/servers.yaml` → Claude `${VAR}` / opencode `{env:VAR}` | Vista y aplicación de MCP |
| `ops/check-updates.py`, `ops/update-project.py` | ya existían | a nivel de stack completo | Proyectos creados con `init-project` |

Ya existe el manifiesto por proyecto (`.claude/.template-manifest.yaml`, con SHA
del template y huellas de cada fichero generado) y `symlinks_enabled`. Hoy solo
lo usan 2 de ~16 proyectos, y uno apunta a un worktree que ya no existe: es la
prueba de que sin panel nadie lo mantiene.

## 4. Aplicar configuración a un repo: tres modos

| Modo | Cuándo | Cómo |
|---|---|---|
| **Global** | Por defecto para skills y agentes de uso general | Instalado en `~/.claude/` desde el catálogo (`make install`). Lo ven los tres harness sin tocar el repo |
| **Enlace** (symlink) | Repo que solo se usa en la VM 111 | `.claude/skills/<x>` → catálogo. Se actualiza solo |
| **Copia fijada** | Repo con CI, GitHub Actions, Antigravity, o que clonan otros | Copia + entrada en el manifiesto con commit y huella. **Un symlink a `/home/ggarrido/…` es un enlace roto en CI**: falla en silencio, que es exactamente cómo se rompió `ui-ux-pro-max` (abril → septiembre sin que nadie lo notara) |

Regla: el modo lo propone el ejecutor (¿hay `.github/workflows`? → copia) y lo
confirma el usuario en el panel. Ficheros sagrados que nunca se tocan:
`CLAUDE.md`, `memory/`, `.github/workflows/` (ya lo respeta `update-project.py`).

## 5. Copia de seguridad: que el catálogo tenga *todo*

Hoy no lo tiene. Medido el 2026-09-23:
- Solo en `~/.claude/skills`, sin git en ningún sitio: `auditoria-curricular-fp`,
  `graphify`, `scraping-reviewer`. Si se pierde la VM 111, se pierden.
- `~/.claude/` no es un repo; lo instalado deriva del catálogo sin aviso
  (`videodb` sin `reference/`, `continuous-learning` retirada pero instalada,
  `SKILL.md` distintos).

Qué hace falta:
1. **`ops/collect.py`** — recoge al catálogo lo que existe instalado y no en git
   (skill, agente, comando), pasa `check-skill-integrity` y deja un commit listo.
   En el panel: botón "recoger" junto a cada pieza marcada *solo instalada*.
2. **`make drift`** — compara `~/.claude/{skills,agents,rules}` y
   `~/.config/opencode/` con el catálogo: *igual / difiere / solo instalada / solo
   catálogo*. El panel lo muestra como semáforo.
3. **Configuración declarativa sin secretos** — `settings.json` como plantilla
   (hooks, permisos, `env` no secretos), lista de plugins y definición MCP única;
   los valores secretos se referencian al vault (`${SECRET:x}`, convención que ya
   usa el vault SOPS), nunca se copian.
4. **Push del catálogo** a GitHub (`GGEdu/claude-god-mode-template`) como copia
   fuera de la VM.

## 6. Fases

Cada fase cierra con algo comprobable desde fuera.

### Catálogo (`claude-god-mode-template`) — va primero

| Fase | Contenido | Salida medible |
|---|---|---|
| **C0** | Fusionar `feat/design-diversity` → `chore/skills-maintenance` → `feat/catalog` (hoy sin push; espera confirmación) | `main` contiene impeccable, `check-skill-integrity`, `repo-eval` ampliada |
| **C1** ✅ | `collect.py` + recoger las 3 skills huérfanas + `make drift` | `make drift` sin filas *solo instalada* |
| **C2** ✅ | `make catalog` → `dist/catalog.json`; `compatibility` en las ~15 skills atadas a Claude | JSON válido con todas las piezas; test que falla si una pieza no aparece |
| **C3** ✅ | Adaptadores opencode y freebuff en `distribute-agents.py` + `AGENTS.md` generado + MCP declarativo | Un agente del catálogo aparece y se invoca en opencode desde un repo de prueba |
| **C4** ✅ | `apply.py` (piezas sueltas, 3 modos) + `check-updates --json` | Aplicar 2 skills a un repo en modo copia y ver el manifiesto actualizado |

### agent-deck — encima del catálogo

| Fase | Contenido | Salida medible |
|---|---|---|
| **D4a** (su Fase 4) | Ejecutor: `AGENT_DECK_CATALOG` en `config.js`; `GET /catalog` (lee `dist/catalog.json`), `GET /repos/:id/config` (lee el manifiesto), `POST /repos/:id/apply` (llama a `apply.py`) | Aplicar una skill a dos repos desde `curl` y que ambos la vean |
| **D4b** | Panel: catálogo por categorías; por repo, qué tiene aplicado, en qué modo y si va por detrás; semáforo de `make drift`; botón "recoger" | Ver un repo desactualizado en el panel y ponerlo al día con un clic |
| **D6** (su Fase 6) | Al lanzar sesión con opencode o freebuff, el ejecutor comprueba que el repo tiene sus adaptadores generados; si no, los genera antes | Lanzar opencode sobre un repo y que vea los agentes del catálogo |

Datos en el ejecutor (añadir a su SQLite, junto a `SkillLink` del plan original):
```
Binding(repo_id, item_type, item_name, mode, catalog_sha, file_sha256, harnesses, applied_at)
```
El manifiesto del repo sigue siendo la verdad del repo; `Binding` es la caché del
panel y se reconstruye leyendo manifiestos (mismo principio que `events.jsonl`).

## 7. Reglas no negociables

1. **Un original por pieza.** Nada de carpetas de skills por harness.
2. **Solo el ejecutor escribe en repos, y solo a través de los comandos del
   catálogo.** El panel nunca toca disco.
3. **Nada se aplica sin pasar `check-skill-integrity`.** Una skill que cita un
   script que no trae no se copia.
4. **Secretos, nunca.** Ni en el catálogo, ni en los manifiestos, ni en la
   respuesta del ejecutor. Referencias al vault.
5. **Lo generado lleva cabecera y un test lo regenera.** Editarlo a mano es un fallo.
6. **Tras cambiar un agente, las sesiones abiertas no lo ven**: Claude Code carga
   `~/.claude/agents/` al arrancar la sesión. El panel debe avisar "reinicia las
   sesiones X para ver el cambio" en vez de dar el cambio por aplicado.

## 8. Lo que NO se construye

- Un almacén de configuración propio de agent-deck.
- Editor de skills en el panel (se editan en el catálogo con git; el panel enlaza).
- Traducción de hooks o pipelines a harness que no los tienen.
- Sincronización bidireccional automática: "recoger" es explícito y deja un commit
  para revisar.

## 9. Riesgos

| Riesgo | Mitigación |
|---|---|
| Symlinks que funcionan en la VM 111 y rompen en CI | Modo por defecto "copia" si el repo tiene `.github/workflows`; `check-updates` en CI |
| Los adaptadores se quedan viejos respecto al original | Cabecera con SHA + test de regeneración + semáforo en el panel |
| Skills atadas a Claude aplicadas en opencode/freebuff | Campo `compatibility` y filtro en `apply.py` |
| El ejecutor crece reimplementando lógica del catálogo | Contrato §3: agent-deck solo invoca comandos del catálogo |
| Dos editores del catálogo (tú en git, el panel con "recoger") | "Recoger" deja commit en rama, nunca en `main` directo |

## 10. Verificado y pendiente

- **Verificado (2026-09-23):** rutas de skills de opencode y freebuff (en sus
  binarios); formato de agentes distinto en ambos; manifiesto y `update-project.py`
  existentes; 3 skills huérfanas; `check-skill-integrity` en verde en catálogo e
  instaladas.
- **Hecho y verificado (C1–C4, 2026-09-23):** `opencode agent list` ve los 38 agentes
  del catálogo; `opencode debug config` carga 8 reglas por `instructions` (antes
  ninguna); `make mcp-diff` sin diferencias en ambos harness; `apply.py` probado en
  repos temporales (enlace, copia con CI, conflicto con fichero a mano, skill solo
  Claude pedida para opencode, eliminación); `repo-status.py` detecta una edición local.
- **Pendiente para agent-deck:** decidir en el panel los 3 agentes cuya copia instalada
  es más nueva que el catálogo (`code-reviewer`, `repo-reviewer`, `tdd-guide`) y
  desinstalar `continuous-learning` (retirada).
- **Sin verificar:** si opencode lee también `.claude/skills` **del proyecto** (por eso
  apply.py usa `.opencode/skills`); agentes de freebuff (`.agents/*.ts` exige `model`
  de OpenRouter y freebuff elige el modelo en su servidor); Codex y Gemini CLI (no
  instalados en la VM 111).
