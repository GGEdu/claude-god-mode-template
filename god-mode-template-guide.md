# 🧠 Guía: Claude Code God Mode Template
## Construcción paso a paso del boilerplate maestro

> **Tiempo estimado:** 45–90 minutos la primera vez  
> **Requisitos previos:** Claude Code instalado, cuenta Anthropic (Pro/Max/API), Node.js 18+, Git, Python 3.10+

---

## Índice

1. [Prerequisitos y verificación](#1-prerequisitos-y-verificación)
2. [Crear la estructura base del repositorio](#2-crear-la-estructura-base-del-repositorio)
3. [Configurar el núcleo: settings.json y CLAUDE.md](#3-configurar-el-núcleo-settingsjson-y-claudemd)
4. [Instalar ECC (Everything Claude Code)](#4-instalar-ecc-everything-claude-code)
5. [Configurar los Git Hooks defensivos](#5-configurar-los-git-hooks-defensivos)
6. [Instalar arscontexta (Sistema de Memoria)](#6-instalar-arscontexta-sistema-de-memoria)
7. [Configurar la pila de MCPs](#7-configurar-la-pila-de-mcps)
8. [Añadir la Skill Jedi Review](#8-añadir-la-skill-jedi-review)
9. [Configurar el sistema de memoria AutoDream](#9-configurar-el-sistema-de-memoria-autodream)
10. [Crear el Makefile de control](#10-crear-el-makefile-de-control)
11. [Flujo de uso: clonar para nuevo proyecto](#11-flujo-de-uso-clonar-para-nuevo-proyecto)
12. [Referencia rápida de comandos](#12-referencia-rápida-de-comandos)

---

## 1. Prerequisitos y verificación

Antes de empezar, verifica que tienes todo instalado:

```bash
# Verifica Claude Code
claude --version
# Necesitas v2.1.0 o superior

# Verifica Node.js
node --version
# Necesitas v18 o superior

# Verifica Python
python3 --version
# Necesitas v3.10 o superior

# Verifica Git
git --version

# Verifica uv (gestor de paquetes Python moderno, necesario para NotebookLM)
uv --version
# Si no lo tienes: curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Si Claude Code no está instalado:**
```bash
npm install -g @anthropic-ai/claude-code
```

---

## 2. Crear la estructura base del repositorio

```bash
# Crea la carpeta del template maestro
mkdir claude-god-mode-template
cd claude-god-mode-template
git init

# Crea la estructura de directorios completa
mkdir -p .claude/rules/common
mkdir -p .claude/rules/typescript
mkdir -p .claude/rules/python
mkdir -p .claude/rules/golang
mkdir -p agents
mkdir -p skills/jedi-review
mkdir -p contexts
mkdir -p examples
mkdir -p .githooks
mkdir -p src
mkdir -p tests
mkdir -p docs
```

Crea el `.gitignore` base:

```bash
cat > .gitignore << 'EOF'
# Secretos — NUNCA subir
.env
.env.*
secrets/
*.key
*.pem

# Settings locales (preferencias personales)
.claude/settings.local.json

# Dependencias
node_modules/
__pycache__/
*.pyc
.venv/

# Datos de arscontexta (se generan localmente)
.arscontexta/

# Datos de NotebookLM MCP
~/.notebooklm-mcp-cli/

# Outputs temporales
output/
dist/
build/

# OS
.DS_Store
Thumbs.db
EOF
```

---

## 3. Configurar el núcleo: settings.json y CLAUDE.md

### 3.1 Crear el `settings.json` del proyecto

```bash
cat > .claude/settings.json << 'EOF'
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "model": "sonnet",
  "env": {
    "MAX_THINKING_TOKENS": "10000",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "50",
    "CLAUDE_CODE_SUBAGENT_MODEL": "haiku"
  },
  "permissions": {
    "allow": [
      "Bash(npm run lint)",
      "Bash(npm run test*)",
      "Bash(npm run build)",
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(git status)",
      "Bash(git diff *)",
      "Bash(git log *)",
      "Bash(python -m pytest*)",
      "Bash(ruff check*)",
      "Bash(ruff format*)"
    ],
    "deny": [
      "Read(./.env)",
      "Read(./.env.*)",
      "Read(./secrets/**)",
      "Bash(git push --force*)",
      "Bash(rm -rf /*)"
    ]
  },
  "disabledMcpjsonServers": ["notebooklm", "n8n-claw"],
  "enabledMcpjsonServers": ["github", "memory"]
}
EOF
```

### 3.2 Crear el `settings.local.json` (para preferencias personales, no se sube a git)

```bash
cat > .claude/settings.local.json << 'EOF'
{
  "theme": "dark",
  "outputStyle": "Explanatory"
}
EOF
```

### 3.3 Crear el `CLAUDE.md` maestro

Este es el cerebro del proyecto. Claude lo lee automáticamente al iniciar cada sesión:

```bash
cat > .claude/CLAUDE.md << 'EOF'
# Claude God Mode Template

## Identidad del proyecto
Este es un repositorio PLANTILLA. Su función es ser clonado para nuevos proyectos.
Cuando trabajes en este repo, estás configurando la base, no un producto final.

## Principios de Context Engineering
1. **Subagentes para exploración**: Delega la investigación a subagentes con contexto limpio. Solo devuelven resúmenes al contexto principal.
2. **Hooks, no prompts, para enforcement**: Todo lo que DEBE ejecutarse siempre (linting, tests, formato) va en un hook, no en un prompt.
3. **Estratificación de modelos**: `haiku` para exploración, `sonnet` para trabajo general, `opus` solo para arquitectura compleja.
4. **Compactar en puntos lógicos**: Usa `/compact` después de investigación, antes de implementación. Nunca en medio de un cambio.

## Comandos críticos de este proyecto
- `/plan` — Planificar cualquier feature antes de implementar
- `/jedi-review` — Panel de 3 expertos revisa el código
- `/tdd` — Enforce test-driven development
- `/code-review` — Review rápido de calidad
- `/security-scan` — Auditoría de seguridad con AgentShield
- `/learn` — Extraer patrones aprendidos en esta sesión
- `/compact` — Compactar contexto en puntos lógicos

## Stack por defecto
- **Lenguaje**: [PERSONALIZAR POR PROYECTO]
- **Framework**: [PERSONALIZAR POR PROYECTO]
- **Tests**: [PERSONALIZAR POR PROYECTO]
- **Linter**: Ruff (Python) / Biome (JS/TS)

## Convenciones
- Commits en formato Conventional Commits: `feat:`, `fix:`, `docs:`, `refactor:`
- Tests obligatorios para toda función nueva (mínimo 80% cobertura)
- No push sin pasar el pre-push hook

## Memoria del proyecto (AutoDream)
El archivo `memory.mmd` en esta carpeta contiene el estado persistente del proyecto.
Si notas que se está volviendo muy largo (>500 líneas), ejecuta el subagente de consolidación:
"Consolida y optimiza el archivo .claude/memory.mmd eliminando información redundante y resumiendo el historial antiguo"
EOF
```

### 3.4 Crear el `memory.mmd` inicial

```bash
cat > .claude/memory.mmd << 'EOF'
# Project Memory

## Estado actual
- Fase: Inicialización del template
- Fecha inicio: [FECHA]

## Decisiones de arquitectura
- [Se irán registrando aquí automáticamente]

## Patrones aprendidos
- [Se irán registrando aquí automáticamente]

## Problemas conocidos
- [Se irán registrando aquí]
EOF
```

---

## 4. Instalar ECC (Everything Claude Code)

ECC es el motor central. Se instala como plugin de Claude Code y te da 125 skills, 28 agentes, 60 comandos y todos los hooks de golpe.

### 4.1 Instalar el plugin (dentro de una sesión de Claude Code)

Abre Claude Code en la carpeta del template y ejecuta:

```
/plugin marketplace add affaan-m/everything-claude-code
/plugin install everything-claude-code@everything-claude-code
```

### 4.2 Instalar las Rules manualmente (el plugin no las distribuye automáticamente)

```bash
# Clona el repositorio de ECC
git clone https://github.com/affaan-m/everything-claude-code.git /tmp/ecc

# Copia las rules comunes (siempre necesarias)
cp -r /tmp/ecc/rules/common/* .claude/rules/common/

# Copia las rules del stack que uses (elige UNO o varios)
cp -r /tmp/ecc/rules/typescript/* .claude/rules/typescript/
# cp -r /tmp/ecc/rules/python/* .claude/rules/python/
# cp -r /tmp/ecc/rules/golang/* .claude/rules/golang/

# Copia los ejemplos de CLAUDE.md por stack para referencia
cp /tmp/ecc/examples/saas-nextjs-CLAUDE.md examples/
cp /tmp/ecc/examples/go-microservice-CLAUDE.md examples/
cp /tmp/ecc/examples/django-api-CLAUDE.md examples/

# Copia los contexts de modo (dev, review, research)
cp /tmp/ecc/contexts/*.md contexts/

# Copia la configuración base de MCPs de ECC
cp /tmp/ecc/mcp-configs/mcp-servers.json .mcp-servers-reference.json

echo "✅ ECC rules instaladas"
```

### 4.3 Configurar el `settings.json` global (se aplica a todos tus proyectos)

```bash
# Crea o actualiza el settings global de Claude Code
mkdir -p ~/.claude
cat >> ~/.claude/settings.json << 'EOF'
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "model": "sonnet",
  "env": {
    "MAX_THINKING_TOKENS": "10000",
    "CLAUDE_AUTOCOMPACT_PCT_OVERRIDE": "50",
    "CLAUDE_CODE_SUBAGENT_MODEL": "haiku"
  }
}
EOF
```

### 4.4 Verificar la instalación

Dentro de Claude Code:
```
/plugin list everything-claude-code@everything-claude-code
```
Deberías ver 60+ comandos listados.

---

## 5. Configurar los Git Hooks defensivos

Estos hooks son la capa defensiva contra alucinaciones de código. Se ejecutan automáticamente antes de cada commit y push.

### 5.1 Crear el pre-commit (linting automático)

```bash
cat > .githooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook: Linting automático
# Se ejecuta ANTES de cada git commit

echo "🔍 Ejecutando pre-commit hooks..."

# Detecta el tipo de proyecto
if [ -f "package.json" ]; then
  echo "📦 Proyecto Node.js detectado — ejecutando Biome..."
  if command -v biome &> /dev/null; then
    npx biome check --apply .
    if [ $? -ne 0 ]; then
      echo "❌ Biome encontró errores. Corrígelos antes de hacer commit."
      exit 1
    fi
  elif command -v eslint &> /dev/null; then
    npx eslint . --fix
  fi
fi

if [ -f "pyproject.toml" ] || [ -f "requirements.txt" ]; then
  echo "🐍 Proyecto Python detectado — ejecutando Ruff..."
  if command -v ruff &> /dev/null; then
    ruff check . --fix
    ruff format .
    if [ $? -ne 0 ]; then
      echo "❌ Ruff encontró errores. Corrígelos antes de hacer commit."
      exit 1
    fi
  fi
fi

# Bloquear commits con secrets obvios
echo "🔐 Verificando que no hay secrets en los cambios..."
if git diff --cached | grep -E "(sk-|ghp_|AKIA|api_key\s*=\s*['\"][^'\"]{20})" --quiet; then
  echo "❌ ALERTA: Posible secret detectado en los cambios. Revisa antes de commitear."
  exit 1
fi

echo "✅ Pre-commit hooks pasados correctamente"
EOF

chmod +x .githooks/pre-commit
```

### 5.2 Crear el pre-push (tests obligatorios)

```bash
cat > .githooks/pre-push << 'EOF'
#!/bin/bash
# Pre-push hook: Tests obligatorios
# Se ejecuta ANTES de cada git push

echo "🧪 Ejecutando tests antes de push..."

# Python con pytest
if [ -f "pyproject.toml" ] || [ -f "pytest.ini" ]; then
  echo "🐍 Ejecutando pytest..."
  python -m pytest tests/ -x -q
  if [ $? -ne 0 ]; then
    echo "❌ Tests fallaron. No se puede hacer push hasta que pasen todos los tests."
    echo "💡 Para saltarte esto en emergencias: git push --no-verify"
    exit 1
  fi
fi

# Node.js con npm test
if [ -f "package.json" ] && grep -q '"test"' package.json; then
  echo "📦 Ejecutando npm test..."
  npm test -- --passWithNoTests
  if [ $? -ne 0 ]; then
    echo "❌ Tests fallaron. No se puede hacer push hasta que pasen todos los tests."
    echo "💡 Para saltarte esto en emergencias: git push --no-verify"
    exit 1
  fi
fi

echo "✅ Todos los tests pasaron. Push autorizado."
EOF

chmod +x .githooks/pre-push
```

### 5.3 Configurar el repositorio para usar los hooks

```bash
# Configura git para usar la carpeta .githooks en lugar de .git/hooks
git config core.hooksPath .githooks

# Verifica la configuración
git config core.hooksPath
# Debe mostrar: .githooks
```

### 5.4 Añadir nota de instalación al README

```bash
cat >> README.md << 'EOF'

## Instalación de hooks (obligatorio al clonar)

```bash
git config core.hooksPath .githooks
```

Esto activa los hooks de pre-commit (linting) y pre-push (tests).
Para saltarlos en emergencias: `git commit --no-verify` o `git push --no-verify`
EOF
```

---

## 6. Instalar arscontexta (Sistema de Memoria)

arscontexta genera tu segundo cerebro personalizado. Es un proceso de una sola vez (~20 minutos).

### 6.1 Instalar el plugin

Dentro de Claude Code:
```
/plugin marketplace add agenticnotetaking/arscontexta
/plugin install arscontexta@agenticnotetaking
```

Reinicia Claude Code después de la instalación.

### 6.2 Ejecutar el setup (una sola vez)

```
/arscontexta:setup
```

El motor te hará 2–4 preguntas sobre tu dominio de trabajo y cómo piensas. Responde con detalle. Este proceso:
- Lee 249 claims de investigación sobre gestión del conocimiento
- Deriva tu arquitectura cognitiva personalizada
- Genera todos los archivos, carpetas, hooks y skills adaptadas a ti
- Tarda ~20 minutos y consume tokens, pero es una inversión única

Después del setup, **reinicia Claude Code de nuevo** para que los hooks generados se activen.

### 6.3 Verificar el sistema generado

```
/arscontexta:help
/arscontexta:health
```

---

## 7. Configurar la pila de MCPs

Los MCPs se configuran en `.mcp.json` (NO en `settings.json`). Todos los no esenciales arrancan desactivados.

### 7.1 Crear el `.mcp.json` del proyecto

```bash
cat > .mcp.json << 'EOF'
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    },
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    },
    "notebooklm": {
      "command": "notebooklm-mcp",
      "args": [],
      "disabled": true,
      "description": "Actívalo para investigación con documentación. Consume 35 herramientas del contexto."
    },
    "n8n-claw": {
      "command": "npx",
      "args": ["-y", "@n8n/mcp-server"],
      "disabled": true,
      "description": "Actívalo para automatizaciones con n8n."
    }
  }
}
EOF
```

### 7.2 Instalar NotebookLM MCP (desactivado por defecto, listo para usar)

```bash
# Instala el cliente CLI de NotebookLM MCP
pip install notebooklm-mcp-cli --break-system-packages
# o con uv (recomendado):
uv tool install notebooklm-mcp-cli

# Configura el MCP para Claude Code automáticamente
nlm setup add claude-code

# Autentica con tu cuenta de Google (abre el navegador)
nlm auth login

# Verifica que funciona
nlm doctor
```

> ⚠️ **Recuerda:** NotebookLM está `disabled: true` en `.mcp.json`. Para activarlo en un proyecto específico, cambia `"disabled": false` en ese proyecto. Tiene 35 herramientas y consume mucho contexto.

### 7.3 Crear el `.mcp.json` global (MCPs disponibles en todos tus proyectos)

```bash
cat > ~/.mcp.json << 'EOF'
{
  "mcpServers": {
    "memory": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-memory"]
    }
  }
}
EOF
```

---

## 8. Añadir la Skill Jedi Review

Esta skill lanza 3 subagentes expertos en paralelo para revisar tu código desde tres perspectivas distintas. Inspirada directamente en el episodio de Codemancers.

```bash
cat > skills/jedi-review/SKILL.md << 'EOF'
---
name: jedi-review
description: "Panel de 3 expertos que revisan tu código en paralelo. Invocar con /jedi-review o cuando el usuario pide una revisión profunda de código. Los expertos son: Kent Beck (simplicidad y TDD), Martin Fowler (arquitectura y refactoring), Mike Acton (rendimiento y datos)."
---

# Jedi Review — Panel de Expertos

Cuando se invoque esta skill, lanza 3 subagentes en paralelo, cada uno con una perspectiva experta diferente. Cada subagente lee el código indicado y produce su análisis independiente.

## Subagente 1: Kent Beck — Simplicidad y TDD

**Perspectiva:** ¿Es este código lo más simple posible? ¿Tiene tests? ¿Los tests son los primeros ciudadanos?

Preguntas que debes hacerte:
- ¿Hay código que se podría eliminar sin perder funcionalidad?
- ¿Los tests cubren los casos de borde importantes?
- ¿El código comunica la intención claramente?
- ¿Hay duplicación que se podría extraer?

Formato de respuesta:
```
[KENT BECK]
✅ Fortalezas: ...
⚠️ Simplificar: ...
❌ Falta: ...
🔧 Sugerencia concreta: ...
```

## Subagente 2: Martin Fowler — Arquitectura y Refactoring

**Perspectiva:** ¿Las responsabilidades están bien separadas? ¿Hay code smells? ¿La arquitectura escala?

Preguntas que debes hacerte:
- ¿Cada clase/función tiene una única responsabilidad?
- ¿Hay acoplamiento que debería ser inyectado?
- ¿Los nombres comunican el dominio del negocio?
- ¿Hay oportunidades de extracción o consolidación?

Formato de respuesta:
```
[MARTIN FOWLER]
✅ Fortalezas: ...
⚠️ Code smells: ...
❌ Problemas: ...
🔧 Refactoring sugerido: ...
```

## Subagente 3: Mike Acton — Rendimiento y Datos

**Perspectiva:** ¿Cómo fluyen los datos? ¿Hay ineficiencias de memoria o CPU? ¿Las estructuras de datos son las correctas?

Preguntas que debes hacerte:
- ¿Las estructuras de datos son apropiadas para el patrón de acceso?
- ¿Hay llamadas innecesarias a la base de datos o la red?
- ¿Hay allocations que se podrían evitar?
- ¿El código hace suposiciones incorrectas sobre el rendimiento?

Formato de respuesta:
```
[MIKE ACTON]
✅ Fortalezas: ...
⚠️ Ineficiencias: ...
❌ Problemas: ...
🔧 Optimización sugerida: ...
```

## Síntesis final

Después de los 3 análisis, produce un resumen ejecutivo:
- **Veredicto general:** [A/B/C/D] con justificación
- **Top 3 acciones prioritarias** (ordenadas por impacto)
- **Estimación de deuda técnica:** [baja/media/alta]
EOF
```

---

## 9. Configurar el sistema de memoria AutoDream

AutoDream es la convención de la comunidad para consolidar el archivo `memory.mmd` automáticamente. Se configura como un hook de Claude Code que se activa al final de cada sesión.

### 9.1 Crear el hook de memoria

```bash
mkdir -p .claude/hooks

cat > .claude/hooks/session-memory.sh << 'EOF'
#!/bin/bash
# Hook de memoria: se ejecuta al final de cada sesión
# Consolida y actualiza el archivo memory.mmd

MEMORY_FILE=".claude/memory.mmd"
MAX_LINES=400

# Si el archivo de memoria supera 400 líneas, lanza consolidación
if [ -f "$MEMORY_FILE" ]; then
  LINE_COUNT=$(wc -l < "$MEMORY_FILE")
  if [ "$LINE_COUNT" -gt "$MAX_LINES" ]; then
    echo "⚠️ memory.mmd tiene $LINE_COUNT líneas (máximo recomendado: $MAX_LINES)"
    echo "💡 Considera ejecutar el subagente de consolidación de memoria"
  fi
fi
EOF

chmod +x .claude/hooks/session-memory.sh
```

### 9.2 Añadir el hook al settings.json

```bash
# Actualiza el settings.json para incluir el hook
python3 << 'EOF'
import json

with open('.claude/settings.json', 'r') as f:
    settings = json.load(f)

settings['hooks'] = {
    "Stop": [
        {
            "matcher": "",
            "hooks": [
                {
                    "type": "command",
                    "command": "bash .claude/hooks/session-memory.sh"
                }
            ]
        }
    ]
}

with open('.claude/settings.json', 'w') as f:
    json.dump(settings, f, indent=2, ensure_ascii=False)

print("✅ Hook de memoria configurado")
EOF
```

### 9.3 Crear el subagente AutoDream de consolidación

```bash
cat > agents/memory-consolidator.md << 'EOF'
---
name: memory-consolidator
description: "Subagente que consolida y optimiza el archivo .claude/memory.mmd cuando está demasiado largo. Invocar cuando memory.mmd supere 400 líneas o cuando el usuario pida consolidar la memoria del proyecto."
tools: ["Read", "Write"]
model: sonnet
---

Eres un subagente especializado en gestión de memoria de proyectos.

Tu tarea es leer el archivo `.claude/memory.mmd` y producir una versión consolidada que:

1. **Elimina duplicados**: Si la misma información aparece varias veces, mantén solo la más reciente y completa.
2. **Resume el historial antiguo**: Las entradas de más de 7 días se comprimen en un resumen de 1–2 líneas.
3. **Preserva lo crítico**: Las decisiones de arquitectura, los problemas conocidos y los patrones aprendidos NUNCA se eliminan, solo se reorganizan.
4. **Mantiene la estructura**: El formato de secciones (## Estado actual, ## Decisiones de arquitectura, etc.) debe mantenerse idéntico.
5. **No excede 300 líneas**: El resultado final debe ser más compacto que el original.

Escribe el resultado directamente sobre el archivo `.claude/memory.mmd`.
Reporta cuántas líneas se redujeron.
EOF
```

---

## 10. Crear el Makefile de control

El Makefile es el panel de control del template. Permite activar/desactivar módulos con un solo comando.

```bash
cat > Makefile << 'EOF'
# ============================================================
# Claude God Mode Template — Panel de Control
# ============================================================

.PHONY: help setup activate-notebooklm deactivate-notebooklm \
        activate-n8n deactivate-n8n hooks-install hooks-uninstall \
        memory-status memory-consolidate new-project check

help: ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# ---- SETUP ----

setup: ## Configuración inicial completa (ejecutar una sola vez)
	@echo "🚀 Iniciando configuración del God Mode Template..."
	git config core.hooksPath .githooks
	@echo "✅ Git hooks configurados"
	@echo ""
	@echo "📋 Pasos siguientes (ejecutar dentro de Claude Code):"
	@echo "   1. /plugin marketplace add affaan-m/everything-claude-code"
	@echo "   2. /plugin install everything-claude-code@everything-claude-code"
	@echo "   3. /plugin marketplace add agenticnotetaking/arscontexta"
	@echo "   4. /plugin install arscontexta@agenticnotetaking"
	@echo "   5. Reiniciar Claude Code"
	@echo "   6. /arscontexta:setup"

# ---- MCPs ----

activate-notebooklm: ## Activa el MCP de NotebookLM para este proyecto
	@python3 -c "\
import json; \
f = open('.mcp.json'); d = json.load(f); f.close(); \
d['mcpServers']['notebooklm']['disabled'] = False; \
f = open('.mcp.json', 'w'); json.dump(d, f, indent=2); f.close(); \
print('✅ NotebookLM MCP activado. Reinicia Claude Code.')"

deactivate-notebooklm: ## Desactiva el MCP de NotebookLM (ahorra ~35 herramientas de contexto)
	@python3 -c "\
import json; \
f = open('.mcp.json'); d = json.load(f); f.close(); \
d['mcpServers']['notebooklm']['disabled'] = True; \
f = open('.mcp.json', 'w'); json.dump(d, f, indent=2); f.close(); \
print('✅ NotebookLM MCP desactivado.')"

activate-n8n: ## Activa el MCP de n8n para automatizaciones
	@python3 -c "\
import json; \
f = open('.mcp.json'); d = json.load(f); f.close(); \
d['mcpServers']['n8n-claw']['disabled'] = False; \
f = open('.mcp.json', 'w'); json.dump(d, f, indent=2); f.close(); \
print('✅ n8n MCP activado. Reinicia Claude Code.')"

deactivate-n8n: ## Desactiva el MCP de n8n
	@python3 -c "\
import json; \
f = open('.mcp.json'); d = json.load(f); f.close(); \
d['mcpServers']['n8n-claw']['disabled'] = True; \
f = open('.mcp.json', 'w'); json.dump(d, f, indent=2); f.close(); \
print('✅ n8n MCP desactivado.')"

# ---- HOOKS ----

hooks-install: ## Instala los git hooks en este repositorio
	git config core.hooksPath .githooks
	@echo "✅ Git hooks activados"

hooks-uninstall: ## Desactiva los git hooks (modo relajado)
	git config --unset core.hooksPath
	@echo "✅ Git hooks desactivados. Úsalos de nuevo con: make hooks-install"

# ---- MEMORIA ----

memory-status: ## Muestra el estado del archivo de memoria
	@echo "📊 Estado de memory.mmd:"
	@if [ -f ".claude/memory.mmd" ]; then \
		LINE_COUNT=$$(wc -l < ".claude/memory.mmd"); \
		echo "   Líneas: $$LINE_COUNT"; \
		if [ "$$LINE_COUNT" -gt 400 ]; then \
			echo "   ⚠️  AVISO: Demasiado largo. Ejecuta: make memory-consolidate"; \
		else \
			echo "   ✅ Tamaño óptimo"; \
		fi; \
	else \
		echo "   ❌ Archivo no encontrado"; \
	fi

memory-consolidate: ## Recuerda cómo consolidar la memoria (ejecutar dentro de Claude Code)
	@echo "💡 Para consolidar la memoria, ejecuta dentro de Claude Code:"
	@echo '   "Usa el agente memory-consolidator para consolidar .claude/memory.mmd"'

# ---- NUEVO PROYECTO ----

new-project: ## Instrucciones para crear un nuevo proyecto desde este template
	@echo "📋 Para crear un nuevo proyecto desde este template:"
	@echo ""
	@echo "   git clone <ruta-de-este-template> mi-nuevo-proyecto"
	@echo "   cd mi-nuevo-proyecto"
	@echo "   make setup"
	@echo ""
	@echo "Después, personaliza:"
	@echo "   - .claude/CLAUDE.md  (stack y convenciones del proyecto)"
	@echo "   - .mcp.json          (activa solo los MCPs que necesitas)"
	@echo "   - .gitignore         (añade los patrones de tu stack)"

# ---- VERIFICACIÓN ----

check: ## Verifica que todo está correctamente configurado
	@echo "🔍 Verificando configuración..."
	@echo ""
	@echo "Git hooks:"
	@git config core.hooksPath && echo "  ✅ Configurados" || echo "  ❌ Ejecuta: make hooks-install"
	@echo ""
	@echo "Archivos críticos:"
	@[ -f ".claude/settings.json" ] && echo "  ✅ .claude/settings.json" || echo "  ❌ Falta .claude/settings.json"
	@[ -f ".claude/CLAUDE.md" ] && echo "  ✅ .claude/CLAUDE.md" || echo "  ❌ Falta .claude/CLAUDE.md"
	@[ -f ".claude/memory.mmd" ] && echo "  ✅ .claude/memory.mmd" || echo "  ❌ Falta .claude/memory.mmd"
	@[ -f ".mcp.json" ] && echo "  ✅ .mcp.json" || echo "  ❌ Falta .mcp.json"
	@echo ""
	@echo "MCP de NotebookLM:"
	@command -v notebooklm-mcp &> /dev/null && echo "  ✅ Instalado" || echo "  ❌ Ejecuta: pip install notebooklm-mcp-cli"
	@echo ""
	@make memory-status
EOF
```

---

## 11. Flujo de uso: clonar para nuevo proyecto

Una vez que el template esté completo, este es el proceso para cada proyecto nuevo.

### 11.1 Clonar el template

```bash
# Clona el template en un nuevo proyecto
git clone /ruta/al/claude-god-mode-template mi-nuevo-proyecto
cd mi-nuevo-proyecto

# Desconecta del origin del template y prepara para el nuevo repo
git remote remove origin
git remote add origin https://github.com/tuusuario/mi-nuevo-proyecto.git

# Configura los hooks
make setup
```

### 11.2 Personalizar para el proyecto

Edita `.claude/CLAUDE.md` y reemplaza las secciones marcadas con `[PERSONALIZAR]`:

```markdown
## Stack por defecto
- **Lenguaje**: TypeScript
- **Framework**: Next.js 15 con App Router
- **Tests**: Vitest + Playwright para E2E
- **Linter**: Biome
- **DB**: PostgreSQL con Prisma
```

### 11.3 Decidir qué MCPs necesitas

```bash
# Si el proyecto requiere investigar documentación externa:
make activate-notebooklm

# Si el proyecto tiene automatizaciones con n8n:
make activate-n8n

# Siempre empieza con todo desactivado y activa según necesidad
```

### 11.4 Verificar que todo funciona

```bash
make check
```

### 11.5 Primer commit

```bash
git add .
git commit -m "feat: inicializar proyecto desde god-mode-template"
# El pre-commit hook se ejecutará automáticamente
```

---

## 12. Referencia rápida de comandos

### Comandos del día a día (dentro de Claude Code)

| Comando | Cuándo usarlo |
|---|---|
| `/plan "descripción"` | Antes de implementar cualquier feature |
| `/jedi-review` | Cuando quieras revisión profunda del código |
| `/tdd` | Para trabajar con test-driven development |
| `/code-review` | Review rápido de los últimos cambios |
| `/security-scan` | Antes de hacer un release |
| `/learn` | Al final de una sesión productiva, para extraer patrones |
| `/compact` | Después de investigar, antes de implementar |
| `/model opus` | Para problemas de arquitectura compleja |
| `/model sonnet` | Para trabajo general (default) |
| `/cost` | Para monitorear el gasto de tokens en la sesión |

### Comandos de mantenimiento del template (terminal)

| Comando | Efecto |
|---|---|
| `make check` | Verifica que todo está bien configurado |
| `make memory-status` | Muestra el estado del archivo de memoria |
| `make activate-notebooklm` | Activa NotebookLM MCP para el proyecto actual |
| `make deactivate-notebooklm` | Desactiva NotebookLM (ahorra contexto) |
| `make hooks-install` | Activa los git hooks |
| `make hooks-uninstall` | Desactiva los git hooks |
| `make new-project` | Instrucciones para clonar el template |

### Estructura final del repositorio

```
claude-god-mode-template/
├── .claude/
│   ├── settings.json          ← Control central (modelo, permisos, tokens)
│   ├── settings.local.json    ← Preferencias personales (en .gitignore)
│   ├── CLAUDE.md              ← Cerebro del proyecto (Claude lo lee al iniciar)
│   ├── memory.mmd             ← Estado persistente del proyecto
│   ├── hooks/
│   │   └── session-memory.sh  ← Hook que vigila el tamaño de la memoria
│   └── rules/
│       ├── common/            ← Reglas universales de ECC
│       └── typescript/        ← Reglas de stack (o python/, golang/)
├── .mcp.json                  ← MCPs del proyecto (aquí funcionan realmente)
├── .githooks/
│   ├── pre-commit             ← Linting automático antes de commit
│   └── pre-push               ← Tests obligatorios antes de push
├── agents/
│   └── memory-consolidator.md ← Subagente AutoDream
├── skills/
│   └── jedi-review/
│       └── SKILL.md           ← Panel de 3 expertos
├── contexts/
│   ├── dev.md                 ← Contexto modo desarrollo
│   ├── review.md              ← Contexto modo revisión
│   └── research.md            ← Contexto modo investigación
├── examples/
│   ├── saas-nextjs-CLAUDE.md  ← CLAUDE.md de referencia para Next.js
│   ├── django-api-CLAUDE.md   ← CLAUDE.md de referencia para Django
│   └── skill-template/        ← Plantilla para crear skills propias
├── src/                       ← Tu código real
├── tests/
├── .env.example               ← Variables necesarias (sin valores reales)
├── .gitignore
├── Makefile                   ← Panel de control del template
└── README.md
```

---

## Notas finales

**Sobre el consumo de tokens:** Con `model: sonnet`, `MAX_THINKING_TOKENS: 10000` y `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE: 50`, el coste por sesión se reduce aproximadamente un 70% respecto a los valores por defecto. Cambia a opus solo para decisiones de arquitectura importantes con `/model opus`.

**Sobre los MCPs:** Cada servidor MCP carga sus herramientas en el contexto. NotebookLM tiene 35 herramientas. Mantener más de 10 MCPs activos simultáneamente puede reducir tu ventana de contexto de 200k a ~70k tokens. Activa solo lo que estés usando.

**Sobre arscontexta:** El setup inicial es costoso en tokens (es una inversión única). Después del setup, el sistema genera hooks automáticos que persisten el contexto sin coste adicional. Trátalo como la configuración de tu entorno de trabajo, no como una tarea repetitiva.

**Sobre la Jedi Review:** Úsala para código que importa, no para scripts descartables. Cada invocación lanza 3 subagentes con contexto propio — es potente pero consume tokens proporcionales.
