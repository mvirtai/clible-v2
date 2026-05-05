/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useEffect } from 'react';
import {
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
  AvailableTranslation,
  BibleResponse,
  InstalledTranslation,
  TextStats,
  WordFrequency,
} from './types/bible';
import type { CompareResult } from './types/compare';
import type { SearchResponse } from './types/search';
import type { SearchQueryOptions, SearchHistoryEntry, SavedSearchRow } from './types/searchQuery';
import { bibleRepository } from './repositories/bibleRepository';
import { bibleService } from './services/bibleService';
import { ReaderView } from './components/ReaderView';
import { SearchView } from './components/SearchView';
import { SearchPanel, type StudyEntryTab } from './components/SearchPanel';
import { SavedSearchesList } from './components/SavedSearchesList';
import { AnalyticsView } from './components/AnalyticsView';
import type { AnalyticsMode } from './components/AnalyticsView';
import { CompareView } from './components/CompareView';
import { TranslationModal } from './components/TranslationModal';
import { SettingsPanel } from './components/SettingsPanel';
import { useAuth } from './AuthContext';
import { LoginView } from './views/LoginView';
import { useSettings } from './user/SettingsContext';
import { ExportModal, ExportFormat } from './components/ExportModal';
import { downloadFile } from './utils/download';
import { t, type UILanguage } from './utils/i18n';

function inferUILanguageFromTranslation(language: string | undefined): 'en' | 'fi' | null {
  const lower = (language ?? '').toLowerCase().trim();
  if (lower === 'fi' || lower.startsWith('fin')) return 'fi';
  if (lower === 'en') return 'en';
  return null;
}

type ViewMode = 'reader' | 'analytics' | 'search' | 'compare';
type SearchType = 'verse' | 'search';

