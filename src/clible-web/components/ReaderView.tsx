import { Sparkles, Loader2, ArrowRight, Share2, Download, Book } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { BibleResponse } from '../types/bible';
import type { UILanguage } from '../utils/bookNames';
import { formatReferenceForDisplay } from '../utils/bookNames';
import { t, verseAriaLabel } from '../utils/i18n';
import { markdownComponents } from '../utils/markdownComponents';

interface ReaderViewProps {
  result: BibleResponse | null;
  uiLanguage: UILanguage;
  aiInsight: string | null;
  aiLoading: boolean;
  onAiInsight: () => void;
  onExport: () => void;
}

export function ReaderView({
  result,
  uiLanguage,
  aiInsight,
  aiLoading,
  onAiInsight,
  onExport,
}: ReaderViewProps) {
  const m = t(uiLanguage);

  if (!result) {
    return (
      <div className="py-24 text-center space-y-6">
        <div className="w-16 h-16 bg-[var(--surface-2)] rounded-full flex items-center justify-center mx-auto text-[var(--accent)]">
          <Book size={32} />
        </div>
        <h3 className="text-xl font-medium">{m.readerEmptyTitle}</h3>
        <p className="text-[var(--muted)]">{m.readerEmptyHint}</p>
      </div>
    );
  }

  return (
    <div className="space-y-12">
      <section className="space-y-8">
        <div className="flex items-end justify-between border-b border-[var(--border-soft)] pb-4">
          <h2 className="text-4xl font-serif italic text-[var(--text)]">
            {formatReferenceForDisplay(result.reference, uiLanguage)}
          </h2>
          <span className="text-sm font-mono text-[var(--muted)] uppercase tracking-widest">{result.translation_name}</span>
        </div>
        <p
          className={`text-2xl leading-relaxed font-serif text-[var(--text-2)] ${
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
                  className="mx-0.5 align-super font-sans text-[0.55em] font-semibold text-[var(--muted)]"
                  aria-label={verseAriaLabel(v.verse, uiLanguage)}
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
          <button className="flex items-center gap-2 px-4 py-2 bg-[var(--surface-2)] hover:opacity-90 rounded-full text-sm font-medium transition-colors">
            <Share2 size={16} /> {m.readerShare}
          </button>
          <button
            onClick={onExport}
            className="flex items-center gap-2 px-4 py-2 bg-[var(--surface-2)] hover:opacity-90 rounded-full text-sm font-medium transition-colors"
          >
            <Download size={16} /> {m.readerExport}
          </button>
        </div>
      </section>

      <section className="bg-[var(--surface-2)] border border-[var(--border)] rounded-3xl p-8 space-y-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-[var(--accent)]">
            <Sparkles size={20} />
            <span className="font-semibold uppercase tracking-wider text-xs">{m.readerAiInsights}</span>
          </div>
          {!aiInsight && !aiLoading && (
            <button
              onClick={onAiInsight}
              className="text-sm font-medium hover:underline flex items-center gap-1"
            >
              {m.readerGenerateInsights} <ArrowRight size={14} />
            </button>
          )}
        </div>
        {aiLoading ? (
          <div className="py-12 flex flex-col items-center justify-center gap-4 text-[#8E8E8E]">
            <Loader2 size={32} className="animate-spin" />
            <p className="text-sm font-medium animate-pulse">{m.readerAiLoading}</p>
          </div>
        ) : aiInsight ? (
          <div className="max-w-none font-sans">
            <ReactMarkdown components={markdownComponents({ invert: false, insightLayout: true })}>
              {aiInsight}
            </ReactMarkdown>
          </div>
        ) : (
          <p className="text-[#8E8E8E] text-sm italic">{m.readerAiPlaceholder}</p>
        )}
      </section>
    </div>
  );
}
