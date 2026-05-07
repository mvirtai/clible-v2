/**
 * Copies the canonical OpenAPI spec into the docs site's public folder
 * so Redoc can fetch it as a static asset at runtime.
 *
 * The spec lives in docs/api/openapi.yml at the repo root and is the single
 * source of truth — never edit the copy under docs-site/public/.
 */

import { copyFile, mkdir } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(here, "..", "..");

const source = resolve(repoRoot, "docs", "api", "openapi.yml");
const targetDir = resolve(here, "..", "public", "api");
const target = resolve(targetDir, "openapi.yml");

await mkdir(targetDir, { recursive: true });
await copyFile(source, target);

console.log(`[docs] synced openapi.yml -> ${target}`);
