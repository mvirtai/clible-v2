/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import express from "express";
import { createServer as createViteServer } from "vite";
import { exec } from "child_process";
import { promisify } from "util";
import path from "path";

const execAsync = promisify(exec);

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  /**
   * API Bridge to Clible CLI
   * This endpoint executes the local 'clible' command and returns its output.
   * Example: /api/clible?cmd=verse&args=John+3:16
   */
  app.get("/api/clible", async (req, res) => {
    const { cmd, args } = req.query;
    
    if (!cmd || typeof cmd !== 'string') {
      return res.status(400).json({ error: "Missing or invalid command" });
    }

    // Allow only specific clible commands
    const allowedCommands = ['verse', 'search', 'analytics', 'seed', 'list'];
    if (!allowedCommands.includes(cmd)) {
      return res.status(403).json({ error: `Command '${cmd}' is not allowed.` });
    }

    try {
      // Basic sanitization: remove any characters that could be used for shell injection
      // We allow spaces, quotes, dashes, and alphanumeric characters for Bible references and flags.
      const sanitizedArgs = (args as string || "").replace(/[;&|`$]/g, "");
      
      const fullCommand = `clible ${cmd} ${sanitizedArgs} --json`;
      
      // Execute the CLI tool
      const { stdout, stderr } = await execAsync(fullCommand);
      
      if (stderr && !stdout) {
        return res.status(500).json({ error: stderr });
      }

      // Return the JSON output from Clible
      try {
        res.json(JSON.parse(stdout));
      } catch (e) {
        res.status(500).json({ 
          error: "Invalid JSON output from Clible CLI", 
          rawOutput: stdout 
        });
      }
    } catch (error: any) {
      console.error("CLI Error:", error);
      res.status(500).json({ 
        error: "Failed to execute Clible CLI", 
        details: error.message,
        stdout: error.stdout,
        stderr: error.stderr,
        hint: "Make sure 'clible' is installed and in your PATH."
      });
    }
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
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
      const { stdout } = await execAsync("clible --version");
      console.log(`Clible CLI detected: ${stdout.trim()}`);
    } catch (e) {
      console.warn("WARNING: 'clible' CLI not found in PATH. API bridge will fail.");
    }
  });
}

startServer();
