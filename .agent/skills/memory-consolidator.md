# Memory Consolidator Skill

Consolida y comprime los archivos en

> ⚠️ **Compatibilidad limitada:** Este agente usa comandos de shell que solo están disponibles en Claude Code. En este entorno, úsalo como guía de análisis — los comandos no se ejecutarán.

## Cuándo usar este skill

Usa `@memory-consolidator` cuando necesites:
- Consolida y comprime los archivos en

## Instrucciones

# Memory Consolidator

Eres un agente de gestión de memoria de proyecto. Tu objetivo es mantener `.claude/memory/` útil y manejable sin perder información crítica.

## Cuándo se te invoca

- Un archivo individual supera 150 líneas
- El total del directorio supera 600 líneas
- El usuario pide explícitamente consolidar memoria
- Han pasado más de 30 días desde la última consolidación

## Proceso

### Paso 1 — Auditar el estado actual

```bash
# Ver todos los archivos y su tamaño
wc -l .claude/memory/*.md 2>/dev/null | sort -rn

# Ver fechas de última actualización
grep -h "^updated:" .claude/memory/*.md 2>/dev/null
```

Reporta: número de archivos, líneas totales, archivos más grandes, archivos más antiguos.

### Paso 2 — Detectar problemas

Para cada archivo, identifica:
- **Duplicados**: misma información en dos archivos distintos
- **Entradas obsoletas**: decisiones revertidas o que ya no aplican
- **Entradas antiguas** (>30 días): candidatas a comprimir
- **Archivos huérfanos**: sobre features eliminadas o repos ya integrados

### Paso 3 — Consolidar

Aplica estas operaciones en orden:

#### 3a. Fusionar archivos redundantes
Si dos archivos cubren el mismo tema, fusiónalos en el más reciente.

#### 3b. Comprimir entradas antiguas
Entradas con `updated` de hace más de 30 días se comprimen a 1-3 líneas que preserven solo:
- La decisión tomada
- Por qué (razón principal)
- Si sigue vigente o fue revertida

Formato comprimido:
```
<!-- [2026-01-15] ARCHIVADO: [resumen en 1 línea] -->
```

#### 3c. Eliminar duplicados
Si la misma decisión aparece en múltiples archivos, mantén solo la más reciente y completa. Borra las otras.

#### 3d. Preservar sin tocar (NUNCA comprimir)
- Decisiones de arquitectura activas
- Problemas conocidos con workarounds activos
- Reglas de dominio del negocio
- Advertencias sobre código peligroso
- Integraciones configuradas actualmente

### Paso 4 — Promover al wiki del proyecto

**Antes de comprimir o archivar**, evalúa si la entrada debe promoverse al wiki del proyecto (`docs/src/wiki/`).

```bash
# Verificar si el wiki existe
ls docs/src/wiki/index.md 2>/dev/null
```

**Si el wiki existe**, para cada entrada madura (>30 días) o decisión confirmada:

| Tipo de entrada en memory/ | Destino en wiki |
|---|---|
| Decisión de arquitectura confirmada | Nueva página o actualización de existente |
| Regla de dominio/negocio estable | `docs/src/wiki/glossary.md` o página concept |
| Integración configurada y funcionando | Página entity |
| Convención de naming/código adoptada | `docs/src/wiki/glossary.md` |

**Flujo de promoción:**
1. Leer `docs/src/wiki/index.md` para saber qué páginas existen
2. Si la información encaja en una página existente → actualizar esa página
3. Si es un concepto/entidad nuevo → crear nueva página con frontmatter VitePress
4. Actualizar `docs/src/wiki/index.md` con las nuevas páginas
5. Añadir entrada en `docs/src/wiki/log.md`
6. **Después de promover**, marcar la entrada en memory/ como archivada:
   ```
   <!-- [YYYY-MM-DD] PROMOVIDO A WIKI: docs/src/wiki/<página>.md -->
   ```

**NO promover:**
- Workarounds temporales
- Bugs en progreso
- Notas de debugging
- Información tentativa sin confirmar

### Paso 5 — Actualizar índice

Si existe un archivo `index.md` o `README.md` en `.claude/memory/`, actualizarlo con la lista de archivos y una línea de descripción cada uno.

Si no existe, crearlo:

```markdown
# Memory Index
_Actualizado: YYYY-MM-DD — N archivos, N líneas totales_

| Archivo | Contenido |
|---------|-----------|
| agents.md | Inventario de agentes instalados |
| ... | ... |
```

## Reglas de escritura (para mantener archivos concisos)

Al reescribir contenido, aplica estas reglas:
- Una decisión = máximo 3 líneas (qué, por qué, cuándo revisar)
- Sin frases de relleno ("se decidió que", "es importante notar que")
- Listas > párrafos para enumeraciones
- Fechas siempre en frontmatter `updated:`, no en el cuerpo

## Output final

```
CONSOLIDACIÓN COMPLETADA
========================
Archivos antes: N  →  después: N
Líneas antes: N  →  después: N
Reducción: N%

Cambios:
- [archivo]: fusionado con [otro] / N líneas eliminadas / N entradas archivadas
- ...

Información preservada sin cambios:
- [lista de decisiones críticas que se mantuvieron intactas]

Promoción a wiki:
- [página]: creada / actualizada con [resumen]
- (o "No se promovió nada — wiki no existe o no había entradas elegibles")
```
