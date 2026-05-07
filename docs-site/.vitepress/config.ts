import { defineConfig } from "vitepress";

const base = process.env.DOCS_BASE ?? "/clible-v2/";

export default defineConfig({
  title: "clible",
  description:
    "Offline-first Bible study tool with full-text search, analytics, and AI insights.",
  lang: "en-US",
  cleanUrls: true,
  lastUpdated: true,

  // GitHub Pages serves the site under the repo path.
  // Override via env var when deploying to a custom domain.
  base,

  head: [
    ["link", { rel: "icon", href: `${base}favicon.svg`, type: "image/svg+xml" }],
    ["meta", { name: "theme-color", content: "#2c3e50" }],
  ],

  markdown: {
    lineNumbers: true,
  },

  themeConfig: {
    siteTitle: "clible docs",

    nav: [
      { text: "Guide", link: "/guide/getting-started" },
      { text: "CLI", link: "/cli/analytics" },
      { text: "Architecture", link: "/architecture/overview" },
      { text: "API", link: "/api/reference" },
      {
        text: "Links",
        items: [
          { text: "GitHub", link: "https://github.com/mvirtai/clible-v2" },
          { text: "Roadmap", link: "/roadmap" },
          { text: "Changelog", link: "/changelog" },
        ],
      },
    ],

    sidebar: {
      "/guide/": [
        {
          text: "Guide",
          items: [
            { text: "Getting started", link: "/guide/getting-started" },
            { text: "Development", link: "/guide/development" },
            { text: "Deployment", link: "/guide/deployment" },
            { text: "Search internals", link: "/guide/search" },
          ],
        },
      ],
      "/cli/": [
        {
          text: "CLI reference",
          items: [
            { text: "Overview", link: "/cli/overview" },
            { text: "seed", link: "/cli/seed" },
            { text: "verse", link: "/cli/verse" },
            { text: "search", link: "/cli/search" },
            { text: "analytics", link: "/cli/analytics" },
            { text: "export", link: "/cli/export" },
          ],
        },
      ],
      "/architecture/": [
        {
          text: "Architecture",
          items: [
            { text: "Overview", link: "/architecture/overview" },
            { text: "Web architecture", link: "/architecture/web" },
            { text: "Project overview", link: "/architecture/project-overview" },
          ],
        },
        {
          text: "Decision records",
          collapsed: false,
          items: [
            {
              text: "ADR-001 Offline-first SQLite",
              link: "/architecture/adr/001-offline-first-sqlite",
            },
            {
              text: "ADR-002 Layered architecture",
              link: "/architecture/adr/002-layered-architecture",
            },
            {
              text: "ADR-003 XML seed parsers",
              link: "/architecture/adr/003-xml-seed-parsers",
            },
            {
              text: "ADR-004 Postgres for user data",
              link: "/architecture/adr/004-postgres-for-user-data",
            },
          ],
        },
      ],
      "/api/": [
        {
          text: "Web API",
          items: [{ text: "Reference", link: "/api/reference" }],
        },
      ],
    },

    socialLinks: [{ icon: "github", link: "https://github.com/mvirtai/clible-v2" }],

    editLink: {
      pattern: "https://github.com/mvirtai/clible-v2/edit/main/docs-site/:path",
      text: "Edit this page on GitHub",
    },

    footer: {
      message: "See NOTICE.md for data sources and acknowledgements.",
      copyright: "© 2025–present Valtteri",
    },

    search: {
      provider: "local",
    },
  },
});

