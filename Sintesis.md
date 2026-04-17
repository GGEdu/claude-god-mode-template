Es una excelente iniciativa. Tratar a Claude Code como un sistema operativo y no como un simple "autocompletado" es exactamente lo que separa a los usuarios promedio de los desarrolladores de alto rendimiento. 

Aquí tienes el resumen estructurado de las partes más importantes del artículo, diseñado específicamente para que puedas leérselo a otra IA y para que tengas claro tu flujo de trabajo diario.

---

### 🧠 Filosofía Central para la IA (El Modelo Operativo)

Para generar el `CLAUDE.md`, la IA debe entender que el repositorio se rige por un **modelo de 5 partes**:

1. **Contexto siempre activo reducido:** El archivo CLAUDE.md debe contener solo el contexto "siempre activo" y reglas inmutables del proyecto. No debe ser un basurero de prompts.
   - **Límite ~200 líneas.** Más de eso diluye la atención de Claude y empeora resultados.
   - **Solo el "qué", no el "por qué":** Comandos build/test, decisiones de arquitectura, gotchas no obvios, convenciones de naming/imports.
   - **No incluir:** lo que el linter ya cubre, dumps de documentación completa, ni explicaciones teóricas de decisiones.
   - **Tres niveles de merge automático:** `~/.claude/CLAUDE.md` (global personal) → `CLAUDE.md` en raíz del proyecto (equipo) → `CLAUDE.md` en subdirectorios (scoped). Claude lee y fusiona los tres.
   - **Overrides personales:** `CLAUDE.local.md` en la raíz del proyecto — se gitignora automáticamente. Preferencias personales sin afectar al equipo.
2. **Procedimientos repetitivos = Skills:** Cualquier tarea que se repita más de dos veces debe convertirse en un "skill", un comando o una regla explícita en el repositorio.
3. **Higiene de sesión estricta:** La sesión principal debe mantenerse libre de código basura o conversaciones secundarias.
4. **Paralelización aislada:** El trabajo paralelo o complejo debe realizarse bajo supervisión estricta y en entornos aislados (worktrees o ramas independientes).
5. **Guardarraíles inteligentes:** Usar el modo automático (Auto Mode) para tareas rutinarias, pero requiriendo validación humana (pruebas, linting) antes de fusionar cualquier código.

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
└── projects/                  # Historial de sesiones + auto-memory
```

**Regla de precedencia:** Claude fusiona global → proyecto → subdirectorio. Lo más específico gana.

---

### �📝 Estructura del Flujo de Trabajo Diario (Para ti y para Claude)

Este es el ciclo que debes seguir día a día. Tu `CLAUDE.md` debe estar diseñado para facilitar este flujo.

#### 1. Ritual de Mañana (10 minutos de Setup)
* **Tú:** Abres la rama, revisas el `CLAUDE.md` para refrescar las reglas del proyecto.
* **Claude:** Se le exige **planificar antes de escribir**. Debe listar etapas, archivos a tocar, riesgos y criterios de aceptación.
* **Tú:** Decides si la tarea requiere una sesión simple o múltiples *worktrees* paralelos.
* **Claude:** Inicias bucles de verificación automáticos. Ejemplo: `/loop "corre los tests y resume los fallos" cada 30 min`.

#### 2. Durante el Día (Ejecución e Higiene de Contexto)
* **Regla de Oro:** Mantén el hilo principal limpio. No mezcles debates teóricos con la ejecución del código.
* **Consultas rápidas:** Usa el comando `/btw` para preguntas rápidas que no requieren leer archivos nuevos ni modificar código (no ensucia el historial).
* **Exploración de alternativas:** Usa `/fork` para crear bifurcaciones de la sesión y probar ideas sin contaminar la sesión principal.
* **Corrección de errores:** Si la IA toma un mal camino, usa `/rewind` (o doble Esc) para borrar ese contexto fallido de inmediato en lugar de discutir el error.
* **Refactorización/Revisión:** Usa `/simplify` para invocar agentes que revisen duplicidad, bugs y eficiencia.
* **Tareas Masivas:** Usa `/batch` para delegar migraciones grandes. Claude dividirá el trabajo en unidades independientes en distintos *worktrees*.

#### 3. Ritual de Fin de Día (Cierre y Traspaso)
* **Claude:** Ejecuta una limpieza de cabos sueltos, código duplicado o notas a medias.
* **Tú:** Actualizas el `CLAUDE.md` o el sistema de `/memory` con cualquier regla nueva, convención o fricción descubierta hoy. *El `CLAUDE.md` es un contrato vivo.*
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