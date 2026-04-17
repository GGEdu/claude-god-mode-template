Es una excelente iniciativa. Tratar a Claude Code como un sistema operativo y no como un simple "autocompletado" es exactamente lo que separa a los usuarios promedio de los desarrolladores de alto rendimiento. 

Aquí tienes el resumen estructurado de las partes más importantes del artículo, diseñado específicamente para que puedas leérselo a otra IA y para que tengas claro tu flujo de trabajo diario.

---

### 🧠 Filosofía Central para la IA (El Modelo Operativo)

Para generar el `CLAUDE.md`, la IA debe entender que el repositorio se rige por un **modelo de 5 partes**:

1. **Contexto siempre activo reducido:** El archivo CLAUDE.md debe contener solo el contexto "siempre activo" y reglas inmutables del proyecto. No debe ser un basurero de prompts.
   - **Límite ~200 líneas.** Más de eso diluye la atención de Claude y empeora resultados. Un CLAUDE.md sobre-especificado hace que Claude **ignore reglas importantes** porque se pierden en el ruido.
   - **Poda agresiva:** Si Claude ya hace algo correctamente sin la instrucción, eliminarla del CLAUDE.md o convertirla en un hook.
   - **Solo el "qué", no el "por qué":** Comandos build/test, decisiones de arquitectura, gotchas no obvios, convenciones de naming/imports.
   - **No incluir:** lo que el linter ya cubre, dumps de documentación completa, ni explicaciones teóricas de decisiones.
   - **Cuatro niveles de carga al inicio de sesión:** Org policy (si existe) → `~/.claude/CLAUDE.md` (global personal) → `CLAUDE.md` en raíz del proyecto (equipo) → `CLAUDE.md` en subdirectorios (scoped) + primeras 200 líneas de `MEMORY.md`. Claude fusiona todos; lo más específico gana.
   - **Overrides personales:** `CLAUDE.local.md` en la raíz del proyecto — se gitignora automáticamente. Preferencias personales sin afectar al equipo.
   - **Asumir contexto cero:** Redactar CLAUDE.md como si Claude no supiera NADA del proyecto. No dar nada por implícito.
2. **Procedimientos repetitivos = Skills:** Cualquier tarea que se repita más de dos veces debe convertirse en un "skill", un comando o una regla explícita en el repositorio.
   - **Crear skills desde ejemplos:** Pegar un output excelente a Claude y pedirle que lo convierta en skill reutilizable. También funciona con screenshots.
   - **Versionado de skills:** Duplicar y versionar skills al refinarlos, en vez de editar el activo. Previene regresiones.
3. **Higiene de sesión estricta:** La sesión principal debe mantenerse libre de código basura o conversaciones secundarias.
   - **Separar proyectos no relacionados** en sesiones distintas para evitar context bleed.
   - **Podar periódicamente** memory, archivos e instrucciones para evitar drift acumulado.
4. **Paralelización aislada:** El trabajo paralelo o complejo debe realizarse bajo supervisión estricta y en entornos aislados (worktrees o ramas independientes).
   - **Memoria por worktree:** Cada Git worktree tiene su propio directorio de auto-memory separado. Las notas de un worktree no contaminan otro.
5. **Guardarraíles inteligentes:** Usar el modo automático (Auto Mode) para tareas rutinarias, pero requiriendo validación humana (pruebas, linting) antes de fusionar cualquier código.
   - **Minimizar decision latency del humano:** Con IA, el cuello de botella ya no es la ejecución — es cada punto donde Claude espera aprobación humana. Cada decisión recurrente que se pueda codificar en una rule, un hook o un `allow` en settings.json = latencia eliminada permanentemente. Reservar intervención humana solo para decisiones genuinamente nuevas o de alto riesgo.
