# Directorio: `layers/`

Los **layers técnicos** son overlays composables que añaden una capa de tecnología horizontal (frontend, infra) sobre cualquier stack backend. Un layer NO reemplaza el stack — se fusiona encima (merge), añadiendo skills, agentes, reglas y comandos específicos de esa tecnología.

> **Layers vs Domains:** Los layers son para **tech horizontal** (React SPA, Docker infra). Los [domains](./domains.md) son para **verticales de negocio** (healthcare, supply-chain).

---

## Layer disponible: `react`

Frontend React 19 + TypeScript SPA, composable sobre cualquier stack backend (Laravel, Python, Go, etc.).

### Skills añadidas por agente

- architect: `api-design` _(diseño de contratos API entre backend y frontend)_
- typescript-reviewer: `frontend-patterns`, `coding-standards`, `design-system` _(agente nuevo — no existe en stacks de backend puro)_
- e2e-runner: `e2e-testing`

### Rules añadidas al proyecto

- `react.md` — arquitectura de componentes, data fetching, performance
- `coding-style.md` — inmutabilidad, organización de archivos TS/JS
- `hooks.md` — patrones de hooks personalizados
- `patterns.md` — patrones React (SWR, React Query, Context)
- `security.md` — XSS, CORS, manejo seguro de tokens
- `testing.md` — Vitest + Testing Library + MSW

### Comandos añadidos

- `design-md`: Al crear componentes React o refactorizar UI — aplica identidad visual

### Append a CLAUDE.md

Cuando se activa `LAYERS=react`, se añade automáticamente al `CLAUDE.md` del proyecto la sección de frontend con la estructura `src/` y los comandos extra.

---

## Uso

```bash
# Solo layer (en este repo, para desarrollo)
make dev-stack STACK=laravel LAYERS=react

# En un proyecto nuevo
make init-project STACK=laravel LAYERS=react PROJECT=/ruta/al/proyecto

# Múltiples layers (comma-separated)
make init-project STACK=laravel LAYERS=react,vue PROJECT=/ruta

# Stack + layers + domain
make init-project STACK=python-api LAYERS=react DOMAIN=healthcare PROJECT=/ruta

# Auto-detección (sugiere LAYERS automáticamente si detecta React)
make setup-project PROJECT=/ruta/al/proyecto
```

---

## Cómo funciona internamente

1. `make init-project` construye una lista de overlay YAMLs: `layers/react/layer.yaml [domains/healthcare/domain.yaml]`
2. `ops/compile-agents.py` recibe los overlays como argumentos posicionales y hace merge en orden (layers → domain)
3. Si un layer añade un agente que no existe en el stack (ej. `typescript-reviewer` en `python-api`), lo crea desde cero con las skills del layer
4. Las rules del layer se copian a `.claude/rules/stack/` junto a las del stack
5. El `CLAUDE-append.md` del layer se añade al `CLAUDE.md` del proyecto

---

## Formato de `layer.yaml`

Mismo schema que `domain.yaml`:

```yaml
name: <nombre>
description: <descripción>
frontend: <lenguaje>           # metadata informativo
frontend_framework: <framework>
tests_frontend: <framework>
linter_frontend: <herramienta>

agent_skills:
  <nombre-agente>:             # puede ser un agente nuevo o uno existente
    - <skill-name>

commands:
  <nombre-command>:
    when: <descripción de cuándo usarlo>

rules:
  - <rule-file>.md             # archivos en layers/<nombre>/rules/
```

---

## Añadir un nuevo layer

1. Crear `layers/<nombre>/` con:
   - `layer.yaml` — definición del layer
   - `rules/*.md` — reglas específicas (scoped a los archivos del tech si posible)
   - `CLAUDE-append.md` — sección a añadir al CLAUDE.md del proyecto (opcional)
   - `design/` — design files opcionales

2. Añadir skills en `skills/<nombre-skill>/SKILL.md` si no existen

3. Probar composición:

   ```bash
   make dev-stack STACK=laravel LAYERS=<nombre>
   make check
   ```

4. Documentar en esta página
