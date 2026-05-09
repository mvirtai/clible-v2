import { useMemo } from 'react';
import { CheckCircle2, Play, XCircle } from 'lucide-react';
import { useReadingPlan } from '../user/ReadingPlanContext';
import { localizedReadingPlanCopy, t, type UILanguage } from '../utils/i18n';

function formatPassage(p: { bookId: string; chapterStart: number; chapterEnd: number }): string {
  return p.chapterStart === p.chapterEnd
    ? `${p.bookId} ${p.chapterStart}`
    : `${p.bookId} ${p.chapterStart}-${p.chapterEnd}`;
}

interface Props {
  uiLanguage: UILanguage;
}

export function ReadingPlanView({ uiLanguage }: Props) {
  const { plans, active, loading, error, startPlan, completeDay, abandonActive } = useReadingPlan();
  const m = t(uiLanguage);
  const activeCopy = active ? localizedReadingPlanCopy(uiLanguage, active.plan) : null;

  const canCompleteToday = !!active && !active.today.completed;

  const progressPct = useMemo(() => {
    if (!active) return 0;
    const total = active.progress.totalDays || 1;
    return Math.round((active.progress.completedDays / total) * 100);
  }, [active]);

  if (loading) {
    return <div className="p-6 text-sm text-[var(--muted)]">{m.readingLoading}</div>;
  }

  return (
    <div className="p-6 max-w-3xl mx-auto text-[var(--text)]">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h2 className="text-xl font-semibold tracking-tight">{m.readingTitle}</h2>
          <p className="text-sm text-[var(--muted)] mt-1">{m.readingSubtitle}</p>
        </div>
      </div>

      {error && (
        <p className="mt-4 text-sm text-red-600" role="alert">
          {error}
        </p>
      )}

      {!active && (
        <div className="mt-6 grid gap-3">
          {plans.map((p) => {
            const card = localizedReadingPlanCopy(uiLanguage, p);
            return (
            <div
              key={p.id}
              className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-4 flex items-start justify-between gap-4"
            >
              <div className="min-w-0">
                <div className="font-semibold">{card.name}</div>
                {card.description && (
                  <div className="text-sm text-[var(--muted)] mt-1">{card.description}</div>
                )}
                <div className="text-xs text-[var(--muted)] mt-2">{m.readingDays(p.durationDays)}</div>
              </div>
              <button
                onClick={() => startPlan(p.id)}
                className="shrink-0 inline-flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-semibold border border-[var(--border)] hover:border-[var(--text)] transition-colors"
              >
                <Play size={16} />
                {m.readingStart}
              </button>
            </div>
          );
          })}
        </div>
      )}

      {active && activeCopy && (
        <div className="mt-6 space-y-4">
          <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-4">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="text-sm text-[var(--muted)]">{m.readingActivePlan}</div>
                <div className="font-semibold">{activeCopy.name}</div>
                {activeCopy.description && (
                  <div className="text-sm text-[var(--muted)] mt-1">{activeCopy.description}</div>
                )}
              </div>
              <button
                onClick={() => abandonActive()}
                className="shrink-0 inline-flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-semibold border border-[var(--border)] hover:border-red-400 hover:text-red-700 transition-colors"
              >
                <XCircle size={16} />
                {m.readingAbandon}
              </button>
            </div>

            <div className="mt-4">
              <div className="flex items-center justify-between text-xs text-[var(--muted)]">
                <span>{m.readingDaysCompleted(active.progress.completedDays, active.progress.totalDays)}</span>
                <span>{progressPct}%</span>
              </div>
              <div className="mt-2 h-2 rounded-full bg-[var(--surface-2)] overflow-hidden">
                <div
                  className="h-full bg-[var(--text)]"
                  style={{ width: `${progressPct}%` }}
                />
              </div>
            </div>
          </div>

          <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-4">
            <div className="flex items-center justify-between gap-4">
              <div>
                <div className="text-sm text-[var(--muted)]">{m.readingToday}</div>
                <div className="font-semibold">{m.readingDay(active.today.dayNumber)}</div>
              </div>
              <button
                onClick={() => completeDay(active.today.dayNumber)}
                disabled={!canCompleteToday}
                className={`inline-flex items-center gap-2 px-3 py-2 rounded-xl text-sm font-semibold border transition-colors ${
                  canCompleteToday
                    ? 'border-[var(--border)] hover:border-[var(--text)]'
                    : 'border-[var(--border-soft)] text-[var(--muted)] cursor-not-allowed'
                }`}
              >
                <CheckCircle2 size={16} />
                {active.today.completed ? m.readingCompleted : m.readingMarkComplete}
              </button>
            </div>

            <ul className="mt-3 space-y-1 text-sm">
              {active.today.passages.length === 0 && (
                <li className="text-[var(--muted)]">{m.readingNoPassages}</li>
              )}
              {active.today.passages.map((p, idx) => (
                <li key={`${p.bookId}-${p.chapterStart}-${p.chapterEnd}-${idx}`}>
                  {formatPassage(p)}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