6. **Autovalidación como prioridad máxima:** Incluir en cada prompt tests, outputs esperados o criterios de verificación para que Claude pueda comprobar su propio trabajo. Es la acción de mayor apalancamiento disponible.
   - **Estándar senior:** Antes de marcar cualquier tarea como completada, preguntarse: "¿Un staff engineer aprobaría esto?" No basta con que el código "se vea bien" — demostrar corrección con diffs, logs y evidencia.
   - **Tablas de racionalización:** Los LLMs generan excusas fluidas para saltarse pasos ("es un cambio pequeño", "ya lo probé manualmente", "añado tests después"). Catalogar en el CLAUDE.md o rules las excusas recurrentes con rebuttals explícitos:
     | Si el agente piensa... | La realidad es... |
     |---|---|
     | "Es demasiado simple para testear" | Código simple también rompe. El test tarda 30 segundos. |
     | "Añado tests después" | Tests-after verifican lo construido, no lo necesitado. Se pierde la prueba de que el test detecta el fallo. |
     | "Ya lo probé manualmente" | Testing manual no es sistemático, no es repetible, no es confiable. |
     | "Este cambio no necesita review" | Sesgo de confianza. Si toca lógica de negocio, necesita review. |
   - Cuando el agente detecte que su razonamiento coincide con una excusa catalogada, debe **detenerse y seguir el protocolo** en vez de racionalizar.
7. **Nunca usar `--dangerously-skip-permissions`:** Usar `allow` en settings.json para comandos rutinarios específicos. Mismo efecto, sin riesgo de ejecución destructiva accidental.
8. **Self-Improvement Loop (Lecciones persistentes):**
   - Después de CADA corrección del usuario → registrar el patrón en un archivo de lecciones (ej: `tasks/lessons.md` o `.planning/lessons.md`).
   - Escribir reglas que prevengan el mismo error.
   - Revisar lecciones al inicio de cada sesión.
   - Las lecciones que se confirman como permanentes se **promueven** a CLAUDE.md o a `rules/`. Así CLAUDE.md se mantiene lean.
   - **Backward propagation (plan ↔ realidad):** Cuando la implementación diverge del plan (dependencia incompatible, esquema conflictivo, regla contradictoria), Claude debe proponer la actualización del plan/CLAUDE.md **antes** de continuar con la nueva dirección. No basta con registrar la lección post-hoc — el plan vivo debe reflejar la realidad actual para que la siguiente sesión arranque desde verdad, no ficción.
9. **Elegancia balanceada:**
   - En cambios no triviales: pausar y preguntar "¿hay una forma más elegante?"
   - Si el fix se siente hacky: reimplementar la solución elegante con todo el conocimiento acumulado.
   - Para fixes simples y obvios: NO sobre-ingenierar. Aplicar y seguir.
10. **Bug fixing autónomo:**
    - Ante un bug report: diagnosticar y resolver sin pedir ayuda al usuario.
    - Investigar logs, errores, tests fallidos de forma independiente.
    - Cero cambio de contexto requerido del usuario.

---

### � Anatomía del Repositorio de Claude Code

Existen **dos directorios** que forman el sistema operativo de Claude:

#### Proyecto (`.claude/` — committed, compartido con el equipo)
```
proyecto/
├── CLAUDE.md                  # Reglas del equipo (committed)
├── CLAUDE.local.md            # Overrides personales (gitignored auto)
└── .claude/
    ├── settings.json          # Permisos y config (committed)
    ├── settings.local.json    # Permisos personales (gitignored auto)
    ├── rules/                 # Reglas modulares por tema
    ├── commands/              # Slash commands del equipo → /project:nombre
    ├── skills/                # Workflows auto-invocados por contexto
    └── agents/                # Sub-agentes especializados
```

#### Global (`~/.claude/` — personal, aplica a todos los repos)
```
~/.claude/
├── CLAUDE.md                  # Preferencias globales (estilo, principios)
├── settings.json              # Permisos globales
├── commands/                  # Slash commands personales → /user:nombre
├── skills/                    # Skills personales (todos los proyectos)
├── agents/                    # Agentes personales (todos los proyectos)
└── projects/<proyecto>/       # Historial de sesiones + auto-memory
    └── memory/
        ├── MEMORY.md          # Índice auto-gestionado por Claude (≤200 líneas cargadas al inicio)
        ├── debugging.md       # Archivos topic creados on-demand por Claude
        └── ...                # Otros archivos topic según necesidad
```

**MEMORY.md vs CLAUDE.md:** `CLAUDE.md` es donde tú escribes instrucciones. `MEMORY.md` es el scratchpad de Claude — él lo crea y actualiza automáticamente con patrones del proyecto, soluciones de debugging, preferencias detectadas y notas de sesiones anteriores. Solo las primeras 200 líneas se cargan al inicio; el resto se lee on-demand durante la sesión. Cuando crece demasiado, Claude mueve detalles a archivos topic (`debugging.md`, `api-conventions.md`, etc.).

