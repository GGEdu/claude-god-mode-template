---
layout: home

hero:
  name: "Claude God Mode Template"
  text: "Boilerplate de Claude Code con superpoderes"
  tagline: "139 skills, 15 stacks de usuario (+common), layers técnicos composables, 4 domain overlays, 38 agentes, sistema de memoria, hooks defensivos y MCPs configurados. Todo listo en menos de una hora."
  actions:
    - theme: brand
      text: Instalación paso a paso
      link: /instalacion
    - theme: alt
      text: Tutorial de uso
      link: /primeros-pasos
    - theme: alt
      text: Referencia rápida
      link: /referencia

features:
  - icon: 🧠
    title: Everything Claude Code (ECC)
    details: 139 skills, 15 tech stacks de usuario y layers técnicos composables (React, etc.) con 4 domain overlays. Los agentes se compilan con skills embebidas por stack + layer — code reviewers, TDD guides, build resolvers, security scanners y más.

  - icon: 🔮
    title: Jedi Review — Panel de Expertos
    details: Tres subagentes en paralelo revisan tu código desde perspectivas distintas. Kent Beck (simplicidad), Martin Fowler (arquitectura) y Mike Acton (rendimiento).

  - icon: 🗃️
    title: Sistema de Memoria Persistente
    details: Hook automático que captura decisiones de arquitectura y reglas de dominio al terminar cada sesión. Los archivos en .claude/memory/ se versionan con git — todo el equipo comparte la misma memoria.

  - icon: 🔒
    title: Hooks Defensivos
    details: Pre-commit con linting automático (Biome/Ruff) y detección de secrets. Pre-push con tests obligatorios. Código que no pasa los checks no puede entrar al repo.

  - icon: 🔌
    title: MCPs Listos para Usar
    details: GitHub, Memory (siempre activos), NotebookLM y n8n preconfigurados pero desactivados. Activa solo lo que necesitas con make activate-notebooklm.

  - icon: ⚡
    title: Optimizado para el Bolsillo
    details: Con sonnet + MAX_THINKING_TOKENS=10000 + autocompact al 50%, el coste por sesión se reduce ~70% respecto a los valores por defecto de Claude Code.

  - icon: 🏗️
    title: Multi-Proyecto
    details: El template está diseñado para clonarse. Cada nuevo proyecto hereda toda la configuración y la personaliza en cinco minutos con make setup.

  - icon: 🔍
    title: Análisis de Proyectos Externos
    details: Clona cualquier repositorio y lanza tres revisores en paralelo (stack, seguridad, calidad). Genera un REPORT.md con los hallazgos sin tocar tu proyecto principal.
---
