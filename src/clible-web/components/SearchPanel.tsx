/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useRef, type KeyboardEvent } from 'react';
import { Search, Book, ChevronDown, ChevronUp, Clock, GitCompareArrows, Languages } from 'lucide-react';
import { BookPickerModal } from './BookPickerModal';
import { bookNameLocalized, type UILanguage } from '../utils/bookNames';
import { t } from '../utils/i18n';
import type {
  SearchMode,
  SearchOperator,
  SearchScope,
  SearchQueryOptions,
  SearchHistoryEntry,
} from '../types/searchQuery';

function historyScopeLabel(entry: SearchHistoryEntry, lang: UILanguage): string {
  const m = t(lang);
  if (entry.search_scope === 'testament' && entry.scope_value === 'NT') {
    return m.historyScopeNT;
  }
  if (entry.search_scope === 'testament' && entry.scope_value === 'OT') {
    return m.historyScopeOT;
  }
  if (entry.search_scope === 'book' && entry.scope_value) {
    return bookNameLocalized(entry.scope_value, lang);
  }
  if (entry.search_scope === 'bible') {
    return m.historyScopeWholeBible;
  }
  return entry.scope_value ?? entry.search_scope ?? '';
}

export type StudyEntryTab = 'scripture' | 'verse' | 'compare' | 'original';

interface SearchPanelProps {
  activeTranslation: string | null;
  uiLanguage: UILanguage;
  entryTab: StudyEntryTab;
  onEntryTabChange: (tab: StudyEntryTab) => void;
  onSearch: (options: SearchQueryOptions) => void;
  onVerseSearch: (reference: string) => void;
  history: SearchHistoryEntry[];
  onHistoryClear: () => void;
  loading: boolean;
  error: string | null;
}

