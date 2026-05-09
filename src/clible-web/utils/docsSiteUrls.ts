/** Published docs site (VitePress in docs-site/). Set VITE_DOCS_SITE_URL for a fork or custom domain. */
const DEFAULT_DOCS_SITE = 'https://mvirtai.github.io/clible-v2';

function trimTrailingSlashes(s: string): string {
  return s.replace(/\/+$/, '');
}

const configured =
  typeof import.meta.env.VITE_DOCS_SITE_URL === 'string' ? import.meta.env.VITE_DOCS_SITE_URL.trim() : '';

export const docsSiteRootUrl = trimTrailingSlashes(configured || DEFAULT_DOCS_SITE);

/** Landing page / welcome — GitHub Pages + base `/clible-v2/` */
export const docsSiteHomeUrl = `${docsSiteRootUrl}/`;

/** OpenAPI / Redoc API reference */
export const docsSiteApiReferenceUrl = `${docsSiteRootUrl}/api/reference`;
