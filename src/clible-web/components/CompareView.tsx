/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { useEffect, useMemo, useState } from 'react';
import { Download, GitCompareArrows, Loader2, Sparkles } from 'lucide-react';

import type { InstalledTranslation } from '../types/bible';
import type { CompareResult, AlignedVerse } from '../types/compare';
import type { UILanguage } from '../utils/bookNames';
import { t } from '../utils/i18n';

/** Greek or Hebrew scriptures as installed translations (Masoretic Greek / Hebrew editions). */
function translationLooksLikeOriginalLanguage(tr: InstalledTranslation | undefined): boolean {
  if (!tr?.language) return false;
  const l = tr.language.toLowerCase().trim();
  if (l.startsWith('grc') || l === 'grc') return true;
  if (l === 'he' || l.startsWith('heb') || l === 'hbo') return true;
  return false;
}

function similarityBarHue(ratio01: number): string {
  const t = Math.max(0, Math.min(1, ratio01));
  return `hsl(${Math.round(t * 120)}, 52%, 40%)`;
}

function verseRef(row: AlignedVerse): string {
  return `${row.book_id} ${row.chapter}:${row.verse}`;
}

export interface CompareViewProps {
  installedTranslations: InstalledTranslation[];
  uiLanguage: UILanguage;
  defaultReference: string | null;
  leftTranslationId: string;
  rightTranslationId: string;
  onLeftTranslationChange: (id: string) => void;
  onRightTranslationChange: (id: string) => void;
  onCompare: (ref: string, leftId: string, rightId: string) => void;
  onExport?: () => void;
  result: CompareResult | null;
  loading: boolean;
  error: string | null;
  /** Full-page layout: tighter top spacing for primary navigation entry. */
  standalone?: boolean;
}

