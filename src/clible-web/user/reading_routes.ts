import { Router } from 'express';
import { randomUUID } from 'crypto';
import { pool } from '../db/pool.js';
import { requireAuth } from '../auth/middleware.js';

type PlanTemplateRow = {
  id: string;
  name: string;
  description: string | null;
  duration_days: number;
  entries: unknown;
};

type PlanSummary = {
  id: string;
  name: string;
  description: string | null;
  durationDays: number;
};

type Passage = { bookId: string; chapterStart: number; chapterEnd: number };
type PlanEntry = { dayNumber: number; passages: Passage[] };

type ActivePlanResponse = {
  plan: PlanSummary;
  startedAt: string;
  today: { dayNumber: number; passages: PlanEntry['passages']; completed: boolean };
  progress: { completedDays: number; totalDays: number };
  streak: { count: number; asOfDate: string | null };
};

function toIsoDate(d: Date): string {
  return d.toISOString().slice(0, 10);
}

function addDaysUtc(date: Date, deltaDays: number): Date {
  const d = new Date(Date.UTC(date.getUTCFullYear(), date.getUTCMonth(), date.getUTCDate()));
  d.setUTCDate(d.getUTCDate() + deltaDays);
  return d;
}

export function computeStreakFromCompletionDates(args: {
  todayUtc: Date;
  completedIsoDates: string[];
}): { count: number; asOfDate: string | null } {
  const todayIso = toIsoDate(args.todayUtc);
  const set = new Set(args.completedIsoDates);

  // If user hasn't completed today yet, streak is counted as of yesterday.
  const start = set.has(todayIso) ? todayIso : toIsoDate(addDaysUtc(args.todayUtc, -1));
  if (!set.has(start)) {
    return { count: 0, asOfDate: null };
  }

  let count = 0;
  let cursor = start;
  while (set.has(cursor)) {
    count += 1;
    const [y, m, d] = cursor.split('-').map((n) => parseInt(n, 10));
    const dt = new Date(Date.UTC(y!, (m ?? 1) - 1, d ?? 1));
    cursor = toIsoDate(addDaysUtc(dt, -1));
  }
  return { count, asOfDate: start };
}

function parseEntries(raw: unknown): PlanEntry[] {
  if (!Array.isArray(raw)) return [];
  return raw as PlanEntry[];
}

async function getActivePlanRow(userId: string): Promise<
  | (PlanTemplateRow & {
      user_plan_id: string;
      started_at: string;
    })
  | null
> {
  const { rows } = await pool.query(
    `SELECT
       up.id AS user_plan_id,
       up.started_at,
       t.id,
       t.name,
       t.description,
       t.duration_days,
       t.entries
     FROM user_reading_plans up
     JOIN reading_plan_templates t ON t.id = up.plan_id
     WHERE up.user_id = $1 AND up.status = 'active'
     ORDER BY up.started_at DESC
     LIMIT 1`,
    [userId],
  );
  return (rows[0] as any) ?? null;
}

async function buildActivePlanResponse(userId: string): Promise<ActivePlanResponse | null> {
  const active = await getActivePlanRow(userId);
  if (!active) return null;

  const plan: PlanSummary = {
    id: active.id,
    name: active.name,
    description: active.description,
    durationDays: Number(active.duration_days),
  };

  const entries = parseEntries(active.entries);
  const startedAt = new Date(active.started_at);
  const todayUtc = new Date();

  const dayNumberRaw =
    Math.floor(
      (Date.UTC(todayUtc.getUTCFullYear(), todayUtc.getUTCMonth(), todayUtc.getUTCDate()) -
        Date.UTC(startedAt.getUTCFullYear(), startedAt.getUTCMonth(), startedAt.getUTCDate())) /
        (24 * 60 * 60 * 1000),
    ) + 1;

  const todayDayNumber = Math.max(1, Math.min(plan.durationDays, dayNumberRaw));
  const todayEntry = entries.find((e) => e.dayNumber === todayDayNumber);
  const passages = todayEntry?.passages ?? [];

  const progressRows = await pool.query(
    `SELECT day_number, completed_at
     FROM reading_progress
     WHERE user_plan_id = $1
     ORDER BY completed_at DESC`,
    [active.user_plan_id],
  );

  const completedDays = new Set<number>();
  const completedIsoDates: string[] = [];
  for (const row of progressRows.rows as Array<{ day_number: number; completed_at: string }>) {
    completedDays.add(Number(row.day_number));
    completedIsoDates.push(toIsoDate(new Date(row.completed_at)));
  }

  const completedToday = completedDays.has(todayDayNumber);
  const streak = computeStreakFromCompletionDates({ todayUtc, completedIsoDates });

  return {
    plan,
    startedAt: new Date(active.started_at).toISOString(),
    today: { dayNumber: todayDayNumber, passages, completed: completedToday },
    progress: { completedDays: completedDays.size, totalDays: plan.durationDays },
    streak,
  };
}

