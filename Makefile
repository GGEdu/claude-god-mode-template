# ============================================================
# Claude God Mode Template — Panel de Control
# ============================================================

.PHONY: help setup install dev-stack init-stack init-project list-stacks list-domains list-layers list-unused-skills activate-notebooklm deactivate-notebooklm \
        activate-n8n deactivate-n8n hooks-install hooks-uninstall \
        new-project load-project analyze-project setup-project check \
        triggers-setup triggers-list setup-labels workflows-status \
        test test-quick

GLOBAL_DIR := $(HOME)/.claude

help: ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

# ---- SETUP ----

# setup  → para contribuidores del template (git hooks + plugin ECC)
# install → para usuarios del template (copia a ~/.claude/ en su máquina)
# Flujo normal de usuario: make install  (setup no es necesario)
# Flujo contribuidor:      make setup && make install

setup: ## Para contribuidores: configura git hooks + plugin ECC en Claude Code
	@echo "🚀 Configurando entorno de desarrollo del template..."
	git config core.hooksPath .githooks
	@echo "✅ Git hooks configurados (.githooks/)"
	@echo ""
	@echo "📋 Instala el plugin ECC dentro de Claude Code:"
	@echo "   1. /plugin marketplace add affaan-m/everything-claude-code"
	@echo "   2. /plugin install everything-claude-code@everything-claude-code"
	@echo "   3. Reiniciar Claude Code"
	@echo ""
	@echo "Luego ejecuta 'make install' para instalar globalmente en ~/.claude/"

install: ## Instala config global en ~/.claude/ (una vez por maquina)
	@echo "Instalando Claude god-mode en $(GLOBAL_DIR)..."
	@mkdir -p $(GLOBAL_DIR)/rules/common $(GLOBAL_DIR)/agents $(GLOBAL_DIR)/skills $(GLOBAL_DIR)/hooks
	@cp rules/* $(GLOBAL_DIR)/rules/common/
	@echo "  ✅ Reglas comunes instaladas"
	@python3 ops/install-global.py "$(GLOBAL_DIR)"
	@cp hooks/session-consolidate.sh $(GLOBAL_DIR)/hooks/session-consolidate.sh
	@chmod +x $(GLOBAL_DIR)/hooks/session-consolidate.sh
	@echo "  ✅ Hook de consolidacion de memoria instalado"
	@cp ops/audit-task.sh $(GLOBAL_DIR)/hooks/audit-task.sh
	@chmod +x $(GLOBAL_DIR)/hooks/audit-task.sh
	@echo "  ✅ Script de auditoria instalado"
	@if [ ! -f $(GLOBAL_DIR)/settings.json ]; then \
		cp .claude/settings.json $(GLOBAL_DIR)/settings.json; \
		echo "  ✅ settings.json instalado"; \
	else \
		echo "  ⚠️  settings.json ya existe en $(GLOBAL_DIR) — no sobreescrito"; \
		echo "     Asegurate de que incluye el Stop hook: hooks/session-consolidate.sh"; \
	fi
	@echo ""
	@echo "Instalacion global completa."
	@echo "Reinicia Claude Code para activar los cambios."
	@echo ""
	@echo "Para inicializar un proyecto: make init-project STACK=laravel PROJECT=/ruta/al/proyecto"

# ---- STACK ----

list-unused-skills: ## Lista skills que existen en skills/ pero no están referenciados en ningún stack ni domain
	@python3 -c "\
import yaml, glob, os; \
used = set(); \
stacks = [yaml.safe_load(open(f)) for f in glob.glob('stacks/*/stack.yaml')]; \
[[used.update(v.get('skills',[])) for v in d.get('agents',{}).values() if isinstance(v,dict)] for d in stacks if isinstance(d.get('agents',{}),dict)]; \
[used.update(d.get('commands',{}).keys() if isinstance(d.get('commands',{}),dict) else d.get('commands',[]) if isinstance(d.get('commands'),list) else []) for d in stacks]; \
[used.update(d.get('skills',{}).keys() if isinstance(d.get('skills',{}),dict) else []) for d in stacks]; \
domains = [yaml.safe_load(open(f)) for f in glob.glob('domains/*/domain.yaml')]; \
[[used.update(skills or []) for skills in (d.get('agent_skills',{}) or {}).values()] for d in domains]; \
[used.update((d.get('commands',{}) or {}).keys()) for d in domains]; \
all_skills = {os.path.basename(p) for p in glob.glob('skills/*') if os.path.isdir(p)}; \
unused = sorted(all_skills - used); \
print('Skills sin usar (' + str(len(unused)) + ' de ' + str(len(all_skills)) + ' totales):'); \
[print('  - ' + s) for s in unused]"

list-stacks: ## Lista los stacks disponibles
	@echo "Stacks disponibles:"
	@echo ""
	@for dir in stacks/*/; do \
		name=$$(basename $$dir); \
		desc=$$(python3 -c "import yaml; d=yaml.safe_load(open('$$dir/stack.yaml')); print(d.get('description',''))" 2>/dev/null || echo ""); \
		printf "  \033[36m%-20s\033[0m %s\n" "$$name" "$$desc"; \
	done
	@echo ""
	@echo "Uso: make dev-stack STACK=laravel"
	@echo "     make dev-stack STACK=laravel LAYERS=react"

