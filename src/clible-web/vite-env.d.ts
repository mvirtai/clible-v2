/// <reference types="vite/client" />

declare const __APP_VERSION__: string;

interface ImportMetaEnv {
  /** Root URL of the VitePress site (no trailing slash). Example: https://mvirtai.github.io/clible-v2 */
  readonly VITE_DOCS_SITE_URL?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
