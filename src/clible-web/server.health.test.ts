import request from "supertest";
import { beforeEach, describe, expect, it } from "vitest";
import { buildExpressApplication } from "./server";

describe("buildExpressApplication /health", () => {
  beforeEach(() => {
    // Match dev server: static block and trust proxy stay off outside production.
    process.env.NODE_ENV = "test";
    delete process.env.CLIBLE_WEB_DIST;
  });

  it("returns 200 JSON and applies security headers", async () => {
    const app = buildExpressApplication();
    const res = await request(app).get("/health").expect(200);
    expect(res.body).toEqual({ status: "ok" });
    expect(res.headers["x-content-type-options"]).toBe("nosniff");
  });
});
