import { describe, expect, it, vi, beforeEach } from "vitest";

import { requireAdmin, requireAiAccess } from "./userAccess";

vi.mock("../db/pool.js", () => {
  return {
    pool: {
      query: vi.fn(),
    },
  };
});

// Import after mock so the module sees the mocked pool.
import { pool } from "../db/pool.js";

function mockRes() {
  const res: any = {};
  res.status = vi.fn().mockReturnValue(res);
  res.json = vi.fn().mockReturnValue(res);
  return res;
}

describe("auth/userAccess", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("requireAiAccess returns 401 when not authenticated", async () => {
    const req: any = { session: {} };
    const res = mockRes();
    const next = vi.fn();

    await requireAiAccess(req, res as any, next);

    expect(res.status).toHaveBeenCalledWith(401);
    expect(next).not.toHaveBeenCalled();
  });

  it("requireAiAccess returns 403 when ai_access is false", async () => {
    (pool.query as any).mockResolvedValueOnce({
      rows: [{ id: "u1", username: "x", ai_access: false, is_admin: false }],
    });

    const req: any = { session: { userId: "u1" } };
    const res = mockRes();
    const next = vi.fn();

    await requireAiAccess(req, res as any, next);

    expect(res.status).toHaveBeenCalledWith(403);
    expect(next).not.toHaveBeenCalled();
  });

  it("requireAiAccess calls next when ai_access is true", async () => {
    (pool.query as any).mockResolvedValueOnce({
      rows: [{ id: "u1", username: "x", ai_access: true, is_admin: false }],
    });

    const req: any = { session: { userId: "u1" } };
    const res = mockRes();
    const next = vi.fn();

    await requireAiAccess(req, res as any, next);

    expect(next).toHaveBeenCalledTimes(1);
  });

  it("requireAdmin returns 403 when is_admin is false", async () => {
    (pool.query as any).mockResolvedValueOnce({
      rows: [{ id: "u1", username: "x", ai_access: true, is_admin: false }],
    });

    const req: any = { session: { userId: "u1" } };
    const res = mockRes();
    const next = vi.fn();

    await requireAdmin(req, res as any, next);

    expect(res.status).toHaveBeenCalledWith(403);
    expect(next).not.toHaveBeenCalled();
  });

  it("requireAdmin calls next when is_admin is true", async () => {
    (pool.query as any).mockResolvedValueOnce({
      rows: [{ id: "u1", username: "x", ai_access: false, is_admin: true }],
    });

    const req: any = { session: { userId: "u1" } };
    const res = mockRes();
    const next = vi.fn();

    await requireAdmin(req, res as any, next);

    expect(next).toHaveBeenCalledTimes(1);
  });
});

