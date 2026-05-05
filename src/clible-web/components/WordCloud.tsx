import type { WordFrequency } from '../types/bible';

interface WordCloudProps {
  words: WordFrequency[];
}

const PALETTE = [
  '#1A1A1A',
  '#D4A373',
  '#6B7280',
  '#92400E',
  '#374151',
  '#B45309',
];

export function WordCloud({ words }: WordCloudProps) {
  if (words.length === 0) {
    return null;
  }

  const max = words[0].value;
  const min = words[words.length - 1].value;
  const range = max - min || 1;

  return (
    <div className="flex flex-wrap gap-x-4 gap-y-3 justify-center items-center p-4 leading-tight select-none">
      {words.map((w, i) => {
        const ratio = (w.value - min) / range;
        const size = Math.round(13 + ratio * 36);
        const weight = ratio > 0.6 ? 700 : ratio > 0.3 ? 600 : 400;
        const color = PALETTE[i % PALETTE.length];
        const opacity = 0.55 + ratio * 0.45;

        return (
          <span
            key={w.name}
            title={`${w.name}: ${w.value}`}
            style={{ fontSize: `${size}px`, fontWeight: weight, color, opacity }}
            className="transition-opacity hover:opacity-100 cursor-default"
          >
            {w.name}
          </span>
        );
      })}
    </div>
  );
}
