import { Flame } from 'lucide-react';
import { useReadingPlan } from '../user/ReadingPlanContext';
import { t, type UILanguage } from '../utils/i18n';

interface Props {
  uiLanguage: UILanguage;
}

export function StreakBadge({ uiLanguage }: Props) {
  const { active, loading } = useReadingPlan();
  const m = t(uiLanguage);

  if (loading) return null;
  const count = active?.streak.count ?? 0;
  if (count <= 0) return null;

  const label = m.readingStreakAriaLabel(count);

  return (
    <div
      className="inline-flex items-center gap-1 px-2 py-1 rounded-full border border-[var(--border)] bg-[var(--surface)] text-[var(--text)] text-xs font-semibold"
      aria-label={label}
      title={label}
    >
      <Flame size={14} />
      <span>{count}</span>
    </div>
  );
}
