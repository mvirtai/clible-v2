/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { Bookmark, BookmarkCheck } from 'lucide-react';
import { useState } from 'react';

interface SaveSearchButtonProps {
  onSave: (name: string) => Promise<void>;
}

export function SaveSearchButton({ onSave }: SaveSearchButtonProps) {
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [showInput, setShowInput] = useState(false);
  const [name, setName] = useState('');

  const handleSave = async () => {
    if (!name.trim()) return;
    setSaving(true);
    try {
      await onSave(name.trim());
      setSaved(true);
      setShowInput(false);
      setName('');
      setTimeout(() => setSaved(false), 3000);
    } finally {
      setSaving(false);
    }
  };

  if (saved) {
    return (
      <span className="flex items-center gap-1.5 text-sm text-[var(--accent)]">
        <BookmarkCheck size={16} /> Saved
      </span>
    );
  }

  return (
    <div className="flex items-center gap-2">
      {showInput ? (
        <>
          <input
            autoFocus
            value={name}
            onChange={(e) => setName(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') void handleSave();
              if (e.key === 'Escape') setShowInput(false);
            }}
            placeholder="Name this search..."
            className="border border-[var(--border)] rounded-lg px-3 py-1.5 text-sm outline-none focus:border-[var(--accent)]"
          />
          <button
            type="button"
            onClick={() => void handleSave()}
            disabled={saving || !name.trim()}
            className="px-3 py-1.5 text-sm bg-[var(--accent)] text-white rounded-lg disabled:opacity-50"
          >
            Save
          </button>
          <button
            type="button"
            onClick={() => setShowInput(false)}
            className="text-sm text-[var(--muted)]"
          >
            Cancel
          </button>
        </>
      ) : (
        <button
          type="button"
          onClick={() => setShowInput(true)}
          className="flex items-center gap-1.5 text-sm text-[var(--muted)] hover:text-[var(--text)] transition-colors"
        >
          <Bookmark size={16} /> Save this search
        </button>
      )}
    </div>
  );
}
