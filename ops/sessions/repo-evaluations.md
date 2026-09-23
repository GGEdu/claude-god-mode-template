# Repository Evaluations Log

<!-- Actualizado automáticamente por repo-reviewer agent y weekly-repo-discovery trigger -->
<!-- NO editar manualmente — el agente gestiona este archivo -->

## Stats
- Total evaluados: 8
- INCLUDE: 5 | REVIEW: 3 | WATCH: 0 | SKIP: 0
- Status válidos: Proposed → Integrated → **Verified** (solo tras `ops/check-skill-integrity.py` en verde)

---

## Evaluaciones

### UI UX Pro Max Skill — https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- **Date:** 2026-04-14
- **Score:** 94/100 (Relevancia: 25/25, Calidad: 33/35, Extractabilidad: 20/20, Coste: 16/20)
- **Tier:** INCLUDE
- **Reason:** Massive (64K+ stars) mature design intelligence framework with 161 reasoning rules, 67 styles, 57 fonts, 161 product types—fills critical gap in design domain. MIT licensed, Python-based, BM25 search engine, design system generator with Master+Overrides pattern.
- **Discovered via:** manual
- **Extracted:** skills: ui-ux-pro-max (search engine, design system gen, 11 domains, 10 tech stacks)
- **Status:** Proposed
- **Notes:** Complements existing design-system/banner-design/brand skills (narrower scope). Large dataset requires integration care. No external dependencies. Medium effort (8-12h).
- **Re-evaluación 2026-09-23:** la integración copió solo `SKILL.md`; `scripts/search.py` y `data/` nunca llegaron y el SKILL.md mandaba ejecutarlos → el modelo caía en sus defaults (causa principal de los diseños repetidos). **Status: Integración parcial — rota**. Resolución (rama `feat/design-diversity`): se retiran las instrucciones del motor y la skill queda como catálogo de reglas UX; no se restaura el motor porque una búsqueda BM25 determinista por tipo de producto reproduce la homogeneidad. Upstream hoy: 130k★, 192 paletas, 22 stacks, skills extra (brand, banner-design, slides, ui-styling) sin evaluar.

### Everything Claude Code — https://github.com/affaan-m/everything-claude-code
- **Date:** 2026-04-16
- **Score:** 82/100 (Relevancia: 24/25, Calidad: 33/35, Extractabilidad: 16/20, Coste: 9/20)
- **Tier:** INCLUDE
- **Reason:** Evolución paralela del mismo concepto (158k stars, Anthropic Hackathon Winner) con 183 skills / 48 agents en estructura SKILL.md compatible. 50+ skills únicos de alto valor no presentes en el template.
- **Discovered via:** manual
- **Extracted:** skills: [agent-introspection-debugging, council, santa-method, hookify-rules], agents: [harness-optimizer, go-reviewer, java-reviewer, kotlin-reviewer, python-reviewer, cpp-reviewer, csharp-reviewer, flutter-reviewer, go-build-resolver, java-build-resolver, kotlin-build-resolver, cpp-build-resolver, dart-build-resolver]
- **Status:** Integrated
- **Notes:** Solapamiento masivo (~60% de skills con nombres idénticos). ECC tiene más amplitud, este template tiene más arquitectura (stacks/layers/compile-agents). Prioridad de extracción: (1) agent-introspection-debugging, (2) council, (3) santa-method, (4) harness-optimizer agent, (5) language-specific reviewers por batch. Algunos skills tienen `origin: ECC` con dependencias a su ecosistema — verificar antes de integrar. MIT licensed.