**Regla de precedencia:** Claude fusiona org policy → global → proyecto → subdirectorio → MEMORY.md. Lo más específico gana.

**Claude Interviews:** Para proyectos grandes o nuevos, iniciar con un prompt mínimo y pedir a Claude que te entreviste usando `AskUserQuestion`. Claude pregunta lo que necesita saber antes de actuar.

---

### �📝 Estructura del Flujo de Trabajo Diario (Para ti y para Claude)

Este es el ciclo que debes seguir día a día. Tu `CLAUDE.md` debe estar diseñado para facilitar este flujo.

#### 1. Ritual de Mañana (10 minutos de Setup)
* **Tú:** Abres la rama, revisas el `CLAUDE.md` para refrescar las reglas del proyecto.
* **Claude:** Se le exige **explorar → planificar → ejecutar**. Primero investigar el contexto (puede incluir otros LLMs), luego planificar en Plan Mode (etapas, archivos, riesgos, criterios de aceptación), después ejecutar en modo normal.
   - **Commitment checkpoint:** Antes de escribir código, Claude debe declarar explícitamente qué enfoque/skill usará, por qué aplica, y los pasos concretos que seguirá. Este compromiso público crea un ancla psicológica que dificulta abandonar el plan mid-task. Desviarse del plan declarado requiere aprobación explícita del usuario.
   - **Non-goals explícitos:** Al planificar, declarar qué NO se va a construir. Sin non-goals, Claude "ayuda" scaffoldeando funcionalidad no solicitada (auth, admin UI, notificaciones). Cada hora podando código no pedido es hora perdida. Los non-goals son la forma más barata de prevenir scope creep de la IA.
   - **Si algo se tuerce, PARAR y re-planificar inmediatamente.** No seguir empujando sobre un plan roto. Los LLMs tienden a "parchear hacia adelante" — esta regla lo previene.
* **Tú:** Decides si la tarea requiere una sesión simple o múltiples *worktrees* paralelos.
* **Claude:** Inicias bucles de verificación automáticos. Ejemplo: `/loop "corre los tests y resume los fallos" cada 30 min`.

#### 2. Durante el Día (Ejecución e Higiene de Contexto)
* **Regla de Oro:** Mantén el hilo principal limpio. No mezcles debates teóricos con la ejecución del código.
* **Consultas rápidas:** Usa el comando `/btw` para preguntas rápidas que no requieren leer archivos nuevos ni modificar código (no ensucia el historial). También disponible `Cmd+;` (Mac) / `Ctrl+;` (Windows/Linux) para abrir un **side chat** — hilo transient que desaparece al cerrarlo, ideal para preguntar sobre un diff o output sin contaminar la sesión principal.
* **Multi-pane (Desktop):** La app desktop permite arrastrar panes para ver diffs de routines completadas, sesiones activas y ejecuciones en curso en paralelo. Útil para monitorear trabajo autónomo mientras desarrollas.
* **Exploración de alternativas:** Usa `/fork` para crear bifurcaciones de la sesión y probar ideas sin contaminar la sesión principal.
* **Corrección de errores:** Si la IA toma un mal camino, usa `/rewind` (o doble Esc) para borrar ese contexto fallido de inmediato en lugar de discutir el error.
* **Regla de los 2 intentos:** Después de 2 correcciones fallidas → `/clear` y reescribir el prompt inicial incorporando lo aprendido. No seguir corrigiendo sobre contexto contaminado.
* **Investigaciones acotadas:** Nunca pedir "investiga X" sin scope — Claude leerá cientos de archivos y llenará el contexto. Acotar el alcance o delegar a subagentes.
* **Refactorización/Revisión:** Usa `/simplify` para invocar agentes que revisen duplicidad, bugs y eficiencia.
* **Tareas Masivas:** Usa `/batch` para delegar migraciones grandes. Claude dividirá el trabajo en unidades independientes en distintos *worktrees*.

