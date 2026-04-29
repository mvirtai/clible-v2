import { BarChart3, Hash, MessageSquareQuote, Activity, Sparkles, Loader2, Download } from 'lucide-react';
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
import { markdownComponents } from '../utils/markdownComponents';

export type AnalyticsMode = 'reference' | 'chapter' | 'book' | 'compare';

interface AnalyticsViewProps {
  analyticsMode: AnalyticsMode;
  nativeStats: TextStats | null;
  nativeFrequency: WordFrequency[];
  toneAnalysis: string | null;
  aiLoading: boolean;
  onModeChange: (mode: AnalyticsMode) => void;
  onExport: () => void;
}

export function AnalyticsView({
  analyticsMode,
  nativeStats,
  nativeFrequency,
  toneAnalysis,
  aiLoading,
  onModeChange,
  onExport,
}: AnalyticsViewProps) {
  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div className="flex gap-2 bg-[var(--surface-2)] p-1 rounded-xl w-fit border border-[var(--border-soft)]">
          {(['reference', 'chapter', 'book'] as const).map((m) => (
            <button
              key={m}
              onClick={() => onModeChange(m)}
              className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all capitalize ${
                analyticsMode === m
                  ? 'bg-[var(--surface)] shadow-sm text-[var(--text)]'
                  : 'text-[var(--muted)] hover:text-[var(--text)]'
              }`}
            >
              {m}
            </button>
          ))}
        </div>
        <button
          onClick={onExport}
          className="flex items-center gap-2 px-4 py-2 bg-[var(--surface-2)] hover:opacity-90 rounded-full text-sm font-medium transition-colors border border-[var(--border)]"
        >
          <Download size={16} /> Export Analytics
        </button>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: 'Words', value: nativeStats?.wordCount, icon: MessageSquareQuote },
          { label: 'Unique', value: nativeStats?.uniqueWords, icon: Hash },
          { label: 'Avg Length', value: nativeStats?.avgWordLength, icon: Activity },
          { label: 'Chars', value: nativeStats?.charCount, icon: BarChart3 },
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
          <h3 className="text-sm font-semibold uppercase tracking-wider text-[#8E8E8E] flex items-center gap-2">
            <BarChart3 size={16} /> Word Frequency
          </h3>
          <div className="h-64 min-h-[16rem] min-w-0 w-full">
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
          </div>
        </div>

        <div className="bg-[#1A1A1A] text-white p-6 rounded-3xl shadow-xl space-y-4 relative overflow-hidden">
          <div className="absolute top-0 right-0 p-6 opacity-10">
            <Sparkles size={80} />
          </div>
          <h3 className="text-sm font-semibold uppercase tracking-wider text-[#8E8E8E] flex items-center gap-2">
            <Sparkles size={16} className="text-[#D4A373]" /> AI Tone Analysis
          </h3>
          {aiLoading ? (
            <div className="py-12 flex flex-col items-center justify-center gap-2">
              <Loader2 size={24} className="animate-spin text-[#D4A373]" />
              <span className="text-xs text-[#8E8E8E]">Analyzing linguistic patterns...</span>
            </div>
          ) : toneAnalysis ? (
            <div className="text-lg font-serif leading-relaxed">
              <ReactMarkdown components={markdownComponents({ invert: true, toneLayout: true })}>
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
    </div>
  );
}
