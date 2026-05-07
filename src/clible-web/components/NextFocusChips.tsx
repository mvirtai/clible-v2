import type { NextFocusItem } from "../utils/nextFocus";

interface NextFocusChipsProps {
  title: string;
  items: NextFocusItem[];
  onPick: (item: NextFocusItem) => void;
}

export function NextFocusChips({ title, items, onPick }: NextFocusChipsProps) {
  if (!items || items.length === 0) return null;

  return (
    <div className="mt-5 rounded-2xl border border-[var(--border-soft)] bg-[var(--surface)] p-4">
      <div className="text-[10px] font-semibold uppercase tracking-wider text-[var(--muted)] mb-2">
        {title}
      </div>
      <div className="flex flex-wrap gap-2">
        {items.map((it, idx) => (
          <button
            key={`${it.kind}:${it.label}:${idx}`}
            type="button"
            onClick={() => onPick(it)}
            title={it.reason}
            className="rounded-full border border-[var(--border)] bg-[var(--surface-2)] px-3 py-1.5 text-xs font-medium text-[var(--text)] hover:opacity-90"
          >
            {it.label}
          </button>
        ))}
      </div>
    </div>
  );
}

