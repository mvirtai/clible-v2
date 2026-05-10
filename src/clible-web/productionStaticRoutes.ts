/**
 * Production-only SPA static file serving with cache semantics for hashed Vite assets.
 */

import express, { type Request, type Response } from "express";
import path from "path";

export function setProductionStaticAssetHeaders(res: Response, filepath: string): void {
  if (path.basename(filepath) === "index.html") {
    res.setHeader("Cache-Control", "no-cache");
    return;
  }
  const assetsDir = `${path.sep}assets${path.sep}`;
  if (filepath.includes(assetsDir)) {
    res.setHeader("Cache-Control", "public, max-age=31536000, immutable");
  }
}

/**
 * Serves {@code rootDir} (Vite {@code dist}) and SPA fallback with correct Cache-Control headers.
 */
export function attachProductionStaticServing(app: express.Application, rootDir: string): void {
  app.use(
    express.static(rootDir, {
      setHeaders: setProductionStaticAssetHeaders,
    }),
  );
  app.get("*", (_req: Request, res: Response) => {
    res.setHeader("Cache-Control", "no-cache");
    res.sendFile(path.join(rootDir, "index.html"));
  });
}
