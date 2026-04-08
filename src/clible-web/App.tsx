/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useEffect, useRef, KeyboardEvent } from 'react';
import {
  Search,
  Book,
  Terminal,
  History,
  Settings,
  Globe,
  Activity,
  LogOut,
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';

import {
  BibleResponse,
  InstalledTranslation,
  TextStats,
  WordFrequency,
} from './types/bible';
import type { SearchResponse } from './types/search';
import { bibleRepository } from './repositories/bibleRepository';
import { bibleService } from './services/bibleService';
import { ReaderView } from './components/ReaderView';
import { SearchView } from './components/SearchView';
import { AnalyticsView } from './components/AnalyticsView';
import type { AnalyticsMode } from './components/AnalyticsView';
import { TranslationModal } from './components/TranslationModal';
import { SettingsPanel } from './components/SettingsPanel';
import { useAuth } from './AuthContext';
import { LoginView } from './views/LoginView';
import { useSettings } from './user/SettingsContext';

type ViewMode = 'reader' | 'analytics' | 'search';
type SearchType = 'verse' | 'search';

export default function App() {
  const { user, loading: authLoading, login, logout } = useAuth();
  const {
    settings,
    loading: settingsLoading,
    error: settingsError,
    updateSettings,
  } = useSettings();

  const [query, setQuery] = useState('');
  const [result, setResult] = useState<BibleResponse | null>(null);
  const [searchResponse, setSearchResponse] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<string[]>([]);
  const [aiInsight, setAiInsight] = useState<string | null>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>('reader');
  const [searchType, setSearchType] = useState<SearchType>('verse');
  const [analyticsMode, setAnalyticsMode] = useState<AnalyticsMode>('reference');
  const [toneAnalysis, setToneAnalysis] = useState<string | null>(null);
  const [installedTranslations, setInstalledTranslations] = useState<InstalledTranslation[]>([]);
  const [translationsLoadError, setTranslationsLoadError] = useState<string | null>(null);
  const [showTranslations, setShowTranslations] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [nativeStats, setNativeStats] = useState<TextStats | null>(null);
  const [nativeFrequency, setNativeFrequency] = useState<WordFrequency[]>([]);

  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (settingsError) {
      setTranslationsLoadError(settingsError);
    }
  }, [settingsError]);

  useEffect(() => {
    if (!user) return;
    inputRef.current?.focus();
    const savedHistory = localStorage.getItem('clible_history');
    if (savedHistory) setHistory(JSON.parse(savedHistory));
  }, [user]);

  useEffect(() => {
    if (!user) return;
    let cancelled = false;
    (async () => {
      try {
        const list = await bibleRepository.listInstalledTranslations();
        if (cancelled) return;
        setInstalledTranslations(list);
        setTranslationsLoadError(null);
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
  }, [user]);

  useEffect(() => {
    if (!user) return;
    if (settingsLoading) return;
    if (!settings) return;
    if (settings.translationId) return;
    if (installedTranslations.length === 0) return;

    // One-time migration from legacy localStorage key into server settings.
    const legacyId = localStorage.getItem("clible_translation_id");
    if (!legacyId) return;
    if (!installedTranslations.some((t) => t.id === legacyId)) return;

    void updateSettings({ translationId: legacyId })
      .then(() => {
        localStorage.removeItem("clible_translation_id");
      })
      .catch(() => {
        // Keep legacy value if server write failed.
      });
  }, [user, settingsLoading, settings, installedTranslations, updateSettings]);

  if (authLoading) return <div className="min-h-screen flex items-center justify-center">Loading...</div>;
  if (!user) return <LoginView onSuccess={login} />;

  const saveToHistory = (q: string) => {
    const newHistory = [q, ...history.filter((h) => h !== q)].slice(0, 10);
    setHistory(newHistory);
    localStorage.setItem('clible_history', JSON.stringify(newHistory));
  };

  const handleSearch = async (q: string) => {
    if (!q.trim()) return;
    if (!settings?.translationId) {
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
        const data = await bibleRepository.getVerse(q, settings.translationId);
        setResult(data);
        setViewMode('reader');
      } else {
        const response = await bibleRepository.search(q, settings.translationId);
        setSearchResponse(response);
        setViewMode('search');
      }
      saveToHistory(q);
      setQuery('');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred.');
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
    } catch {
      setAiInsight('Failed to generate insights.');
    } finally {
      setAiLoading(false);
    }
  };

  const handleAnalytics = async (modeOverride?: AnalyticsMode) => {
    if (!result) return;
    if (!settings?.translationId) {
      setError(
        'Select a translation first (globe menu). Install one with: clible seed install <id>'
      );
      return;
    }
    const mode = modeOverride ?? analyticsMode;
    setAnalyticsMode(mode);
    setViewMode('analytics');
    setAiLoading(true);
    try {
      const { stats, frequency } = await bibleService.getNativeAnalytics(
        mode,
        result.reference,
        settings.translationId
      );
      setNativeStats(stats);
      setNativeFrequency(frequency);
      const tone = await bibleService.getAiTone(result.text);
      setToneAnalysis(tone);
    } catch (err) {
      console.error('Analytics error:', err);
      setNativeStats(bibleService.calculateStats(result.text));
      setNativeFrequency(bibleService.calculateWordFrequency(result.text));
    } finally {
      setAiLoading(false);
    }
  };

  const handleTranslationSelect = (id: string) => {
    void updateSettings({ translationId: id }).catch((e: unknown) => {
      setTranslationsLoadError(
        e instanceof Error ? e.message : "Failed to save settings."
      );
    });
    setShowTranslations(false);
    setError(null);
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
            <h1 className="text-xl font-semibold tracking-tight">
              Clible <span className="text-[#8E8E8E] font-normal">Web</span>
            </h1>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowTranslations(!showTranslations)}
              className="flex items-center gap-2 px-3 py-1.5 hover:bg-[#F5F5F5] rounded-full transition-colors text-sm font-medium border border-[#E5E5E5]"
            >
              <Globe size={16} className="text-[#D4A373]" />
              <span
                className={
                  settings?.translationId ? 'uppercase' : 'text-[#8E8E8E] normal-case'
                }
              >
                {settings?.translationId ?? 'Choose translation'}
              </span>
            </button>
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="p-2 hover:bg-[#F5F5F5] rounded-full transition-colors relative"
            >
              <History size={20} />
              {history.length > 0 && (
                <span className="absolute top-1 right-1 w-2 h-2 bg-[#D4A373] rounded-full" />
              )}
            </button>
            <button
              onClick={() => setShowSettings(true)}
              className="p-2 hover:bg-[#F5F5F5] rounded-full transition-colors"
              title="Settings"
            >
              <Settings size={20} />
            </button>
            <div className="flex items-center gap-2 pl-2 border-l border-[#E5E5E5]">
              <span className="text-sm text-[#8E8E8E]">{user!.username}</span>
              <button
                onClick={() => void logout()}
                className="p-2 hover:bg-[#F5F5F5] rounded-full transition-colors text-[#8E8E8E] hover:text-[#1A1A1A]"
                title="Sign out"
              >
                <LogOut size={18} />
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-12">
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
              placeholder={
                searchType === 'verse'
                  ? "Enter verse (e.g., John 3:16)..."
                  : "Search text (e.g., 'mountain', 'grace')..."
              }
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
          {viewMode === 'reader' && (
            <motion.div key="reader" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }}>
              <ReaderView
                result={result}
                aiInsight={aiInsight}
                aiLoading={aiLoading}
                onAiInsight={handleAiInsight}
              />
            </motion.div>
          )}
          {viewMode === 'search' && (
            <motion.div key="search" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
              <SearchView
                searchResponse={searchResponse}
                onResultClick={handleSearch}
              />
            </motion.div>
          )}
          {viewMode === 'analytics' && (
            <motion.div key="analytics" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
              <AnalyticsView
                analyticsMode={analyticsMode}
                nativeStats={nativeStats}
                nativeFrequency={nativeFrequency}
                toneAnalysis={toneAnalysis}
                aiLoading={aiLoading}
                onModeChange={(m) => void handleAnalytics(m)}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      <AnimatePresence>
        {showTranslations && (
          <TranslationModal
            installedTranslations={installedTranslations}
            translationsLoadError={translationsLoadError}
            activeTranslation={settings?.translationId ?? null}
            onSelect={handleTranslationSelect}
            onClose={() => setShowTranslations(false)}
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {showSettings && (
          <SettingsPanel
            open={showSettings}
            onClose={() => setShowSettings(false)}
            username={user!.username}
            userId={user!.id}
            settings={settings}
            loading={settingsLoading}
            error={settingsError}
            installedTranslations={installedTranslations}
            onPickTranslation={() => {
              setShowSettings(false);
              setShowTranslations(true);
            }}
            onSetTheme={(theme) => {
              void updateSettings({ theme }).catch(() => {});
            }}
          />
        )}
      </AnimatePresence>

      <footer className="max-w-5xl mx-auto px-6 py-12 border-t border-[#F5F5F5] mt-24">
        <div className="flex flex-col md:flex-row justify-between items-center gap-8">
          <div className="flex items-center gap-2 text-[#8E8E8E] text-sm">
            <Terminal size={14} /><span>Inspired by Clible CLI</span>
          </div>
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
