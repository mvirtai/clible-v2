/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useEffect, useRef, KeyboardEvent } from 'react';
import { 
  Search, 
  Book, 
  Sparkles, 
  Terminal, 
  ChevronRight, 
  History, 
  Settings, 
  Share2, 
  Download,
  Loader2,
  X,
  ArrowRight,
  BarChart3,
  Hash,
  MessageSquareQuote,
  Activity,
  Globe,
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import ReactMarkdown from 'react-markdown';
import type { Components } from 'react-markdown';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip, 
  ResponsiveContainer, 
  Cell 
} from 'recharts';

// Import our layers
import {
  BibleResponse,
  InstalledTranslation,
  TextStats,
  WordFrequency,
} from './types/bible';
import type { SearchResponse } from './types/search';
import { bibleRepository } from './repositories/bibleRepository';
import { bibleService } from './services/bibleService';
import { bookName } from './utils/bookNames';

type ViewMode = 'reader' | 'analytics' | 'search';
type SearchType = 'verse' | 'search';

function markdownComponents(options: {
  invert: boolean;
  /** Larger ## / ### hierarchy for AI Insights (Reader panel). */
  insightLayout?: boolean;
  /** Dark analytics card: ## section titles larger than body **bold**. */
  toneLayout?: boolean;
}): Components {
  const { invert, insightLayout, toneLayout } = options;
  const body = invert ? 'text-gray-200' : 'text-[#333]';
  const strongCls = invert ? 'font-semibold text-white' : 'font-semibold text-[#1A1A1A]';
  const codeBg = invert ? 'bg-gray-800 text-gray-100' : 'bg-[#F0F0F0] text-[#1A1A1A]';
  const quoteBorder = invert ? 'border-gray-600' : 'border-[#D4A373]';

  const headings: Pick<Components, 'h1' | 'h2' | 'h3'> =
    insightLayout && !invert
      ? {
          h1: ({ children }) => (
            <h1 className="mb-4 mt-1 text-3xl font-bold tracking-tight text-[#1A1A1A] first:mt-0">
              {children}
            </h1>
          ),
          h2: ({ children }) => (
            <h2 className="mt-10 border-b border-[#E8E4DC] pb-2 text-2xl font-bold text-[#1A1A1A] first:mt-2 mb-3">
              {children}
            </h2>
          ),
          h3: ({ children }) => (
            <h3 className="mb-2 mt-6 text-lg font-semibold text-[#1A1A1A]">
              {children}
            </h3>
          ),
        }
      : toneLayout && invert
        ? {
            h1: ({ children }) => (
              <h1 className="mb-3 mt-1 text-2xl font-bold tracking-tight text-gray-100 first:mt-0">
                {children}
              </h1>
            ),
            h2: ({ children }) => (
              <h2 className="mb-3 mt-8 border-b border-gray-600 pb-2 text-xl font-bold text-gray-100 first:mt-3">
                {children}
              </h2>
            ),
            h3: ({ children }) => (
              <h3 className="mb-2 mt-5 text-lg font-semibold text-gray-100">
                {children}
              </h3>
            ),
          }
        : {
            h1: ({ children }) => (
              <h3 className={`mb-2 mt-4 text-lg font-semibold ${strongCls}`}>
                {children}
              </h3>
            ),
            h2: ({ children }) => (
              <h3 className={`mb-2 mt-3 text-base font-semibold ${strongCls}`}>
                {children}
              </h3>
            ),
            h3: ({ children }) => (
              <h4 className={`mb-1 mt-2 text-sm font-semibold ${strongCls}`}>
                {children}
              </h4>
            ),
          };

  return {
    ...headings,
    p: ({ children }) => (
      <p
        className={`mb-3 last:mb-0 leading-relaxed ${body} ${
          toneLayout && invert ? 'text-base' : ''
        }`}
      >
        {children}
      </p>
    ),
    strong: ({ children }) => (
      <strong
        className={
          toneLayout && invert
            ? 'font-semibold text-gray-200'
            : strongCls
        }
      >
        {children}
      </strong>
    ),
    em: ({ children }) => <em className="italic">{children}</em>,
    ul: ({ children }) => (
      <ul className={`mb-3 list-disc space-y-1 pl-5 ${body}`}>{children}</ul>
    ),
    ol: ({ children }) => (
      <ol className={`mb-3 list-decimal space-y-1 pl-5 ${body}`}>{children}</ol>
    ),
    li: ({ children }) => <li className="leading-relaxed">{children}</li>,
    code: ({ children }) => (
      <code className={`rounded px-1 py-0.5 font-mono text-[0.9em] ${codeBg}`}>
        {children}
      </code>
    ),
    blockquote: ({ children }) => (
      <blockquote
        className={`my-3 border-l-4 pl-3 opacity-90 ${quoteBorder}`}
      >
        {children}
      </blockquote>
    ),
    hr: () => (
      <hr
        className={`my-4 border-0 border-t ${invert ? 'border-gray-600' : 'border-[#E5E5E5]'}`}
      />
    ),
  };
}

