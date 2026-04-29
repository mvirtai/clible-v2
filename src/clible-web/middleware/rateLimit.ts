/**
 * Simple in-memory rate limiter for beta testing
 * Tracks requests per user session
 */

import { Request, Response, NextFunction } from "express";

interface RateLimitEntry {
  count: number;
  resetAt: number;
}

const store = new Map<string, RateLimitEntry>();

// Cleanup old entries every 5 minutes
setInterval(() => {
  const now = Date.now();
  for (const [key, entry] of store.entries()) {
    if (entry.resetAt < now) {
      store.delete(key);
    }
  }
}, 5 * 60 * 1000);

export function createRateLimiter(options: {
  windowMs: number;
  maxRequests: number;
  message?: string;
}) {
  return (req: Request, res: Response, next: NextFunction) => {
    const userId = (req.session as any)?.userId || req.ip || "anonymous";
    const key = `${userId}:${req.path}`;
    const now = Date.now();

    let entry = store.get(key);

    if (!entry || entry.resetAt < now) {
      entry = {
        count: 0,
        resetAt: now + options.windowMs,
      };
      store.set(key, entry);
    }

    entry.count++;

    const remaining = Math.max(0, options.maxRequests - entry.count);
    const resetIn = Math.ceil((entry.resetAt - now) / 1000);

    res.setHeader("X-RateLimit-Limit", options.maxRequests);
    res.setHeader("X-RateLimit-Remaining", remaining);
    res.setHeader("X-RateLimit-Reset", resetIn);

    if (entry.count > options.maxRequests) {
      return res.status(429).json({
        error: options.message || "Too many requests",
        retryAfter: resetIn,
      });
    }

    next();
  };
}
