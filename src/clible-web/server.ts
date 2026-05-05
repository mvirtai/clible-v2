/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import "./load-env";
import express, { type Request, type Response, type NextFunction } from "express";
import { exec, spawn } from "child_process";
import { promisify } from "util";
import path from "path";
import { GoogleGenAI } from "@google/genai";
import {
  buildInsightUserPrompt,
  buildOriginalStudyPrompt,
  buildStudyUserPrompt,
  buildToneUserPrompt,
  geminiModels,
  insightSystemInstruction,
  originalStudySystemInstruction,
  studySystemInstruction,
  toneSystemInstruction,
} from "./ai.config";

import session from "express-session";
import connectPgSimple from "connect-pg-simple";
import { pool } from "./db/pool";
import { runMigrations } from "./db/migrate";
import { authRouter } from "./auth/routes";
import { requireAuth } from "./auth/middleware";
import { settingsRouter } from "./user/settings_routes";
import { createRateLimiter } from "./middleware/rateLimit";

const execAsync = promisify(exec);
const PgSession = connectPgSimple(session);

/** Normalize GEMINI_API_KEY from env / Docker --env-file (trim, strip wrapping quotes). */
function normalizeGeminiApiKey(raw: string | undefined): string | undefined {
  if (raw == null) return undefined;
  let s = raw.trim();
  if (!s) return undefined;
  if (
    (s.startsWith('"') && s.endsWith('"')) ||
    (s.startsWith("'") && s.endsWith("'"))
  ) {
    s = s.slice(1, -1).trim();
  }
  return s || undefined;
}

