---
name: project-wiki
description: AI-maintained project knowledge base. Claude builds and updates a structured wiki in docs/src/wiki/ from ingested documents and session decisions. The wiki compounds over time — every source, decision, and question makes the knowledge base richer. Activates on "wiki", "ingest", "knowledge base", "glossary", or when Claude makes permanent decisions during normal work.
origin: internal
version: 1.0.0
---

# Project Wiki — Knowledge Base Persistente

Mantienes un **wiki de proyecto** en `docs/src/wiki/`. Este wiki es conocimiento permanente y acumulativo — a diferencia de `.claude/memory/` que es efímero y de sesión.

**Dos sistemas, dos propósitos:**
- `.claude/memory/` → contexto efímero de sesión (auto-limpiado, gitignored)
- `docs/src/wiki/` → conocimiento permanente del proyecto (committed, visible al equipo)

---

## Estructura del Wiki

```
docs/src/wiki/
├── index.md          # Catálogo de TODAS las páginas — tu mapa de navegación
├── overview.md       # Síntesis del proyecto (evoluciona con cada ingest)
├── glossary.md       # Términos, convenciones, deprecated terms
├── log.md            # Timeline de operaciones wiki
├── sources/          # Un resumen por documento procesado
│   └── *.md
├── concepts/         # Páginas de conceptos técnicos o de dominio
│   └── *.md
├── decisions/        # Decisiones de arquitectura/diseño (formato ADR ligero)
│   └── *.md
├── entities/         # Servicios, APIs, sistemas, personas
│   └── *.md
└── analyses/         # Respuestas a queries guardadas como conocimiento
    └── *.md
```

---

## Tipos de Página

### source-summary
Resumen de un documento fuente procesado via ingest.
```markdown
---
title: "[Título del documento]"
type: source-summary
source: "[ruta original del documento]"
ingested: YYYY-MM-DD
---
# [Título]

## Puntos clave
- ...

## Decisiones extraídas
- ...

## Términos nuevos
- ...

## Relaciones
- Relacionado con: [link a otras páginas wiki]
```

### concept
Página sobre un concepto técnico o de dominio.
```markdown
---
title: "[Nombre del concepto]"
type: concept
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
# [Concepto]

## Definición
...

## Uso en este proyecto
...

## Relaciones
- Depende de: [links]
- Usado por: [links]
```

### decision
Decisión de arquitectura o diseño (formato ADR ligero).
```markdown
---
title: "[Decisión]"
type: decision
status: accepted | deprecated | superseded
date: YYYY-MM-DD
---
# [Decisión]

## Contexto
[Qué problema motivó esta decisión]

## Decisión
[Qué se decidió]

## Alternativas consideradas
- [Opción A]: [razón de rechazo]
- [Opción B]: [razón de rechazo]

## Consecuencias
- [Qué se gana / qué se pierde]
```

### entity
Servicio, API, sistema, persona u otra entidad nombrada.
```markdown
---
title: "[Nombre de la entidad]"
type: entity
category: service | api | system | person | team
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
# [Entidad]

## Descripción
...

## Relaciones
- Se comunica con: [links]
- Depende de: [links]
```

### analysis
Respuesta a una query guardada como conocimiento permanente.
```markdown
---
title: "[Pregunta o tema analizado]"
type: analysis
date: YYYY-MM-DD
sources: ["[páginas wiki consultadas]"]
---
# [Título]

## Hallazgos
...

## Conclusión
...
```

---

## Operaciones

### `/wiki init`

Inicializa `docs/src/wiki/` con la estructura base.

**Proceso:**
1. Verifica que no existe ya `docs/src/wiki/index.md` (si existe, informa y para)
2. Crea `docs/src/wiki/` con subdirectorios: `sources/`, `concepts/`, `decisions/`, `entities/`, `analyses/`
3. Copia los templates: `index.md`, `overview.md`, `glossary.md`, `log.md`
4. Lee los archivos del proyecto (README.md, CLAUDE.md, package.json/composer.json) para popular el overview inicial
5. Registra la operación en `log.md`

**Templates:** Los templates están en `@templates/index.md`, `@templates/overview.md`, `@templates/glossary.md`, `@templates/log.md` dentro de esta carpeta de skill.

---

### `/wiki ingest <path>`

Procesa un documento desde cualquier ruta y actualiza el wiki.

**Proceso:**
1. Lee el documento fuente en `<path>` (NUNCA modificar el archivo fuente)
2. Lee `docs/src/wiki/index.md` para entender el estado actual del wiki
3. Discute los puntos clave con el usuario (breve — 3-5 bullets)
4. Crea página `source-summary` en `docs/src/wiki/sources/`
5. Para cada entidad, concepto o decisión encontrada:
   - Si la página ya existe → actualízala con la nueva información
   - Si no existe → crea la página correspondiente