export const readingRouter = Router();
readingRouter.use(requireAuth);

// GET /api/user/reading/plans
readingRouter.get('/plans', async (_req, res) => {
  const { rows } = await pool.query(
    'SELECT id, name, description, duration_days FROM reading_plan_templates ORDER BY duration_days ASC, name ASC',
  );
  const plans: PlanSummary[] = (rows as any[]).map((r) => ({
    id: String(r.id),
    name: String(r.name),
    description: r.description == null ? null : String(r.description),
    durationDays: Number(r.duration_days),
  }));
  res.json(plans);
});

// GET /api/user/reading/active
readingRouter.get('/active', async (req, res) => {
  const userId = req.session.userId!;
  const payload = await buildActivePlanResponse(userId);
  res.json(payload);
});

// POST /api/user/reading/start/:planId
readingRouter.post('/start/:planId', async (req, res) => {
  const userId = req.session.userId!;
  const planId = typeof req.params.planId === 'string' ? req.params.planId.trim() : '';
  if (!planId) return res.status(400).json({ error: 'Missing planId.' });

  const { rowCount: templateExists } = await pool.query(
    'SELECT 1 FROM reading_plan_templates WHERE id = $1',
    [planId],
  );
  if (!templateExists) return res.status(404).json({ error: `Unknown plan '${planId}'.` });

  await pool.query("UPDATE user_reading_plans SET status = 'abandoned' WHERE user_id = $1 AND status = 'active'", [
    userId,
  ]);

  const userPlanId = randomUUID();
  await pool.query(
    `INSERT INTO user_reading_plans (id, user_id, plan_id, status)
     VALUES ($1, $2, $3, 'active')`,
    [userPlanId, userId, planId],
  );

  const payload = await buildActivePlanResponse(userId);
  res.json(payload);
});

// POST /api/user/reading/complete/:dayNumber
readingRouter.post('/complete/:dayNumber', async (req, res) => {
  const userId = req.session.userId!;
  const dayRaw = typeof req.params.dayNumber === 'string' ? req.params.dayNumber.trim() : '';
  const dayNumber = Number(dayRaw);
  if (!Number.isInteger(dayNumber) || dayNumber <= 0) {
    return res.status(400).json({ error: "Invalid 'dayNumber'." });
  }

  const active = await getActivePlanRow(userId);
  if (!active) return res.status(404).json({ error: 'No active reading plan.' });

  const totalDays = Number(active.duration_days);
  if (dayNumber > totalDays) {
    return res.status(400).json({ error: `'dayNumber' must be between 1 and ${totalDays}.` });
  }

  const id = randomUUID();
  const result = await pool.query(
    `INSERT INTO reading_progress (id, user_plan_id, day_number)
     VALUES ($1, $2, $3)
     ON CONFLICT (user_plan_id, day_number) DO NOTHING`,
    [id, active.user_plan_id, dayNumber],
  );

  const payload = await buildActivePlanResponse(userId);
  res.json({ ok: true, alreadyCompleted: result.rowCount === 0, active: payload });
});

// DELETE /api/user/reading/active
readingRouter.delete('/active', async (req, res) => {
  const userId = req.session.userId!;
  await pool.query("UPDATE user_reading_plans SET status = 'abandoned' WHERE user_id = $1 AND status = 'active'", [
    userId,
  ]);
  res.json({ ok: true });
});