### LightRAG — https://github.com/HKUDS/LightRAG
- **Date:** 2026-04-16
- **Score:** 62/100 (Relevancia: 14/25, Calidad: 30/35, Extractabilidad: 10/20, Coste: 8/20)
- **Tier:** REVIEW
- **Reason:** Knowledge-graph-enhanced RAG de alta calidad (33k stars, paper EMNLP2025) pero bajo overlap con el sistema actual — jcodemunch+context7+memory ya cubren sus casos de uso principales.
- **Discovered via:** manual
- **Extracted:** skills: [], agents: [], rules: []
- **Status:** Watchlist
- **Notes:** Valor real solo si hay colecciones de documentos privados a gran escala (+10k docs). 10x más barato que GraphRAG. Reconsiderar si Maya DMS necesita RAG sobre docs clínicos/legales. MIT licensed. Python package `lightrag-hku`.

### Impeccable — https://github.com/pbakaus/impeccable
- **Date:** 2026-09-23
- **Score:** 92/100 (Relevancia: 25/25, Calidad: 35/35, Extractabilidad: 18/20, Coste: 14/20)
- **Tier:** INCLUDE
- **Reason:** Único repo evaluado que ataca la homogeneidad por diseño: `concept-seed` asigna la dirección (excluye el default de la categoría y su opuesto), fuentes y looks de IA vetados, craft-floor, detector de 60+ antipatrones, 24 comandos (critique, audit, bolder, quieter, distill, polish, live…). 70k★, Apache-2.0, activo.
- **Discovered via:** manual
- **Extracted:** skills: [impeccable (verbatim)], agents: [ui-engineer reescrito sobre él]
- **Status:** Integrated (rama `feat/design-diversity`, pendiente de merge)
- **Notes:** Motor Rust descargado de GitHub Releases → huella fijada en `skills/impeccable/ENGINE.sha256` (verificada contra sidecar y `digest` de GitHub). `concept-seed` hace un GET a impeccable.style/api/roll sin datos del proyecto; telemetría y update-check desactivados por env. El valor está en `reference/new-work.md` (52 KB), no en SKILL.md: el límite de 5 ficheros de la Fase 2 no lo habría visto.

### ui-skills — https://github.com/ibelick/ui-skills
- **Date:** 2026-09-23
- **Score:** 78/100 (Relevancia: 12/25, Calidad: 30/35, Extractabilidad: 20/20, Coste: 16/20)
- **Tier:** REVIEW
- **Reason:** 7 skills propias de design engineering (9k★, MIT): auditorías útiles (fixing-accessibility, fixing-motion-performance, fixing-metadata, improve-ui) y create-design-md; no aportan variedad estética.
- **Discovered via:** manual
- **Extracted:** skills: [fixing-accessibility, fixing-motion-performance, fixing-metadata, improve-ui] (candidatas)
- **Status:** Proposed — aplazado hasta medir impeccable (council 2026-09-23)
- **Notes:** `baseline-ui` impone defaults de Tailwind → aumenta la homogeneidad; no adoptar como default. `create-design-md` es fusionable en `design-md`.

### Agentic Design Patterns — https://github.com/evoiz/Agentic-Design-Patterns
- **Date:** 2026-09-23
- **Score:** 50/100 (Relevancia: 6/25, Calidad: 24/35, Extractabilidad: 8/20, Coste: 12/20)
- **Tier:** REVIEW
- **Reason:** Libro de Antonio Gulli (21 patrones: chaining, routing, reflection, planning, multi-agente, guardrails, evaluación) + 66 notebooks. Conceptos ya cubiertos por autonomous-loops, santa-method, council, blueprint.
- **Discovered via:** manual
- **Extracted:** (nada)
- **Status:** Skip — solo referencia conceptual
- **Notes:** Sin licencia declarada y redistribuye el PDF completo del libro: no copiar texto. El pipeline "N direcciones en paralelo → evaluador → gate humano → build → crítica" que sugiere ya lo implementa impeccable.

<!-- Formato por entrada:

### [Nombre del Repo] — https://github.com/<owner>/<repo>
- **Date:** YYYY-MM-DD
- **Score:** X/100 (Relevancia: N/25, Calidad: N/35, Extractabilidad: N/20, Coste: N/20)
- **Tier:** INCLUDE | REVIEW | WATCH | SKIP
- **Reason:** [razón en 1 línea]
- **Discovered via:** manual | weekly-discovery | <otro>
- **Extracted:** skills: [skill1, skill2], agents: [agent1], rules: [rule.md]
- **Status:** Proposed | Integrated | Watchlist | Skip
- **Notes:** [info adicional relevante]

