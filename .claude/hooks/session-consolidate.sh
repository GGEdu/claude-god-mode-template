#!/usr/bin/env bash
# session-consolidate.sh — Consolidación automática de memoria al final de cada sesión
#
# Se ejecuta como Stop hook de Claude Code. Vuelca lo relevante de la sesión a
# vault/ (si existe, memoria curada por proyecto) o .claude/memory/ (fallback,
# proyectos sin vault todavía), luego mantiene Graphify y MemPalace al día.
#
# Decisión 2026-07-14 (council unánime, ver vault/memory/decisions/ de este
# repo): sustituye a MCP `memory` — nunca se usó en ningún proyecto porque
# requería población manual explícita. Estos 3 se autoactualizan (git hook
# para Graphify, este mismo Stop hook para vault + MemPalace) sin que el
# usuario tenga que pedirlo.

set -euo pipefail

# ── Anti-recursión ─────────────────────────────────────────────────────────────
# Claude Code lanza este script, que a su vez llama `claude`. Sin esta guardia,
# el subproceso claude también activaría el hook al terminar → bucle infinito.
if [ "${CLAUDE_CONSOLIDATION_RUNNING:-0}" = "1" ]; then
    exit 0
fi

# ── Solo en proyectos con .claude/ ─────────────────────────────────────────────
if [ ! -d ".claude" ]; then
    exit 0
fi

# ── Elegir destino de memoria: vault/ si existe, si no .claude/memory/ ─────────
if [ -d "vault" ]; then
    MEM_DIR="vault/memory"
    mkdir -p "$MEM_DIR/conversations" "$MEM_DIR/decisions" "$MEM_DIR/research"
    MEM_LAYOUT="vault/memory/ — subcarpetas: conversations/ (qué se hizo en la sesión), decisions/ (decisiones de arquitectura y por qué), research/ (hallazgos de investigación por tema)."
else
    MEM_DIR=".claude/memory"
    mkdir -p "$MEM_DIR"
    MEM_LAYOUT=".claude/memory/ — un archivo por tema (ej: auth.md, architecture.md, domain-rules.md)."
fi

# ── Lanzar consolidación ───────────────────────────────────────────────────────
export CLAUDE_CONSOLIDATION_RUNNING=1

claude --print \
    --model claude-haiku-4-5-20251001 \
    --max-turns 5 \
    "Eres un agente de consolidación de memoria de proyecto. Al final de cada sesión de trabajo capturas decisiones y contexto para que la próxima sesión arranque informada.

DIRECTORIO DE MEMORIA: $MEM_DIR
LAYOUT: $MEM_LAYOUT

TU TAREA:
1. Ejecuta: git log --oneline -10 2>/dev/null || true
2. Ejecuta: git diff HEAD~1 HEAD --name-only 2>/dev/null || true
3. Ejecuta: git status --short 2>/dev/null || true
4. Lista los archivos existentes en $MEM_DIR
5. Lee los archivos de memoria que ya existen para no duplicar

SIEMPRE escribe al menos un archivo si hubo cualquier actividad en la sesión
(commits, archivos modificados, o archivos en staging). Una sesión sin commits
puede igualmente haber producido decisiones valiosas visibles en el status.

QUÉ CAPTURAR (en orden de prioridad):
1. Decisiones de arquitectura o diseño tomadas (por qué se eligió X sobre Y)
2. Problemas encontrados y cómo se resolvieron
3. Reglas de dominio o restricciones de negocio explicadas en la sesión
4. Integraciones, configuraciones o dependencias nuevas descubiertas
5. Advertencias sobre partes del código que requieren cuidado especial
6. Si no hay nada de lo anterior: un resumen breve de qué archivos se tocaron y con qué objetivo

QUÉ NO GUARDAR (nunca):
- Credenciales, tokens, passwords, API keys
- Variables de entorno con valores reales
- Información personal o de usuarios finales

FORMATO de archivos en $MEM_DIR:
- Un archivo por tema/decisión, nombre descriptivo (con fecha si aplica)
- Frontmatter obligatorio:
  ---
  name: nombre-descriptivo
  description: una línea — qué contiene este archivo
  type: project
  updated: YYYY-MM-DD
  ---
