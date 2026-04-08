import { Router } from 'express';
import bcrypt from 'bcryptjs';
import { randomUUID } from 'crypto';
import { usersDb } from './db';

// it is needed to expand 'expression-session' type with 'userId' in TS
declare module 'express-session' {
    interface SessionData {
        userId: string;
    }
}

export const authRouter = Router();

// POST /api/auth/register
authRouter.post("/register", async (req, res) => {
    const { username, password } = req.body;

    if (!username || !password) {
        return res.status(400).json({ error: "Username and password required."});
    }
    if (password.length < 8) {
        return res.status(400).json({ error: "Password must be at least 8 characters."})
    }

    // Existing username
    const existing = usersDb.prepare("SELECT id FROM users WHERE username = ?").get(username);
    if (existing) {
        return res.status(409).json({ error: "Username already taken." });
    }

    // bcrypt hash and salt
    // 12 is well-balanced with the safety and speed
    const hash = await bcrypt.hash(password, 12);
    const id = randomUUID();

    usersDb.prepare(
        "INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)"
    ).run(id, username, hash);

    // Login right after registering
    req.session.userId = id;
    res.status(201).json({ id, username });

    // POST /api/auth/login
    authRouter.post("/login", async (req, res) => {
        const { username, password } = req.body;

        const user = usersDb
            .prepare("SELECT id, username, password_hash FROM users WHERE username = ?")
            .get(username) as { id: string; username: string; password_hash: string } | undefined;
        
        // Important: error msg should not reveal which one is wrong - pswd or username
        if (!user) {
            return res.status(401).json({ error: "Invalid credentials."});
        }

        const match = await bcrypt.compare(password, user.password_hash)
        if (!match) {
            return res.status(401).json({ error: "Invalid credentials." })
        }

        req.session.userId = user.id;
        res.json({ id: user.id, username: user.username });
    });

    // POST /api/auth/logout
    authRouter.post("/logout", (req, res) => {
        req.session.destroy(() => {
            res.clearCookie("connect.sid");
            res.json({ ok: true });
        });
    });

    authRouter.get("/me", (req, res) => {
  if (!req.session.userId) {
    return res.status(401).json({ error: "Not authenticated." });
  }

//   GET /api/auth/me - user's login status
  const user = usersDb
    .prepare("SELECT id, username FROM users WHERE id = ?")
    .get(req.session.userId) as { id: string; username: string } | undefined;

  if (!user) {
    req.session.destroy(() => {});
    return res.status(401).json({ error: "User not found." });
  }

  res.json(user);
});
})