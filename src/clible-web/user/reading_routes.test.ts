import { describe, expect, it } from 'vitest';
import { computeStreakFromCompletionDates } from './reading_routes';

describe('user/reading_routes computeStreakFromCompletionDates', () => {
  it('returns 0 when nothing completed', () => {
    const todayUtc = new Date(Date.UTC(2026, 0, 10));
    const streak = computeStreakFromCompletionDates({ todayUtc, completedIsoDates: [] });
    expect(streak).toEqual({ count: 0, asOfDate: null });
  });

  it('counts streak ending today if today completed', () => {
    const todayUtc = new Date(Date.UTC(2026, 0, 10));
    const streak = computeStreakFromCompletionDates({
      todayUtc,
      completedIsoDates: ['2026-01-08', '2026-01-09', '2026-01-10'],
    });
    expect(streak).toEqual({ count: 3, asOfDate: '2026-01-10' });
  });

  it('counts streak ending yesterday if today not completed', () => {
    const todayUtc = new Date(Date.UTC(2026, 0, 10));
    const streak = computeStreakFromCompletionDates({
      todayUtc,
      completedIsoDates: ['2026-01-08', '2026-01-09'],
    });
    expect(streak).toEqual({ count: 2, asOfDate: '2026-01-09' });
  });

  it('breaks streak on missing day', () => {
    const todayUtc = new Date(Date.UTC(2026, 0, 10));
    const streak = computeStreakFromCompletionDates({
      todayUtc,
      completedIsoDates: ['2026-01-07', '2026-01-09'],
    });
    expect(streak).toEqual({ count: 1, asOfDate: '2026-01-09' });
  });
});