#### 3. Ritual de Fin de Día (Cierre y Traspaso)
* **Claude:** Ejecuta una limpieza de cabos sueltos, código duplicado o notas a medias.
* **Tú:** Actualizas el `CLAUDE.md` o el sistema de `/memory` con cualquier regla nueva, convención o fricción descubierta hoy. *El `CLAUDE.md` es un contrato vivo.*
* **Claude:** Actualiza el archivo de lecciones con patrones de errores corregidos durante la sesión.
* **Tú:** Cierras bucles, matas sesiones ruidosas y dejas un "handoff" (traspaso) claro para la sesión de mañana.

---

### 📏 Rules — Reglas Modulares con Scoping

Cuando CLAUDE.md crece demasiado, se fragmenta en `.claude/rules/`:

```
.claude/rules/
├── code-style.md
├── testing.md
├── api-conventions.md
└── security.md
```

- **Sin frontmatter `paths:`** → la regla se carga en TODAS las sesiones.
- **Con frontmatter `paths:`** → solo se carga cuando Claude toca archivos que coinciden:

```yaml
---
paths:
  - "src/api/**/*.ts"
  - "src/handlers/**/*.ts"
---
# Reglas de API
- Todos los handlers retornan { data, error }
- Validación con zod en cada handler
```

**Beneficio:** Claude no ve reglas de API cuando está editando un componente React. Contexto limpio = mejores resultados.

---

### ⚡ Slash Commands — Automatización de Workflows

Un archivo `.md` en `.claude/commands/` se convierte automáticamente en un slash command:

- `review.md` → `/project:review`
- `fix-issue.md` → `/project:fix-issue`

**Sintaxis especial:**
- `` !`comando shell` `` — ejecuta el comando y alimenta su output al prompt
- `$ARGUMENTS` — recibe parámetros del usuario

**Ejemplo (code review):**
```markdown
---
description: Review del branch actual antes de merge
---
## Cambios
!`git diff --name-only main...HEAD`
## Diff completo
!`git diff main...HEAD`
Revisa: calidad, seguridad, cobertura de tests, performance.
Feedback específico y accionable por archivo.
```

**Ejemplo (fix issue con argumento):**
```markdown
---
description: Investigar y corregir un issue de GitHub
argument-hint: [número-de-issue]
---
Analiza el issue #$ARGUMENTS.
!`gh issue view $ARGUMENTS`
Encuentra la causa raíz, corrígelo, y escribe un test que lo habría detectado.
```

- **Equipo:** `.claude/commands/` → `/project:nombre` (committed)
- **Personal:** `~/.claude/commands/` → `/user:nombre` (todos los repos)

---

### 🎯 Skills vs Commands

| Aspecto | Commands | Skills |
|---------|----------|--------|
| Activación | Solo manual (`/nombre`) | Automática por contexto O manual |
| Estructura | Un solo archivo `.md` | Carpeta con `SKILL.md` + archivos companion |
| Referencia a otros archivos | No | Sí, con `@ARCHIVO.md` |
| Ubicación | `.claude/commands/` | `.claude/skills/nombre/SKILL.md` |

**Skills se auto-activan** cuando Claude detecta una situación que coincide con su `description` en el frontmatter YAML. Mencionar "security review" en la conversación activa automáticamente el skill de seguridad.

**Unificación:** Anthropic fusionó ambos sistemas — un skill en `.claude/skills/deploy/SKILL.md` y un command en `.claude/commands/deploy.md` generan el mismo `/deploy`. Los commands existentes siguen funcionando.

---

### 🤖 Agents — Sub-agentes Especializados

Definidos en `.claude/agents/`, son personas especializadas con su propio contexto aislado:

```yaml
---
name: code-reviewer
description: Revisor experto. Usar PROACTIVAMENTE al revisar PRs o validar implementaciones.
model: sonnet
tools: Read, Grep, Glob
---
Eres un revisor senior enfocado en corrección y mantenibilidad.
- Flaggea bugs, no solo estilo
- Sugiere fixes concretos, no mejoras vagas
- Verifica edge cases y manejo de errores
- Performance solo cuando importa a escala
```

