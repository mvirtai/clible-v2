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
    define: {
      __APP_VERSION__: JSON.stringify(process.env.npm_package_version ?? '0.0.0'),
    },
    build: {
      outDir: 'dist',
      emptyOutDir: true,
      rollupOptions: {
        output: {
          manualChunks(id) {
            if (!id.includes('node_modules')) return;
            if (id.includes('node_modules/react-dom') || id.includes('node_modules/react/')) {
              return 'vendor-react';
            }
            if (id.includes('node_modules/lucide-react')) return 'vendor-icons';
            if (id.includes('node_modules/motion')) return 'vendor-motion';
            if (id.includes('node_modules/recharts')) return 'vendor-charts';
            if (id.includes('node_modules/d3')) return 'vendor-d3';
            if (
              id.includes('node_modules/react-markdown') ||
              id.includes('node_modules/remark') ||
              id.includes('node_modules/mdast') ||
              id.includes('node_modules/micromark')
            ) {
              return 'vendor-markdown';
            }
          },
        },
      },
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
    test: {
      environment: 'happy-dom',
      setupFiles: './test/setupTests.ts',
      globals: false,
      css: true,
    },
  };
});
