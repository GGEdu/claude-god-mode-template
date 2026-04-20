# Skills: cómo funcionan y cuándo usarlas

Esta página explica los tres tipos de assets que Claude puede usar y cómo
decidir cuál necesitas.

---

## Los cuatro niveles de conocimiento de Claude

```text
┌─────────────────────────────────────────────────┐
│  NIVEL 4 — .claude/agents/        AUTÓNOMO      │
│  Subagentes especializados con skills embebidas  │
│  por compilación. Claude los lanza en paralelo o  │
│  se invocan explícitamente. Compilados por         │
│  dev-stack según el stack activo.                │
├─────────────────────────────────────────────────┤
│  NIVEL 3 — .claude/rules/          SIEMPRE      │
│  Se carga automáticamente en cada sesión.        │
│  Claude lo aplica sin que lo pidas.              │
├─────────────────────────────────────────────────┤
│  NIVEL 2 — .claude/commands/       MANUAL       │
│  Disponibles como slash commands.                │
│  Se usan cuando los invocas: /skill-name         │
├─────────────────────────────────────────────────┤
│  NIVEL 1 — skills/ / agents/        INERTE      │
│  Solo texto. Claude no los lee.                  │
│  dev-stack mueve los relevantes al nivel         │
│  correcto automáticamente.                       │
└─────────────────────────────────────────────────┘
```

**Regla práctica**: si quieres que Claude actúe de forma autónoma con contexto
aislado, úsalo como agente (nivel 4). Si quieres que aplique algo siempre,
ponlo en `rules/` (nivel 3). Si quieres invocarlo tú cuando lo necesitas,
que esté en `commands/` (nivel 2). Si está solo en `skills/` o `agents/`, no hace nada.

---

## Qué hace `make dev-stack`

Al ejecutar `make dev-stack STACK=laravel LAYERS=react`, el comando:

1. Copia `stacks/laravel/rules/*.md` + `layers/react/rules/*.md` → `.claude/rules/stack/` (**Nivel 3**)
   Las convenciones del stack quedan activas en cada sesión sin invocar nada.

2. **Compila** los agentes con skills embebidas → `.claude/agents/` (**Nivel 4**)
   `ops/compile-agents.py` lee `stack.yaml`, toma cada agente base de `agents/`,
   y concatena los SKILL.md asignados bajo `# Embedded Skills Reference`.
   El developer nunca invoca skills manualmente — los agentes ya los conocen.

3. Copia los slash commands standalone de `skills/` → `.claude/commands/` (**Nivel 2**)
   Solo los declarados en `commands:` del `stack.yaml`. Son herramientas que
   el developer invoca explícitamente (ej: `/jedi-review`, `/git-workflow`).

4. Copia `stacks/laravel/CLAUDE.md` → `.claude/CLAUDE.md` (y appenda `layers/react/CLAUDE-append.md` si hay layer)
   Configura el cerebro del proyecto con los datos del stack.

5. Si se indicó `DOMAIN=`, añade skills del domain a los agentes (merge)
   y copia rules del domain a `.claude/rules/stack/`.

---

## Skills activadas para el stack `laravel` + `LAYERS=react`

Después de `make dev-stack STACK=laravel LAYERS=react`, estos slash commands quedan
disponibles:

### Slash commands standalone (comandos reales)

| Comando | Cuándo invocarlo |
| --- | --- |
| `/jedi-review` | Review de 3 expertos en paralelo para cambios críticos. |
| `/git-workflow` | Recordatorio de commits, branch y PR workflow. |
| `/workflow-runner <nombre>` | Ejecuta pipelines declarados en `.claude/pipeline.yaml` (`feature`, `hotfix`, `refactor`). |
| `/canary-watch URL` | Monitoreo post-deploy en staging/producción. |
| `/laravel-plugin-discovery` | Descubrir y evaluar paquetes Laravel. |
| `/security-scan` | Auditoría de seguridad de `.claude/` y configuración. |
| `/design-md` | Aplicar dirección visual en trabajo UI (cuando está habilitado en el stack). |
| `/benchmark` | Medir regresiones de rendimiento antes/después de cambios. |
| `/codebase-onboarding` | Generar guía de onboarding de un repo. |
| `/continuous-learning` y `/continuous-learning-v2` | Persistir patrones aprendidos de la sesión. |
| `/ck` | Memoria persistente por proyecto (git-aware). |
| `/plankton-code-quality` | Enforcement de formato/lint durante edición. |
| `/strategic-compact` | Recomendar momentos óptimos para compactar contexto. |
| `/context-budget` | Auditar consumo de contexto/tokens. |
| `/skill-comply` y `/skill-stocktake` | Auditoría de cumplimiento/calidad de skills. |
| `/prompt-optimizer` | Mejorar prompts del developer. |
| `/repo-scan` | Auditoría cross-stack del código fuente. |
| `/product-lens` | Diagnóstico de producto pre-feature. |
| `/token-budget-advisor` | Controlar profundidad de respuesta. |
| `/team-builder` | Componer equipos de agentes en paralelo. |
| `/rules-distill` | Destilar patrones en nuevas reglas. |