**Campos clave:**
- `model:` — asignar modelo diferente por agente (haiku para tareas rápidas, opus para razonamiento profundo). **Reduce costes** sin sacrificar calidad.
- `tools:` — restricción deliberada de permisos. Un auditor de seguridad solo debe leer, no escribir.
- **Contexto separado:** el agente trabaja aislado, condensa sus hallazgos y devuelve un resumen a la sesión principal. No infla el contexto del hilo principal.
- **Aislamiento de contexto en pipelines:** Cuando el mismo contexto planifica, implementa y revisa, la revisión es cosmética — el mismo "cerebro" se auto-aprueba. En pipelines de agentes (architect → coder → tester → reviewer), cada agente debe recibir **solo el output de los pasos declarados como dependencia**, no todo el contexto acumulado. El architect planifica sin detalles de implementación. El tester testea sin saber qué el coder consideró "fine". El reviewer revisa sin el sesgo optimista del implementador. Aislamiento crea accountability.
- **Agente ≠ upgrade de un workflow:** Si cada paso tiene una sola acción correcta y el path está completamente definido, usar un script, un command o un hook — no un agente. Los agentes añaden latencia, coste y no-determinismo. Reservarlos para problemas donde la decisión intermedia requiere razonamiento: múltiples paths posibles, outputs variables, o necesidad de adaptarse a resultados inesperados.
- **Personal:** `~/.claude/agents/` aplica a todos los proyectos.

---

### 🔒 Permisos — settings.json