export default function App() {
  // UI State
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<BibleResponse | null>(null);
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(
    null
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<string[]>([]);
  const [aiInsight, setAiInsight] = useState<string | null>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>('reader');
  const [searchType, setSearchType] = useState<SearchType>('verse');
  const [analyticsMode, setAnalyticsMode] = useState<'reference' | 'chapter' | 'book' | 'compare'>('reference');
  const [toneAnalysis, setToneAnalysis] = useState<string | null>(null);
  const [translation, setTranslation] = useState<string | null>(null);
  const [installedTranslations, setInstalledTranslations] = useState<
    InstalledTranslation[]
  >([]);
  const [translationsLoadError, setTranslationsLoadError] = useState<
    string | null
  >(null);
  const [showTranslations, setShowTranslations] = useState(false);
  
  // Native Analytics State
  const [nativeStats, setNativeStats] = useState<TextStats | null>(null);
  const [nativeFrequency, setNativeFrequency] = useState<WordFrequency[]>([]);

  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    inputRef.current?.focus();
    const savedHistory = localStorage.getItem('clible_history');
    if (savedHistory) setHistory(JSON.parse(savedHistory));
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const list = await bibleRepository.listInstalledTranslations();
        if (cancelled) return;
        setInstalledTranslations(list);
        setTranslationsLoadError(null);
        const savedId = localStorage.getItem('clible_translation_id');
        if (savedId && list.some((t) => t.id === savedId)) {
          setTranslation(savedId);
        }
      } catch (e: unknown) {
        if (!cancelled) {
          setTranslationsLoadError(
            e instanceof Error ? e.message : 'Failed to load translations.'
          );
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  const saveToHistory = (q: string) => {
    const newHistory = [q, ...history.filter(h => h !== q)].slice(0, 10);
    setHistory(newHistory);
    localStorage.setItem('clible_history', JSON.stringify(newHistory));
  };

  const handleSearch = async (q: string) => {
    if (!q.trim()) return;
    if (!translation) {
      setError(
        'Select a translation first (globe menu). Install one with: clible seed install <id>'
      );
      return;
    }
    setLoading(true);
    setError(null);
    setAiInsight(null);
    setToneAnalysis(null);
    setNativeStats(null);
    setNativeFrequency([]);
    
    try {
      if (searchType === 'verse') {
        const data = await bibleRepository.getVerse(q, translation);
        setResult(data);
        setViewMode('reader');
      } else {
        const response = await bibleRepository.search(q, translation);
        setSearchResponse(response);
        setViewMode('search');
      }
      saveToHistory(q);
      setQuery('');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAiInsight = async () => {
    if (!result) return;
    setAiLoading(true);
    try {
      const insight = await bibleService.getAiInsight(result);
      setAiInsight(insight);
    } catch (err) {
      setAiInsight("Failed to generate insights.");
    } finally {
      setAiLoading(false);
    }
  };

  const handleAnalytics = async (modeOverride?: 'reference' | 'chapter' | 'book' | 'compare') => {
    if (!result) return;
    if (!translation) {
      setError(
        'Select a translation first (globe menu). Install one with: clible seed install <id>'
      );
      return;
    }
    const mode = modeOverride || analyticsMode;
    setAnalyticsMode(mode);
    setViewMode('analytics');
    setAiLoading(true);
    try {
      const { stats, frequency } = await bibleService.getNativeAnalytics(
        mode,
        result.reference,
        translation
      );
      setNativeStats(stats);
      setNativeFrequency(frequency);
      
      // Also get AI tone
      const tone = await bibleService.getAiTone(result.text);
      setToneAnalysis(tone);
    } catch (err) {
      console.error("Analytics error:", err);
      // Fallback to JS calculation if CLI fails
      setNativeStats(bibleService.calculateStats(result.text));
      setNativeFrequency(bibleService.calculateWordFrequency(result.text));
    } finally {
      setAiLoading(false);
    }
  };

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Enter') handleSearch(query);
  };

  return (
    <div className="min-h-screen bg-[#FDFCFB] text-[#1A1A1A] font-sans selection:bg-[#E6D5B8] selection:text-[#1A1A1A]">
      <header className="border-b border-[#E5E5E5] bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-5xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 bg-[#1A1A1A] rounded-lg flex items-center justify-center text-white">
              <Terminal size={18} />
            </div>
            <h1 className="text-xl font-semibold tracking-tight">Clible <span className="text-[#8E8E8E] font-normal">Web</span></h1>
          </div>
          
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setShowTranslations(!showTranslations)}
              className="flex items-center gap-2 px-3 py-1.5 hover:bg-[#F5F5F5] rounded-full transition-colors text-sm font-medium border border-[#E5E5E5]"
            >
              <Globe size={16} className="text-[#D4A373]" />
              <span className={translation ? 'uppercase' : 'text-[#8E8E8E] normal-case'}>
                {translation ?? 'Choose translation'}
              </span>
            </button>
            <button onClick={() => setShowHistory(!showHistory)} className="p-2 hover:bg-[#F5F5F5] rounded-full transition-colors relative">
              <History size={20} />
              {history.length > 0 && <span className="absolute top-1 right-1 w-2 h-2 bg-[#D4A373] rounded-full" />}
            </button>
            <button className="p-2 hover:bg-[#F5F5F5] rounded-full transition-colors"><Settings size={20} /></button>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-12">
        {/* Search Bar with Mode Toggle */}
        <div className="space-y-4 mb-8">
          <div className="flex gap-2">
            <button 
              onClick={() => setSearchType('verse')}
              className={`px-3 py-1 rounded-full text-xs font-semibold transition-all ${searchType === 'verse' ? 'bg-[#1A1A1A] text-white' : 'bg-[#F5F5F5] text-[#8E8E8E]'}`}
            >
              Verse Lookup
            </button>
            <button 
              onClick={() => setSearchType('search')}
              className={`px-3 py-1 rounded-full text-xs font-semibold transition-all ${searchType === 'search' ? 'bg-[#1A1A1A] text-white' : 'bg-[#F5F5F5] text-[#8E8E8E]'}`}
            >
              FTS5 Search
            </button>
          </div>

          {error && (
            <p className="text-sm text-red-600 mb-2" role="alert">
              {error}
            </p>
          )}
          
          <div className="relative group">
            <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none text-[#8E8E8E] group-focus-within:text-[#1A1A1A] transition-colors">
              {searchType === 'verse' ? <Book size={20} /> : <Search size={20} />}
            </div>
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={searchType === 'verse' ? "Enter verse (e.g., John 3:16)..." : "Search text (e.g., 'mountain', 'grace')..."}
              className="w-full bg-white border-2 border-[#E5E5E5] focus:border-[#1A1A1A] rounded-2xl py-4 pl-12 pr-4 text-lg outline-none transition-all shadow-sm hover:shadow-md"
            />
          </div>
        </div>

        {result && (
          <div className="flex gap-1 bg-[#F5F5F5] p-1 rounded-xl w-fit mb-8">
            <button 
              onClick={() => setViewMode('reader')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${viewMode === 'reader' ? 'bg-white shadow-sm text-[#1A1A1A]' : 'text-[#8E8E8E] hover:text-[#1A1A1A]'}`}
            >
              <div className="flex items-center gap-2"><Book size={16} /> Reader</div>
            </button>
            <button 
              onClick={() => void handleAnalytics()}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${viewMode === 'analytics' ? 'bg-white shadow-sm text-[#1A1A1A]' : 'text-[#8E8E8E] hover:text-[#1A1A1A]'}`}
            >
              <div className="flex items-center gap-2"><Activity size={16} /> Analytics</div>
            </button>
          </div>
        )}

        <AnimatePresence mode="wait">
          {viewMode === 'reader' ? (
            <motion.div key="reader" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }}>
              {result ? (
                <div className="space-y-12">
                  <section className="space-y-8">
                    <div className="flex items-end justify-between border-b border-[#F5F5F5] pb-4">
                      <h2 className="text-4xl font-serif italic text-[#1A1A1A]">{result.reference}</h2>
                      <span className="text-sm font-mono text-[#8E8E8E] uppercase tracking-widest">{result.translation_name}</span>
                    </div>
                    <p
                      className={`text-2xl leading-relaxed font-serif text-[#333] ${
                        result.verses.length === 0
                          ? 'first-letter:float-left first-letter:mt-1 first-letter:mr-3 first-letter:text-5xl first-letter:font-bold'
                          : ''
                      }`}
                    >
                      {result.verses.length > 0 ? (
                        result.verses.map((v, idx) => (
                          <span
                            key={`${v.book_name}-${v.chapter}-${v.verse}-${idx}`}
                            className="inline"
                          >
                            <sup
                              className="mx-0.5 align-super font-sans text-[0.55em] font-semibold text-[#8E8E8E]"
                              aria-label={`Verse ${v.verse}`}
                            >
                              {v.verse}
                            </sup>
                            {v.text}
                            {idx < result.verses.length - 1 ? ' ' : null}
                          </span>
                        ))
                      ) : (
                        result.text
                      )}
                    </p>
                    <div className="flex items-center gap-4 pt-4">
                      <button className="flex items-center gap-2 px-4 py-2 bg-[#F5F5F5] hover:bg-[#E5E5E5] rounded-full text-sm font-medium transition-colors"><Share2 size={16} /> Share</button>
                      <button className="flex items-center gap-2 px-4 py-2 bg-[#F5F5F5] hover:bg-[#E5E5E5] rounded-full text-sm font-medium transition-colors"><Download size={16} /> Export</button>
                    </div>
                  </section>
                  <section className="bg-[#FAF9F6] border border-[#E5E5E5] rounded-3xl p-8 space-y-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2 text-[#D4A373]"><Sparkles size={20} /><span className="font-semibold uppercase tracking-wider text-xs">AI Insights</span></div>
                      {!aiInsight && !aiLoading && <button onClick={handleAiInsight} className="text-sm font-medium hover:underline flex items-center gap-1">Generate Insights <ArrowRight size={14} /></button>}
                    </div>
                    {aiLoading ? <div className="py-12 flex flex-col items-center justify-center gap-4 text-[#8E8E8E]"><Loader2 size={32} className="animate-spin" /><p className="text-sm font-medium animate-pulse">Consulting the archives...</p></div> : aiInsight ? (
                      <div className="max-w-none font-sans">
                        <ReactMarkdown
                          components={markdownComponents({
                            invert: false,
                            insightLayout: true,
                          })}
                        >
                          {aiInsight}
                        </ReactMarkdown>
                      </div>
                    ) : <p className="text-[#8E8E8E] text-sm italic">Click above for AI-powered context and study notes.</p>}
                  </section>
                </div>
              ) : <div className="py-24 text-center space-y-6"><div className="w-16 h-16 bg-[#F5F5F5] rounded-full flex items-center justify-center mx-auto text-[#D4A373]"><Book size={32} /></div><h3 className="text-xl font-medium">Ready for study</h3><p className="text-[#8E8E8E]">Enter a verse to begin.</p></div>}
            </motion.div>
          ) : viewMode === 'search' ? (
            <motion.div key="search" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }} className="space-y-6">
              <div className="flex flex-col gap-2 border-b border-[#F5F5F5] pb-4">
                <div className="flex items-center justify-between">
                  <h2 className="text-2xl font-serif italic">Search Results</h2>
                  {searchResponse && (
                    <span className="text-sm text-[#8E8E8E]">
                      {searchResponse.statistics.uniqueVerses} unique verse
                      {searchResponse.statistics.uniqueVerses === 1 ? '' : 's'}
                    </span>
                  )}
                </div>
                {searchResponse && (
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                    <div className="space-y-3">
                      <div className="rounded-xl border border-[#E5E5E5] bg-[#FAF9F6] px-3 py-2">
                        <div className="text-[10px] uppercase tracking-wider text-[#8E8E8E]">
                          Occurrences
                        </div>
                        <div className="font-mono font-semibold text-[#1A1A1A]">
                          {searchResponse.statistics.totalOccurrences}
                        </div>
                      </div>
                      <div className="rounded-xl border border-[#E5E5E5] bg-[#FAF9F6] px-3 py-2">
                        <div className="text-[10px] uppercase tracking-wider text-[#8E8E8E]">
                          Unique verses
                        </div>
                        <div className="font-mono font-semibold text-[#1A1A1A]">
                          {searchResponse.statistics.uniqueVerses}
                        </div>
                      </div>
                      <div className="rounded-xl border border-[#E5E5E5] bg-[#FAF9F6] px-3 py-2">
                        <div className="text-[10px] uppercase tracking-wider text-[#8E8E8E]">
                          Books
                        </div>
                        <div className="font-mono font-semibold text-[#1A1A1A]">
                          {searchResponse.statistics.booksWithMatches}
                        </div>
                      </div>
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
                      {searchResponse.statistics.topBooks.length === 0 ? (
                        <div className="pt-2 font-mono text-xs text-[#8E8E8E]">
                          —
                        </div>
                      ) : (
                        <ol className="pt-2 space-y-1">
                          {searchResponse.statistics.topBooks.map(
                            ([bookId, count], idx) => (
                              <li
                                key={`${bookId}-${idx}`}
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
                            )
                          )}
                        </ol>
                      )}
                    </div>
                  </div>
                )}
                {searchResponse &&
                  searchResponse.rows.length > 0 &&
                  searchResponse.rows.length <
                    searchResponse.statistics.uniqueVerses && (
                    <p className="text-sm text-[#8E8E8E]">
                      Showing first {searchResponse.rows.length} of{' '}
                      {searchResponse.statistics.uniqueVerses} matching verses
                      (limit).
                    </p>
                  )}
              </div>
              {searchResponse && searchResponse.rows.length === 0 && (
                <p className="text-center text-[#8E8E8E] py-8">
                  No verses found for this search.
                </p>
              )}
              <div className="space-y-4">
                {searchResponse?.rows.map((res, i) => (
                  <button 
                    key={i} 
                    onClick={() => handleSearch(res.reference)}
                    className="w-full text-left p-6 bg-white border border-[#E5E5E5] rounded-2xl hover:border-[#1A1A1A] transition-all group"
                  >
                    <div className="flex justify-between items-center mb-2">
                      <span className="font-bold text-[#D4A373]">{res.reference}</span>
                      <ChevronRight size={16} className="text-[#E5E5E5] group-hover:text-[#1A1A1A] transition-colors" />
                    </div>
                    <p className="text-[#4A4A4A] line-clamp-2">{res.text}</p>
                  </button>
                ))}
              </div>
            </motion.div>
          ) : (
            <motion.div key="analytics" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }} className="space-y-8">
              <div className="flex gap-2 bg-[#F5F5F5] p-1 rounded-xl w-fit">
                {(['reference', 'chapter', 'book'] as const).map((m) => (
                  <button 
                    key={m}
                    onClick={() => handleAnalytics(m)}
                    className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all capitalize ${analyticsMode === m ? 'bg-white shadow-sm text-[#1A1A1A]' : 'text-[#8E8E8E] hover:text-[#1A1A1A]'}`}
                  >
                    {m}
                  </button>
                ))}
              </div>

              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                {[
                  { label: 'Words', value: nativeStats?.wordCount, icon: MessageSquareQuote },
                  { label: 'Unique', value: nativeStats?.uniqueWords, icon: Hash },
                  { label: 'Avg Length', value: nativeStats?.avgWordLength, icon: Activity },
                  { label: 'Chars', value: nativeStats?.charCount, icon: BarChart3 }
                ].map((s, i) => (
                  <div key={i} className="bg-white border border-[#E5E5E5] p-4 rounded-2xl shadow-sm">
                    <div className="flex items-center gap-2 text-[#8E8E8E] mb-2"><s.icon size={14} /><span className="text-[10px] uppercase tracking-wider font-semibold">{s.label}</span></div>
                    <div className="text-2xl font-mono font-bold">{s.value || '0'}</div>
                  </div>
                ))}
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div className="bg-white border border-[#E5E5E5] p-6 rounded-3xl shadow-sm space-y-4">
                  <h3 className="text-sm font-semibold uppercase tracking-wider text-[#8E8E8E] flex items-center gap-2"><BarChart3 size={16} /> Word Frequency</h3>
                  <div className="h-64 w-full">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={nativeFrequency} layout="vertical" margin={{ left: 20 }}>
                        <XAxis type="number" hide />
                        <YAxis dataKey="name" type="category" width={80} axisLine={false} tickLine={false} tick={{ fontSize: 12, fill: '#8E8E8E' }} />
                        <Tooltip cursor={{ fill: '#F5F5F5' }} contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }} />
                        <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                          {nativeFrequency.map((_, i) => <Cell key={i} fill={i === 0 ? '#1A1A1A' : '#D4A373'} fillOpacity={1 - (i * 0.1)} />)}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div className="bg-[#1A1A1A] text-white p-6 rounded-3xl shadow-xl space-y-4 relative overflow-hidden">
                  <div className="absolute top-0 right-0 p-6 opacity-10"><Sparkles size={80} /></div>
                  <h3 className="text-sm font-semibold uppercase tracking-wider text-[#8E8E8E] flex items-center gap-2"><Sparkles size={16} className="text-[#D4A373]" /> AI Tone Analysis</h3>
                  {aiLoading ? (
                    <div className="py-12 flex flex-col items-center justify-center gap-2">
                      <Loader2 size={24} className="animate-spin text-[#D4A373]" />
                      <span className="text-xs text-[#8E8E8E]">Analyzing linguistic patterns...</span>
                    </div>
                  ) : toneAnalysis ? (
                    <div className="text-lg font-serif leading-relaxed">
                      <ReactMarkdown
                        components={markdownComponents({
                          invert: true,
                          toneLayout: true,
                        })}
                      >
                        {toneAnalysis}
                      </ReactMarkdown>
                    </div>
                  ) : (
                    <p className="text-lg font-serif italic leading-relaxed text-gray-400">
                      Select a passage to analyze its tone.
                    </p>
                  )}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Translation Modal */}
      <AnimatePresence>
        {showTranslations && (
          <motion.div 
            initial={{ opacity: 0 }} 
            animate={{ opacity: 1 }} 
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] bg-black/40 backdrop-blur-sm flex items-center justify-center p-6"
          >
            <motion.div 
              initial={{ scale: 0.9, opacity: 0 }} 
              animate={{ scale: 1, opacity: 1 }}
              className="bg-white w-full max-w-lg rounded-3xl shadow-2xl overflow-hidden"
            >
              <div className="p-6 border-b border-[#F5F5F5] flex justify-between items-center">
                <h3 className="text-lg font-semibold">Select Translation</h3>
                <button onClick={() => setShowTranslations(false)}><X size={20} /></button>
              </div>
              <div className="p-6 max-h-[60vh] overflow-y-auto grid grid-cols-1 sm:grid-cols-2 gap-3">
                {translationsLoadError && (
                  <p className="col-span-full text-sm text-red-600" role="alert">
                    {translationsLoadError}
                  </p>
                )}
                {!translationsLoadError && installedTranslations.length === 0 && (
                  <p className="col-span-full text-sm text-[#8E8E8E]">
                    No translations installed. On the machine or container where Clible runs, install
                    one with:{' '}
                    <code className="font-mono text-[#1A1A1A]">clible seed install &lt;id&gt;</code>
                    . Then refresh this page.
                  </p>
                )}
                {installedTranslations.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => {
                      setTranslation(t.id);
                      localStorage.setItem('clible_translation_id', t.id);
                      setShowTranslations(false);
                      setError(null);
                    }}
                    className={`px-4 py-3 rounded-xl text-left border-2 transition-all ${translation === t.id ? 'border-[#1A1A1A] bg-[#F5F5F5]' : 'border-[#E5E5E5] hover:border-[#1A1A1A]'}`}
                  >
                    <span className="uppercase font-bold text-sm block">{t.id}</span>
                    <span className="text-xs text-[#8E8E8E] block mt-1">{t.name}</span>
                    <span className="text-[10px] text-[#8E8E8E] uppercase tracking-wide">
                      {t.language} · {t.format}
                    </span>
                  </button>
                ))}
              </div>
              <div className="p-6 bg-[#F5F5F5] text-xs text-[#8E8E8E]">
                <p>
                  Only translations installed in this environment appear here. Use{' '}
                  <code className="font-mono text-[#1A1A1A]">clible seed list</code> in the terminal to
                  verify.
                </p>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <footer className="max-w-5xl mx-auto px-6 py-12 border-t border-[#F5F5F5] mt-24">
        <div className="flex flex-col md:flex-row justify-between items-center gap-8">
          <div className="flex items-center gap-2 text-[#8E8E8E] text-sm"><Terminal size={14} /><span>Inspired by Clible CLI</span></div>
          <div className="flex gap-8 text-sm font-medium text-[#8E8E8E]">
            <a href="#" className="hover:text-[#1A1A1A] transition-colors">Documentation</a>
            <a href="#" className="hover:text-[#1A1A1A] transition-colors">API</a>
            <a href="#" className="hover:text-[#1A1A1A] transition-colors">GitHub</a>
          </div>
          <div className="text-[#8E8E8E] text-xs font-mono">v2.0.0-WEB</div>
        </div>
      </footer>
    </div>
  );
}