### Skills embebidas en agentes (no slash commands)

Estas skills se incorporan dentro de los agentes durante la compilación y se
aplican cuando Claude activa esos agentes:

| Agente | Skills embebidas clave |
| --- | --- |
| `architect` | `api-design`, `laravel-patterns`, `architecture-decision-records`, `deployment-patterns`, `docker-patterns` |
| `planner` | `laravel-patterns`, `search-first` |
| `tdd-guide` | `tdd-workflow`, `laravel-tdd` |
| `code-reviewer` | `laravel-verification`, `verification-loop` |
| `typescript-reviewer` | `frontend-patterns`, `coding-standards`, `design-system` |
| `security-reviewer` | `security-review`, `laravel-security` |
| `database-reviewer` | `database-migrations` |
| `e2e-runner` | `e2e-testing` |

---

## Agentes vs. skills de stack: diferencia clave

Los **agentes** (`.claude/agents/`) son subprocesos autónomos con contexto aislado y herramientas propias — Claude los lanza en paralelo para tareas independientes. Las **skills** (`.claude/commands/`) son conocimiento que se inyecta en la sesión actual cuando tú las invocas. No se sustituyen — se complementan:

| Agente | Complementa con la skill embebida |
| --- | --- |
| `planner` (planifica) | `laravel-patterns` para convenciones del stack |
| `tdd-guide` (guía TDD) | `laravel-tdd` para reglas Pest específicas |
| `security-reviewer` (audita) | `laravel-security` para checklist Laravel |
| `code-reviewer` (revisa calidad) | `laravel-verification` para criterios del stack |

**Flujo típico:**

```text
Tú → "Implementa con TDD: [feature]"   (Claude lanza tdd-guide con laravel-tdd ya embebida)
                                         (ciclo RED/GREEN/REFACTOR)
```

---

## Skills en `skills/` que NO se activan con `laravel` + `LAYERS=react`

Las 139 skills del directorio `skills/` cubren muchos otros stacks y casos.
Las que no forman parte del stack activo no se mueven a `commands/` y no
interfieren en tu sesión. Están disponibles si en algún momento las necesitas:

```bash
# Para activar una skill manualmente en la sesión actual:
# Simplemente dile a Claude que lea el archivo:
"Lee skills/deep-research/SKILL.md y aplica ese proceso a..."
```

Si usas frecuentemente una skill no incluida en tu stack, añádela al
`stacks/tu-stack/stack.yaml` y vuelve a ejecutar `make dev-stack`.

---

## Añadir tu propio stack

Crea la carpeta y el archivo de configuración:

```bash
mkdir -p stacks/mi-stack/rules

# stack.yaml — define el stack
cat > stacks/mi-stack/stack.yaml << 'EOF'
name: mi-stack
description: "Mi stack personalizado"

rules:
  - mi-framework.md

agents:
  architect:
    skills:
      - api-design
  tdd-guide:
    skills:
      - tdd-workflow
  code-reviewer:
    skills: []
  security-reviewer:
    skills:
      - security-review
  planner:
    skills: []
  build-error-resolver:
    skills: []

commands:
  jedi-review:
    when: "Para código crítico — review de 3 expertos"
  security-scan:
    when: "Antes de cada release"

mcps:
  notebooklm: false
  n8n: false
EOF

# rules/mi-framework.md — convenciones siempre activas
# (Claude las leerá en cada sesión automáticamente)
```

Los agentes se **compilan** con `ops/compile-agents.py`: toma el agente base de `agents/<name>.md` y le concatena los SKILL.md listados en `skills:`. Los comandos en `commands:` se copian como slash commands standalone.

Después: `make dev-stack STACK=mi-stack`