-->

### Everything Claude Code (v2.0.0-rc.1) — https://github.com/affaan-m/everything-claude-code
- **Date:** 2026-05-31
- **Score:** 89/100 (Relevancia: 25/25, Calidad: 34/35, Extractabilidad: 18/20, Coste: 12/20)
- **Tier:** INCLUDE
- **Reason:** v2 RC adds 5 critical agent-optimization skills (parallel-executor, benchmark-loop, latency-critical, recursive-ledger, data-throughput) + 95 new domain skills; zero breaking changes to v1 integrated skills. 243 total skills, 2568 passing tests, cross-harness design. RC status mitigated by validation gates and content stability claim.
- **Discovered via:** manual re-evaluation
- **Extracted:** skills (v2-new, priority): [parallel-execution-optimizer, benchmark-optimization-loop, recursive-decision-ledger, latency-critical-systems, data-throughput-accelerator], skills (v1-compat, already integrated): [agent-introspection-debugging, council, santa-method, hookify-rules], agents: no new critical agents vs v1.10.0
- **Status:** Integrate v2 RC now
- **Notes:** v1.10.0 skills (council, santa-method, agent-introspection, hookify-rules) have zero breaking changes—forks remain valid. RC released 2026-05-25 with tarball + cross-harness surfaces (Codex, OpenCode, Cursor, Gemini, Zed). New optimization pack directly enables speedup in harness orchestration. Itô prediction-market skills are gated/separate billing, low priority for core template. Adoption path: (1) pull v2.0.0-rc.1 tarball, (2) extract 5 optimization skills + refresh 4 existing forks, (3) integrate 95 new domain skills on backlog. Estimated effort: 4-6h for top 9, 20-30h for full domain suite. Recommendation: ADOPT RC NOW vs waiting for GA—ECC has battle-tested track record (199k stars, Hackathon winner), RC gates adequate, early adoption = 3-4mo competitive advantage in agent perf tuning.


### google-labs-code/design.md — https://github.com/google-labs-code/design.md
- **Date:** 2026-07-24
- **Score:** 88/100 (Relevancia: 23/25, Calidad: 34/35, Extractabilidad: 18/20, Coste: 13/20)
- **Tier:** INCLUDE
- **Reason:** Official Google Labs specification for DESIGN.md format (YAML+Markdown tokens for AI agents). Brand-new (April 2026) but massively adopted (26k stars, 2k forks in 3 months). Template already uses DESIGN.md format in 3+ skills—integrating official spec + CLI tooling (lint, diff, WCAG validation) enhances without breaking changes. Apache 2.0 licensed, zero external dependencies, local-first validation.
- **Discovered via:** user evaluation request
- **Extracted:** new skill: design-md-validate (CLI wrapper for lint/diff/validation); enhancements to existing: design-md (spec reference), design-system (validation integration), ui-engineer (spec compliance documentation)
- **Status:** Proposed
- **Notes:** Complementary to, not competitive with, existing `skills/design-md/` and `skills/design-system/` — spec legitimizes existing format usage. No breaking changes required. Effort: 3-5h (immediate: 1h docs + spec link, short-term: 1-2h validate skill, backlog: 1-2h workflow integration). Integration plan: (1) Update CLAUDE.md to reference official spec, (2) Create `design-md-validate` skill using @google/design.md CLI, (3) Add npm dependency to Node stacks, (4) Optionally integrate validation into design-system workflow. Existing design files (stripe.md, linear.md) are documentation-grade, not required to upgrade but can be validated/migrated at leisure. v0.3.0 stable, pushed 2026-07-22 (4 days ago), latest release 2026-06-15. Risk mitigation: pin major version in package.json, monitor spec evolution in weekly reviews.

