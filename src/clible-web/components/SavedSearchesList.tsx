/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { Trash2 } from 'lucide-react';
import type { SavedSearchRow } from '../types/searchQuery';
import type { UILanguage } from '../utils/bookNames';
import { t } from '../utils/i18n';

interface SavedSearchesListProps {
  uiLanguage: UILanguage;
  searches: SavedSearchRow[];
  onRun: (search: SavedSearchRow) => void;
  onDelete: (id: string) => void;
}

export function SavedSearchesList({ uiLanguage, searches, onRun, onDelete }: SavedSearchesListProps) {
  if (searches.length === 0) return null;

  const m = t(uiLanguage);

  return (
    <div className="mb-6">
      <p className="text-xs font-semibold text-[var(--muted)] uppercase tracking-wide mb-2">
        {m.savedSearchesLabel}
      </p>
      <div className="flex flex-wrap gap-2">
        {searches.map((s) => (
          <div
            key={s.id}
            className="flex items-center gap-1 pl-3 pr-2 py-1.5 rounded-full border border-[var(--border)] text-sm"
          >
            <button
              type="button"
              onClick={() => onRun(s)}
              className="font-medium hover:text-[var(--accent)] transition-colors"
              title={m.savedSearchScopeTitle(String(s.scope_value ?? s.search_scope))}
            >
              {s.name}
            </button>
            <button
              type="button"
              onClick={() => onDelete(s.id)}
              className="ml-1 text-[var(--muted)] hover:text-red-500 transition-colors"
              title={m.savedSearchRemove}
            >
              <Trash2 size={13} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