list-domains: ## Lista los domain overlays disponibles
	@echo "Domain overlays disponibles:"
	@echo ""
	@for dir in domains/*/; do \
		name=$$(basename $$dir); \
		desc=$$(python3 -c "import yaml; d=yaml.safe_load(open('$$dir/domain.yaml')); print(d.get('description',''))" 2>/dev/null || echo ""); \
		printf "  \033[35m%-20s\033[0m %s\n" "$$name" "$$desc"; \
	done
	@echo ""
	@echo "Uso: make init-project STACK=laravel DOMAIN=healthcare PROJECT=/ruta"
	@echo "     make init-project STACK=laravel LAYERS=react PROJECT=/ruta"

list-layers: ## Lista los layers tecnicos disponibles (frontend/infra composables)
	@echo "Layers tecnicos disponibles:"
	@echo ""
	@for dir in layers/*/; do \
		[ -f "$$dir/layer.yaml" ] || continue; \
		name=$$(basename $$dir); \
		desc=$$(python3 -c "import yaml; d=yaml.safe_load(open('$$dir/layer.yaml')); print(d.get('description',''))" 2>/dev/null || echo ""); \
		printf "  \033[33m%-20s\033[0m %s\n" "$$name" "$$desc"; \
	done
	@echo ""
	@echo "Uso: make init-project STACK=python-api LAYERS=react PROJECT=/ruta"
	@echo "     make dev-stack STACK=laravel LAYERS=react"

dev-stack: ## Activa un stack en este repo para desarrollarlo (ej: make dev-stack STACK=laravel [LAYERS=react])
	$(MAKE) init-stack STACK=$(STACK) LAYERS=$(LAYERS) DOMAIN=$(DOMAIN)

