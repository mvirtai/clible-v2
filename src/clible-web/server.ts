/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import express from "express";
import { exec, spawn } from "child_process";
import { promisify } from "util";
import path from "path";
import { GoogleGenAI } from "@google/genai";
import {
  buildInsightUserPrompt,
  buildToneUserPrompt,
  geminiModels,
  insightSystemInstruction,
  toneSystemInstruction,
} from "./ai.config";

import session from "express-session";
import { usersDb } from "./auth/db";
import { authRouter } from "./auth/routes";
import { requireAuth } from "./auth/middleware";
import { settingsRouter } from "./user/settings_routes";

const execAsync = promisify(exec);

// Own SQLite-based session store
class SQLiteStore extends session.Store {
  get(sid: string, cb: (err: any, session?: any) => void) {
    const row = usersDb
      .prepare("SELECT data, expires FROM sessions WHERE sid = ?")
      .get(sid) as { data: string; expires: number } | undefined;

    if (!row || row.expires < Date.now()) return cb(null, null);

    try {
      cb(null, JSON.parse(row.data));
    } catch {
      cb(null, null);
    }
  }

  set(sid: string, sessionData: any, cb?: (err?: any) => void) {
    const expires = sessionData.cookie?.expires
      ? new Date(sessionData.cookie.expires).getTime()
      : Date.now() + 24 * 60 * 60 * 1000;

    const data = JSON.stringify(sessionData);
    usersDb
      .prepare("INSERT OR REPLACE INTO sessions (sid, data, expires) VALUES (?, ?, ?)")
      .run(sid, data, expires);

    cb?.();
  }

  destroy(sid: string, cb?: (err?: any) => void) {
    usersDb.prepare("DELETE FROM sessions WHERE sid = ?").run(sid);
    cb?.();
  }
}

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
  if (cmd === "verse" || cmd === "search" || cmd === "analytics") {
    argv.push("--json");
  } else if (cmd === "seed" && tokens[0] === "list") {
    argv.push("--json");
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

function getAiClientOrNull(): GoogleGenAI | null {
  const apiKey = normalizeGeminiApiKey(process.env.GEMINI_API_KEY);
  if (!apiKey) return null;
  return new GoogleGenAI({ apiKey });
}

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  app.use(
    session({
      store: new SQLiteStore(),
      secret: process.env.SESSION_SECRET ?? "dev-secret-change-in-production",
      resave: false,
      saveUninitialized: false,
      cookie: {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        maxAge: 24 * 60 * 60 * 1000,
      },
    })
  );

  // Auth routes (no auth required)
  app.use("/api/auth", authRouter);

  // Authenticated user settings
  app.use("/api/user/settings", settingsRouter);

  app.post("/api/ai/insight", requireAuth, async (req, res) => {
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

  app.post("/api/ai/tone", requireAuth, async (req, res) => {
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

      const { stdout, stderr } = await runClible(argv);

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
        details: msg,
        hint: "Make sure 'clible' is installed and in your PATH.",
      });
    }
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

  app.listen(PORT, "0.0.0.0", async () => {
    console.log(`Server running on http://localhost:${PORT}`);
    console.log(`API Bridge active at /api/clible`);
    
    // Check if clible is available
    try {
      const { stdout } = await execAsync("clible --help");
      // Only print first line to keep startup logs compact.
      const firstLine = stdout.split("\n").find(Boolean) ?? "clible available";
      console.log(`Clible CLI detected: ${firstLine}`);
    } catch (e) {
      console.warn("WARNING: 'clible' CLI not found in PATH. API bridge will fail.");
    }
  });
}

startServer().catch((err) => {
  console.error("Failed to start server:", err);
  process.exit(1);
});
