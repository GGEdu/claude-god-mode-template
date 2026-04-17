import { defineConfig } from 'vitepress';

export default defineConfig({
  title: "__PROJECT_NAME__",
  description: "__PROJECT_DESCRIPTION__",
  lang: 'es-ES',

  base: '/',
  srcDir: './src',

  ignoreDeadLinks: true,

  themeConfig: {
    nav: [
      { text: 'Inicio', link: '/' },
      { text: 'Getting Started', link: '/getting-started' },
      { text: 'Arquitectura', link: '/architecture' },
    ],

    sidebar: [
      {
        text: '🚀 Getting Started',
        items: [
          { text: 'Inicio', link: '/' },
          { text: 'Getting Started', link: '/getting-started' },
          { text: 'Arquitectura', link: '/architecture' },
        ]
      },
      {
        text: '📚 Wiki',
        collapsed: false,
        items: [
          { text: 'Índice', link: '/wiki/' },
          { text: 'Overview', link: '/wiki/overview' },
          { text: 'Glosario', link: '/wiki/glossary' },
          { text: 'Log', link: '/wiki/log' },
        ]
      },
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/__GITHUB_USER__/__PROJECT_NAME__' }
    ]
  }
});
