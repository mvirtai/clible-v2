/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import type { ReactNode } from 'react';
import { ChevronRight, Download } from 'lucide-react';
import type { SearchResponse } from '../types/search';
import { SearchStatsPanel } from './SearchStatsPanel';
import { SaveSearchButton } from './SaveSearchButton';

function _escapeRegex(text: string): string {
  return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

function _termToHighlightPattern(term: string, mode?: string): string {
  if (mode !== 'wildcard') {
    return _escapeRegex(term);
  }
  // Match the whole wildcard expression so unknown wildcard characters
  // (e.g. suffix matched by *) are highlighted as well.
  return _escapeRegex(term).replace(/\\\*/g, '\\w*').replace(/\\\?/g, '.');
}

function highlightTerms(text: string, terms: string[], mode?: string): ReactNode {
  const safe = terms.map((t) => t.trim()).filter(Boolean);
  if (!safe.length) return text;
  try {
    const inner = safe.map((t) => _termToHighlightPattern(t, mode)).join('|');
    const pattern = new RegExp(`(${inner})`, 'giu');
    const out: ReactNode[] = [];
    let last = 0;
    const re = new RegExp(pattern.source, 'giu');
    let m: RegExpExecArray | null;
    while ((m = re.exec(text)) !== null) {
      if (m.index > last) {
        out.push(text.slice(last, m.index));
      }
      out.push(
        <strong
          key={`${m.index}-${m[0]}`}
          className="font-semibold text-[var(--text)]"
        >
          {m[0]}
        </strong>
      );
      last = m.index + m[0].length;
    }
    if (last < text.length) {
      out.push(text.slice(last));
    }
    return out.length ? <>{out}</> : text;
  } catch {
    return text;
  }
}

interface SearchViewProps {
  searchResponse: SearchResponse | null;
  searchTerms: string[];
  onResultClick: (reference: string) => void;
  onExport: () => void;
  onSaveSearch?: (name: string) => Promise<void>;
}

export function SearchView({
  searchResponse,
  searchTerms,
  onResultClick,
  onExport,
  onSaveSearch,
}: SearchViewProps) {
  const terms =
    searchResponse?.highlightTerms && searchResponse.highlightTerms.length > 0
      ? searchResponse.highlightTerms
      : searchTerms;
  const mode = searchResponse?.searchMode;

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
              {onSaveSearch && <SaveSearchButton onSave={onSaveSearch} />}
              <button
                type="button"
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
            type="button"
            onClick={() => onResultClick(res.reference)}
            className="w-full text-left p-6 bg-[var(--surface)] border border-[var(--border)] rounded-2xl hover:border-[var(--text)] transition-all group"
          >
            <div className="flex justify-between items-center mb-2">
              <span className="font-bold text-[var(--accent)]">{res.reference}</span>
              <ChevronRight
                size={16}
                className="text-[var(--border)] group-hover:text-[var(--text)] transition-colors"
              />
            </div>
            <p className="text-[var(--text-2)] line-clamp-2">
              {highlightTerms(res.text, terms, mode)}
            </p>
          </button>
        ))}
      </div>
    </div>
  );
}