export function CompareView({
  installedTranslations,
  uiLanguage,
  defaultReference,
  leftTranslationId,
  rightTranslationId,
  onLeftTranslationChange,
  onRightTranslationChange,
  onCompare,
  onExport,
  result,
  loading,
  error,
  standalone = false,
}: CompareViewProps) {
  const m = t(uiLanguage);
  const [reference, setReference] = useState(() => defaultReference?.trim() ?? '');

  useEffect(() => {
    if (defaultReference?.trim()) {
      setReference((prev) => (prev.trim() ? prev : defaultReference.trim()));
    }
  }, [defaultReference]);

  const sortedTranslations = useMemo(
    () => [...installedTranslations].sort((a, b) => a.id.localeCompare(b.id)),
    [installedTranslations],
  );

  const secondaryOptionsRight = useMemo(
    () => sortedTranslations.filter((tr) => tr.id !== leftTranslationId),
    [sortedTranslations, leftTranslationId],
  );

  const leftMeta = sortedTranslations.find((t) => t.id === leftTranslationId);
  const rightMeta = sortedTranslations.find((t) => t.id === rightTranslationId);
  const showAiStudySlot =
    translationLooksLikeOriginalLanguage(leftMeta) ||
    translationLooksLikeOriginalLanguage(rightMeta);

  const summary = result?.summary;

  return (
    <div className={standalone ? 'space-y-8' : 'space-y-8 mt-8'}>
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex items-center gap-2 text-[var(--text)]">
          <GitCompareArrows size={22} className="text-[#D4A373]" />
          <h2 className="text-lg font-semibold">{m.compareTitle}</h2>
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

      <div className="rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-sm space-y-4">
        <div className="space-y-1">
          <label className="text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">
            {m.compareReferenceLabel}
          </label>
          <input
            type="text"
            value={reference}
            onChange={(e) => setReference(e.target.value)}
            placeholder={m.compareReferencePlaceholder}
            className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface-2)] px-4 py-2.5 text-sm"
            disabled={sortedTranslations.length < 2}
          />
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-1">
            <label className="text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">
              {m.compareLeftLabel}
            </label>
            <select
              value={leftTranslationId}
              onChange={(e) => onLeftTranslationChange(e.target.value)}
              className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface-2)] px-4 py-2.5 text-sm uppercase"
              disabled={sortedTranslations.length === 0}
            >
              {sortedTranslations.map((tr) => (
                <option key={tr.id} value={tr.id}>
                  {tr.id} · {tr.name}
                </option>
              ))}
            </select>
          </div>
          <div className="space-y-1">
            <label className="text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">
              {m.compareRightLabel}
            </label>
            <select
              value={
                secondaryOptionsRight.some((x) => x.id === rightTranslationId)
                  ? rightTranslationId
                  : secondaryOptionsRight[0]?.id ?? ''
              }
              onChange={(e) => onRightTranslationChange(e.target.value)}
              className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface-2)] px-4 py-2.5 text-sm uppercase"
              disabled={secondaryOptionsRight.length === 0}
            >
              {secondaryOptionsRight.map((tr) => (
                <option key={tr.id} value={tr.id}>
                  {tr.id} · {tr.name}
                </option>
              ))}
            </select>
          </div>
        </div>

        {sortedTranslations.length < 2 ? (
          <p className="text-sm text-amber-700 dark:text-amber-400">{m.compareNeedTwoTranslations}</p>
        ) : null}

        <div className="flex flex-wrap items-center gap-3">
          <button
            type="button"
            disabled={loading || sortedTranslations.length < 2}
            onClick={() => {
              const left = leftTranslationId;
              let right = rightTranslationId;
              if (right === left) {
                right = secondaryOptionsRight.find((t) => t.id !== left)?.id ?? right;
              }
              onCompare(reference.trim(), left, right);
            }}
            className="inline-flex items-center gap-2 rounded-full bg-[#1A1A1A] px-6 py-2.5 text-sm font-medium text-white hover:opacity-90 disabled:opacity-40"
          >
            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <GitCompareArrows size={18} />}
            {m.compareRunButton}
          </button>

          {showAiStudySlot ? (
            <div className="flex flex-col sm:flex-row sm:items-center gap-2">
              <button
                type="button"
                disabled
                title={m.compareAiStudyHint}
                className="inline-flex items-center gap-2 rounded-full border border-dashed border-[var(--border)] px-5 py-2 text-sm font-medium text-[var(--muted)] cursor-not-allowed opacity-75"
              >
                <Sparkles size={18} /> {m.compareAiStudy}
              </button>
              <span className="text-xs text-[var(--muted)] max-w-md">{m.compareAiStudyHint}</span>
            </div>
          ) : null}
        </div>
      </div>

      {error ? (
        <p className="text-sm text-red-600 dark:text-red-400" role="alert">
          {error}
        </p>
      ) : null}

      {loading ? (
        <div className="flex items-center gap-2 text-[var(--muted)] text-sm">
          <Loader2 className="h-4 w-4 animate-spin" />
          {m.compareLoading}
        </div>
      ) : null}

      {!loading && !result && !error ? (
        <p className="text-sm text-[var(--muted)]">{m.compareNoResult}</p>
      ) : null}

      {summary && result ? (
        <div className="rounded-3xl border border-[var(--border)] bg-[var(--surface)] p-6 shadow-sm space-y-3">
          <h3 className="text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">
            {result.reference}
          </h3>
          <dl className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-2 text-sm">
            <div>
              <dt className="text-[var(--muted)]">{m.compareAvgSimilarity}</dt>
              <dd className="font-mono font-semibold">
                {(summary.average_similarity * 100).toFixed(1)}%
              </dd>
            </div>
            <div>
              <dt className="text-[var(--muted)]">{m.compareExactMatches}</dt>
              <dd className="font-mono font-semibold">
                {summary.exact_matches}{' '}
                <span className="font-sans font-normal text-[var(--muted)]">
                  ({(summary.exact_match_ratio * 100).toFixed(1)}%)
                </span>
              </dd>
            </div>
            <div>
              <dt className="text-[var(--muted)]">{m.compareAlignedVerses}</dt>
              <dd className="font-mono font-semibold">{summary.fully_aligned_verses}</dd>
            </div>
            <div>
              <dt className="text-[var(--muted)]">{m.compareTotalVerses}</dt>
              <dd className="font-mono font-semibold">{summary.total_verses}</dd>
            </div>
          </dl>
          {summary.most_similar_verse ? (
            <p className="text-sm">
              <span className="text-[var(--muted)]">{m.compareMostSimilar}: </span>
              <span className="font-mono">
                {summary.most_similar_verse.reference}{' '}
                ({(summary.most_similar_verse.similarity * 100).toFixed(1)}%)
              </span>
            </p>
          ) : null}
          {summary.top_shared_words.length > 0 ? (
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-[var(--muted)] mb-1">
                {m.compareSharedWords}
              </p>
              <p className="text-sm leading-relaxed flex flex-wrap gap-x-4 gap-y-2">
                {summary.top_shared_words.slice(0, 8).map(([w, n], i) => (
                  <span
                    key={w + String(i)}
                    className="inline-flex items-baseline gap-1.5 whitespace-nowrap"
                  >
                    <span className="font-mono">{w}</span>
                    <span className="text-[var(--muted)]">({n})</span>
                  </span>
                ))}
              </p>
            </div>
          ) : null}
        </div>
      ) : null}

      {result && result.aligned_verses.length > 0 ? (
        <div className="overflow-x-auto rounded-3xl border border-[var(--border)] shadow-sm">
          <table className="min-w-full text-sm border-collapse">
            <thead>
              <tr className="bg-[var(--surface-2)] text-left text-[var(--muted)] uppercase text-[10px] tracking-wider">
                <th className="px-4 py-3 border-b border-[var(--border)] whitespace-nowrap">
                  {m.compareVerseColumn}
                </th>
                <th className="px-4 py-3 border-b border-[var(--border)] min-w-[12rem]">
                  {leftMeta?.name ?? leftTranslationId}
                </th>
                <th className="px-4 py-3 border-b border-[var(--border)] min-w-[12rem]">
                  {rightMeta?.name ?? rightTranslationId}
                </th>
                <th className="px-4 py-3 border-b border-[var(--border)] w-[10rem]">
                  {m.compareSimilarityColumn}
                </th>
              </tr>
            </thead>
            <tbody>
              {result.aligned_verses.map((row) => {
                    const pct = row.similarity * 100;
                    return (
                      <tr key={verseRef(row)} className="align-top border-b border-[var(--border-soft)]">
                        <td className="px-4 py-3 font-mono text-[var(--muted)] whitespace-nowrap">
                          {verseRef(row)}
                        </td>
                        <td className="px-4 py-3">
                          <p className="text-[var(--text)] whitespace-pre-wrap break-words">
                            {row.text_a?.trim() ? row.text_a : '—'}
                          </p>
                        </td>
                        <td className="px-4 py-3">
                          <p className="text-[var(--text)] whitespace-pre-wrap break-words">
                            {row.text_b?.trim() ? row.text_b : '—'}
                          </p>
                        </td>
                        <td className="px-4 py-3">
                          <div className="space-y-1">
                            <span className="font-mono text-xs block">
                              {pct.toFixed(1)}%
                            </span>
                            <div
                              className="h-2 rounded-full bg-[var(--surface-2)] overflow-hidden border border-[var(--border-soft)]"
                              role="presentation"
                            >
                              <div
                                className="h-full rounded-full transition-all"
                                style={{
                                  width: `${pct}%`,
                                  backgroundColor: similarityBarHue(row.similarity),
                                }}
                              />
                            </div>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
            </tbody>
          </table>
        </div>
      ) : null}
    </div>
  );
}
