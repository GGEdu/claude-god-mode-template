# Directorio: `domains/`

Los **4 domain overlays** añaden skills extra a los agentes de cualquier tech stack. Un domain NO reemplaza el stack — se fusiona encima (merge), añadiendo contexto vertical de negocio a los agentes existentes.

> `make dev-stack STACK=<s> DOMAIN=<d>` o `make init-project STACK=<s> DOMAIN=<d>` activan el overlay. `ops/compile-agents.py` recibe el `domain.yaml` como quinto argumento y hace merge de skills.

---

## Los 4 dominios

### `ai-agent` — Sistemas de agentes de IA

El overlay más extenso. Orienta el stack hacia construcción de pipelines de agentes, evaluación de LLMs y operaciones de flota Claude.

**Skills añadidas por agente:**

- architect: agentic-engineering, autonomous-loops, agent-harness-construction, claude-api, mcp-server-patterns, ralphinho-rfc-pipeline
- planner: agentic-engineering, cost-aware-llm-pipeline, ai-first-engineering
- tdd-guide: eval-harness, ai-regression-testing
- code-reviewer: agentic-engineering, continuous-agent-loop
- security-reviewer: agent-payment-x402

**Comandos extra (7):**

- `deep-research`: Research profundo con múltiples fuentes
- `exa-search`: Búsqueda semántica web via Exa
- `blueprint`: Genera blueprint de arquitectura de agentes
- `dmux-workflows`: Workflows de orquestación con tmux
- `enterprise-agent-ops`: Operaciones de flota de agentes en producción
- `agent-eval`: Framework de evaluación de agentes
- `claude-devfleet`: Gestión de múltiples instancias Claude

---

### `healthcare` — Sistemas de salud y EMR

Añade compliance con regulaciones sanitarias (HIPAA, PHI) y patrones de decisión clínica a los agentes de revisión.

**Skills añadidas por agente:**

- architect: healthcare-emr-patterns, healthcare-cdss-patterns
- tdd-guide: healthcare-eval-harness
- code-reviewer: healthcare-phi-compliance
- security-reviewer: healthcare-phi-compliance

**Comandos extra:** Ninguno (el dominio opera vía skills, no comandos).

---

### `content-creator` — Creación de contenido y media

Orienta el stack hacia pipelines de contenido, artículos y distribución multi-canal.

**Skills añadidas por agente:**

- architect: content-engine, article-writing
- planner: content-engine

**Comandos extra (12):**

- `deep-research`: Investigación profunda multi-fuente con citas
- `exa-search`: Búsqueda neural web, código y empresas
- `data-scraper-agent`: Scraping automatizado de fuentes públicas
- `investor-materials`: Pitch decks, one-pagers y memos para inversores
- `investor-outreach`: Emails y comunicaciones para fundraising
- `market-research`: Análisis de mercado y competencia
- `crosspost`: Distribuir contenido a múltiples plataformas
- `x-api`: Publicar o leer de X/Twitter programáticamente
- `frontend-slides`: Crear presentaciones HTML con animaciones
- `fal-ai-media`: Generar imágenes, video o audio con IA
- `video-editing`: Editar video con FFmpeg, Remotion o CapCut
- `videodb`: Indexar, buscar y editar video con VideoDB

---

### `supply-chain` — Cadena de suministro y logística

Añade patrones de supply chain, gestión de inventario y optimización de rutas a los agentes de arquitectura y revisión.

**Skills añadidas por agente:**

- architect: carrier-relationship-management, inventory-demand-planning, energy-procurement
- planner: production-scheduling
- code-reviewer: logistics-exception-management, quality-nonconformance, returns-reverse-logistics
- security-reviewer: customs-trade-compliance

**Comandos extra:** Ninguno (el dominio opera vía skills, no comandos).

---

## Resumen comparativo

- ai-agent: 14 skills, 5 agentes afectados, 7 comandos extra.
- healthcare: 5 skills, 4 agentes afectados, 0 comandos extra.
- content-creator: 3 skills, 2 agentes afectados, 12 comandos extra.
- supply-chain: 8 skills, 4 agentes afectados, 0 comandos extra.

---

## Formato de `domain.yaml`

```yaml
name: <nombre>
description: <descripción>

agent_skills:
  <nombre-agente>:
    - <skill-name>

commands:
  <nombre-command>:
    when: <descripción de cuándo usarlo>
```

---

## Cómo combinar stack + domain

```bash
# Desarrollo local (en este repo)
make dev-stack STACK=nextjs-saas DOMAIN=ai-agent

# En un proyecto nuevo
make init-project STACK=python-api DOMAIN=healthcare
```

El resultado son agentes que conocen tanto las reglas del framework (Python + FastAPI) como las del dominio vertical (PHI compliance, EMR patterns).

---

## Añadir un nuevo dominio

1. Crear `domains/<nombre>/domain.yaml` con el formato anterior
2. Añadir skills en `skills/<nombre-skill>/SKILL.md` si no existen
3. Probar compilación:

   ```bash
   make dev-stack STACK=nextjs-saas DOMAIN=<nombre>
   make check
   ```
