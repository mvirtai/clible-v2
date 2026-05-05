import { BarChart3, Hash, MessageSquareQuote, Activity, Sparkles, Loader2, Download, Cloud } from 'lucide-react';
import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { TextStats, WordFrequency } from '../types/bible';
import type { UILanguage } from '../utils/bookNames';
import { t } from '../utils/i18n';
import { markdownComponents } from '../utils/markdownComponents';
import { WordCloud } from './WordCloud';

export type AnalyticsMode = 'reference' | 'chapter' | 'book';

interface AnalyticsViewProps {
  analyticsMode: AnalyticsMode;
  nativeStats: TextStats | null;
  nativeFrequency: WordFrequency[];
  toneAnalysis: string | null;
  aiLoading: boolean;
  uiLanguage: UILanguage;
  onModeChange: (mode: AnalyticsMode) => void;
  onExport: () => void;
}

export function AnalyticsView({
  analyticsMode,
  nativeStats,
  nativeFrequency,
  toneAnalysis,
  aiLoading,
  uiLanguage,
  onModeChange,
  onExport,
}: AnalyticsViewProps) {
  const m = t(uiLanguage);
  const [freqView, setFreqView] = useState<'bar' | 'cloud'>('bar');
  const analyticsModes: Array<{ mode: AnalyticsMode; label: string }> = [
    { mode: 'reference', label: m.analyticsModeReference },
    { mode: 'chapter', label: m.analyticsModeChapter },
    { mode: 'book', label: m.analyticsModeBook },
  ];

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div className="flex gap-2 bg-[var(--surface-2)] p-1 rounded-xl w-fit border border-[var(--border-soft)]">
          {analyticsModes.map(({ mode, label }) => (
            <button
              key={mode}
              onClick={() => onModeChange(mode)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                analyticsMode === mode
                  ? 'bg-[var(--surface)] shadow-sm text-[var(--text)]'
                  : 'text-[var(--muted)] hover:text-[var(--text)]'
              }`}
            >
              {label}
            </button>
          ))}
        </div>
        <button
          onClick={onExport}
          className="flex items-center gap-2 px-4 py-2 bg-[var(--surface-2)] hover:opacity-90 rounded-full text-sm font-medium transition-colors border border-[var(--border)]"
        >
          <Download size={16} /> {m.analyticsExport}
        </button>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: m.statsWords, value: nativeStats?.wordCount, icon: MessageSquareQuote },
          { label: m.statsUnique, value: nativeStats?.uniqueWords, icon: Hash },
          { label: m.statsAvgLength, value: nativeStats?.avgWordLength, icon: Activity },
          { label: m.statsChars, value: nativeStats?.charCount, icon: BarChart3 },
        ].map((s, i) => (
          <div key={i} className="bg-[var(--surface)] border border-[var(--border)] p-4 rounded-2xl shadow-sm">
            <div className="flex items-center gap-2 text-[var(--muted)] mb-2">
              <s.icon size={14} />
              <span className="text-[10px] uppercase tracking-wider font-semibold">{s.label}</span>
            </div>
            <div className="text-2xl font-mono font-bold">{s.value || '0'}</div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="bg-white border border-[#E5E5E5] p-6 rounded-3xl shadow-sm space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold uppercase tracking-wider text-[#8E8E8E] flex items-center gap-2">
              <BarChart3 size={16} /> {m.analyticsWordFrequency}
            </h3>
            <div className="flex gap-1 bg-[#F5F5F5] p-0.5 rounded-lg">
              <button
                onClick={() => setFreqView('bar')}
                className={`p-1.5 rounded-md transition-colors ${freqView === 'bar' ? 'bg-white shadow-sm text-[#1A1A1A]' : 'text-[#8E8E8E] hover:text-[#1A1A1A]'}`}
                title={m.analyticsFreqViewBarTitle}
              >
                <BarChart3 size={14} />
              </button>
              <button
                onClick={() => setFreqView('cloud')}
                className={`p-1.5 rounded-md transition-colors ${freqView === 'cloud' ? 'bg-white shadow-sm text-[#1A1A1A]' : 'text-[#8E8E8E] hover:text-[#1A1A1A]'}`}
                title={m.analyticsFreqViewCloudTitle}
              >
                <Cloud size={14} />
              </button>
            </div>
          </div>
          <div className="h-64 min-h-[16rem] min-w-0 w-full flex items-center justify-center overflow-hidden">
            {freqView === 'bar' ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={nativeFrequency} layout="vertical" margin={{ left: 20 }}>
                  <XAxis type="number" hide />
                  <YAxis
                    dataKey="name"
                    type="category"
                    width={80}
                    axisLine={false}
                    tickLine={false}
                    tick={{ fontSize: 12, fill: '#8E8E8E' }}
                  />
                  <Tooltip
                    cursor={{ fill: '#F5F5F5' }}
                    contentStyle={{ borderRadius: '12px', border: 'none', boxShadow: '0 4px 12px rgba(0,0,0,0.1)' }}
                  />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                    {nativeFrequency.map((_, i) => (
                      <Cell key={i} fill={i === 0 ? '#1A1A1A' : '#D4A373'} fillOpacity={1 - i * 0.1} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <WordCloud words={nativeFrequency} />
            )}
          </div>
        </div>

        <div className="bg-[#1A1A1A] text-white p-6 rounded-3xl shadow-xl space-y-4 relative overflow-hidden">
          <div className="absolute top-0 right-0 p-6 opacity-10">
            <Sparkles size={80} />
          </div>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-[#8E8E8E] flex items-center gap-2">
            <Sparkles size={16} className="text-[#D4A373]" /> {m.analyticsAiTone}
          </h3>
          {aiLoading ? (
            <div className="py-12 flex flex-col items-center justify-center gap-2">
              <Loader2 size={24} className="animate-spin text-[#D4A373]" />
              <span className="text-xs text-[#8E8E8E]">{m.analyticsAiLoading}</span>
            </div>
          ) : toneAnalysis ? (
            <div className="text-lg font-serif leading-relaxed">
              <ReactMarkdown components={markdownComponents({ invert: true, toneLayout: true })}>
                {toneAnalysis}
              </ReactMarkdown>
            </div>
          ) : (
            <p className="text-lg font-serif italic leading-relaxed text-gray-400">
              {m.analyticsTonePlaceholder}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