`settings.json` en `.claude/` controla qué puede hacer Claude sin preguntar:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Read", "Write", "Edit"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(curl *)",
      "Read(./.env)",
      "Read(./.env.*)"
    ]
  }
}
```

**Tres zonas:**
- `allow` — ejecución silenciosa, sin confirmación
- `deny` — bloqueado absoluto, nunca se ejecuta
- **Todo lo demás** — Claude pide permiso antes de proceder (zona de seguridad)

**`$schema`** habilita autocompletado y validación en VS Code.
**`settings.local.json`** para overrides personales (gitignored automáticamente).

**Control de auto-memory:**
- `"autoMemoryEnabled": false` en `settings.json` del proyecto (desactiva solo ese proyecto) o en `~/.claude/settings.json` (desactiva globalmente).
- Variable de entorno `CLAUDE_CODE_DISABLE_AUTO_MEMORY=1` para forzar desactivación en CI/CD — sobreescribe cualquier configuración de settings.json.
- Toggle rápido en sesión: `/memory` → seleccionar `Auto-memory: on/off`.

---

### 🚀 Orden de Setup Progresivo (De Cero a Productivo)

1. **`/init`** — Claude lee el proyecto y genera un CLAUDE.md starter. Recortarlo a lo esencial (~20 líneas: build commands, arquitectura, gotchas).
2. **`settings.json`** — Permisos básicos: allow test/build scripts, deny .env y comandos destructivos.
3. **1-2 commands** — Los workflows que más repites (code review, fix-issue).
4. **`rules/`** — Cuando CLAUDE.md supere ~50 líneas, fragmentar en archivos temáticos con path scoping.
5. **`~/.claude/CLAUDE.md`** — Preferencias personales de coding que aplican a todos tus proyectos.
6. **Skills y Agents** — Añadir cuando un workflow complejo se repita. No antes.

> **Regla del 95%:** Los pasos 1-5 cubren el 95% de las necesidades. Skills y agents son optimización avanzada.

---

### 🪝 Hooks — Acciones Automáticas Sin Excepción

Los hooks son diferentes a rules y skills: se ejecutan **siempre**, antes o después de una acción de herramienta, sin variación ni juicio de Claude.

- **PreToolUse:** Validación antes de ejecutar (ej: lint antes de commit)
- **PostToolUse:** Acción después de ejecutar (ej: format después de write)
- **Stop:** Verificación al cerrar sesión

**Cuándo usar hook vs rule:** Si la acción debe ocurrir el 100% de las veces sin excepción → hook. Si depende del contexto → rule o skill.

---

### ⏰ Routines — Ejecución Autónoma en la Nube

Una routine es una configuración guardada (prompt + repositorio GitHub + connectors) que se ejecuta de forma autónoma en infraestructura de Anthropic. No requiere terminal abierto ni sesión activa.

**Modelo de ejecución:**
- Anthropic levanta una VM fresca, clona el repo y ejecuta el prompt con acceso a los connectors configurados.
- Cada ejecución es una **sesión discreta** — comienza limpia, hace su trabajo y termina. Sin estado entre ejecuciones, lo que previene drift de contexto.
- Variable `CLAUDE_CODE_REMOTE=true` disponible para que scripts de setup detecten ejecución cloud y ajusten comportamiento (evitar instalaciones pesadas locales).

**Tres tipos de trigger:**

| Trigger | Configuración | Caso de uso |
|---|---|---|
| **Schedule** | Cron via CLI (`/schedule`) o web UI | Mantenimiento nocturno: doc drift, stale issues, dependency checks |
| **API** | Endpoint HTTP + bearer token | Webhooks de Sentry/Datadog/PagerDuty → diagnóstico automático |
| **GitHub** | Eventos: `pull_request.opened`, `release`, tags | PR review automático, release notes |

Se pueden combinar múltiples triggers en una misma routine.

**Branch protection (crítico):**
- Por defecto, routines solo pueden pushear a branches con prefijo `claude/`.
- **Nunca** habilitar push directo a main. La routine crea branch + PR; un humano revisa y mergea.

**Scope de connectors:**
- Aplicar **least privilege**: solo conectar Slack, Linear, GitHub, etc. si la routine los necesita.
- Menos connectors = menor radio de impacto ante errores de prompt.

**Límites diarios:**

| Plan | Routines/día |
|---|---|
| Pro | 5 |
| Max | 15 |
| Team/Enterprise | 25 |

**Tres patrones prácticos para empezar:**
1. **Nightly Issue Groomer** (schedule): Asigna labels, identifica equipo responsable, publica resumen en Slack.
2. **PR Review Bot** (GitHub trigger): Prompt adversarial que busca edge cases, concurrencia y lógica — ignora estilo (el linter lo cubre).
3. **Deploy Verifier** (API trigger): Post-deploy smoke checks + scan de error logs + trace al commit responsable.

**Limitaciones actuales (research preview):**
- Intervalo mínimo de schedule: 1 hora. Para polling más frecuente, usar `/loop` en sesión activa.
- API triggers y GitHub webhooks solo configurables vía web console (requieren OAuth).
- Sin encadenamiento nativo de routines. Workaround: la routine A llama al API endpoint de la routine B como paso final.

**Regla de arranque:** Empezar con UNA routine schedule de bajo riesgo (stale TODOs, doc drift). Observar output una semana antes de escalar.

---

### 📚 Wiki de Proyecto — Memoria Permanente Acumulativa

Inspirado en el patrón "LLM Wiki" (Karpathy): un directorio de documentos Markdown que crece con cada sesión y persiste como documentación committable del proyecto.

**Dos sistemas complementarios:**
| Sistema | Ubicación | Persistencia | Propósito |
|---|---|---|---|
| `memory/` | `.claude/memory/` | Efímera (gitignored) | Contexto de sesión, decisiones tentativas, WIP |
| `auto-memory` | `~/.claude/projects/<proj>/memory/` | Semi-persistente (local) | MEMORY.md auto-gestionado por Claude + archivos topic on-demand |
| `wiki/` | `docs/src/wiki/` | Permanente (committed) | Conocimiento confirmado del proyecto |

**Flujo de conocimiento:**
```
Sesión de trabajo → .claude/memory/ (captura rápida)
                         ↓ (promoción automática o manual)
                   docs/src/wiki/ (conocimiento permanente)
