import tailwindcss from '@tailwindcss/vite';
import react from '@vitejs/plugin-react';
import path from 'path';
import {fileURLToPath} from 'url';
import {defineConfig} from 'vite';

function getDirname(): string {
  // When loaded via Vite itself, import.meta.url is usually a file: URL.
  // When loaded via tsx (server.ts), import.meta.url may use a custom scheme.
  const u = import.meta.url;
  if (typeof u === 'string' && u.startsWith('file:')) {
    return path.dirname(fileURLToPath(u));
  }
  // Fallback: in dev we run from src/clible-web, so cwd is the Vite root.
  return process.cwd();
}

const __dirname = getDirname();

export default defineConfig(({mode}) => {
  const root = path.resolve(__dirname);
  return {
    root,
    plugins: [react(), tailwindcss()],
    build: {
      outDir: 'dist',
      emptyOutDir: true,
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, '.'),
      },
    },
    server: {
      proxy: {
        '/api': {
          target: 'http://localhost:3000',
          changeOrigin: true,
        },
      },
      // HMR is disabled in AI Studio via DISABLE_HMR env var.
      // Do not modify—file watching is disabled to prevent flickering during agent edits.
      hmr: process.env.DISABLE_HMR !== 'true',
    },
  };
});
