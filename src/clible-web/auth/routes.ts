import { Router } from 'express';
import bcrypt from 'bcryptjs';
import { randomUUID } from 'crypto';
import { pool } from './db.js';

// Augment express-session so req.session.userId is typed.
declare module 'express-session' {
  interface SessionData {
    userId: string;
  }
}

export const authRouter = Router();

// POST /api/auth/register
authRouter.post('/register', async (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({ error: 'Username and password required.' });
  }
  if (password.length < 8) {
    return res.status(400).json({ error: 'Password must be at least 8 characters.' });
  }

  const { rowCount } = await pool.query(
    'SELECT id FROM users WHERE username = $1',
    [username],
  );
  if (rowCount && rowCount > 0) {
    return res.status(409).json({ error: 'Username already taken.' });
  }

  // 12 rounds: well-balanced between safety and speed.
  const hash = await bcrypt.hash(password, 12);
  const id = randomUUID();

  await pool.query(
    'INSERT INTO users (id, username, password_hash) VALUES ($1, $2, $3)',
    [id, username, hash],
  );

  req.session.userId = id;
  res.status(201).json({ id, username });
});

// POST /api/auth/login
authRouter.post('/login', async (req, res) => {
  const { username, password } = req.body;

  const { rows } = await pool.query<{
    id: string;
    username: string;
    password_hash: string;
  }>('SELECT id, username, password_hash FROM users WHERE username = $1', [username]);

  const user = rows[0];

  // Don't reveal which field is wrong.
  if (!user) {
    return res.status(401).json({ error: 'Invalid credentials.' });
  }

  const match = await bcrypt.compare(password, user.password_hash);
  if (!match) {
    return res.status(401).json({ error: 'Invalid credentials.' });
  }

  req.session.userId = user.id;
  res.json({ id: user.id, username: user.username });
});

// POST /api/auth/logout
authRouter.post('/logout', (req, res) => {
  req.session.destroy(() => {
    res.clearCookie('connect.sid');
    res.json({ ok: true });
  });
});

// GET /api/auth/me
authRouter.get('/me', async (req, res) => {
  if (!req.session.userId) {
    return res.status(401).json({ error: 'Not authenticated.' });
  }

  const { rows } = await pool.query<{ id: string; username: string }>(
    'SELECT id, username FROM users WHERE id = $1',
    [req.session.userId],
  );
  const user = rows[0];

  if (!user) {
    req.session.destroy(() => {});
    return res.status(401).json({ error: 'User not found.' });
  }

  res.json(user);
});

// (user settings routes live in src/clible-web/user/settings_routes.ts)
