/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useState, useEffect } from 'react';
import {
  Book,
  BookOpen,
  Terminal,
  History,
  Settings,
  Globe,
  Activity,
  LogOut,
  Shield,
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
import type { OriginalStudyResult, StudyScope } from './types/originalStudy';
import type { NextFocusItem } from './utils/nextFocus';
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
import { OriginalStudyView } from './components/OriginalStudyView';
import { TranslationModal } from './components/TranslationModal';
import { SettingsPanel } from './components/SettingsPanel';
import { AdminView } from './components/AdminView';
import { ReadingPlanView } from './components/ReadingPlanView';
import { StreakBadge } from './components/StreakBadge';
import { useAuth } from './AuthContext';
import { LoginView } from './views/LoginView';
import { useSettings } from './user/SettingsContext';
import { ExportModal, ExportFormat } from './components/ExportModal';
import { downloadFile } from './utils/download';
import {
  buildAnalyticsExportArgs,
  buildCompareExportArgs,
  buildOriginalStudyExportArgs,
  buildSavedSearchOptions,
  buildSearchExportArgs,
} from './utils/appViewHelpers';
import { appendExportNotes } from './utils/exportPostProcess';
import { t, type UILanguage } from './utils/i18n';

function inferUILanguageFromTranslation(language: string | undefined): 'en' | 'fi' | null {
  const lower = (language ?? '').toLowerCase().trim();
  if (lower === 'fi' || lower.startsWith('fin')) return 'fi';
  if (lower === 'en') return 'en';
  return null;
}

type ViewMode = 'reader' | 'reading' | 'analytics' | 'search' | 'compare' | 'original' | 'admin';
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
  const [aiInsightNextFocus, setAiInsightNextFocus] = useState<NextFocusItem[]>([]);
  const [aiInsightDeepDive, setAiInsightDeepDive] = useState<string | null>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [viewMode, setViewMode] = useState<ViewMode>('reader');
  const [searchType, setSearchType] = useState<SearchType>('verse');
  const [analyticsMode, setAnalyticsMode] = useState<AnalyticsMode>('reference');
  const [toneAnalysis, setToneAnalysis] = useState<string | null>(null);
  const [toneNextFocus, setToneNextFocus] = useState<NextFocusItem[]>([]);
  const [toneDeepDive, setToneDeepDive] = useState<string | null>(null);
  const [installedTranslations, setInstalledTranslations] = useState<InstalledTranslation[]>([]);
  const [availableTranslations, setAvailableTranslations] = useState<AvailableTranslation[]>([]);
  const [loadingAvailableTranslations, setLoadingAvailableTranslations] = useState(false);
  const [translationsLoadError, setTranslationsLoadError] = useState<string | null>(null);
  const [translationInstallError, setTranslationInstallError] = useState<string | null>(null);
  const [translationInstallSuccess, setTranslationInstallSuccess] = useState<string | null>(null);
  const [installingTranslationId, setInstallingTranslationId] = useState<string | null>(null);
  const [showTranslations, setShowTranslations] = useState(false);
  const [translationQuery, setTranslationQuery] = useState('');
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
  const [originalResult, setOriginalResult] = useState<OriginalStudyResult | null>(null);
  const [originalLoading, setOriginalLoading] = useState(false);
  const [originalError, setOriginalError] = useState<string | null>(null);
  const [originalDeepDive, setOriginalDeepDive] = useState<string | null>(null);
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
    let cancelled = false;
    const handle = window.setTimeout(() => {
      void (async () => {
        try {
          setLoadingAvailableTranslations(true);
          const available = await bibleRepository.listAvailableTranslations(translationQuery);
          if (!cancelled) {
            setAvailableTranslations(available);
            setTranslationsLoadError(null);
          }
        } catch (e: unknown) {
          if (!cancelled) {
            setTranslationsLoadError(
              e instanceof Error
                ? e.message
                : t((settings?.uiLanguage ?? 'en') as UILanguage).errFailedLoadTranslations
            );
          }
        } finally {
          if (!cancelled) setLoadingAvailableTranslations(false);
        }
      })();
    }, 250);
    return () => {
      cancelled = true;
      window.clearTimeout(handle);
    };
  }, [user, settings?.uiLanguage, translationQuery]);

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
      setAiInsight(insight.text);
      setAiInsightNextFocus(insight.nextFocus ?? []);
      setAiInsightDeepDive(null);
    } catch (err) {
      setAiInsight(err instanceof Error ? err.message : shell.errInsightsFailed);
      setAiInsightNextFocus([]);
      setAiInsightDeepDive(null);
    } finally {
      setAiLoading(false);
    }
  };

  const handleAiInsightFocus = async (item: NextFocusItem) => {
    if (!result) return;
    setAiLoading(true);
    try {
      const dd = await bibleService.getAiDeepDive({
        topic: item.label,
        outputLanguage: uiLang,
        context: { feature: "insight", reference: result.reference },
      });
      setAiInsightDeepDive(dd.text);
    } catch (err) {
      setAiInsightDeepDive(err instanceof Error ? err.message : shell.errInsightsFailed);
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
        setToneAnalysis(tone.text);
        setToneNextFocus(tone.nextFocus ?? []);
        setToneDeepDive(null);
      } catch (err) {
        console.warn('AI tone unavailable:', err);
        setToneAnalysis(err instanceof Error ? err.message : shell.errAiToneUnavailable);
        setToneNextFocus([]);
        setToneDeepDive(null);
      }
    } catch (err) {
      console.error('Analytics error:', err);
      setNativeStats(bibleService.calculateStats(result.text));
      setNativeFrequency(bibleService.calculateWordFrequency(result.text));
    } finally {
      setAiLoading(false);
    }
  };

  const handleToneFocus = async (item: NextFocusItem) => {
    if (!result) return;
    if (!toneAnalysis) return;
    setAiLoading(true);
    try {
      const dd = await bibleService.getAiDeepDive({
        topic: item.label,
        outputLanguage: uiLang,
        context: { feature: "tone", reference: result.reference },
      });
      setToneDeepDive(dd.text);
    } catch (err) {
      console.warn('AI tone unavailable:', err);
      setToneDeepDive(err instanceof Error ? err.message : shell.errAiToneUnavailable);
    } finally {
      setAiLoading(false);
    }
  };

  const handleEntryTabChange = (tab: StudyEntryTab) => {
    setStudyEntryTab(tab);
    setError(null);
    setCompareError(null);
    setOriginalError(null);
    if (tab === 'compare') {
      setViewMode('compare');
      return;
    }
    if (tab === 'original') {
      setViewMode('original');
      return;
    }
    setViewMode((vm) => (vm === 'compare' || vm === 'original' ? 'reader' : vm));
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

  const handleOriginalStudy = async (
    ref: string,
    originalId: string,
    translationIds: string[],
    scope: StudyScope,
    focus?: string,
  ) => {
    setOriginalLoading(true);
    setOriginalError(null);
    try {
      const data = await bibleService.getOriginalStudyResult(
        ref,
        originalId,
        translationIds,
        installedTranslations,
        scope,
        focus,
      );
      setOriginalResult(data);
      setOriginalDeepDive(null);
    } catch (err: unknown) {
      setOriginalResult(null);
      setOriginalError(err instanceof Error ? err.message : shell.errUnexpected);
      setOriginalDeepDive(null);
    } finally {
      setOriginalLoading(false);
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

      const exportedAiText = exportContext.aiInsight ?? aiInsight ?? toneAnalysis;
      content = appendExportNotes({
        content,
        format,
        cmd: exportContext.cmd,
        args: exportContext.args,
        title: exportContext.title,
        exportAiText: exportedAiText,
        toneAnalysis,
      });

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
              onClick={() => setViewMode('reading')}
              className="flex items-center gap-2 px-3 py-1.5 hover:bg-[#F5F5F5] rounded-full transition-colors text-sm font-medium border border-[#E5E5E5]"
              title={t(uiLang).tabReading}
            >
              <BookOpen size={16} />
              <span>{t(uiLang).tabReading}</span>
              <StreakBadge uiLanguage={uiLang} />
            </button>
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
            {user.isAdmin && (
              <button
                onClick={() => setViewMode('admin')}
                className="p-2 hover:bg-[#F5F5F5] rounded-full transition-colors"
                title="Admin"
              >
                <Shield size={20} />
              </button>
            )}
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
          viewMode === 'compare' || viewMode === 'original' || viewMode === 'admin'
            ? 'max-w-5xl'
            : 'max-w-4xl'
        }`}
      >
        <div className="space-y-4 mb-8">
          {error && (
            <p className="text-sm text-red-600 mb-2" role="alert">
              {error}
            </p>
          )}

          {viewMode !== 'reading' && (
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
          )}

          {viewMode !== 'compare' && viewMode !== 'original' && viewMode !== 'admin' && viewMode !== 'reading' && (
          <SavedSearchesList
            uiLanguage={uiLang}
            searches={savedSearches}
            onRun={(s) => {
              if (!settings?.translationId) return;
              void handleAdvancedSearch(buildSavedSearchOptions(s, settings.translationId));
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

        {viewMode !== 'compare' && viewMode !== 'original' && viewMode !== 'admin' && (
        <div className="flex gap-1 bg-[#F5F5F5] p-1 rounded-xl w-fit mb-8">
          <button
            type="button"
            onClick={() => {
              setViewMode('reader');
              setStudyEntryTab((t) => (t === 'compare' || t === 'original' ? 'verse' : t));
            }}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${viewMode === 'reader' ? 'bg-white shadow-sm text-[#1A1A1A]' : 'text-[#8E8E8E] hover:text-[#1A1A1A]'}`}
          >
            <div className="flex items-center gap-2"><Book size={16} /> {shell.tabReader}</div>
          </button>
          <button
            type="button"
            onClick={() => setViewMode('reading')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${viewMode === 'reading' ? 'bg-white shadow-sm text-[#1A1A1A]' : 'text-[#8E8E8E] hover:text-[#1A1A1A]'}`}
          >
            <div className="flex items-center gap-2">
              <BookOpen size={16} /> Reading
            </div>
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
          {viewMode === 'admin' && (
            <motion.div
              key="admin"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
            >
              <AdminView currentUserId={user.id} />
            </motion.div>
          )}
          {viewMode === 'reading' && (
            <motion.div
              key="reading"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
            >
              <ReadingPlanView uiLanguage={uiLang} />
            </motion.div>
          )}
          {viewMode === 'reader' && (
            <motion.div key="reader" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }}>
              <ReaderView
                result={result}
                uiLanguage={settings?.uiLanguage ?? 'en'}
                aiInsight={aiInsight}
                aiNextFocus={aiInsightNextFocus}
                aiLoading={aiLoading}
                onAiInsight={handleAiInsight}
                onAiNextFocusPick={handleAiInsightFocus}
                deepDiveText={aiInsightDeepDive}
                onDeepDiveClose={() => setAiInsightDeepDive(null)}
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
                    const args = buildSearchExportArgs(searchResponse, settings.translationId);
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
                toneNextFocus={toneNextFocus}
                aiLoading={aiLoading}
                uiLanguage={uiLang}
                onModeChange={(nextMode) => void handleAnalytics(nextMode)}
                onToneNextFocusPick={handleToneFocus}
                deepDiveText={toneDeepDive}
                onDeepDiveClose={() => setToneDeepDive(null)}
                onExport={() => {
                  if (!settings?.translationId) return;
                  if (!result?.reference) return;
                  const args = buildAnalyticsExportArgs(
                    analyticsMode,
                    result.reference,
                    settings.translationId
                  );
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
                  const args = buildCompareExportArgs(ref, left, right);
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
          {viewMode === 'original' && (
            <motion.div
              key="original"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
            >
              <OriginalStudyView
                standalone
                installedTranslations={installedTranslations}
                activeTranslationId={settings?.translationId ?? null}
                uiLanguage={uiLang}
                installingTranslationId={installingTranslationId}
                installError={translationInstallError}
                installSuccess={translationInstallSuccess}
                onInstallTranslation={handleTranslationInstall}
                result={originalResult}
                loading={originalLoading}
                error={originalError}
                defaultReference={result?.reference ?? null}
                onStudy={(ref, originalId, translationIds, scope) =>
                  void handleOriginalStudy(ref, originalId, translationIds, scope)
                }
                onNextFocusPick={(item) => {
                  if (!originalResult) return;
                  setOriginalLoading(true);
                  setOriginalError(null);
                  void bibleService
                    .getAiDeepDive({
                      topic: item.label,
                      outputLanguage: uiLang,
                      context: { feature: "original-study", reference: originalResult.reference },
                    })
                    .then((dd) => setOriginalDeepDive(dd.text))
                    .catch((e: unknown) =>
                      setOriginalDeepDive(e instanceof Error ? e.message : shell.errUnexpected),
                    )
                    .finally(() => setOriginalLoading(false));
                }}
                deepDiveText={originalDeepDive}
                onDeepDiveClose={() => setOriginalDeepDive(null)}
                onExport={() => {
                  if (!originalResult) return;
                  const ref = originalResult.reference.trim();
                  const originalId = originalResult.originalId.trim();
                  if (!ref || !originalId) return;
                  triggerExport(
                    'verse',
                    buildOriginalStudyExportArgs(ref, originalId),
                    `Original Study: ${ref} (${originalId})`,
                    originalResult.analysis
                  );
                }}
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
            query={translationQuery}
            onQueryChange={setTranslationQuery}
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
            <Terminal size={14} /><span>{shell.footerCopyright({ year: new Date().getFullYear() })}</span>
          </div>
          <div className="flex gap-8 text-sm font-medium text-[#8E8E8E]">
            <a href="/docs" className="hover:text-[#1A1A1A] transition-colors">{shell.footerDocumentation}</a>
            <a href="/docs#api" className="hover:text-[#1A1A1A] transition-colors">{shell.footerApi}</a>
            <a
              href="https://github.com/mvirtai/clible-v2"
              target="_blank"
              rel="noopener noreferrer"
              className="hover:text-[#1A1A1A] transition-colors"
            >
              {shell.footerGithub}
            </a>
          </div>
          <div className="text-[#8E8E8E] text-xs font-mono">v{__APP_VERSION__}</div>
        </div>
      </footer>
    </div>
  );
}
