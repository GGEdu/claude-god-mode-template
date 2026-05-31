# Repository Evaluations Log

<!-- Actualizado automáticamente por repo-reviewer agent y weekly-repo-discovery trigger -->
<!-- NO editar manualmente — el agente gestiona este archivo -->

## Stats
- Total evaluados: 4
- INCLUDE: 3 | REVIEW: 1 | WATCH: 0 | SKIP: 0

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