6. Actualiza `glossary.md` con términos nuevos
7. Actualiza `overview.md` si la síntesis del proyecto cambió
8. Actualiza `index.md` con todas las páginas nuevas
9. Registra la operación en `log.md` con timestamp y resumen

**Regla crítica:** UN documento fuente puede tocar 10-15 páginas wiki. Esto es normal y esperado.

---

### `/wiki query <pregunta>`

Consulta el wiki para responder una pregunta.

**Proceso:**
1. Lee `docs/src/wiki/index.md` para encontrar páginas relevantes
2. Lee las páginas identificadas (NO leer el wiki entero)
3. Sintetiza la respuesta desde el wiki
4. Pregunta: "¿Guardar esta respuesta como página de análisis en el wiki?"
5. Si el usuario acepta → crea página `analysis` en `docs/src/wiki/analyses/`
6. Registra la query en `log.md`

**Las preguntas enriquecen el wiki** — no desaparecen en el chat.

---

### `/wiki lint`

Auditoría de salud del wiki.

**Proceso:**
1. Lee todas las páginas del wiki
2. Detecta:
   - **Contradicciones**: información que se contradice entre páginas
   - **Páginas huérfanas**: sin links apuntando a ellas (excepto index)
   - **Referencias rotas**: links a páginas que no existen
   - **Información stale**: páginas con `updated` de hace >60 días sin revisión
   - **Términos inconsistentes**: mismo concepto con nombres diferentes
   - **Páginas sin tipo**: falta frontmatter `type:`
3. Reporta hallazgos con severidad (CRITICAL/WARN/INFO)
4. Pregunta qué fixes aplicar
5. Registra el lint en `log.md`

Ejecutar cada ~10 ingests o cuando algo parezca inconsistente.

---

### `/wiki migrate`

Migra `.claude/memory/` existente al wiki (operación one-time).

**Proceso:**
1. Lee todos los archivos en `.claude/memory/`
2. Clasifica cada entrada: ¿decision? ¿concept? ¿entity? ¿efímero?
3. Las entradas permanentes → crea páginas correspondientes en el wiki
4. Las efímeras → deja en memory/ (se auto-limpiarán)
5. Actualiza index, glossary, overview según lo migrado
6. Registra en `log.md`

---

## Actualización Automática (CRÍTICO)

**No esperar a que el usuario invoque `/wiki`.**

Durante el trabajo NORMAL de cualquier sesión, Claude DEBE actualizar el wiki cuando:

1. **Tome una decisión de arquitectura** → crear/actualizar página `decision`
2. **Descubra una convención del proyecto** → actualizar `glossary.md`
3. **Integre un servicio o API nueva** → crear/actualizar página `entity`
4. **Resuelva un problema no trivial** → actualizar la página `concept` correspondiente
5. **El overview del proyecto haya cambiado** → actualizar `overview.md`

**Condición:** solo si `docs/src/wiki/index.md` existe. Si no existe, no hacer nada (el usuario debe ejecutar `/wiki init` primero).

**Después de cada actualización:** actualizar `index.md` y `log.md`.

---

## Navegación Eficiente

**NUNCA leer el wiki entero.** Siempre:
1. Leer `index.md` primero → identifica páginas relevantes
2. Leer solo las páginas necesarias → drill-down
3. Si index.md no tiene lo que buscas → `glossary.md` como segundo mapa

Esto mantiene el consumo de contexto bajo incluso con wikis de cientos de páginas.

---

## Cross-Referencing

Usar links relativos markdown (compatibles con VitePress y GitHub):

```markdown
Ver [autenticación](../concepts/authentication.md) para detalles.
Decisión relacionada: [ADR: usar JWT](../decisions/use-jwt.md)
```

**Regla:** cada página DEBE tener al menos un link a otra página del wiki (excepto la primera página creada). Páginas aisladas son casi inútiles.

---

## Federación Cross-Repo (Futuro)

Para proyectos con múltiples repositorios interrelacionados (microservicios):

### Convenciones de naming
- Referencias cross-repo usan prefijo: `@service-name/page-name`
- Ejemplo: `Ver [@auth-service/jwt-configuration](link-externo)` 

### Sección Related Services
En `index.md`, mantener una sección:
```markdown
## Related Services
| Service | Wiki URL | Descripción |
|---------|----------|-------------|
| auth-service | [link] | Autenticación y autorización |
| payment-api | [link] | Procesamiento de pagos |
```

### `/wiki federate` (no implementado)
Futuro comando para sincronizar glossaries y entidades compartidas entre repos.

---

## Formato VitePress

Todas las páginas deben ser VitePress-compatible:
- Frontmatter YAML válido (`---` delimiters)
- Links relativos markdown (no wiki-links `[[]]`)
- No usar HTML raw salvo que sea necesario
- Headings jerárquicos (un solo `#` por página)