```

**Tipos de páginas wiki:**
- **Overview** (`_overview.md`): Propósito, stack, decisiones fundacionales
- **Entity** (`entities/*.md`): Modelos, servicios, módulos del sistema
- **Concept** (`concepts/*.md`): Patrones, convenciones, reglas de negocio
- **Decision** (`decisions/*.md`): ADRs — decisiones con contexto y alternativas
- **Glossary** (`glossary.md`): Términos del dominio
- **Log** (`log.md`): Registro cronológico de cambios al wiki

**Criterios de promoción (memory → wiki):**
- ✅ Decisiones de arquitectura confirmadas
- ✅ Reglas de negocio estables
- ✅ Convenciones adoptadas por el equipo
- ❌ Workarounds temporales
- ❌ Bugs en progreso
- ❌ Información tentativa

**Integración automática:**
- El hook `session-consolidate.sh` promueve conocimiento elegible al wiki al cerrar sesión
- El agente `memory-consolidator` marca entradas promovidas como archivadas antes de comprimir
- Los agentes `planner`, `architect`, `doc-updater` consultan y actualizan el wiki durante el trabajo

---

### �📐 Estructura de Prompts Efectivos
**Context engineering > prompt engineering:** Curar *qué información entra* en el contexto importa más que *cómo escribes* la instrucción. Un prompt mediocre en un contexto bien curado supera a un prompt brillante enterrado en ruido. Todo lo que este documento hace (CLAUDE.md lean, rules con path scoping, agents con contexto aislado, higiene de sesión diaria) es context engineering aplicado. El prompt es la última milla — el contexto es el sistema.
Fórmula base para prompts a Claude Code:

```
[Rol] + [Tarea] + [Contexto]
```

- **Front-load lo importante:** La instrucción más crítica va al inicio del prompt.
- **Ser específico:** Claude solo puede inferir contexto — cuanto más preciso, mejor resultado.
- **Incluir verificación:** Tests, outputs esperados o criterios de éxito para que Claude se auto-valide.
- **Authority language en reglas críticas:** Las restricciones importantes deben usar lenguaje imperativo (MUST, non-negotiable, no exceptions) en vez de sugerencias ("sería bueno", "considera"). Los LLMs exhiben compliance significativamente mayor ante framing autoritativo que ante recomendaciones suaves. Reservar este tono solo para reglas verdaderamente críticas — si todo es "non-negotiable", nada lo es.

**Prompts interactivos vs prompts para Routines:**
- **Interactivo:** Puede pedir clarificación mid-session. Tolera ambigüedad porque hay un humano presente.
- **Routine (autónomo):** Debe ser **completamente determinista**. Cubrir cada punto de decisión, qué hacer si no encuentra resultados, formato exacto de output, y acción alternativa ante fallos. No hay humano para resolver ambigüedades.

---

### 🧭 Principios Core de Ingeniería

- **Simplicity First:** Cada cambio debe ser lo más simple posible. Impactar el mínimo código.
- **No Laziness:** Buscar la causa raíz. Nunca fixes temporales. Estándar de desarrollador senior.
- **Minimal Impact:** Los cambios solo tocan lo necesario. Evitar introducir bugs colaterales.
- **Kill Process, Don't Optimize It:** En desarrollo con IA, el proceso que no aporta valor = latencia pura. Eliminar ceremonia, no optimizarla. Si un paso existe solo por inercia organizacional y no previene un fallo concreto, eliminarlo. Sprints, estimation y standups son scaffolding para limitaciones humanas de ejecución — con IA, la ejecución es abundante y el cuello de botella se mueve a decisiones y governance.

---

### 🤖 Prompt sugerido para entregarle a la otra IA

Puedes copiar y pegar este bloque directamente a la IA que te ayudará a configurar tu repositorio:

> "Actúa como un Arquitecto de Software Experto en herramientas de IA. Voy a inicializar un repositorio padre que será gestionado principalmente a través de la CLI de **Claude Code**. 
> 
> Basado en el flujo de trabajo de élite de Claude Code (Q1 2026), necesito que redactes el archivo **`CLAUDE.md`** inicial para este repositorio. Este archivo debe actuar como un 'contrato vivo' y debe instruir a Claude para que siga estrictamente estas directivas:
> 
> 1. **Planificación Obligatoria:** Antes de escribir código, Claude debe generar un plan estructurado (archivos afectados, riesgos, criterios de aceptación).
> 2. **Higiene de Contexto:** Instruir a Claude para que sugiera el uso de `/fork` para experimentos y mantenga la sesión principal enfocada solo en la tarea actual.
> 3. **Verificación Continua:** Establecer reglas para usar `/loop` y comandos de testeo locales paso a paso, en lugar de confiar ciegamente en la generación.
> 4. **Prevención de Código Duplicado:** Obligar a invocar herramientas de revisión y linting o el uso del concepto `/simplify` antes de dar por terminada una tarea.
> 5. **Actualización Diaria:** Un recordatorio en el prompt del sistema para que, al final del día, sugiera qué aprendizajes nuevos deben añadirse a este mismo archivo `CLAUDE.md`.
> 
> Redacta el `CLAUDE.md` en formato Markdown, estructurado, directo y sin texto de relleno. Incluye marcadores de posición `[como este]` para los comandos específicos de testeo/linting de mi stack tecnológico que te proporcionaré más adelante."