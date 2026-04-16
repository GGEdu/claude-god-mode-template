import { defineConfig } from 'vitepress';
import { withMermaid } from 'vitepress-plugin-mermaid';  // Necesario para diagramas C4/Mermaid

export default withMermaid(
  defineConfig({
    title: "Claude God Mode Template",
    description: "Boilerplate de Claude Code con superpoderes",
    lang: 'es-ES',

    // Para GitHub Pages
    base: '/claude-god-mode-template/',
    srcDir: './src',

    ignoreDeadLinks: true,

    mermaid: {
      theme: 'dark'
    },

    themeConfig: {
      nav: [
        { text: 'Inicio', link: '/' },
        { text: 'Instalación', link: '/instalacion' },
        { text: 'Primeros Pasos', link: '/primeros-pasos' },
        { text: 'Referencia', link: '/referencia' },
      ],

      sidebar: [
        {
          text: '🚀 Getting Started',
          items: [
            { text: 'Instalación', link: '/instalacion' },
            { text: 'Primeros Pasos', link: '/primeros-pasos' },
            { text: 'Comandos Básicos', link: '/makefile' },
            { text: 'Referencia', link: '/referencia' },
          ]
        },
        {
          text: '🛠️ Skills y Agentes',
          collapsed: false,
          items: [
            { text: 'Skills', link: '/skills' },
          ]
        },
        {
          text: '📂 Plantillas y Proyectos',
          collapsed: false,
          items: [
            { text: 'Inicializar un proyecto', link: '/inicializar-proyecto' },
            { text: 'Analizar Proyecto Externo', link: '/analizar-proyecto-externo' },
          ]
        },
        {
          text: '⚙️ Stacks',
          collapsed: true,
          items: [
            { text: 'C++ / CMake', link: '/stacks/cpp' },
            { text: 'Flutter', link: '/stacks/flutter' },
            { text: 'Go API', link: '/stacks/go-api' },
            { text: 'Java / Spring Boot', link: '/stacks/java-springboot' },
            { text: 'Kotlin Multiplatform', link: '/stacks/kotlin-multiplatform' },
            { text: 'Laravel API', link: '/stacks/laravel' },
            { text: 'Laravel Livewire', link: '/stacks/laravel-livewire' },
            { text: 'ML / PyTorch', link: '/stacks/ml-pytorch' },
            { text: 'Next.js SaaS', link: '/stacks/nextjs-saas' },
            { text: 'Nuxt SaaS', link: '/stacks/nuxt-saas' },
            { text: 'Odoo 19', link: '/stacks/odoo' },
            { text: 'Perl', link: '/stacks/perl' },
            { text: 'Python API', link: '/stacks/python-api' },
            { text: 'Rust API', link: '/stacks/rust-api' },
            { text: 'Swift / iOS', link: '/stacks/swift-ios' },
          ]
        },
        {
          text: '📁 Estructura del Repositorio',
          collapsed: true,
          items: [
            { text: 'agents/', link: '/estructura/agents' },
            { text: 'stacks/', link: '/estructura/stacks' },
            { text: 'layers/', link: '/estructura/layers' },
            { text: 'domains/', link: '/estructura/domains' },
            { text: 'skills/', link: '/estructura/skills' },
            { text: 'ops/', link: '/estructura/ops' },
            { text: 'hooks/', link: '/estructura/hooks' },
            { text: '.githooks/', link: '/estructura/githooks' },
            { text: '.claude/', link: '/estructura/claude-config' },
          ]
        },
        {
          text: '📋 Ejemplos',
          collapsed: true,
          items: [
            { text: 'Flujo Feature Laravel+React', link: '/examples/flujo-feature-laravel-react' },
            { text: 'Tutorial: Laravel+React (TaskFlow)', link: '/examples/tutorial-laravel-react' },
            { text: 'Orquestación: GitHub Actions + Antigravity', link: '/examples/orquestacion-laravel-react' },
          ]
        },
        {
          text: '🔧 Para mantenedores',
          collapsed: true,
          items: [
            { text: 'Arquitectura interna', link: '/construccion' },
          ]
        }
      ],

      socialLinks: [
        { icon: 'github', link: 'https://github.com/ggarrido/claude-god-mode-template' }
      ],

      footer: {
        message: 'Claude God Mode Template',
        copyright: 'Copyright © 2026'
      },

      search: {
        provider: 'local'
      },

      editLink: {
        pattern: 'https://github.com/ggarrido/claude-god-mode-template/edit/main/docs/:path',
        text: 'Editar esta página en GitHub'
      },

      lastUpdated: {
        text: 'Última actualización',
        formatOptions: {
          dateStyle: 'short',
          timeStyle: 'short'
        }
      }
    }
  })
)
