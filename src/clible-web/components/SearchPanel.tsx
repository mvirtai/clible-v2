/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useRef, type KeyboardEvent } from 'react';
import { Search, Book, ChevronDown, ChevronUp, Clock } from 'lucide-react';
import { BookPickerModal } from './BookPickerModal';
import type {
  SearchMode,
  SearchOperator,
  SearchScope,
  SearchQueryOptions,
  SearchHistoryEntry,
} from '../types/searchQuery';

interface SearchPanelProps {
  activeTranslation: string | null;
  onSearch: (options: SearchQueryOptions) => void;
  onVerseSearch: (reference: string) => void;
  history: SearchHistoryEntry[];
  onHistoryClear: () => void;
  loading: boolean;
  error: string | null;
}

export function SearchPanel({
  activeTranslation,
  onSearch,
  onVerseSearch,
  history,
  onHistoryClear,
  loading,
  error,
}: SearchPanelProps) {
  const [query, setQuery] = useState('');
  const [secondTerm, setSecondTerm] = useState('');
  const [mode, setMode] = useState<SearchMode>('phrase');
  const [operator, setOperator] = useState<SearchOperator>('and');
  const [scope, setScope] = useState<SearchScope>('bible');
  const [selectedBook, setSelectedBook] = useState<string | null>(null);
  const [showBookPicker, setShowBookPicker] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [isVerseMode, setIsVerseMode] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = () => {
    if (!query.trim()) return;
    setShowHistory(false);

    if (isVerseMode) {
      onVerseSearch(query.trim());
      return;
    }

    const terms =
      mode === 'words' && secondTerm.trim()
        ? [query.trim(), secondTerm.trim()]
        : [query.trim()];

    onSearch({
      terms,
      mode,
      operator,
      scope,
      book: selectedBook,
      translationId: activeTranslation ?? '',
    });
  };

  const handleKey = (e: KeyboardEvent) => {
    if (e.key === 'Enter') void handleSubmit();
    if (e.key === 'Escape') setShowHistory(false);
  };

  const handleHistorySelect = (entry: SearchHistoryEntry) => {
    setQuery(entry.query_text);
    const em = entry.mode;
    if (em === 'boolean') setMode('words');
    else if (em === 'phrase') setMode('phrase');
    else if (em === 'wildcard') setMode('wildcard');

    if (entry.search_scope === 'testament') {
      setScope(entry.scope_value === 'NT' ? 'nt' : 'ot');
      setSelectedBook(null);
    } else if (entry.search_scope === 'book' && entry.scope_value) {
      setScope('book');
      setSelectedBook(entry.scope_value);
    } else {
      setScope('bible');
      setSelectedBook(null);
    }
    setShowHistory(false);
  };

  const wildcardHint =
    mode === 'wildcard'
      ? 'Use * for any ending (lov* finds love, loves, loving). Use ? for one letter (wom?n).'
      : null;

  return (
    <div className="space-y-3">
      <div className="flex gap-2">
        <button
          type="button"
          onClick={() => setIsVerseMode(false)}
          className={`px-3 py-1 rounded-full text-xs font-semibold transition-all ${
            !isVerseMode ? 'bg-[#1A1A1A] text-white' : 'bg-[#F5F5F5] text-[#8E8E8E]'
          }`}
        >
          Find in Scripture
        </button>
        <button
          type="button"
          onClick={() => setIsVerseMode(true)}
          className={`px-3 py-1 rounded-full text-xs font-semibold transition-all ${
            isVerseMode ? 'bg-[#1A1A1A] text-white' : 'bg-[#F5F5F5] text-[#8E8E8E]'
          }`}
        >
          Verse Lookup
        </button>
      </div>

      {error && (
        <p className="text-sm text-red-600" role="alert">
          {error}
        </p>
      )}

      <div className="relative group">
        <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none text-[#8E8E8E] group-focus-within:text-[#1A1A1A] transition-colors">
          {isVerseMode ? <Book size={20} /> : <Search size={20} />}
        </div>
        <input
          ref={inputRef}
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKey}
          onFocus={() => {
            if (!query && history.length > 0) setShowHistory(true);
          }}
          onBlur={() => setTimeout(() => setShowHistory(false), 150)}
          disabled={loading}
          placeholder={
            isVerseMode
              ? 'Enter verse (e.g. John 3:16, Psalms 23)...'
              : mode === 'wildcard'
                ? 'Enter a pattern (e.g. lov*, faith?)...'
                : 'Find a word, theme, or phrase...'
          }
          className="w-full bg-white border-2 border-gray-500 text-gray-700 focus:border-[#1A1A1A] rounded-2xl py-4 pl-12 pr-4 text-lg outline-none transition-all shadow-sm hover:shadow-md"
          aria-label={isVerseMode ? 'Enter Bible reference' : 'Search Bible text'}
        />
        {showHistory && history.length > 0 && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-[var(--surface)] border border-[var(--border)] rounded-xl shadow-lg z-20 overflow-hidden">
            <div className="flex justify-between items-center px-4 py-2 border-b border-[var(--border-soft)]">
              <span className="text-xs font-semibold text-[var(--muted)] flex items-center gap-1.5">
                <Clock size={12} /> Recent searches
              </span>
              <button
                type="button"
                onClick={onHistoryClear}
                className="text-xs text-[var(--muted)] hover:text-red-500 transition-colors"
              >
                Clear
              </button>
            </div>
            {history.slice(0, 5).map((entry) => (
              <button
                key={entry.id}
                type="button"
                onMouseDown={() => handleHistorySelect(entry)}
                className="w-full text-left px-4 py-2.5 hover:bg-[var(--surface-2)] transition-colors flex justify-between items-center"
              >
                <span className="text-sm font-medium">{entry.query_text}</span>
                <span className="text-xs text-[var(--muted)]">
                  {entry.scope_value ?? entry.search_scope} · {entry.result_count} verses
                </span>
              </button>
            ))}
          </div>
        )}
      </div>

      {!isVerseMode && mode === 'words' && (
        <div className="flex items-center gap-2">
          <span className="text-sm text-[var(--muted)] whitespace-nowrap">
            {operator === 'and'
              ? 'and also contains'
              : operator === 'or'
                ? 'or contains'
                : 'but not'}
          </span>
          <input
            type="text"
            value={secondTerm}
            onChange={(e) => setSecondTerm(e.target.value)}
            placeholder="second word..."
            disabled={loading}
            className="flex-1 border border-[var(--border)] rounded-xl py-2.5 px-3 text-sm outline-none focus:border-[#1A1A1A]"
          />
        </div>
      )}

      {wildcardHint && (
        <p className="text-xs text-[var(--muted)] bg-[var(--surface-2)] rounded-lg px-3 py-2">
          {wildcardHint}
        </p>
      )}

      {!isVerseMode && (
        <div className="flex flex-wrap gap-2 items-center">
          <span className="text-xs text-[var(--muted)]">Search in:</span>
          {(['bible', 'ot', 'nt', 'book'] as SearchScope[]).map((s) => (
            <button
              key={s}
              type="button"
              onClick={() => {
                setScope(s);
                if (s === 'book' && !selectedBook) setShowBookPicker(true);
              }}
              className={`px-3 py-1 rounded-full text-xs font-medium border transition-all ${
                scope === s
                  ? 'bg-[#1A1A1A] text-white border-[#1A1A1A]'
                  : 'border-[var(--border)] text-[var(--text-2)] hover:border-[#1A1A1A]'
              }`}
            >
              {s === 'bible'
                ? 'All Bible'
                : s === 'ot'
                  ? 'Old Testament'
                  : s === 'nt'
                    ? 'New Testament'
                    : scope === 'book' && selectedBook
                      ? selectedBook
                      : 'A specific book...'}
            </button>
          ))}
        </div>
      )}

      {!isVerseMode && (
        <div>
          <button
            type="button"
            onClick={() => setShowAdvanced(!showAdvanced)}
            className="flex items-center gap-1 text-xs text-[var(--muted)] hover:text-[var(--text)] transition-colors"
            aria-expanded={showAdvanced}
          >
            {showAdvanced ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            {showAdvanced ? 'Hide options' : 'Refine your search'}
          </button>

          {showAdvanced && (
            <div className="mt-3 p-4 border border-[var(--border-soft)] rounded-xl space-y-4 bg-[var(--surface-2)]">
              <div>
                <p className="text-xs font-semibold text-[var(--muted)] mb-2 uppercase tracking-wide">
                  Search type
                </p>
                <div className="space-y-1.5">
                  {(
                    [
                      {
                        value: 'phrase' as const,
                        label: 'Any word in verse',
                        desc: 'Finds verses containing the word or phrase',
                      },
                      {
                        value: 'words' as const,
                        label: 'Combine words',
                        desc: 'Find verses with multiple words (AND / OR / NOT)',
                      },
                      {
                        value: 'wildcard' as const,
                        label: 'Word pattern',
                        desc: 'lov* finds love, loves, loving',
                      },
                    ] as const
                  ).map(({ value, label, desc }) => (
                    <label key={value} className="flex items-start gap-2.5 cursor-pointer group">
                      <input
                        type="radio"
                        name="searchMode"
                        value={value}
                        checked={mode === value}
                        onChange={() => setMode(value)}
                        className="mt-0.5"
                      />
                      <div>
                        <span className="text-sm font-medium group-hover:text-[var(--accent)]">
                          {label}
                        </span>
                        <p className="text-xs text-[var(--muted)]">{desc}</p>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              {mode === 'words' && (
                <div>
                  <p className="text-xs font-semibold text-[var(--muted)] mb-2 uppercase tracking-wide">
                    Match
                  </p>
                  <div className="flex gap-2">
                    {(
                      [
                        { value: 'and' as const, label: 'All words' },
                        { value: 'or' as const, label: 'Any word' },
                        { value: 'not' as const, label: 'Exclude second' },
                      ] as const
                    ).map(({ value, label }) => (
                      <button
                        key={value}
                        type="button"
                        onClick={() => setOperator(value)}
                        className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                          operator === value
                            ? 'bg-[#1A1A1A] text-white border-[#1A1A1A]'
                            : 'border-[var(--border)] text-[var(--text-2)]'
                        }`}
                      >
                        {label}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {showBookPicker && (
        <BookPickerModal
          onSelect={(book) => {
            setSelectedBook(book);
            setScope('book');
          }}
          onClose={() => {
            setShowBookPicker(false);
            if (!selectedBook) setScope('bible');
          }}
        />
      )}
    </div>
  );
}
