import Database from 'better-sqlite3';
import path from 'path';

const dbPath = path.join(process.cwd(), 'data', 'users.db');

export const usersDb = new Database(dbPath);

usersDb.exec(`
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS sessions (
        sid TEXT PRIMARY KEY,
        data TEXT NOT NULL,
        expires INTEGER NOT NULL
    );

    CREATE TABLE IF NOT EXISTS session_queries (
        session_id TEXT NOT NULL,
        query_id TEXT NOT NULL,
        PRIMARY KEY (session_id, query_id)
    );
    `);