import { SearchStatistics } from '../types/search';
import { bookName } from '../utils/bookNames';

interface StatMetricProps {
  label: string;
  value: number;
}

function StatMetric({ label, value }: StatMetricProps) {
  return (
    <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-2)] px-3 py-2">
      <div className="text-[10px] uppercase tracking-wider text-[var(--muted)]">
        {label}
      </div>
      <div className="font-mono font-semibold text-[var(--text)]">{value}</div>
    </div>
  );
}

interface SearchStatsPanelProps {
  statistics: SearchStatistics;
  /** Number of verse rows currently displayed (may be less than uniqueVerses when limited). */
  rowCount: number;
}

export function SearchStatsPanel({ statistics, rowCount }: SearchStatsPanelProps) {
  const truncated = rowCount > 0 && rowCount < statistics.uniqueVerses;

  return (
    <div className="space-y-2">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
        <div className="space-y-3">
          <StatMetric label="Occurrences" value={statistics.totalOccurrences} />
          <StatMetric label="Unique verses" value={statistics.uniqueVerses} />
          <StatMetric label="Books" value={statistics.booksWithMatches} />
        </div>

        <div className="rounded-xl border border-[var(--border)] bg-[var(--surface-2)] px-3 py-2">
          <div className="flex items-center justify-between">
            <div className="text-[10px] uppercase tracking-wider text-[var(--muted)]">
              Top books
            </div>
            <div className="text-[10px] uppercase tracking-wider text-[var(--muted)]">
              Occurrences
            </div>
          </div>
          {statistics.topBooks.length === 0 ? (
            <div className="pt-2 font-mono text-xs text-[var(--muted)]">—</div>
          ) : (
            <ol className="pt-2 space-y-1">
              {statistics.topBooks.map(([bookId, count], idx) => (
                <li
                  key={bookId}
                  className="flex items-baseline justify-between gap-3"
                >
                  <div className="flex items-baseline gap-2 min-w-0">
                    <span className="inline-flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full border border-[var(--border)] bg-[var(--surface)] text-[10px] font-semibold text-[var(--muted)]">
                      {idx + 1}
                    </span>
                    <span className="truncate text-xs text-[var(--text)]">
                      {bookName(bookId)}{' '}
                      <span className="font-mono font-semibold text-[var(--accent)]">
                        {bookId}
                      </span>
                    </span>
                  </div>
                  <span className="font-mono text-xs text-[var(--text-2)]">
                    {count}
                  </span>
                </li>
              ))}
            </ol>
          )}
        </div>
      </div>

      {truncated && (
        <p className="text-sm text-[var(--muted)]">
          Showing first {rowCount} of {statistics.uniqueVerses} matching verses
          (limit).
        </p>
      )}
    </div>
  );
}