export function SearchPanel({
  activeTranslation,
  uiLanguage,
  entryTab,
  onEntryTabChange,
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
  const inputRef = useRef<HTMLInputElement>(null);

  const m = t(uiLanguage);
  const isVerseMode = entryTab === 'verse';
  const isCompareTab = entryTab === 'compare';
  const isOriginalTab = entryTab === 'original';
  const isLandingOnly = isCompareTab || isOriginalTab;

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
    mode === 'wildcard' ? m.searchWildcardHint : null;

  const operatorConnector =
    operator === 'and'
      ? m.searchOperatorAnd
      : operator === 'or'
        ? m.searchOperatorOr
        : m.searchOperatorNot;

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        <button
          type="button"
          onClick={() => onEntryTabChange('scripture')}
          className={`px-3 py-1 rounded-full text-xs font-semibold transition-all ${
            entryTab === 'scripture'
              ? 'bg-[var(--text)] text-[var(--surface)]'
              : 'bg-[var(--surface-2)] text-[var(--muted)]'
          }`}
        >
          {m.searchFindInScripture}
        </button>
        <button
          type="button"
          onClick={() => onEntryTabChange('verse')}
          className={`px-3 py-1 rounded-full text-xs font-semibold transition-all ${
            entryTab === 'verse' ? 'bg-[var(--text)] text-[var(--surface)]' : 'bg-[var(--surface-2)] text-[var(--muted)]'
          }`}
        >
          {m.searchVerseLookup}
        </button>
        <button
          type="button"
          onClick={() => onEntryTabChange('compare')}
          className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold transition-all ${
            entryTab === 'compare'
              ? 'bg-[var(--text)] text-[var(--surface)]'
              : 'bg-[var(--surface-2)] text-[var(--muted)]'
          }`}
        >
          <GitCompareArrows size={13} aria-hidden />
          {m.searchEntryCompare}
        </button>
        <button
          type="button"
          onClick={() => onEntryTabChange('original')}
          className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold transition-all ${
            entryTab === 'original'
              ? 'bg-[var(--text)] text-[var(--surface)]'
              : 'bg-[var(--surface-2)] text-[var(--muted)]'
          }`}
        >
          <Languages size={13} aria-hidden />
          {m.tabOriginalStudy}
        </button>
      </div>

      {isCompareTab ? (
        <p className="text-sm text-[var(--muted)] leading-relaxed">{m.searchCompareLandingHint}</p>
      ) : null}
      {isOriginalTab ? (
        <p className="text-sm text-[var(--muted)] leading-relaxed">{m.originalStudyLandingHint}</p>
      ) : null}

      {error ? (
        <p className="text-sm text-red-600" role="alert">
          {error}
        </p>
      ) : null}

      {!isLandingOnly ? (
        <>
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
              ? m.searchPlaceholderVerse
              : mode === 'wildcard'
                ? m.searchPlaceholderWildcard
                : m.searchPlaceholderGeneral
          }
          className="w-full bg-white border-2 border-gray-500 text-gray-700 focus:border-[#1A1A1A] rounded-2xl py-4 pl-12 pr-4 text-lg outline-none transition-all shadow-sm hover:shadow-md"
          aria-label={isVerseMode ? m.searchAriaVerse : m.searchAriaSearch}
        />
        {showHistory && history.length > 0 && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-[var(--surface)] border border-[var(--border)] rounded-xl shadow-lg z-20 overflow-hidden">
            <div className="flex justify-between items-center px-4 py-2 border-b border-[var(--border-soft)]">
              <span className="text-xs font-semibold text-[var(--muted)] flex items-center gap-1.5">
                <Clock size={12} /> {m.searchRecentHeader}
              </span>
              <button
                type="button"
                onClick={onHistoryClear}
                className="text-xs text-[var(--muted)] hover:text-red-500 transition-colors"
              >
                {m.searchClear}
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
                  {m.searchHistoryMeta({
                    count: entry.result_count,
                    scopeLabel: historyScopeLabel(entry, uiLanguage),
                  })}
                </span>
              </button>
            ))}
          </div>
        )}
      </div>

      {!isVerseMode && mode === 'words' && (
        <div className="flex items-center gap-2">
          <span className="text-sm text-[var(--muted)] whitespace-nowrap">
            {operatorConnector}
          </span>
          <input
            type="text"
            value={secondTerm}
            onChange={(e) => setSecondTerm(e.target.value)}
            placeholder={m.searchSecondWordPlaceholder}
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
          <span className="text-xs text-[var(--muted)]">{m.searchScopePrefix}</span>
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
                ? m.searchAllBible
                : s === 'ot'
                  ? m.searchOldTestament
                  : s === 'nt'
                    ? m.searchNewTestament
                    : scope === 'book' && selectedBook
                      ? bookNameLocalized(selectedBook, uiLanguage)
                      : m.searchPickBook}
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
            {showAdvanced ? m.searchHideOptions : m.searchRefine}
          </button>

          {showAdvanced && (
            <div className="mt-3 p-4 border border-[var(--border-soft)] rounded-xl space-y-4 bg-[var(--surface-2)]">
              <div>
                <p className="text-xs font-semibold text-[var(--muted)] mb-2 uppercase tracking-wide">
                  {m.searchTypeHeading}
                </p>
                <div className="space-y-1.5">
                  {(
                    [
                      {
                        value: 'phrase' as const,
                        label: m.searchModePhrase,
                        desc: m.searchModePhraseDesc,
                      },
                      {
                        value: 'words' as const,
                        label: m.searchModeWords,
                        desc: m.searchModeWordsDesc,
                      },
                      {
                        value: 'wildcard' as const,
                        label: m.searchModeWildcard,
                        desc: m.searchModeWildcardDesc,
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
                    {m.searchMatchHeading}
                  </p>
                  <div className="flex gap-2">
                    {(
                      [
                        { value: 'and' as const, label: m.searchMatchAll },
                        { value: 'or' as const, label: m.searchMatchAny },
                        { value: 'not' as const, label: m.searchMatchExclude },
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
          uiLanguage={uiLanguage}
          onSelect={(bookId) => {
            setSelectedBook(bookId);
            setScope('book');
          }}
          onClose={() => {
            setShowBookPicker(false);
            if (!selectedBook) setScope('bible');
          }}
        />
      )}
        </>
      ) : null}
    </div>
  );
}
