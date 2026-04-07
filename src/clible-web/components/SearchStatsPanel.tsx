import { SearchStatistics } from '../types/search';
import { bookName } from '../utils/bookNames';

interface StatMetricProps {
  label: string;
  value: number;
}

function StatMetric({ label, value }: StatMetricProps) {
  return (
    <div className="rounded-xl border border-[#E5E5E5] bg-[#FAF9F6] px-3 py-2">
      <div className="text-[10px] uppercase tracking-wider text-[#8E8E8E]">
        {label}
      </div>
      <div className="font-mono font-semibold text-[#1A1A1A]">{value}</div>
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

        <div className="rounded-xl border border-[#E5E5E5] bg-[#FAF9F6] px-3 py-2">
          <div className="flex items-center justify-between">
            <div className="text-[10px] uppercase tracking-wider text-[#8E8E8E]">
              Top books
            </div>
            <div className="text-[10px] uppercase tracking-wider text-[#8E8E8E]">
              Occurrences
            </div>
          </div>
          {statistics.topBooks.length === 0 ? (
            <div className="pt-2 font-mono text-xs text-[#8E8E8E]">—</div>
          ) : (
            <ol className="pt-2 space-y-1">
              {statistics.topBooks.map(([bookId, count], idx) => (
                <li
                  key={bookId}
                  className="flex items-baseline justify-between gap-3"
                >
                  <div className="flex items-baseline gap-2 min-w-0">
                    <span className="inline-flex h-5 w-5 flex-shrink-0 items-center justify-center rounded-full border border-[#E5E5E5] bg-white text-[10px] font-semibold text-[#8E8E8E]">
                      {idx + 1}
                    </span>
                    <span className="truncate text-xs text-[#1A1A1A]">
                      {bookName(bookId)}{' '}
                      <span className="font-mono font-semibold text-[#D4A373]">
                        {bookId}
                      </span>
                    </span>
                  </div>
                  <span className="font-mono text-xs text-[#4A4A4A]">
                    {count}
                  </span>
                </li>
              ))}
            </ol>
          )}
        </div>
      </div>

      {truncated && (
        <p className="text-sm text-[#8E8E8E]">
          Showing first {rowCount} of {statistics.uniqueVerses} matching verses
          (limit).
        </p>
      )}
    </div>
  );
}
