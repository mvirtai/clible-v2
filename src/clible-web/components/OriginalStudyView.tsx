/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useEffect, useMemo, useState } from 'react';
import { BookOpenCheck, Download, Languages, Loader2, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

import type { InstalledTranslation } from '../types/bible';
import type { OriginalStudyResult, OriginalStudyVerse, StudyScope } from '../types/originalStudy';
import type { UILanguage } from '../utils/bookNames';
import { t } from '../utils/i18n';
import { markdownComponents } from '../utils/markdownComponents';
import { escapeOrderedListStarts } from '../utils/markdownText';
import type { NextFocusItem } from '../utils/nextFocus';
import { NextFocusChips } from './NextFocusChips';
import { DeepDiveCard } from './DeepDiveCard';

const GREEK_PACK_ID = 'greeksblgnt';
/**
 * Default Hebrew pack to install from the UI.
 *
 * Note: some upstream catalogs label Hebrew packs with language "en" even when
 * the text is Hebrew. We therefore use ID heuristics (see isOriginalLanguage)
 * and avoid relying on `language` alone.
 */
const HEBREW_PACK_ID = 'hebrewaleppocodex';
const MAX_TARGETS = 3;
const STUDY_SCOPES: StudyScope[] = ['verse', 'chapter', 'book'];

function isOriginalLanguage(tr: InstalledTranslation): boolean {
  const l = (tr.language ?? '').toLowerCase().trim();
  if (l === 'grc' || l === 'he' || l === 'hbo' || l.startsWith('heb')) return true;

  // Fallback: treat clearly-named IDs as original-language sources even if
  // the catalog metadata is inaccurate (e.g. language "en").
  const id = (tr.id ?? '').toLowerCase().trim();
  if (id === GREEK_PACK_ID) return true;
  if (id.startsWith('hebrew')) return true;
  if (id.includes('leningrad')) return true;
  return false;
}

function verseRow(rows: OriginalStudyVerse[], chapter: number, verse: number): OriginalStudyVerse | undefined {
  return rows.find((r) => r.chapter === chapter && r.verse === verse);
}

export interface OriginalStudyViewProps {
  installedTranslations: InstalledTranslation[];
  activeTranslationId: string | null;
  uiLanguage: UILanguage;
  installingTranslationId: string | null;
  installError?: string | null;
  installSuccess?: string | null;
  onInstallTranslation: (id: string) => void;
  result: OriginalStudyResult | null;
  loading: boolean;
  error: string | null;
  defaultReference: string | null;
  onStudy: (
    reference: string,
    originalId: string,
    translationIds: string[],
    scope: StudyScope,
  ) => void;
  onNextFocusPick?: (item: NextFocusItem) => void;
  deepDiveText?: string | null;
  onDeepDiveClose?: () => void;
  onExport?: () => void;
  standalone?: boolean;
}

export function OriginalStudyView({
  installedTranslations,
  activeTranslationId,
  uiLanguage,
  installingTranslationId,
  installError = null,
  installSuccess = null,
  onInstallTranslation,
  result,
  loading,
  error,
  defaultReference,
  onStudy,
  onNextFocusPick,
  deepDiveText,
  onDeepDiveClose,
  onExport,
  standalone = false,
}: OriginalStudyViewProps) {
  const m = t(uiLanguage);

  const originalOptions = useMemo(
    () => installedTranslations.filter(isOriginalLanguage).sort((a, b) => a.id.localeCompare(b.id)),
    [installedTranslations],
  );
  const targetOptions = useMemo(
    () =>
      installedTranslations
        .filter((tr) => !isOriginalLanguage(tr))
        .sort((a, b) => a.id.localeCompare(b.id)),
    [installedTranslations],
  );

  const greekInstalled = installedTranslations.some((tr) => tr.id === GREEK_PACK_ID);
  const hebrewInstalled = installedTranslations.some((tr) => tr.id === HEBREW_PACK_ID);

  const [reference, setReference] = useState(() => defaultReference?.trim() ?? '');
  const [scope, setScope] = useState<StudyScope>('verse');
  const [originalId, setOriginalId] = useState<string>(() => originalOptions[0]?.id ?? '');
  const [targetIds, setTargetIds] = useState<string[]>(() => {
    if (activeTranslationId && !isOriginalLanguage({ id: activeTranslationId, name: '', language: '', format: '' })) {
      return [activeTranslationId];
    }
    return targetOptions[0] ? [targetOptions[0].id] : [];
  });

  useEffect(() => {
    if (defaultReference?.trim()) {
      setReference((prev) => (prev.trim() ? prev : defaultReference.trim()));
    }
  }, [defaultReference]);

  useEffect(() => {
    if (originalOptions.length === 0) {
      setOriginalId('');
      return;
    }
    if (!originalOptions.some((tr) => tr.id === originalId)) {
      setOriginalId(originalOptions[0].id);
    }
  }, [originalOptions, originalId]);

  useEffect(() => {
    setTargetIds((prev) => {
      const allowed = new Set(targetOptions.map((tr) => tr.id));
      const filtered = prev.filter((id) => allowed.has(id));
      if (filtered.length > 0) return filtered;
      if (
        activeTranslationId &&
        allowed.has(activeTranslationId) &&
        activeTranslationId !== originalId
      ) {
        return [activeTranslationId];
      }
      const first = targetOptions[0]?.id;
      return first ? [first] : [];
    });
  }, [targetOptions, activeTranslationId, originalId]);

  const noOriginalsInstalled = originalOptions.length === 0;
  const targetsAvailable = targetOptions.length > 0;
  const canRun =
    !loading &&
    !!reference.trim() &&
    !!originalId &&
    targetIds.length > 0 &&
    targetIds.length <= MAX_TARGETS;

  const scopeLabels: Record<StudyScope, string> = {
    verse: uiLanguage === 'fi' ? 'Jae' : 'Verse',
    chapter: uiLanguage === 'fi' ? 'Kappale' : 'Chapter',
    book: uiLanguage === 'fi' ? 'Kirja' : 'Book',
  };

  const scopeReferenceHint = (() => {
    if (scope === 'chapter') {
      return uiLanguage === 'fi'
        ? 'Kappalehaku: käytä muotoa "Johannes 3" ilman jaenumeroa.'
        : 'Chapter scope: use a reference like "John 3" without a verse number.';
    }
    if (scope === 'book') {
      return uiLanguage === 'fi'
        ? 'Kirjahaku: käytä vain kirjan nimeä. Analyysi painottaa rakennetta ja avainkohtia.'
        : 'Book scope: use only a book name. Analysis focuses on structure and key passages.';
    }
    return uiLanguage === 'fi'
      ? 'Jaehaku: yksittäinen jae tai jaealue toimii parhaiten.'
      : 'Verse scope: a single verse or short range works best.';
  })();

  const toggleTarget = (id: string) => {
    setTargetIds((prev) => {
      if (prev.includes(id)) {
        return prev.filter((x) => x !== id);
      }
      if (prev.length >= MAX_TARGETS) return prev;
      return [...prev, id];
    });
  };

  const renderSetup = () => (
    <div className="rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-sm space-y-4">
      <div className="flex items-center gap-2">
        <Languages size={20} className="text-[#D4A373]" />
        <h3 className="text-base font-semibold">{m.originalSetupTitle}</h3>
      </div>
      <p className="text-sm text-[var(--muted)] leading-relaxed">{m.originalSetupHint}</p>
      {installError && (
        <p className="text-sm text-red-600" role="alert">
          {installError}
        </p>
      )}
      {installSuccess && (
        <p className="text-sm text-emerald-700" role="status">
          {installSuccess}
        </p>
      )}
      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          disabled={greekInstalled || installingTranslationId === GREEK_PACK_ID}
          onClick={() => onInstallTranslation(GREEK_PACK_ID)}
          className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] px-4 py-2 text-sm font-medium hover:bg-[var(--surface-2)] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {installingTranslationId === GREEK_PACK_ID ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <BookOpenCheck size={16} />
          )}
          {greekInstalled ? `${m.originalAlreadyInstalled}: ${GREEK_PACK_ID}` : m.originalInstallGreek}
        </button>
        <button
          type="button"
          disabled={hebrewInstalled || installingTranslationId === HEBREW_PACK_ID}
          onClick={() => onInstallTranslation(HEBREW_PACK_ID)}
          className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] px-4 py-2 text-sm font-medium hover:bg-[var(--surface-2)] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {installingTranslationId === HEBREW_PACK_ID ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <BookOpenCheck size={16} />
          )}
          {hebrewInstalled ? `${m.originalAlreadyInstalled}: ${HEBREW_PACK_ID}` : m.originalInstallHebrew}
        </button>
      </div>
    </div>
  );

  const renderForm = () => (
    <div className="rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-sm space-y-5">
      <div className="space-y-1">
        <div className="flex flex-wrap gap-2 pb-2" role="tablist" aria-label="Study scope">
          {STUDY_SCOPES.map((nextScope) => {
            const active = scope === nextScope;
            return (
              <button
                key={nextScope}
                type="button"
                role="tab"
                aria-selected={active}
                onClick={() => setScope(nextScope)}
                className={`rounded-full border px-3 py-1.5 text-xs font-semibold uppercase tracking-wide transition-colors ${
                  active
                    ? 'border-[#D4A373] bg-[var(--surface-2)] text-[var(--text)]'
                    : 'border-[var(--border)] text-[var(--muted)] hover:bg-[var(--surface-2)]'
                }`}
              >
                {scopeLabels[nextScope]}
              </button>
            );
          })}
        </div>
        <label className="text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">
          {m.originalReferenceLabel}
        </label>
        <input
          type="text"
          value={reference}
          onChange={(e) => setReference(e.target.value)}
          placeholder={m.originalReferencePlaceholder}
          className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface-2)] px-4 py-2.5 text-sm"
        />
        <p className="text-xs text-[var(--muted)]">{scopeReferenceHint}</p>
      </div>

      <div className="space-y-1">
        <label className="text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">
          {m.originalSelectOriginal}
        </label>
        <select
          value={originalId}
          onChange={(e) => setOriginalId(e.target.value)}
          className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface-2)] px-4 py-2.5 text-sm uppercase"
          disabled={originalOptions.length === 0}
        >
          {originalOptions.map((tr) => (
            <option key={tr.id} value={tr.id}>
              {tr.id} · {tr.name} ({tr.language})
            </option>
          ))}
        </select>
      </div>

      <div className="space-y-2">
        <label className="text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">
          {m.originalSelectTranslations}
        </label>
        {targetsAvailable ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {targetOptions.map((tr) => {
              const checked = targetIds.includes(tr.id);
              const disabled = !checked && targetIds.length >= MAX_TARGETS;
              return (
                <label
                  key={tr.id}
                  className={`flex items-center gap-2 rounded-xl border px-3 py-2 text-sm cursor-pointer transition-colors ${
                    checked
                      ? 'border-[#D4A373] bg-[var(--surface-2)]'
                      : 'border-[var(--border)] hover:bg-[var(--surface-2)]'
                  } ${disabled ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <input
                    type="checkbox"
                    className="accent-[#D4A373]"
                    checked={checked}
                    disabled={disabled}
                    onChange={() => toggleTarget(tr.id)}
                  />
                  <span className="font-mono uppercase text-xs">{tr.id}</span>
                  <span className="text-[var(--muted)] truncate">{tr.name}</span>
                </label>
              );
            })}
          </div>
        ) : (
          <p className="text-sm text-amber-700 dark:text-amber-400">
            {m.compareNeedTwoTranslations}
          </p>
        )}
      </div>

      {targetsAvailable && targetIds.length === 0 ? (
        <p className="text-xs text-amber-700 dark:text-amber-400">{m.originalNeedTargets}</p>
      ) : null}

      <div>
        <button
          type="button"
          disabled={!canRun}
          onClick={() => onStudy(reference.trim(), originalId, targetIds, scope)}
          className="inline-flex items-center gap-2 rounded-full bg-[#1A1A1A] px-6 py-2.5 text-sm font-medium text-white hover:opacity-90 disabled:opacity-40"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles size={18} />}
          {m.originalRunButton}
        </button>
      </div>
    </div>
  );

  const renderResult = () => {
    if (!result) return null;
    const allRows = [
      ...result.originalVerses,
      ...result.translations.flatMap((t) => t.verses),
    ];
    const verseKeys = Array.from(
      new Set(allRows.map((v) => `${v.chapter}:${v.verse}`)),
    ).sort((a, b) => {
      const [ac, av] = a.split(':').map(Number);
      const [bc, bv] = b.split(':').map(Number);
      return ac - bc || av - bv;
    });

    const originalMeta = installedTranslations.find((tr) => tr.id === result.originalId);

    return (
      <div className="space-y-6">
        <div className="overflow-x-auto rounded-3xl border border-[var(--border)] shadow-sm">
          <table className="min-w-full text-sm border-collapse">
            <caption className="bg-[var(--surface)] text-left px-4 py-3 text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">
              {m.originalVersesHeading} · {result.reference}
            </caption>
            <thead>
              <tr className="bg-[var(--surface-2)] text-left text-[var(--muted)] uppercase text-[10px] tracking-wider">
                <th className="px-4 py-3 border-b border-[var(--border)] whitespace-nowrap">
                  {m.compareVerseColumn}
                </th>
                <th className="px-4 py-3 border-b border-[var(--border)] min-w-[14rem]">
                  {originalMeta?.name ?? result.originalId} ({result.sourceLanguage})
                </th>
                {result.translations.map((tr) => (
                  <th
                    key={tr.id}
                    className="px-4 py-3 border-b border-[var(--border)] min-w-[14rem]"
                  >
                    {tr.name}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {verseKeys.map((key) => {
                const [chapter, verse] = key.split(':').map(Number);
                const orig = verseRow(result.originalVerses, chapter, verse);
                return (
                  <tr key={key} className="align-top border-b border-[var(--border-soft)]">
                    <td className="px-4 py-3 font-mono text-[var(--muted)] whitespace-nowrap">
                      {orig?.book_name ?? ''} {chapter}:{verse}
                    </td>
                    <td className="px-4 py-3">
                      <p
                        lang={result.sourceLanguage === 'he' ? 'he' : 'el'}
                        dir={result.sourceLanguage === 'he' ? 'rtl' : 'ltr'}
                        className="text-[var(--text)] whitespace-pre-wrap break-words leading-loose"
                      >
                        {orig?.text?.trim() ? orig.text : '—'}
                      </p>
                    </td>
                    {result.translations.map((tr) => {
                      const row = verseRow(tr.verses, chapter, verse);
                      return (
                        <td key={tr.id} className="px-4 py-3">
                          <p className="text-[var(--text)] whitespace-pre-wrap break-words">
                            {row?.text?.trim() ? row.text : '—'}
                          </p>
                        </td>
                      );
                    })}
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {result.analysis.trim() ? (
          <div className="rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-sm">
            <h3 className="mb-3 text-xs font-semibold uppercase tracking-wider text-[var(--muted)] flex items-center gap-2">
              <Sparkles size={14} className="text-[#D4A373]" />
              {m.originalAnalysisHeading}
            </h3>
            <div className="prose prose-sm max-w-none">
              <ReactMarkdown
                components={markdownComponents({ invert: false, insightLayout: true })}
                remarkPlugins={[remarkGfm]}
              >
                {escapeOrderedListStarts(result.analysis)}
              </ReactMarkdown>
            </div>
            {onNextFocusPick ? (
              <NextFocusChips
                title={uiLanguage === 'fi' ? 'Syvennä seuraavaksi' : 'Next focus'}
                items={result.nextFocus ?? []}
                onPick={onNextFocusPick}
              />
            ) : null}
            {deepDiveText && onDeepDiveClose ? (
              <DeepDiveCard
                title={uiLanguage === 'fi' ? 'Syvennys' : 'Deep dive'}
                text={deepDiveText}
                onClose={onDeepDiveClose}
              />
            ) : null}
          </div>
        ) : null}
      </div>
    );
  };

  return (
    <div className={standalone ? 'space-y-8' : 'space-y-8 mt-8'}>
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-2 text-[var(--text)]">
          <Languages size={22} className="text-[#D4A373]" />
          <h2 className="text-lg font-semibold">{m.originalStudyTitle}</h2>
        </div>
        {onExport && result ? (
          <button
            type="button"
            onClick={onExport}
            className="flex items-center gap-2 px-4 py-2 bg-[var(--surface-2)] hover:opacity-90 rounded-full text-sm font-medium transition-colors border border-[var(--border)]"
          >
            <Download size={16} /> {m.compareExport}
          </button>
        ) : null}
      </div>

      {noOriginalsInstalled ? renderSetup() : renderForm()}

      {error ? (
        <p className="text-sm text-red-600 dark:text-red-400" role="alert">
          {error}
        </p>
      ) : null}

      {loading ? (
        <div className="flex items-center gap-2 text-[var(--muted)] text-sm">
          <Loader2 className="h-4 w-4 animate-spin" />
          {m.originalLoading}
        </div>
      ) : null}

      {!loading && !result && !error ? (
        <p className="text-sm text-[var(--muted)]">{m.originalNoResult}</p>
      ) : null}

      {!loading && result ? renderResult() : null}
    </div>
  );
}
