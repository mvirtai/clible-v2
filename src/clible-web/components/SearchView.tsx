import { ChevronRight, Download } from 'lucide-react';
import type { SearchResponse } from '../types/search';
import { SearchStatsPanel } from './SearchStatsPanel';

interface SearchViewProps {
  searchResponse: SearchResponse | null;
  onResultClick: (reference: string) => void;
  onExport: () => void;
}

export function SearchView({ searchResponse, onResultClick, onExport }: SearchViewProps) {
  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-2 border-b border-[var(--border-soft)] pb-4">
        <div className="flex items-center justify-between">
          <h2 className="text-2xl font-serif italic">Search Results</h2>
          {searchResponse && (
            <div className="flex items-center gap-3">
              <span className="text-sm text-[var(--muted)]">
                {searchResponse.statistics.uniqueVerses} unique verse
                {searchResponse.statistics.uniqueVerses === 1 ? '' : 's'}
              </span>
              <button
                onClick={onExport}
                className="p-2 hover:bg-[var(--surface-2)] rounded-full transition-colors text-[var(--accent)]"
                title="Export results"
              >
                <Download size={18} />
              </button>
            </div>
          )}
        </div>
        {searchResponse && (
          <SearchStatsPanel
            statistics={searchResponse.statistics}
            rowCount={searchResponse.rows.length}
          />
        )}
      </div>
      {searchResponse && searchResponse.rows.length === 0 && (
        <p className="text-center text-[var(--muted)] py-8">No verses found for this search.</p>
      )}
      <div className="space-y-4">
        {searchResponse?.rows.map((res, i) => (
          <button
            key={i}
            onClick={() => onResultClick(res.reference)}
            className="w-full text-left p-6 bg-[var(--surface)] border border-[var(--border)] rounded-2xl hover:border-[var(--text)] transition-all group"
          >
            <div className="flex justify-between items-center mb-2">
              <span className="font-bold text-[var(--accent)]">{res.reference}</span>
              <ChevronRight size={16} className="text-[var(--border)] group-hover:text-[var(--text)] transition-colors" />
            </div>
            <p className="text-[var(--text-2)] line-clamp-2">{res.text}</p>
          </button>
        ))}
      </div>
    </div>
  );
}
