import { X } from "lucide-react";
import ReactMarkdown from "react-markdown";

import { markdownComponents } from "../utils/markdownComponents";

interface DeepDiveCardProps {
  title: string;
  text: string;
  invert?: boolean;
  onClose: () => void;
}

export function DeepDiveCard({ title, text, invert = false, onClose }: DeepDiveCardProps) {
  if (!text.trim()) return null;
  return (
    <div
      className={`mt-4 rounded-3xl border p-5 shadow-sm ${
        invert
          ? "border-gray-700 bg-[#111] text-white"
          : "border-[var(--border)] bg-[var(--surface)] text-[var(--text)]"
      }`}
    >
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">
          {title}
        </div>
        <button
          type="button"
          onClick={onClose}
          className={invert ? "text-gray-300 hover:text-white" : "text-[var(--muted)] hover:text-[var(--text)]"}
          aria-label="Close"
        >
          <X size={16} />
        </button>
      </div>
      <div className={invert ? "prose prose-invert prose-sm max-w-none" : "prose prose-sm max-w-none"}>
        <ReactMarkdown components={markdownComponents({ invert, insightLayout: !invert, toneLayout: invert })}>
          {text}
        </ReactMarkdown>
      </div>
    </div>
  );
}

