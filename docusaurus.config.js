// @ts-check
// Libra OS — documentation + blog. SEO-friendly static build; emits llms.txt for agents.
const {themes: prismThemes} = require('prism-react-renderer');

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Libra OS',
  tagline: 'The Operating System for the AI Workforce — one sovereign AI layer over everything your company knows',
  favicon: 'img/favicon.png',

  // Public site lives under libraos.com/docs/ (Caddy serves the static build there).
  url: 'https://libraos.com',
  baseUrl: '/docs/',
  trailingSlash: true,

  organizationName: 'libraos',
  projectName: 'docs',

  onBrokenLinks: 'warn',
  markdown: {
    hooks: {
      onBrokenMarkdownLinks: 'warn',
    },
  },

  i18n: {defaultLocale: 'en', locales: ['en']},

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          routeBasePath: '/',                 // docs at /docs/
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/libraos/docs/edit/main/',
          showLastUpdateTime: true,
        },
        blog: {
          routeBasePath: 'blog',              // blog at /docs/blog/
          blogTitle: 'Libra OS blog',
          blogDescription: 'Product notes and updates from the Libra OS team.',
          showReadingTime: true,
          feedOptions: {type: ['rss', 'atom'], xslt: true},
          onInlineTags: 'warn',
          onInlineAuthors: 'warn',
          onUntruncatedBlogPosts: 'warn',
        },
        theme: {customCss: require.resolve('./src/css/custom.css')},
        // SEO: XML sitemap generated at /docs/sitemap.xml
        sitemap: {changefreq: 'weekly', priority: 0.5, filename: 'sitemap.xml'},
        // Google Analytics on every page (production build only).
        gtag: {trackingID: 'G-6VRK11VQNW', anonymizeIP: true},
      }),
    ],
  ],

  // llms.txt + llms-full.txt for AI agents (grounds the desk help widget too).
  plugins: [
    [
      '@docusaurus/plugin-client-redirects',
      {
        redirects: [
          { from: ['/user-guide/overview', '/category/user-guide'], to: '/' },
        ],
      },
    ],
    [
      'docusaurus-plugin-llms',
      {
        generateLLMsTxt: true,
        generateLLMsFullTxt: true,
        docsDir: 'docs',
        includeBlog: true,
        title: 'Libra OS',
        description: 'The operating system for the AI workforce — one sovereign AI layer over everything your company knows. Runs on your own hardware, air-gapped if you want.',
      },
    ],
  ],

  themeConfig: {
    image: 'img/libraos-icon-white.svg',
    metadata: [
      {name: 'keywords', content: 'sovereign AI, on-prem AI, air-gapped AI, AI operating system, AI workforce, Libra OS, digital employees'},
      {name: 'robots', content: 'index, follow'},
    ],
    colorMode: {defaultMode: 'dark', respectPrefersColorScheme: true},
    navbar: {
      title: 'Libra OS',
      logo: {alt: 'Libra OS', src: 'img/libraos-icon-black.svg', srcDark: 'img/libraos-icon-white.svg'},
      items: [
        {type: 'docSidebar', sidebarId: 'docsSidebar', position: 'left', label: 'Docs'},
        {to: '/blog', label: 'Blog', position: 'left'},
        {href: 'https://libraos.com/download/', label: 'Download', position: 'right'},
        {href: 'https://libraos.com/', label: 'libraos.com', position: 'right'},
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {label: 'Getting started', to: '/getting-started'},
            {label: 'Deployment', to: '/deployment'},
            {label: 'Security', to: '/security'},
          ],
        },
        {
          title: 'Product',
          items: [
            {label: 'libraos.com', href: 'https://libraos.com/'},
            {label: 'Download', href: 'https://libraos.com/download/'},
            {label: 'Pricing', href: 'https://libraos.com/pricing/'},
          ],
        },
        {
          title: 'Community',
          items: [
            {label: 'Report a bug', href: 'https://github.com/libraos/community'},
            {label: 'SDK', href: 'https://github.com/libraos/sdk'},
            {label: 'Contact', href: 'mailto:contact@meganova.ai'},
          ],
        },
      ],
      copyright: `© 2023–${new Date().getFullYear()} Nebula Nova Inc. Libra OS — the operating system for the AI workforce. One sovereign AI layer over everything your company knows.`,
    },
    prism: {theme: prismThemes.oneLight, darkTheme: prismThemes.oneDark},
  },
};

module.exports = config;
