---
name: lessons-readme
description: Schema y convenciones del sistema de lessons (Sintesis.md §1.8). Define estructura de cada entry y reglas de promoción.
type: project
updated: 2026-04-25
---

# Lessons — Sistema de aprendizaje persistente

Este directorio almacena **lessons** — patrones aprendidos en sesiones de Claude que merecen recordarse para evitar repetir errores. Es la primera capa del [Self-Improvement Loop](../../../Sintesis.md#18-self-improvement-loop) (Sintesis.md §1.8).

## Estructura del directorio

```
.claude/memory/lessons/
├── README.md           # Este archivo (schema + convenciones)
├── _index.yaml         # Índice de todas las lessons activas (≤200 entries)
├── archive/            # Lessons archivadas (status: archived)
│   └── .gitkeep
└── lesson-YYYY-MM-DD-NNN.yaml   # Una lesson por archivo
```

## Schema obligatorio de una lesson

Cada lesson es un archivo YAML independiente con el siguiente schema:

```yaml
# lesson-2026-04-25-001.yaml
id: lesson-2026-04-25-001
date: 2026-04-25
scope: api-auth                  # Namespace para detectar contradicciones
trigger: "Qué causó el error (acción concreta)"
pattern: "Qué hacía mal (patrón reconocible)"
fix: "Qué debe hacer en su lugar (acción correctiva)"
confidence: 0.5                  # 0.3 tentativa | 0.5 moderada | 0.7 fuerte | 0.9 casi certeza
rule_created: false              # true si ya se promovió a rule
sessions_without_repeat: 0       # Incrementado por session-consolidate
last_referenced: 2026-04-25
supersedes: null                 # ID de lesson anterior reemplazada
superseded_by: null              # ID de lesson que reemplaza esta
status: active                   # active | promoted | archived | superseded
```

### Confidence

Inicia en `0.5` al crear la lesson. Sube +0.1 (máx. 0.9) cada vez que `sessions_without_repeat` se incrementa sin contradicción, o cuando 2+ agentes la referencian en sesiones distintas. Baja a `0.3` si aparece un caso límite que casi contradice el `fix` sin llegar a supersederlo. Sirve como señal de promoción alternativa a `sessions_without_repeat` — ver más abajo.

## Reglas de operación

### Creación

- Una lesson por evento de corrección. **Una corrección = una lesson.**
- `id` formato: `lesson-YYYY-MM-DD-NNN` con NNN secuencial dentro del día.
- `scope` es OBLIGATORIO — sin scope no hay detección de contradicciones.

### Detección de contradicciones (Sintesis.md §1.8)

Antes de escribir una lesson nueva:

1. Buscar lessons activas con **mismo `scope`** Y keywords solapantes en `trigger`/`pattern`.
2. Si match → la nueva lesson **reemplaza** la anterior:
   - Anterior: `status: superseded`, `superseded_by: <new_id>`
   - Nueva: `supersedes: <old_id>`
3. Sin match → crear lesson nueva con `supersedes: null`.

### Promoción a rule (lesson → rule)

Una lesson se promueve a rule (en `~/.claude/rules/` o `.claude/rules/`) si cumple **una** de:

| Señal | Condición | Acción |
|---|---|---|
| **Explícita** | Usuario ejecuta `/promote <lesson-id>` | Inmediata |
| **Implícita** | `sessions_without_repeat >= 5` Y `status == active` | Automática en session-consolidate |
| **Confianza** | `confidence >= 0.8` Y `status == active` | Automática — puede calificar antes que el umbral de 5 sesiones |
| **Consenso** | 2+ agentes referencian la misma lesson en sesiones distintas | Automática |

**Al promover, elegir destino según alcance:**

| Destino | Cuándo |
|---|---|
| `.claude/rules/<topic>.md` (project) | El `fix` depende del dominio/negocio de este proyecto (módulo específico, convención de este codebase) |
| `~/.claude/rules/common/<topic>.md` (global, cross-proyecto) | El `fix` seguiría siendo cierto en un proyecto distinto con otro stack (hábito de tooling, práctica de seguridad genérica, workflow de git) |

Heurística: "¿esta lección es sobre CÓMO trabajar o sobre QUÉ hace este proyecto?" — lo primero es global, lo segundo es project.

Tras promover: `rule_created: true`, `status: promoted` en la lesson.

### Garbage collection (TTL)

- `last_referenced` se actualiza automáticamente por `session-consolidate.sh` (Stop hook) cuando la lesson aparece en `session-reads.log`.
- Lesson con `last_referenced > 30 días` Y `status: active` → mover a `archive/` con `status: archived`.
- Lesson `superseded` → archivar inmediatamente.

## `_index.yaml` — Índice ligero

`_index.yaml` lista todas las lessons activas para acceso O(1) sin leer cada archivo. Schema:

```yaml
last_updated: 2026-04-25
count: 12
entries:
  - id: lesson-2026-04-25-001
    scope: api-auth
    keywords: [oauth, google, callback]
    confidence: 0.5
    last_referenced: 2026-04-25
    status: active
  # ...
```

Mantenerlo ≤200 entries. Al exceder, archivar las más antiguas.

## Cómo detectar correcciones

**Corrección** (genera lesson):
- Usuario revierte un cambio explícitamente.
- Usuario dice "eso está mal", "no funciona", "incorrecto".
- Test fallaba con la implementación anterior.

**Cambio de opinión** (NO genera lesson):
- Usuario pide una dirección diferente sin indicar error en la actual.
- Usuario explora alternativas.

## Ejemplo completo

Sesión: usuario corrige a Claude que estaba usando JWT cuando el proyecto usa session cookies.

```yaml
# lesson-2026-04-25-001.yaml
id: lesson-2026-04-25-001
date: 2026-04-25
scope: auth-storage
trigger: "Usuario revirtió commit que añadía generación de JWT en login"
pattern: "Asumir JWT como mecanismo de autenticación por defecto"
fix: "Verificar config/auth.php antes de proponer mecanismo. Este proyecto usa session cookies (Laravel default)."
confidence: 0.5
rule_created: false
sessions_without_repeat: 0
last_referenced: 2026-04-25
supersedes: null
superseded_by: null
status: active
```

El `fix` depende de una decisión de este proyecto concreto (Laravel + session cookies) — no de una práctica universal — así que su destino de promoción es `.claude/rules/auth.md` (project), no global. Tras 5 sesiones sin que el error se repita, o `confidence >= 0.8` antes, se promueve ahí.