function parseClibleArgTokens(sanitized: string): string[] {
  return (
    sanitized
      .match(/(?:[^\s"]+|"[^"]*")+/g)
      ?.map((s) => s.replace(/^"(.*)"$/, "$1"))
      .filter(Boolean) ?? []
  );
}

function buildClibleArgv(cmd: string, tokens: string[]): string[] {
  const argv = [cmd, ...tokens];
  const isExport = tokens.some((t) => t.includes("--stdout-export"));

  if (!isExport) {
    if (cmd === "verse" || cmd === "search" || cmd === "analytics") {
      argv.push("--json");
    } else if (cmd === "seed" && tokens[0] === "list") {
      argv.push("--json");
    }
  }
  return argv;
}

function stripAnsi(text: string): string {
  return text.replace(/\x1b\[[0-9;]*m/g, "").trim();
}

function clibleFailureMessage(
  err: Error & { code?: number; stdout?: string; stderr?: string }
): string {
  const combined = `${err.stderr ?? ""}\n${err.stdout ?? ""}`.trim();
  if (combined) return stripAnsi(combined);
  return stripAnsi(err.message);
}

function conciseClibleError(message: string): string {
  if (message.includes("database is locked")) {
    return "Server database is busy. Please retry in a few seconds.";
  }
  const firstUsefulLine =
    message
      .split("\n")
      .map((line) => line.trim())
      .find(
        (line) =>
          line.length > 0 &&
          !line.startsWith("Traceback") &&
          !line.startsWith("File ")
      ) ?? "";
  return firstUsefulLine || "Unexpected CLI error.";
}

function buildSeedAvailableArgs(query?: string): string[] {
  const args = ["seed", "available", "--json", "--limit", "0"];
  if (query && query.trim()) {
    args.push("--query", query.trim());
  }
  return args;
}

function isValidTranslationId(value: string): boolean {
  return /^[a-z0-9][a-z0-9-]{0,63}$/i.test(value);
}

type AvailableTranslation = {
  id: string;
  name: string;
  language: string;
  format: string;
  size_mb?: number | null;
};

function parseAvailableTranslations(stdout: string): AvailableTranslation[] {
  const parsed = JSON.parse(stdout) as unknown;
  if (!Array.isArray(parsed)) {
    throw new Error("Invalid JSON output from seed available.");
  }
  return parsed as AvailableTranslation[];
}

function runClible(argv: string[]): Promise<{ stdout: string; stderr: string }> {
  return new Promise((resolve, reject) => {
    const child = spawn("clible", argv, {
      env: process.env,
    });
    let stdout = "";
    let stderr = "";
    child.stdout.setEncoding("utf8");
    child.stderr.setEncoding("utf8");
    child.stdout.on("data", (chunk) => {
      stdout += chunk;
    });
    child.stderr.on("data", (chunk) => {
      stderr += chunk;
    });
    child.on("error", reject);
    child.on("close", (code) => {
      if (code === 0) {
        resolve({ stdout, stderr });
      } else {
        const err = new Error(`clible exited with code ${code}`) as Error & {
          code: number;
          stdout?: string;
          stderr?: string;
        };
        err.code = code ?? 1;
        err.stdout = stdout;
        err.stderr = stderr;
        reject(err);
      }
    });
  });
}

let seedClibleQueue: Promise<void> = Promise.resolve();

/**
 * Serialize seed commands to avoid SQLite lock races (startup auto-seed vs UI install/list).
 */
function runClibleWithSeedLock(argv: string[]): Promise<{ stdout: string; stderr: string }> {
  if (argv[0] !== "seed") {
    return runClible(argv);
  }

  const run = async () => runClible(argv);
  const next = seedClibleQueue.then(run, run);
  seedClibleQueue = next.then(
    () => undefined,
    () => undefined,
  );
  return next;
}

async function seedTranslationsOnStartup(): Promise<void> {
  const raw = process.env.CLIBLE_AUTO_SEED?.trim();
  if (!raw) return;

  const ids = raw
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);

  if (ids.length === 0) return;

  console.log(`[seed] auto-seeding ${ids.length} translation(s): ${ids.join(", ")}`);

  for (const id of ids) {
    try {
      const { stdout, stderr } = await runClibleWithSeedLock(["seed", "install", id]);
      const msg = stripAnsi(`${stdout}\n${stderr}`).trim();
      console.log(`[seed] installed ${id}: ${msg.split("\n")[0]}`);
    } catch (err: any) {
      const msg = clibleFailureMessage(err);
      if (msg.toLowerCase().includes("already installed")) {
        console.log(`[seed] ${id}: already installed, skipping`);
      } else {
        console.warn(`[seed] failed to install ${id}: ${msg.split("\n")[0]}`);
      }
    }
  }

  console.log("[seed] auto-seed complete");
}

function getAiClientOrNull(): GoogleGenAI | null {
  // Prefer beta key if set, fallback to regular key
  const apiKey = normalizeGeminiApiKey(
    process.env.GEMINI_API_KEY_FOR_BETA_TESTERS || process.env.GEMINI_API_KEY
  );
  if (!apiKey) return null;
  return new GoogleGenAI({ apiKey });
}

function getSessionSecret(): string {
  const raw = process.env.SESSION_SECRET;
  const normalized = typeof raw === "string" ? raw.trim() : "";
  return normalized || "dev-secret-change-in-production";
}

async function startServer() {
  const app = express();
  const PORT = parseInt(process.env.PORT || "3000");
  const isProduction = process.env.NODE_ENV === "production";

  // Cloud Run terminates TLS before forwarding traffic to Express.
  // trust proxy is required so secure session cookies can be set.
  if (isProduction) {
    app.set("trust proxy", 1);
  }

  app.use(express.json());

  app.get("/health", (_req, res) => {
    res.status(200).json({ status: "ok" });
  });

  app.use(
    session({
      store: new PgSession({
        pool,
        tableName: "sessions",
        // Expired sessions are pruned every hour.
        pruneSessionInterval: 60 * 60,
      }),
      secret: getSessionSecret(),
      resave: false,
      saveUninitialized: false,
      cookie: {
        httpOnly: true,
        secure: isProduction,
        sameSite: "lax",
        maxAge: 24 * 60 * 60 * 1000,
      },
    })
  );

  // Auth routes (no auth required)
  app.use("/api/auth", authRouter);

  // Authenticated user settings
  app.use("/api/user/settings", settingsRouter);

  // Rate limiters for AI endpoints
  const aiRateLimit = createRateLimiter({
    windowMs: 60 * 60 * 1000, // 1 hour
    maxRequests: parseInt(process.env.MAX_REQUESTS_PER_HOUR || "20"),
    message: "AI request limit reached. Please try again later.",
  });

  app.post("/api/ai/insight", requireAuth, aiRateLimit, async (req, res) => {
    const ai = getAiClientOrNull();
    if (!ai) {
      return res.status(503).json({
        error: "AI disabled",
        hint: "Set GEMINI_API_KEY to enable AI features.",
      });
    }

    const text = typeof req.body?.text === "string" ? req.body.text : "";
    if (!text.trim()) {
      return res.status(400).json({ error: "Missing or invalid 'text'." });
    }

    try {
      const response = await ai.models.generateContent({
        model: geminiModels.insight,
        contents: buildInsightUserPrompt(text),
        config: {
          systemInstruction: insightSystemInstruction,
        },
      });

      res.json({ text: response.text ?? "" });
    } catch (error: any) {
      console.error("AI insight error:", error);
      res.status(500).json({
        error: "Failed to generate AI insight",
        details: error?.message ?? String(error),
      });
    }
  });

  app.post("/api/ai/tone", requireAuth, aiRateLimit, async (req, res) => {
    const ai = getAiClientOrNull();
    if (!ai) {
      return res.status(503).json({
        error: "AI disabled",
        hint: "Set GEMINI_API_KEY to enable AI features.",
      });
    }

    const text = typeof req.body?.text === "string" ? req.body.text : "";
    if (!text.trim()) {
      return res.status(400).json({ error: "Missing or invalid 'text'." });
    }

    try {
      const response = await ai.models.generateContent({
        model: geminiModels.tone,
        contents: buildToneUserPrompt(text),
        config: {
          systemInstruction: toneSystemInstruction,
        },
      });

      res.json({ text: response.text ?? "" });
    } catch (error: any) {
      console.error("AI tone error:", error);
      res.status(500).json({
        error: "Failed to analyze tone",
        details: error?.message ?? String(error),
      });
    }
  });

  app.post("/api/ai/study", requireAuth, aiRateLimit, async (req, res) => {
    const ai = getAiClientOrNull();
    if (!ai) {
      return res.status(503).json({
        error: "AI disabled",
        hint: "Set GEMINI_API_KEY to enable AI features.",
      });
    }

    const reference = typeof req.body?.reference === "string" ? req.body.reference.trim() : "";
    const sourceText =
      typeof req.body?.sourceText === "string" ? req.body.sourceText.trim() : "";
    const translationText =
      typeof req.body?.translationText === "string" ? req.body.translationText.trim() : "";
    const rawLang =
      typeof req.body?.sourceLanguage === "string" ? req.body.sourceLanguage.trim().toLowerCase() : "";
    const sourceLanguage = rawLang === "he" || rawLang.startsWith("hbo") || rawLang.startsWith("heb")
      ? "he"
      : "grc";

    if (!reference || !sourceText || !translationText) {
      return res.status(400).json({
        error: "Missing or invalid payload. Provide 'reference', 'sourceText', and 'translationText'.",
      });
    }

    try {
      const response = await ai.models.generateContent({
        model: geminiModels.study,
        contents: buildStudyUserPrompt({
          reference,
          sourceLanguage,
          sourceText,
          translationText,
        }),
        config: {
          systemInstruction: studySystemInstruction,
        },
      });

      res.json({ text: response.text ?? "" });
    } catch (error: any) {
      console.error("AI study error:", error);
      res.status(500).json({
        error: "Failed to generate study analysis",
        details: error?.message ?? String(error),
      });
    }
  });

  app.get("/api/translations/available", requireAuth, async (req, res) => {
    const query = typeof req.query?.query === "string" ? req.query.query : undefined;
    try {
      const { stdout } = await runClibleWithSeedLock(buildSeedAvailableArgs(query));
      const items = parseAvailableTranslations(stdout);
      res.json(items);
    } catch (error: any) {
      const msg = clibleFailureMessage(error);
      if (msg.includes("Invalid JSON")) {
        return res.status(500).json({
          error: "Failed to parse available translations.",
          details: conciseClibleError(msg),
        });
      }
      return res.status(500).json({
        error: "Failed to fetch available translations.",
        details: conciseClibleError(msg),
      });
    }
  });

  app.post("/api/translations/install", requireAuth, async (req, res) => {
    const translationId = typeof req.body?.translationId === "string" ? req.body.translationId.trim() : "";
    if (!translationId) {
      return res.status(400).json({ error: "Missing 'translationId'." });
    }
    if (!isValidTranslationId(translationId)) {
      return res.status(400).json({ error: "Invalid translation ID format." });
    }

    try {
      const { stdout, stderr } = await runClibleWithSeedLock(["seed", "install", translationId]);
      const message = stripAnsi(`${stdout}\n${stderr}`).trim() || `Installed ${translationId}.`;
      return res.json({
        ok: true,
        translationId,
        message,
      });
    } catch (error: any) {
      const msg = clibleFailureMessage(error);
      if (msg.toLowerCase().includes("already installed")) {
        return res.json({
          ok: true,
          translationId,
          alreadyInstalled: true,
          message: `Translation '${translationId}' already installed.`,
        });
      }
      if (msg.toLowerCase().includes("unknown translation")) {
        return res.status(400).json({
          error: `Unknown translation '${translationId}'.`,
          details: conciseClibleError(msg),
        });
      }
      return res.status(500).json({
        error: `Failed to install translation '${translationId}'.`,
        details: conciseClibleError(msg),
      });
    }
  });

  app.get("/api/search/history", requireAuth, async (_req, res) => {
    try {
      const { stdout } = await runClible(["search", "--history", "--json"]);
      res.json(JSON.parse(stdout.trim()));
    } catch (error: unknown) {
      console.error("search history:", error);
      res.status(500).json({ error: "Failed to fetch search history" });
    }
  });

  app.delete("/api/search/history", requireAuth, async (_req, res) => {
    try {
      const { stdout } = await runClible(["search", "--clear-history", "--json"]);
      res.json(JSON.parse(stdout.trim()));
    } catch (error: unknown) {
      console.error("clear search history:", error);
      res.status(500).json({ error: "Failed to clear search history" });
    }
  });

  app.get("/api/saved-searches", requireAuth, async (_req, res) => {
    try {
      const { stdout } = await runClible(["saved", "search", "list", "--json"]);
      res.json(JSON.parse(stdout.trim()));
    } catch (error: unknown) {
      console.error("list saved searches:", error);
      res.status(500).json({ error: "Failed to list saved searches" });
    }
  });

  app.delete("/api/saved-searches/:id", requireAuth, async (req, res) => {
    const id = typeof req.params.id === "string" ? req.params.id.trim() : "";
    if (!id) {
      return res.status(400).json({ error: "Missing id." });
    }
    try {
      await runClible(["saved", "search", "delete", id]);
      return res.json({ ok: true });
    } catch (error: unknown) {
      console.error("delete saved search:", error);
      return res.status(500).json({ error: "Failed to delete saved search" });
    }
  });

  app.post("/api/saved-searches", requireAuth, async (req, res) => {
    const body = req.body as Record<string, unknown>;
    const name = typeof body.name === "string" ? body.name.trim() : "";
    if (!name) {
      return res.status(400).json({ error: "Missing 'name'." });
    }
    const terms = Array.isArray(body.terms)
      ? (body.terms as unknown[]).map((t) => String(t).trim()).filter((s) => s.length > 0)
      : [];
    if (terms.length === 0) {
      return res.status(400).json({ error: "Missing 'terms'." });
    }
    const translationId = typeof body.translationId === "string" ? body.translationId.trim() : "";
    if (!translationId || !isValidTranslationId(translationId)) {
      return res.status(400).json({ error: "Invalid or missing 'translationId'." });
    }
    const modeRaw = typeof body.mode === "string" ? body.mode.toLowerCase() : "phrase";
    if (!["phrase", "words", "wildcard"].includes(modeRaw)) {
      return res.status(400).json({ error: "Invalid 'mode'." });
    }
    const operator = typeof body.operator === "string" ? body.operator.toLowerCase() : "and";
    const scope = typeof body.scope === "string" ? body.scope : "bible";
    const book = body.book == null || body.book === "" ? null : String(body.book);

    const argv: string[] = ["search"];
    if (modeRaw === "words") {
      for (const t of terms) {
        argv.push(t);
      }
    } else {
      argv.push(terms.join(" "));
    }
    argv.push("-t", translationId, "--mode", modeRaw);
    if (modeRaw === "words") {
      argv.push("--operator", operator);
    }
    if (scope === "ot") {
      argv.push("--ot");
    } else if (scope === "nt") {
      argv.push("--nt");
    } else if (scope === "book" && book) {
      argv.push("--book", book);
    }
    argv.push("--save", name);

    try {
      await runClible(argv);
      return res.json({ ok: true, name });
    } catch (error: unknown) {
      console.error("save search:", error);
      return res.status(500).json({ error: "Failed to save search" });
    }
  });

  // Original-language study: multi-translation comparison with phonetic transliteration.
  app.post("/api/ai/original-study", requireAuth, aiRateLimit, async (req, res) => {
    const ai = getAiClientOrNull();
    if (!ai) return res.status(503).json({ error: "AI disabled", hint: "Set GEMINI_API_KEY." });
  
    const { reference, sourceText, sourceLanguage, translations } = req.body as {
      reference?: string;
      sourceText?: string;
      sourceLanguage?: string;
      translations?: Array<{ id: string; name: string; text: string }>;
    };
  
    if (!reference?.trim() || !sourceText?.trim() || !Array.isArray(translations) || translations.length === 0) {
      return res.status(400).json({ error: "Missing required fields." });
    }
    const lang = sourceLanguage === "he" ? "he" : "grc";
  
    try {
      const response = await ai.models.generateContent({
        model: geminiModels.originalStudy,
        contents: buildOriginalStudyPrompt({ reference, sourceText, sourceLanguage: lang, translations }),
        config: { systemInstruction: originalStudySystemInstruction },
      });
      res.json({ text: response.text ?? "" });
    } catch (error: any) {
      res.status(500).json({ error: "Failed to generate original study", details: error?.message });
    }
  });

  /**
   * API Bridge to Clible CLI
   * This endpoint executes the local 'clible' command and returns its output.
   * Example: /api/clible?cmd=verse&args=John+3:16
   */
  app.get("/api/clible", requireAuth, async (req, res) => {
    const { cmd, args } = req.query;
    
    if (!cmd || typeof cmd !== 'string') {
      return res.status(400).json({ error: "Missing or invalid command" });
    }

    // Allow only specific clible commands
    const allowedCommands = ["verse", "search", "analytics", "seed"];
    if (!allowedCommands.includes(cmd)) {
      return res.status(403).json({ error: `Command '${cmd}' is not allowed.` });
    }

    try {
      const sanitizedArgs = (args as string || "").replace(/[;&|`$<>`]/g, "");
      const tokens = parseClibleArgTokens(sanitizedArgs);
      const argv = buildClibleArgv(cmd, tokens);

      const debugBridge = process.env.NODE_ENV !== "production";
      if (debugBridge) {
        console.log("[clible-web] bridge: argv", ["clible", ...argv].join(" "));
      }

      const { stdout, stderr } = await runClibleWithSeedLock(argv);

      if (debugBridge) {
        console.log(
          "[clible-web] bridge: stdout chars",
          stdout.length,
          "stderr chars",
          stderr.length
        );
      }

      if (stderr && !stdout.trim()) {
        return res.status(500).json({ error: stderr });
      }

      const isExport = tokens.some((t) => t.includes("--stdout-export"));
      if (isExport) {
        // Return raw content for exports
        const formatMatch = sanitizedArgs.match(/--stdout-export\s+(\w+)/i);
        const format = formatMatch ? formatMatch[1].toLowerCase() : "txt";
        
        const contentTypes: Record<string, string> = {
          html: "text/html",
          json: "application/json",
          csv: "text/csv",
          xml: "application/xml",
          md: "text/markdown",
        };
        
        res.setHeader("Content-Type", contentTypes[format] || "text/plain");
        return res.send(stdout);
      }

      try {
        const parsed = JSON.parse(stdout);
        if (debugBridge) {
          console.log(
            "[clible-web] bridge: JSON ok, top-level keys",
            parsed && typeof parsed === "object" && !Array.isArray(parsed)
              ? Object.keys(parsed as object)
              : "(array or primitive)"
          );
        }
        res.json(parsed);
      } catch {
        if (debugBridge) {
          console.warn(
            "[clible-web] bridge: stdout is not valid JSON (first 200 chars):",
            stdout.slice(0, 200)
          );
        }
        res.status(500).json({
          error: "Invalid JSON output from Clible CLI",
          rawOutput: stdout,
        });
      }
    } catch (error: any) {
      const msg = clibleFailureMessage(error);
      const code = error.code ?? 1;
      if (
        code === 1 &&
        (msg.includes("not found") || msg.includes("Verse(s) not found"))
      ) {
        return res.status(404).json({
          error: msg,
          hint: "Install a translation in the container, e.g. clible seed install web",
        });
      }
      console.error("CLI Error:", error);
      res.status(500).json({
        error: "Failed to execute Clible CLI",
        details: conciseClibleError(msg),
        hint: "Make sure 'clible' is installed and in your PATH.",
      });
    }
  });

  app.use("/api", (_req: Request, res: Response) => {
    res.status(404).json({ error: "Not found" });
  });

  // Static assets in production only. In development, run Vite as a separate dev server
  // and proxy /api/* requests to this server.
  if (process.env.NODE_ENV === "production") {
    const distPath = path.join(process.cwd(), 'dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.use((err: Error, req: Request, res: Response, _next: NextFunction) => {
    console.error(
      JSON.stringify({
        event: "unhandled_error",
        message: err.message,
        path: req.path,
        method: req.method,
        timestamp: new Date().toISOString(),
      })
    );
    if (res.headersSent) {
      return;
    }
    res.status(500).json({ error: "Internal server error" });
  });

  app.listen(PORT, "0.0.0.0", async () => {
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`API Bridge active at /api/clible`);

    // Run DB migrations after the server is already listening so Cloud Run's
    // health check can succeed even if migrations take a few seconds.
    try {
      await runMigrations();
      console.log("[migrate] all migrations applied");
    } catch (err) {
      console.error("[migrate] failed:", (err as Error).message);
      process.exit(1);
    }

    // Check if clible is available
    try {
      const { stdout } = await execAsync("clible --help");
      // Only print first line to keep startup logs compact.
      const firstLine = stdout.split("\n").find(Boolean) ?? "clible available";
      console.log(`Clible CLI detected: ${firstLine}`);
    } catch (e) {
      console.warn("WARNING: 'clible' CLI not found in PATH. API bridge will fail.");
    }

    // Seed translations declared in CLIBLE_AUTO_SEED (comma-separated IDs).
    // Runs after the server is listening so health checks are not delayed.
    // Already-installed translations are skipped silently.
    seedTranslationsOnStartup().catch((err) => {
      console.warn("[seed] unexpected error during auto-seed:", (err as Error).message);
    });
  });
}

startServer().catch((err) => {
  console.error("Failed to start server:", err);
  process.exit(1);
});