init-stack: ## [deprecado] Usar dev-stack en su lugar
	@[ -n "$(STACK)" ] || (echo "❌ Indica el stack: make init-stack STACK=laravel" && exit 1)
	@[ -d "stacks/$(STACK)" ] || (echo "❌ Stack '$(STACK)' no encontrado. Usa: make list-stacks" && exit 1)
	@if [ -n "$(DOMAIN)" ] && [ ! -d "domains/$(DOMAIN)" ]; then \
		echo "❌ Domain '$(DOMAIN)' no encontrado. Usa: make list-domains"; \
		exit 1; \
	fi
	@if [ -n "$(LAYERS)" ]; then \
		for layer in $$(echo "$(LAYERS)" | tr ',' ' '); do \
			[ -d "layers/$$layer" ] || (echo "❌ Layer '$$layer' no encontrado. Usa: make list-layers" && exit 1); \
		done; \
	fi
	@echo "Inicializando stack: $(STACK)$(if $(LAYERS), + layers: $(LAYERS),)$(if $(DOMAIN), + domain: $(DOMAIN),)"
	@echo ""
	@# 1. Copiar rules del stack a .claude/rules/stack/ (siempre activas)
	@mkdir -p .claude/rules/stack
	@if [ -d "stacks/$(STACK)/rules" ]; then \
		cp stacks/$(STACK)/rules/*.md .claude/rules/stack/ 2>/dev/null || true; \
		echo "✅ Rules (siempre activas):"; \
		for f in .claude/rules/stack/*.md; do echo "   - $$f"; done; \
	fi
	@# 1b. Copiar rules de cada layer
	@if [ -n "$(LAYERS)" ]; then \
		for layer in $$(echo "$(LAYERS)" | tr ',' ' '); do \
			if [ -d "layers/$$layer/rules" ]; then \
				cp layers/$$layer/rules/*.md .claude/rules/stack/ 2>/dev/null || true; \
				echo "✅ Layer rules copiadas ($$layer)"; \
			fi; \
		done; \
	fi
	@# 1c. Copiar rules del domain si se indicó
	@if [ -n "$(DOMAIN)" ] && [ -d "domains/$(DOMAIN)/rules" ]; then \
		cp domains/$(DOMAIN)/rules/*.md .claude/rules/stack/ 2>/dev/null || true; \
		echo "✅ Domain rules copiadas"; \
	fi
	@echo ""
	@# 2. Compilar agentes con skills embebidas (.claude/agents/)
	@mkdir -p .claude/agents
	@echo "✅ Agentes compilados con skills embebidas:"
	@OVERLAY_ARGS=""; \
	if [ -n "$(LAYERS)" ]; then \
		for layer in $$(echo "$(LAYERS)" | tr ',' ' '); do \
			OVERLAY_ARGS="$$OVERLAY_ARGS layers/$$layer/layer.yaml"; \
		done; \
	fi; \
	if [ -n "$(DOMAIN)" ]; then \
		OVERLAY_ARGS="$$OVERLAY_ARGS domains/$(DOMAIN)/domain.yaml"; \
	fi; \
	python3 ops/compile-agents.py stacks/$(STACK)/stack.yaml skills agents .claude/agents $$OVERLAY_ARGS
	@echo ""
	@# 3. Activar comandos standalone (.claude/commands/)
	@mkdir -p .claude/commands
	@echo "✅ Comandos standalone activados:"
	@OVERLAY_ARGS=""; \
	if [ -n "$(LAYERS)" ]; then \
		for layer in $$(echo "$(LAYERS)" | tr ',' ' '); do \
			OVERLAY_ARGS="$$OVERLAY_ARGS layers/$$layer/layer.yaml"; \
		done; \
	fi; \
	if [ -n "$(DOMAIN)" ]; then \
		OVERLAY_ARGS="$$OVERLAY_ARGS domains/$(DOMAIN)/domain.yaml"; \
	fi; \
	python3 ops/copy-commands.py "$$PWD" stacks/$(STACK)/stack.yaml $$OVERLAY_ARGS
	@echo ""
	@# 3b. Distribuir agentes a Antigravity (.agent/skills/) y Copilot (.github/prompts/)
	@echo "✅ Agentes distribuidos a Antigravity y Copilot:"
	@python3 ops/distribute-agents.py stacks/$(STACK)/stack.yaml agents "$$PWD"
	@echo ""
	@# 4. Copiar pipeline.yaml
	@if [ -f "stacks/$(STACK)/pipeline.yaml" ]; then \
		cp stacks/$(STACK)/pipeline.yaml .claude/pipeline.yaml; \
		echo "✅ Pipeline de workflows copiado — usa /workflow para ejecutar"; \
	fi
	@# 4b. Copiar GitHub Actions workflows comunes
	@if [ -d "stacks/common/workflows" ] && [ -n "$$(ls stacks/common/workflows/*.yml 2>/dev/null)" ]; then \
		mkdir -p .github/workflows; \
		cp stacks/common/workflows/*.yml .github/workflows/; \
		echo "✅ GitHub Actions copiados a .github/workflows/ — añade ANTHROPIC_API_KEY en Settings → Secrets"; \
	fi
	@# 5. Copiar CLAUDE.md del stack + append layers + append domain
	@if [ -f "stacks/$(STACK)/CLAUDE.md" ]; then \
		cp stacks/$(STACK)/CLAUDE.md .claude/CLAUDE.md; \
		echo "✅ CLAUDE.md actualizado — edita los [PLACEHOLDER]"; \
	fi
	@if [ -n "$(LAYERS)" ]; then \
		for layer in $$(echo "$(LAYERS)" | tr ',' ' '); do \
			if [ -f "layers/$$layer/CLAUDE-append.md" ]; then \
				cat layers/$$layer/CLAUDE-append.md >> .claude/CLAUDE.md; \
				echo "✅ Layer context appended to CLAUDE.md ($$layer)"; \
			fi; \
		done; \
	fi
	@if [ -n "$(DOMAIN)" ] && [ -f "domains/$(DOMAIN)/CLAUDE-append.md" ]; then \
		cat domains/$(DOMAIN)/CLAUDE-append.md >> .claude/CLAUDE.md; \
		echo "✅ Domain context appended to CLAUDE.md"; \
	fi
	@echo ""
	@echo "Stack '$(STACK)' listo."
	@echo ""
	@echo "Reinicia Claude Code para que los agentes queden disponibles."
	@echo "Ejecuta 'make check' para verificar la configuración."

init-project: ## Inicializa un proyecto externo: make init-project STACK=laravel PROJECT=/ruta [LAYERS=react] [DOMAIN=healthcare]
	@[ -n "$(STACK)" ] || (echo "❌ Indica el stack: make init-project STACK=laravel PROJECT=/ruta" && exit 1)
	@[ -n "$(PROJECT)" ] || (echo "❌ Indica la ruta: make init-project STACK=laravel PROJECT=/ruta" && exit 1)
	@[ -d "stacks/$(STACK)" ] || (echo "❌ Stack '$(STACK)' no encontrado. Usa: make list-stacks" && exit 1)
	@if [ -n "$(DOMAIN)" ] && [ ! -d "domains/$(DOMAIN)" ]; then \
		echo "❌ Domain '$(DOMAIN)' no encontrado. Usa: make list-domains"; \
		exit 1; \
	fi
	@if [ -n "$(LAYERS)" ]; then \
		for layer in $$(echo "$(LAYERS)" | tr ',' ' '); do \
			[ -d "layers/$$layer" ] || (echo "❌ Layer '$$layer' no encontrado. Usa: make list-layers" && exit 1); \
		done; \
	fi
	@echo "Inicializando stack '$(STACK)'$(if $(LAYERS), + layers '$(LAYERS)',)$(if $(DOMAIN), + domain '$(DOMAIN)',) en $(PROJECT)..."
	@mkdir -p "$(PROJECT)/.claude/rules/stack" "$(PROJECT)/.claude/commands" "$(PROJECT)/.claude/agents" "$(PROJECT)/.claude/memory"
	@# 1. Copiar rules del stack (siempre activas)
	@if [ -d "stacks/$(STACK)/rules" ]; then \
		cp stacks/$(STACK)/rules/*.md "$(PROJECT)/.claude/rules/stack/"; \
		echo "  ✅ Stack rules copiadas a $(PROJECT)/.claude/rules/stack/"; \
	fi
	@# 1b. Copiar rules de cada layer
	@if [ -n "$(LAYERS)" ]; then \
		for layer in $$(echo "$(LAYERS)" | tr ',' ' '); do \
			if [ -d "layers/$$layer/rules" ]; then \
				cp layers/$$layer/rules/*.md "$(PROJECT)/.claude/rules/stack/"; \
				echo "  ✅ Layer rules copiadas ($$layer)"; \
			fi; \
		done; \
	fi
	@# 1c. Copiar rules del domain si se indicó
	@if [ -n "$(DOMAIN)" ] && [ -d "domains/$(DOMAIN)/rules" ]; then \
		cp domains/$(DOMAIN)/rules/*.md "$(PROJECT)/.claude/rules/stack/"; \
		echo "  ✅ Domain rules copiadas a $(PROJECT)/.claude/rules/stack/"; \
	fi
	@# 2. Compilar agentes con skills embebidas (+ layers + domain merge si aplica)
	@echo "  Compilando agentes con skills embebidas..."
	@OVERLAY_ARGS=""; \
	if [ -n "$(LAYERS)" ]; then \
		for layer in $$(echo "$(LAYERS)" | tr ',' ' '); do \
			OVERLAY_ARGS="$$OVERLAY_ARGS layers/$$layer/layer.yaml"; \
		done; \
	fi; \
	if [ -n "$(DOMAIN)" ]; then \
		OVERLAY_ARGS="$$OVERLAY_ARGS domains/$(DOMAIN)/domain.yaml"; \
	fi; \
	python3 ops/compile-agents.py stacks/$(STACK)/stack.yaml skills agents "$(PROJECT)/.claude/agents" $$OVERLAY_ARGS
	@# 3. Copiar comandos standalone al proyecto (stack + layers + domain)
	@OVERLAY_ARGS=""; \
	if [ -n "$(LAYERS)" ]; then \
		for layer in $$(echo "$(LAYERS)" | tr ',' ' '); do \
			OVERLAY_ARGS="$$OVERLAY_ARGS layers/$$layer/layer.yaml"; \
		done; \
	fi; \
	if [ -n "$(DOMAIN)" ]; then \
		OVERLAY_ARGS="$$OVERLAY_ARGS domains/$(DOMAIN)/domain.yaml"; \
	fi; \
	python3 ops/copy-commands.py "$(PROJECT)" stacks/$(STACK)/stack.yaml $$OVERLAY_ARGS
	@# 3b. Distribuir agentes a Antigravity (.agent/skills/) y Copilot (.github/prompts/)
	@echo "  Distribuyendo agentes a Antigravity y Copilot..."
	@python3 ops/distribute-agents.py stacks/$(STACK)/stack.yaml agents "$(PROJECT)"
	@# 4. Copiar pipeline.yaml
	@if [ -f "stacks/$(STACK)/pipeline.yaml" ]; then \
		cp stacks/$(STACK)/pipeline.yaml "$(PROJECT)/.claude/pipeline.yaml"; \
		echo "  ✅ Pipeline de workflows copiado — usa /workflow para ejecutar"; \
	fi
	@# 4b. Copiar GitHub Actions workflows comunes
	@if [ -d "stacks/common/workflows" ] && [ -n "$$(ls stacks/common/workflows/*.yml 2>/dev/null)" ]; then \
		mkdir -p "$(PROJECT)/.github/workflows"; \
		cp stacks/common/workflows/*.yml "$(PROJECT)/.github/workflows/"; \
		echo "  ✅ GitHub Actions copiados a .github/workflows/ — añade ANTHROPIC_API_KEY en Settings → Secrets"; \
	fi
	@# 5. Copiar audit-task.sh
	@mkdir -p "$(PROJECT)/ops"
	@cp ops/audit-task.sh "$(PROJECT)/ops/audit-task.sh"
	@chmod +x "$(PROJECT)/ops/audit-task.sh"
	@echo "  ✅ Script de auditoria copiado"
	@# 6. CLAUDE.md solo si no existe (+ layer appends + domain append)
	@if [ ! -f "$(PROJECT)/.claude/CLAUDE.md" ]; then \
		cp stacks/$(STACK)/CLAUDE.md "$(PROJECT)/.claude/CLAUDE.md"; \
		echo "  ✅ CLAUDE.md creado — edita los [PLACEHOLDER] con el contexto del proyecto"; \
	else \
		echo "  ⚠️  .claude/CLAUDE.md ya existe — no sobreescrito"; \
	fi
	@if [ -n "$(LAYERS)" ]; then \
		for layer in $$(echo "$(LAYERS)" | tr ',' ' '); do \
			if [ -f "layers/$$layer/CLAUDE-append.md" ]; then \
				cat layers/$$layer/CLAUDE-append.md >> "$(PROJECT)/.claude/CLAUDE.md"; \
				echo "  ✅ Layer context appended to CLAUDE.md ($$layer)"; \
			fi; \
		done; \
	fi
	@if [ -n "$(DOMAIN)" ] && [ -f "domains/$(DOMAIN)/CLAUDE-append.md" ]; then \
		cat domains/$(DOMAIN)/CLAUDE-append.md >> "$(PROJECT)/.claude/CLAUDE.md"; \
		echo "  ✅ Domain context appended to CLAUDE.md"; \
	fi
	@# 7. Actualizar .gitignore del proyecto (excluir archivos generados de Claude)
	@if [ -f "$(PROJECT)/.gitignore" ]; then \
		if ! grep -q "\.claude/agents/" "$(PROJECT)/.gitignore"; then \
			printf '\n# Claude Code — archivos generados (no commitear)\n.claude/agents/\n.claude/commands/\n.claude/rules/\n.claude/pipeline.yaml\n# Claude Code — si commitear (contexto del proyecto)\n!.claude/CLAUDE.md\n!.claude/memory/\n' >> "$(PROJECT)/.gitignore"; \
			echo "  ✅ .gitignore actualizado — archivos generados de Claude excluidos"; \
		else \
			echo "  ✅ .gitignore ya tiene entradas de Claude"; \
		fi; \
	fi
	@echo "  ✅ .claude/memory/ listo — se llenara automaticamente al trabajar con Claude"
	@echo ""
	@echo "Proyecto listo."
	@echo "  Agentes: skills embebidas (el developer no necesita invocar skills manualmente)"
	@echo "  Workflows: /workflow feature | /workflow hotfix | /workflow refactor"
	@echo "  Layers disponibles: make list-layers"
	@echo "  Domains disponibles: make list-domains"
	@echo "  Los agentes globales adicionales vienen de ~/.claude/ (make install)."

setup-project: ## Flujo unificado: auto-detecta stack + confirma + inicializa proyecto (ej: make setup-project PROJECT=/ruta)
	@[ -n "$(PROJECT)" ] || (echo "❌ Indica la ruta: make setup-project PROJECT=/ruta/al/proyecto" && exit 1)
	@[ -d "$(PROJECT)" ] || (echo "❌ No existe el directorio: $(PROJECT)" && exit 1)
	@echo "🔍 Analizando proyecto en $(PROJECT)..."
	@RESULT=$$(python3 ops/detect-stack.py "$(PROJECT)"); \
	echo "$$RESULT" | head -n -1; \
	LAST_LINE=$$(echo "$$RESULT" | tail -1); \
	DETECTED_STACK=$$(echo "$$LAST_LINE" | grep -o 'STACK=[^ ]*' | sed 's/STACK=//'); \
	DETECTED_LAYERS=$$(echo "$$LAST_LINE" | grep -o 'LAYERS=[^ ]*' | sed 's/LAYERS=//' || echo ""); \
	if [ -z "$$DETECTED_STACK" ] || [ "$$DETECTED_STACK" = "unknown" ]; then \
		echo ""; \
		echo "No se pudo detectar el stack automaticamente."; \
		echo "Stacks disponibles:"; \
		for d in stacks/*/; do echo "  - $$(basename $$d)"; done; \
		read -p "Selecciona stack: " DETECTED_STACK; \
		DETECTED_LAYERS=""; \
	else \
		echo ""; \
		LAYERS_HINT=$$([ -n "$$DETECTED_LAYERS" ] && echo " LAYERS=$$DETECTED_LAYERS" || echo ""); \
		read -p "¿Usar stack '$$DETECTED_STACK'$$LAYERS_HINT? [Y/n] " CONFIRM; \
		if [ "$$CONFIRM" = "n" ] || [ "$$CONFIRM" = "N" ]; then \
			echo "Stacks disponibles:"; \
			for d in stacks/*/; do echo "  - $$(basename $$d)"; done; \
			read -p "Selecciona stack: " DETECTED_STACK; \
			DETECTED_LAYERS=""; \
		fi; \
	fi; \
	echo ""; \
	$(MAKE) init-project STACK=$$DETECTED_STACK LAYERS=$$DETECTED_LAYERS PROJECT=$(PROJECT)

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
	@echo "✅ Git hooks desactivados. Usalos de nuevo con: make hooks-install"

# ---- NUEVO PROYECTO ----

new-project: ## Instrucciones para inicializar un proyecto existente con el god-mode
	@echo "Flujo para usar god-mode en un proyecto existente:"
	@echo ""
	@echo "  1. Instalacion global (una vez por maquina):"
	@echo "     make install"
	@echo ""
	@echo "  2a. Modo automatico (detecta stack y configura):"
	@echo "      make setup-project PROJECT=/ruta/al/proyecto"
	@echo ""
	@echo "  2b. Modo manual (stack explicito):"
	@echo "      make init-project STACK=laravel PROJECT=/ruta/al/proyecto"
	@echo ""
	@echo "  2c. Con layer tecnico (ej: frontend React):"
	@echo "      make init-project STACK=laravel LAYERS=react PROJECT=/ruta"
	@echo ""
	@echo "  2d. Con layer + domain overlay:"
	@echo "      make init-project STACK=laravel LAYERS=react DOMAIN=healthcare PROJECT=/ruta"
	@echo ""
	@echo "  3. Personalizar el contexto del proyecto:"
	@echo "     Edita /ruta/al/proyecto/.claude/CLAUDE.md"
	@echo "     → Reemplaza los [PLACEHOLDER] con el contexto real del proyecto"
	@echo ""
	@echo "  Stacks disponibles: make list-stacks"

# ---- PROYECTOS EXTERNOS ----

load-project: ## Clona un proyecto externo en projects/<nombre> para análisis (ej: make load-project URL=https://github.com/usuario/repo.git)
	@if [ -z "$(URL)" ]; then \
		echo "❌ Uso: make load-project URL=https://github.com/usuario/repo.git"; \
		exit 1; \
	fi
	@NAME=$$(basename $(URL) .git); \
	echo "📦 Clonando $$NAME en projects/$$NAME..."; \
	mkdir -p projects; \
	git clone $(URL) projects/$$NAME; \
	echo ""; \
	echo "✅ Proyecto listo en projects/$$NAME"; \
	echo ""; \
	echo "Siguiente paso:"; \
	echo "  make analyze-project NAME=$$NAME"

analyze-project: ## Análisis completo de un proyecto cargado: genera REPORT.md con issues de stack, seguridad y código (ej: make analyze-project NAME=maya-dashboard)
	@if [ -z "$(NAME)" ]; then \
		echo "❌ Uso: make analyze-project NAME=<nombre-del-proyecto>"; \
		echo "   Proyectos disponibles:"; \
		ls projects/ 2>/dev/null | sed 's/^/     - /' || echo "     (ninguno — usa make load-project primero)"; \
		exit 1; \
	fi
	@if [ ! -d "projects/$(NAME)" ]; then \
		echo "❌ No existe projects/$(NAME)"; \
		echo "   Carga el proyecto primero: make load-project URL=<url>"; \
		exit 1; \
	fi
	@echo "🔍 Analizando projects/$(NAME)..."
	@echo "   Lanzando 3 agentes en paralelo: architect + security-reviewer + code-reviewer"
	@echo "   Resultado → projects/$(NAME)/REPORT.md"
	@echo ""
	claude --print --max-turns 15 \
		"Analiza el proyecto en projects/$(NAME)/. \
Lanza en paralelo 3 agentes especializados: \
(1) architect — stack, arquitectura y puntos de mejora estructural; \
(2) security-reviewer — vulnerabilidades OWASP Top 10, auth, inputs, secretos; \
(3) code-reviewer — calidad, bugs, anti-patrones y deuda técnica. \
Consolida todos los resultados en projects/$(NAME)/REPORT.md con secciones claramente separadas por agente. \
Al final incluye un apartado 'Top 5 acciones' con las mejoras más impactantes ordenadas por severidad."
	@echo ""
	@echo "✅ Análisis completo. Resultado en projects/$(NAME)/REPORT.md"

# ---- TESTS ----

test: ## Ejecuta la suite de tests integral (struct + embed + invoke)
	python3 ops/test-suite.py

test-quick: ## Tests rápidos sin invocaciones de Claude (solo struct + embed)
	python3 ops/test-suite.py --no-invoke

# ---- VERIFICACION ----

check: ## Verifica que todo esta correctamente configurado
	@echo "Verificando configuracion..."
	@echo ""
	@echo "── Instalacion global (~/.claude/) ──────────────────"
	@[ -f "$(GLOBAL_DIR)/settings.json" ] \
		&& echo "  ✅ settings.json global" \
		|| echo "  ❌ Falta settings.json global — ejecuta: make install"
	@[ -d "$(GLOBAL_DIR)/rules/common" ] && [ -n "$$(ls $(GLOBAL_DIR)/rules/common/*.md 2>/dev/null)" ] \
		&& echo "  ✅ Reglas comunes globales ($$(ls $(GLOBAL_DIR)/rules/common/*.md 2>/dev/null | wc -l | tr -d ' ') archivos)" \
		|| echo "  ❌ Sin reglas comunes globales — ejecuta: make install"
	@[ -d "$(GLOBAL_DIR)/agents" ] && [ -n "$$(ls $(GLOBAL_DIR)/agents/*.md 2>/dev/null)" ] \
		&& echo "  ✅ Agentes globales ($$(ls $(GLOBAL_DIR)/agents/*.md 2>/dev/null | wc -l | tr -d ' ') agentes)" \
		|| echo "  ❌ Sin agentes globales — ejecuta: make install"
	@[ -x "$(GLOBAL_DIR)/hooks/session-consolidate.sh" ] \
		&& echo "  ✅ Hook de consolidacion de memoria" \
		|| echo "  ❌ Sin hook de memoria — ejecuta: make install"
	@echo ""
	@echo "── Este repositorio (.claude/) ──────────────────────"
	@git config core.hooksPath > /dev/null 2>&1 \
		&& echo "  ✅ Git hooks configurados" \
		|| echo "  ❌ Ejecuta: make hooks-install"
	@[ -f ".claude/settings.json" ] && echo "  ✅ .claude/settings.json" || echo "  ❌ Falta .claude/settings.json"
	@[ -f ".claude/CLAUDE.md" ] && echo "  ✅ .claude/CLAUDE.md" || echo "  ❌ Falta .claude/CLAUDE.md"
	@[ -f ".mcp.json" ] && echo "  ✅ .mcp.json" || echo "  ❌ Falta .mcp.json"
	@echo ""
	@echo "── MCPs opcionales ──────────────────────────────────"
	@command -v notebooklm-mcp &> /dev/null \
		&& echo "  ✅ NotebookLM MCP instalado" \
		|| echo "  ℹ️  NotebookLM MCP no instalado (opcional): pip install notebooklm-mcp-cli"
	@echo ""
	@echo "── Sincronización de agentes ────────────────────────"
	@SOURCE_COUNT=$$(ls agents/*.md 2>/dev/null | wc -l | tr -d ' '); \
	LOCAL_COUNT=$$(ls .claude/agents/*.md 2>/dev/null | wc -l | tr -d ' '); \
	GLOBAL_COUNT=$$(ls $(GLOBAL_DIR)/agents/*.md 2>/dev/null | wc -l | tr -d ' '); \
	echo "  Fuente: $$SOURCE_COUNT agentes en agents/"; \
	echo "  Local:  $$LOCAL_COUNT agentes en .claude/agents/ (compilados con skills del stack activo)"; \
	echo "  Global: $$GLOBAL_COUNT agentes en ~/.claude/agents/"; \
	if [ $$SOURCE_COUNT -eq 0 ]; then \
		echo "  ❌ No hay agentes fuente en agents/"; \
	else \
		echo "  ✅ Agentes fuente disponibles"; \
	fi
	@echo ""
	@echo "── ops/ scripts ─────────────────────────────────────"
	@[ -f "ops/compile-agents.py" ] \
		&& echo "  ✅ compile-agents.py" \
		|| echo "  ❌ Falta ops/compile-agents.py"
	@[ -f "ops/detect-stack.py" ] \
		&& echo "  ✅ detect-stack.py" \
		|| echo "  ❌ Falta ops/detect-stack.py"
	@[ -f "ops/audit-task.sh" ] \
		&& echo "  ✅ audit-task.sh" \
		|| echo "  ❌ Falta ops/audit-task.sh"

# ---- TRIGGERS (Antigravity scheduled jobs) ----

triggers-setup: ## Imprime los comandos /schedule create para activar los triggers en Claude Code
	@echo "Pega estos comandos en Claude Code para activar los triggers programados:"
	@echo ""
	@for f in ops/triggers/*.yaml; do \
		[ -f "$$f" ] || continue; \
		NAME=$$(python3 -c "import yaml,sys; d=yaml.safe_load(open('$$f')); print(d['name'])"); \
		SCHEDULE=$$(python3 -c "import yaml,sys; d=yaml.safe_load(open('$$f')); print(d['schedule'])"); \
		PROMPT=$$(python3 -c "import yaml,sys; d=yaml.safe_load(open('$$f')); print(d['prompt'].strip().replace(chr(10), ' '))"); \
		echo "/schedule create $$NAME \\"; \
		echo "  --cron \"$$SCHEDULE\" \\"; \
		echo "  --prompt \"$$PROMPT\""; \
		echo ""; \
	done

triggers-list: ## Lista los triggers definidos en ops/triggers/
	@echo "Triggers definidos en ops/triggers/:"
	@echo ""
	@for f in ops/triggers/*.yaml; do \
		[ -f "$$f" ] || continue; \
		NAME=$$(python3 -c "import yaml; d=yaml.safe_load(open('$$f')); print(d['name'])"); \
		DESC=$$(python3 -c "import yaml; d=yaml.safe_load(open('$$f')); print(d.get('description',''))"); \
		SCHED=$$(python3 -c "import yaml; d=yaml.safe_load(open('$$f')); print(d['schedule'])"); \
		echo "  $$NAME — $$DESC (cron: $$SCHED)"; \
	done
	@echo ""
	@echo "Para activarlos: make triggers-setup"
	@echo "Para ver activos en Claude Code: /schedule list"

setup-labels: ## Crea en GitHub las labels necesarias para los agent workflows (ejecutar una vez por repositorio)
	@echo "Creando labels para agent workflows..."
	@gh label create "needs-plan"      --color "#0075ca" --description "Triggers planner agent"        --force 2>/dev/null || true
	@gh label create "planned"         --color "#0075ca" --description "Has implementation plan"       --force 2>/dev/null || true
	@gh label create "needs-review"    --color "#e11d48" --description "Triggers code/security review" --force 2>/dev/null || true
	@gh label create "reviewed"        --color "#22c55e" --description "Agent review complete"          --force 2>/dev/null || true
	@gh label create "review-blocked"  --color "#dc2626" --description "CRITICAL issues found"         --force 2>/dev/null || true
	@gh label create "audit"           --color "#e4e669" --description "Automated audit report"        --force 2>/dev/null || true
	@echo "Labels configuradas. Verifica con: gh label list"

workflows-status: ## Muestra los GitHub Actions instalados y el secret requerido
	@echo "GitHub Actions instalados en .github/workflows/:"
	@echo ""
	@for f in .github/workflows/agent-*.yml; do \
		[ -f "$$f" ] || continue; \
		NAME=$$(basename $$f); \
		TRIGGER=$$(grep -m1 "^on:" $$f -A3 | grep -E "pull_request|push|schedule|issues|workflow_dispatch" | head -1 | tr -d ' '); \
		printf "  %-40s %s\n" "$$NAME" "$$TRIGGER"; \
	done
	@echo ""
	@echo "Secret requerido en Settings → Secrets → Actions:"
	@echo "  ANTHROPIC_API_KEY — tu clave de la API de Anthropic"
	@echo ""
	@echo "Para crear las labels de los workflows: make setup-labels"
