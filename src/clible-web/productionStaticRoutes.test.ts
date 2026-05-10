import path from "path";
import fs from "fs";
import os from "os";
import express from "express";
import compression from "compression";
import helmet from "helmet";
import request from "supertest";
import { describe, expect, it, vi } from "vitest";
import type { Response } from "express";
import {
  attachProductionStaticServing,
  setProductionStaticAssetHeaders,
} from "./productionStaticRoutes";

describe("setProductionStaticAssetHeaders", () => {
  it("sets no-cache when the file is index.html", () => {
    const setHeader = vi.fn();
    const res = { setHeader } as unknown as Response;
    setProductionStaticAssetHeaders(res, `/app/dist${path.sep}index.html`);
    expect(setHeader).toHaveBeenCalledTimes(1);
    expect(setHeader).toHaveBeenCalledWith("Cache-Control", "no-cache");
  });

  it("sets long immutable cache for hashed files under assets/", () => {
    const setHeader = vi.fn();
    const res = { setHeader } as unknown as Response;
    const fp = path.join("/app", "dist", "assets", "index-Ab3f9c1.js");
    setProductionStaticAssetHeaders(res, fp);
    expect(setHeader).toHaveBeenCalledTimes(1);
    expect(setHeader).toHaveBeenCalledWith(
      "Cache-Control",
      "public, max-age=31536000, immutable",
    );
  });

  it("does not set Cache-Control for other root files", () => {
    const setHeader = vi.fn();
    const res = { setHeader } as unknown as Response;
    setProductionStaticAssetHeaders(res, `/app/dist${path.sep}robots.txt`);
    expect(setHeader).not.toHaveBeenCalled();
  });
});

function buildTmpDist(): string {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), "clible-web-dist-"));
  fs.writeFileSync(path.join(dir, "index.html"), "<!doctype html><html><body>x</body></html>");
  fs.mkdirSync(path.join(dir, "assets"));
  // compression middleware defaults to a 1KiB minimum response size
  fs.writeFileSync(
    path.join(dir, "assets", "main-abc123.js"),
    `console.log("${"x".repeat(1200)}");`,
  );
  return dir;
}

describe("attachProductionStaticServing", () => {
  it("serves hashed assets with immutable cache and compresses when accepted", async () => {
    const dist = buildTmpDist();
    const app = express();
    app.use(
      helmet({
        contentSecurityPolicy: false,
        crossOriginEmbedderPolicy: false,
      }),
    );
    app.use(compression());
    attachProductionStaticServing(app, dist);

    const res = await request(app)
      .get("/assets/main-abc123.js")
      .set("Accept-Encoding", "gzip")
      .expect(200);

    expect(res.headers["cache-control"]).toBe("public, max-age=31536000, immutable");
    expect(res.headers["content-encoding"]).toBe("gzip");

    await fs.promises.rm(dist, { recursive: true, force: true });
  });

  it("serves index.html with no-cache and SPA fallback applies to unknown paths", async () => {
    const dist = buildTmpDist();
    const app = express();
    app.use(
      helmet({
        contentSecurityPolicy: false,
        crossOriginEmbedderPolicy: false,
      }),
    );
    app.use(compression());
    attachProductionStaticServing(app, dist);

    const indexRes = await request(app).get("/index.html").expect(200);
    expect(indexRes.headers["cache-control"]).toBe("no-cache");

    const spaRes = await request(app).get("/any/deep/route").expect(200);
    expect(spaRes.headers["cache-control"]).toBe("no-cache");
    expect(spaRes.text).toContain("<body>x</body>");

    await fs.promises.rm(dist, { recursive: true, force: true });
  });
});