export default function App() {
  const { user, loading: authLoading, login, logout } = useAuth();
  const {
    settings,
    loading: settingsLoading,
    error: settingsError,
    updateSettings,
  } = useSettings();

  const [effectiveTheme, setEffectiveTheme] = useState<'light' | 'dark'>('light');

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
  const [availableTranslations, setAvailableTranslations] = useState<AvailableTranslation[]>([]);
  const [loadingAvailableTranslations, setLoadingAvailableTranslations] = useState(false);
  const [translationsLoadError, setTranslationsLoadError] = useState<string | null>(null);
  const [translationInstallError, setTranslationInstallError] = useState<string | null>(null);
  const [translationInstallSuccess, setTranslationInstallSuccess] = useState<string | null>(null);
  const [installingTranslationId, setInstallingTranslationId] = useState<string | null>(null);
  const [showTranslations, setShowTranslations] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [nativeStats, setNativeStats] = useState<TextStats | null>(null);
  const [nativeFrequency, setNativeFrequency] = useState<WordFrequency[]>([]);
  const [showExport, setShowExport] = useState(false);
  const [searchHistoryApi, setSearchHistoryApi] = useState<SearchHistoryEntry[]>([]);
  const [savedSearches, setSavedSearches] = useState<SavedSearchRow[]>([]);
  const [currentSearchTerms, setCurrentSearchTerms] = useState<string[]>([]);
  const [lastSearchOptions, setLastSearchOptions] = useState<SearchQueryOptions | null>(null);
  const [exporting, setExporting] = useState(false);
  const [compareResult, setCompareResult] = useState<CompareResult | null>(null);
  const [compareLeft, setCompareLeft] = useState<string | null>(null);
  const [compareRight, setCompareRight] = useState<string | null>(null);
  const [compareLoading, setCompareLoading] = useState(false);
  const [compareError, setCompareError] = useState<string | null>(null);
  const [exportContext, setExportContext] = useState<{
    cmd: "verse" | "search" | "analytics";
    args: string;
    title: string;
    aiInsight?: string | null;
  } | null>(null);
  const [studyEntryTab, setStudyEntryTab] = useState<StudyEntryTab>('scripture');

  useEffect(() => {
    if (settingsError) {
      setTranslationsLoadError(settingsError);
    }
  }, [settingsError]);

  useEffect(() => {
    const selected = settings?.theme ?? 'system';
    const mq = window.matchMedia?.('(prefers-color-scheme: dark)');

    const compute = () => {
      if (selected === 'light' || selected === 'dark') {
        setEffectiveTheme(selected);
        return;
      }
      setEffectiveTheme(mq?.matches ? 'dark' : 'light');
    };

    compute();

    if (selected === 'system' && mq) {
      mq.addEventListener('change', compute);
      return () => mq.removeEventListener('change', compute);
    }
    return;
  }, [settings?.theme]);

  useEffect(() => {
    document.documentElement.dataset.theme = effectiveTheme;
    return () => {
      delete document.documentElement.dataset.theme;
    };
  }, [effectiveTheme]);

  useEffect(() => {
    if (!user) return;
    const savedHistory = localStorage.getItem('clible_history');
    if (savedHistory) setHistory(JSON.parse(savedHistory));
  }, [user]);

  useEffect(() => {
    if (!user) return;
    let cancelled = false;
    (async () => {
      try {
        setLoadingAvailableTranslations(true);
        const [installed, available] = await Promise.all([
          bibleRepository.listInstalledTranslations(),
          bibleRepository.listAvailableTranslations(),
        ]);
        if (cancelled) return;
        setInstalledTranslations(installed);
        setAvailableTranslations(available);
        setTranslationsLoadError(null);
      } catch (e: unknown) {
        if (!cancelled) {
          setTranslationsLoadError(
            e instanceof Error
              ? e.message
              : t((settings?.uiLanguage ?? 'en') as UILanguage).errFailedLoadTranslations
          );
        }
      } finally {
        if (!cancelled) {
          setLoadingAvailableTranslations(false);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [user, settings?.uiLanguage]);

  useEffect(() => {
    if (!user) return;
    if (settingsLoading) return;
    if (!settings) return;
    if (settings.translationId) return;
    if (installedTranslations.length === 0) return;

    // One-time migration from legacy localStorage key into server settings.
    const legacyId = localStorage.getItem("clible_translation_id");
    if (!legacyId) return;
    if (!installedTranslations.some((tr) => tr.id === legacyId)) return;

    void updateSettings({ translationId: legacyId })
      .then(() => {
        localStorage.removeItem("clible_translation_id");
      })
      .catch(() => {
        // Keep legacy value if server write failed.
      });
  }, [user, settingsLoading, settings, installedTranslations, updateSettings]);

  useEffect(() => {
    if (installedTranslations.length < 2) {
      setCompareLeft(null);
      setCompareRight(null);
      return;
    }
    const preferred = settings?.translationId;
    const left =
      preferred != null &&
      preferred !== '' &&
      installedTranslations.some((t) => t.id === preferred)
        ? preferred
        : installedTranslations[0].id;
    const right = installedTranslations.find((t) => t.id !== left)?.id ?? null;
    setCompareLeft(left);
    setCompareRight(right);
  }, [installedTranslations, settings?.translationId]);

  useEffect(() => {
    if (!user) return;
    let cancelled = false;
    void (async () => {
      try {
        const [hist, saved] = await Promise.all([
          bibleRepository.getSearchHistory(),
          bibleRepository.getSavedSearches(),
        ]);
        if (!cancelled) {
          setSearchHistoryApi(hist);
          setSavedSearches(saved);
        }
      } catch {
        /* offline bridge errors ignored */
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [user]);

  if (authLoading)
    return (
      <div className="min-h-screen flex items-center justify-center">{t('en').appBootLoading}</div>
    );
  if (!user) return <LoginView onSuccess={login} />;

  const uiLang: UILanguage = settings?.uiLanguage ?? 'en';
  const shell = t(uiLang);

  const compareLeftResolved =
    compareLeft ??
    settings?.translationId ??
    installedTranslations[0]?.id ??
    '';
  const compareRightResolved =
    compareRight ??
    installedTranslations.find((t) => t.id !== compareLeftResolved)?.id ??
    '';

  const saveToHistory = (q: string) => {
    const newHistory = [q, ...history.filter((h) => h !== q)].slice(0, 10);
    setHistory(newHistory);
    localStorage.setItem('clible_history', JSON.stringify(newHistory));
  };

  const handleAdvancedSearch = async (options: SearchQueryOptions) => {
    if (!options.terms[0]?.trim()) return;
    if (!settings?.translationId) {
      setError(shell.errSelectTranslationFirst);
      return;
    }
    setStudyEntryTab('scripture');
    setLoading(true);
    setError(null);
    setAiInsight(null);
    setToneAnalysis(null);
    setCurrentSearchTerms(options.terms);
    setLastSearchOptions({ ...options, translationId: settings.translationId });
    try {
      const response = await bibleRepository.searchAdvanced({
        ...options,
        translationId: settings.translationId,
      });
      setSearchResponse(response);
      setViewMode('search');
      setSearchType('search');
      const hist = await bibleRepository.getSearchHistory();
      setSearchHistoryApi(hist);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : shell.errSearchFailed);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (q: string, overrideType?: SearchType) => {
    if (!q.trim()) return;
    if (!settings?.translationId) {
      setError(shell.errSelectTranslationFirst);
      return;
    }
    setLoading(true);
    setError(null);
    setAiInsight(null);
    setToneAnalysis(null);
    setNativeStats(null);
    setNativeFrequency([]);

    try {
      const typeToUse = overrideType ?? searchType;
      if (typeToUse === 'verse') {
        setStudyEntryTab('verse');
        const data = await bibleRepository.getVerse(q, settings.translationId);
        setResult(data);
        setViewMode('reader');
        setSearchType('verse');
      } else {
        setStudyEntryTab('scripture');
        const response = await bibleRepository.search(q, settings.translationId);
        setSearchResponse(response);
        setCurrentSearchTerms([q.trim()]);
        setLastSearchOptions({
          terms: [q.trim()],
          mode: 'phrase',
          operator: 'and',
          scope: 'bible',
          book: null,
          translationId: settings.translationId,
        });
        setViewMode('search');
        setSearchType('search');
      }
      saveToHistory(q);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : shell.errUnexpected);
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
      setAiInsight(err instanceof Error ? err.message : shell.errInsightsFailed);
    } finally {
      setAiLoading(false);
    }
  };

  const handleAnalytics = async (modeOverride?: AnalyticsMode) => {
    const mode = modeOverride ?? analyticsMode;
    if (!result?.reference) {
      setError(shell.errAnalyticsNeedVerse);
      return;
    }
    setError(null);
    setStudyEntryTab('scripture');
    setAnalyticsMode(mode);
    setViewMode('analytics');

    if (!settings?.translationId) {
      setError(shell.errSelectTranslationFirst);
      return;
    }
    setAiLoading(true);
    try {
      const { stats, frequency } = await bibleService.getNativeAnalytics(
        mode,
        result!.reference,
        settings.translationId
      );
      setNativeStats(stats);
      setNativeFrequency(frequency);
      try {
        const tone = await bibleService.getAiTone(result.text);
        setToneAnalysis(tone);
      } catch (err) {
        console.warn('AI tone unavailable:', err);
        setToneAnalysis(err instanceof Error ? err.message : shell.errAiToneUnavailable);
      }
    } catch (err) {
      console.error('Analytics error:', err);
      setNativeStats(bibleService.calculateStats(result.text));
      setNativeFrequency(bibleService.calculateWordFrequency(result.text));
    } finally {
      setAiLoading(false);
    }
  };

  const handleEntryTabChange = (tab: StudyEntryTab) => {
    setStudyEntryTab(tab);
    setError(null);
    setCompareError(null);
    if (tab === 'compare') {
      setViewMode('compare');
      return;
    }
    setViewMode((vm) => (vm === 'compare' ? 'reader' : vm));
  };

  const handleCompare = async (ref: string, leftId: string, rightId: string) => {
    setCompareLoading(true);
    setCompareError(null);
    try {
      const data = await bibleService.getCompareResult(ref, leftId, rightId);
      setCompareResult(data);
      setCompareLeft(leftId);
      setCompareRight(rightId);
    } catch (err: unknown) {
      setCompareResult(null);
      setCompareError(err instanceof Error ? err.message : shell.errUnexpected);
    } finally {
      setCompareLoading(false);
    }
  };

  const handleTranslationSelect = (id: string) => {
    const meta =
      installedTranslations.find((t) => t.id === id) ??
      availableTranslations.find((t) => t.id === id);
    const inferred = inferUILanguageFromTranslation(meta?.language);
    void updateSettings({
      translationId: id,
      ...(inferred !== null ? { uiLanguage: inferred } : {}),
    }).catch((e: unknown) => {
      setTranslationsLoadError(
        e instanceof Error ? e.message : shell.errSaveSettings
      );
    });
    setShowTranslations(false);
    setError(null);
  };

  const handleTranslationInstall = (id: string) => {
    setTranslationInstallError(null);
    setTranslationInstallSuccess(null);
    setInstallingTranslationId(id);
    void bibleRepository
      .installTranslation(id)
      .then(async (result) => {
        setTranslationInstallSuccess(result.message);
        const installed = await bibleRepository.listInstalledTranslations();
        setInstalledTranslations(installed);
      })
      .catch((e: unknown) => {
        setTranslationInstallError(
          e instanceof Error ? e.message : shell.errInstallTranslation
        );
      })
      .finally(() => {
        setInstallingTranslationId(null);
      });
  };

  const triggerExport = (
    cmd: "verse" | "search" | "analytics",
    args: string,
    title: string,
    insight?: string | null
  ) => {
    setExportContext({ cmd, args, title, aiInsight: insight });
    setShowExport(true);
  };

  const handleExport = async (format: ExportFormat) => {
    if (!exportContext) return;
    setExporting(true);
    try {
      let { content, contentType } = await bibleRepository.export(
        exportContext.cmd,
        exportContext.args,
        format,
        exportContext.aiInsight ?? null
      );

      // Append AI Insight if this is a verse export and we have one
      if (exportContext.cmd === 'verse' && (aiInsight || toneAnalysis)) {
        const aiText = aiInsight || toneAnalysis;
        let separator = '';
        if (format === 'md') separator = '\n\n---\n\n## AI Study Notes\n\n';
        else if (format === 'txt') separator = '\n\n---\n\nAI STUDY NOTES:\n\n';
        else if (format === 'html') separator = '\n\n---\n\n<h2>AI Study Notes</h2>\n\n';
        else if (format === 'xml') separator = '\n\n---\n\n<ai_study_notes>\n';

        if (separator) {
          content += separator + aiText;
          if (format === 'xml') content += '\n</ai_study_notes>';
        }
      }

      // Append Tone Analysis if this is an analytics export (not translation compare) and we have one
      if (
        exportContext.cmd === 'analytics' &&
        toneAnalysis &&
        !exportContext.args.trimStart().startsWith('compare ')
      ) {
        let separator = '';
        if (format === 'md') separator = '\n\n---\n\n## AI Tone & Style Analysis\n\n';
        else if (format === 'txt') separator = '\n\n---\n\nAI TONE & STYLE ANALYSIS:\n\n';
        else if (format === 'html') separator = '\n\n---\n\n<h2>AI Tone & Style Analysis</h2>\n\n';

        if (separator) content += separator + toneAnalysis;
      }

      const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
      const filename = `clible_export_${timestamp}.${format}`;
      downloadFile(content, filename, contentType);
      setShowExport(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : shell.errExportFailed);
    } finally {
      setExporting(false);
    }
  };

  return (
    <div
      className="min-h-screen font-sans selection:bg-[#E6D5B8] selection:text-[#1A1A1A] bg-[var(--bg)] text-[var(--text)]"
    >
      <header
        className="border-b backdrop-blur-md sticky top-0 z-50 border-[var(--border)] bg-[color:color-mix(in_srgb,var(--surface)_80%,transparent)]"
      >
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
                {settings?.translationId ?? shell.chooseTranslation}
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
              title={shell.settingsTitle}
            >
              <Settings size={20} />
            </button>
            <div className="flex items-center gap-2 pl-2 border-l border-[#E5E5E5]">
              <span className="text-sm text-[#8E8E8E]">{user!.username}</span>
              <button
                onClick={() => void logout()}
                className="p-2 hover:bg-[#F5F5F5] rounded-full transition-colors text-[#8E8E8E] hover:text-[#1A1A1A]"
                title={shell.signOutTitle}
              >
                <LogOut size={18} />
              </button>
            </div>
          </div>
        </div>
      </header>

      <main
        className={`mx-auto px-6 py-12 ${
          viewMode === 'compare' ? 'max-w-5xl' : 'max-w-4xl'
        }`}
      >
        <div className="space-y-4 mb-8">
          {error && (
            <p className="text-sm text-red-600 mb-2" role="alert">
              {error}
            </p>
          )}

          <SearchPanel
            activeTranslation={settings?.translationId ?? null}
            uiLanguage={settings?.uiLanguage ?? 'en'}
            entryTab={studyEntryTab}
            onEntryTabChange={handleEntryTabChange}
            onSearch={handleAdvancedSearch}
            onVerseSearch={(ref) => void handleSearch(ref, 'verse')}
            history={searchHistoryApi}
            onHistoryClear={() => {
              void bibleRepository.clearSearchHistory().then(() => setSearchHistoryApi([]));
            }}
            loading={loading}
            error={null}
          />

          {viewMode !== 'compare' && (
          <SavedSearchesList
            uiLanguage={uiLang}
            searches={savedSearches}
            onRun={(s) => {
              if (!settings?.translationId) return;
              const scope: SearchQueryOptions['scope'] =
                s.search_scope === 'testament' && s.scope_value === 'NT'
                  ? 'nt'
                  : s.search_scope === 'testament' && s.scope_value === 'OT'
                    ? 'ot'
                    : s.search_scope === 'book'
                      ? 'book'
                      : 'bible';
              void handleAdvancedSearch({
                terms: [s.query_text.trim()],
                mode: 'phrase',
                operator: 'and',
                scope,
                book: s.search_scope === 'book' ? s.scope_value : null,
                translationId: s.translation_id ?? settings.translationId,
              });
            }}
            onDelete={(id) => {
              void bibleRepository
                .deleteSavedSearch(id)
                .then(() => bibleRepository.getSavedSearches())
                .then(setSavedSearches)
                .catch((e: unknown) =>
                  setError(e instanceof Error ? e.message : shell.errDeleteFailed)
                );
            }}
          />
          )}
        </div>

        {viewMode !== 'compare' && (
        <div className="flex gap-1 bg-[#F5F5F5] p-1 rounded-xl w-fit mb-8">
          <button
            type="button"
            onClick={() => {
              setViewMode('reader');
              setStudyEntryTab((t) => (t === 'compare' ? 'verse' : t));
            }}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${viewMode === 'reader' ? 'bg-white shadow-sm text-[#1A1A1A]' : 'text-[#8E8E8E] hover:text-[#1A1A1A]'}`}
          >
            <div className="flex items-center gap-2"><Book size={16} /> {shell.tabReader}</div>
          </button>
          <button
            type="button"
            onClick={() => void handleAnalytics()}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${viewMode === 'analytics' ? 'bg-white shadow-sm text-[#1A1A1A]' : 'text-[#8E8E8E] hover:text-[#1A1A1A]'}`}
          >
            <div className="flex items-center gap-2"><Activity size={16} /> {shell.tabAnalytics}</div>
          </button>
        </div>
        )}

        <AnimatePresence mode="wait">
          {viewMode === 'reader' && (
            <motion.div key="reader" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }}>
              <ReaderView
                result={result}
                uiLanguage={settings?.uiLanguage ?? 'en'}
                aiInsight={aiInsight}
                aiLoading={aiLoading}
                onAiInsight={handleAiInsight}
                onExport={() => {
                  if (result && settings?.translationId) {
                    triggerExport(
                      'verse',
                      `"${result.reference}" -t ${settings.translationId}`,
                      result.reference,
                      aiInsight
                    );
                  }
                }}
              />
            </motion.div>
          )}
          {viewMode === 'search' && (
            <motion.div key="search" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
              <SearchView
                searchResponse={searchResponse}
                searchTerms={currentSearchTerms}
                uiLanguage={settings?.uiLanguage ?? 'en'}
                onResultClick={(ref) => void handleSearch(ref, 'verse')}
                onExport={() => {
                  if (searchResponse && settings?.translationId) {
                    let args = `"${searchResponse.query}" -t ${settings.translationId}`;
                    if (searchResponse.scope) args += ` --scope ${searchResponse.scope}`;
                    if (searchResponse.scopeRef) args += ` -r "${searchResponse.scopeRef}"`;
                    if (searchResponse.searchMode) {
                      const m =
                        searchResponse.searchMode === 'boolean' ? 'words' : searchResponse.searchMode;
                      args += ` --mode ${m}`;
                    }
                    if (searchResponse.searchOperator) {
                      args += ` --operator ${searchResponse.searchOperator.toLowerCase()}`;
                    }
                    triggerExport('search', args, `Search: ${searchResponse.query}`);
                  }
                }}
                onSaveSearch={
                  lastSearchOptions
                    ? async (name) => {
                        await bibleRepository.saveNamedSearch({
                          name,
                          ...lastSearchOptions,
                          translationId: settings?.translationId ?? lastSearchOptions.translationId,
                        });
                        const s = await bibleRepository.getSavedSearches();
                        setSavedSearches(s);
                      }
                    : undefined
                }
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
                uiLanguage={uiLang}
                onModeChange={(nextMode) => void handleAnalytics(nextMode)}
                onExport={() => {
                  if (!settings?.translationId) return;
                  if (!result?.reference) return;
                  let args = '';
                  if (analyticsMode === 'reference') {
                    args = `reference "${result.reference}" -t ${settings.translationId}`;
                  } else if (analyticsMode === 'chapter') {
                    const parts = result.reference.split(' ');
                    const book = parts.slice(0, -1).join(' ');
                    const chapter = parts[parts.length - 1].split(':')[0];
                    args = `chapter "${book}" ${chapter} -t ${settings.translationId}`;
                  } else if (analyticsMode === 'book') {
                    const book = result.reference.split(' ')[0];
                    args = `book "${book}" -t ${settings.translationId}`;
                  }
                  if (args) {
                    triggerExport('analytics', args, `Analytics: ${result.reference}`);
                  }
                }}
              />
            </motion.div>
          )}
          {viewMode === 'compare' && (
            <motion.div
              key="compare"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
            >
              <CompareView
                standalone
                installedTranslations={installedTranslations}
                uiLanguage={uiLang}
                defaultReference={result?.reference ?? null}
                leftTranslationId={compareLeftResolved}
                rightTranslationId={compareRightResolved}
                onLeftTranslationChange={(id) => {
                  setCompareLeft(id);
                  setCompareRight((r) => {
                    if (r && r !== id) return r;
                    return (
                      installedTranslations.find((tr) => tr.id !== id)?.id ?? r ?? ''
                    );
                  });
                }}
                onRightTranslationChange={(id) => {
                  setCompareRight(id);
                  setCompareLeft((l) => {
                    if (l && l !== id) return l;
                    return (
                      installedTranslations.find((tr) => tr.id !== id)?.id ?? l ?? ''
                    );
                  });
                }}
                onCompare={(ref, leftId, rightId) => void handleCompare(ref, leftId, rightId)}
                onExport={() => {
                  if (!compareResult) return;
                  const ref = compareResult.reference.trim();
                  const left = compareLeftResolved;
                  const right = compareRightResolved;
                  if (!ref || !left || !right) return;
                  const args = `compare ${JSON.stringify(ref)} --left ${left} --right ${right}`;
                  triggerExport(
                    'analytics',
                    args,
                    `Compare: ${ref} (${left} vs ${right})`
                  );
                }}
                result={compareResult}
                loading={compareLoading}
                error={compareError}
              />
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      <AnimatePresence>
        {showTranslations && (
          <TranslationModal
            installedTranslations={installedTranslations}
            availableTranslations={availableTranslations}
            loadingAvailableTranslations={loadingAvailableTranslations}
            translationsLoadError={translationsLoadError}
            installError={translationInstallError}
            installSuccess={translationInstallSuccess}
            installingTranslationId={installingTranslationId}
            activeTranslation={settings?.translationId ?? null}
            uiLanguage={uiLang}
            onSelect={handleTranslationSelect}
            onInstall={handleTranslationInstall}
            onClose={() => setShowTranslations(false)}
          />
        )}
      </AnimatePresence>

      <AnimatePresence>
        {showExport && exportContext && (
          <ExportModal
            title={exportContext.title}
            uiLanguage={uiLang}
            isExporting={exporting}
            onExport={handleExport}
            onClose={() => setShowExport(false)}
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
            uiLanguage={uiLang}
            onPickTranslation={() => {
              setShowSettings(false);
              setShowTranslations(true);
            }}
            onSetTheme={(theme) => {
              void updateSettings({ theme }).catch(() => { });
            }}
            onSetUILanguage={(lang) => {
              void updateSettings({ uiLanguage: lang }).catch(() => { });
            }}
          />
        )}
      </AnimatePresence>

      <footer className="max-w-5xl mx-auto px-6 py-12 border-t border-[#F5F5F5] mt-24">
        <div className="flex flex-col md:flex-row justify-between items-center gap-8">
          <div className="flex items-center gap-2 text-[#8E8E8E] text-sm">
            <Terminal size={14} /><span>{shell.footerInspired}</span>
          </div>
          <div className="flex gap-8 text-sm font-medium text-[#8E8E8E]">
            <a href="#" className="hover:text-[#1A1A1A] transition-colors">{shell.footerDocumentation}</a>
            <a href="#" className="hover:text-[#1A1A1A] transition-colors">{shell.footerApi}</a>
            <a href="#" className="hover:text-[#1A1A1A] transition-colors">{shell.footerGithub}</a>
          </div>
          <div className="text-[#8E8E8E] text-xs font-mono">v2.0.0-WEB</div>
        </div>
      </footer>
    </div>
  );
}