- Si el archivo ya existe, actualízalo en lugar de crear uno nuevo

REGLAS DE ESCRITURA (para controlar el crecimiento):
- Una decisión = máximo 3 líneas: qué, por qué, cuándo revisar
- Sin frases de relleno ('se decidió que', 'es importante notar')
- Usa listas en lugar de párrafos
- Nunca repitas información que ya está en el archivo

Máximo 4 archivos creados o actualizados por sesión." \
    2>>"$HOME/.claude/hooks/session-consolidate.log" || true

# ── Promoción a wiki del proyecto ──────────────────────────────────────────────
# Si el proyecto tiene docs/src/wiki/, promueve decisiones permanentes al wiki.
if [ -d "docs/src/wiki" ] && [ -f "docs/src/wiki/index.md" ]; then
    claude --print \
        --model claude-haiku-4-5-20251001 \
        --max-turns 5 \
        "Eres un agente de promoción de conocimiento al wiki del proyecto.

WIKI DEL PROYECTO: docs/src/wiki/

TU TAREA:
1. Lee los archivos recién actualizados en $MEM_DIR
2. Lee docs/src/wiki/index.md para conocer las páginas existentes
3. Evalúa qué información de memory/ es PERMANENTE y merece estar en el wiki

CRITERIOS DE PROMOCIÓN (solo promover si cumple):
- Decisiones de arquitectura confirmadas (no tentativas)
- Reglas de dominio/negocio que no cambiarán entre sesiones
- Convenciones de código o naming adoptadas por el equipo
- Integraciones configuradas y funcionando
- NO promover: workarounds temporales, bugs en progreso, notas de sesión

OPERACIONES:
- Actualizar páginas existentes del wiki si la info es relevante
- Crear nuevas páginas solo para conceptos/entidades importantes
- Actualizar docs/src/wiki/glossary.md con términos nuevos
- Actualizar docs/src/wiki/index.md con páginas nuevas
- Añadir entrada en docs/src/wiki/log.md con fecha y resumen

FORMATO: Respetar el frontmatter VitePress existente en cada página.
Si no hay nada que promover, NO escribir nada. Es preferible no actuar a contaminar el wiki.

Máximo 3 páginas actualizadas o creadas." \
        2>>"$HOME/.claude/hooks/session-consolidate.log" || true
fi

# ── Graphify: instalar el git hook si aún no está (idempotente) ────────────────
# No reconstruye nada aquí — el propio hook post-commit de Graphify ya se
# encarga del grafo en cada commit. Esto solo asegura que el hook exista.
if command -v graphify >/dev/null 2>&1 && [ -d ".git" ]; then
    if graphify hook status 2>/dev/null | grep -q "not installed"; then
        graphify hook install >>"$HOME/.claude/hooks/session-consolidate.log" 2>&1 || true
    fi
fi

# ── MemPalace: indexar semánticamente lo que cambió en la sesión ───────────────
# 100% local (embeddings locales, sin LLM/API en modo 'projects'). Si el
# proyecto no tiene mempalace.yaml todavía, se inicializa primero (heurísticas
# only, --no-llm — nunca manda contenido a un LLM externo).
if command -v mempalace >/dev/null 2>&1; then
    if [ ! -f "mempalace.yaml" ]; then
        mempalace init . --yes --no-llm >>"$HOME/.claude/hooks/mempalace-mine.log" 2>&1 || true
    fi
    mempalace mine "$(pwd)" >>"$HOME/.claude/hooks/mempalace-mine.log" 2>&1 || true
fi

# Rotar logs si superan 200 líneas (evita crecimiento indefinido)
for LOG in "$HOME/.claude/hooks/session-consolidate.log" "$HOME/.claude/hooks/mempalace-mine.log"; do
    if [ -f "$LOG" ] && [ "$(wc -l < "$LOG")" -gt 200 ]; then
        tail -100 "$LOG" > "$LOG.tmp" && mv "$LOG.tmp" "$LOG"
    fi
done
