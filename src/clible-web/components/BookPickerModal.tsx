/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { X } from 'lucide-react';

import { bookNameLocalized, type UILanguage } from '../utils/bookNames';
import { t } from '../utils/i18n';

type Group = { name: Record<UILanguage, string>; bookIds: readonly string[] };

const BOOK_GROUPS: { label: Record<UILanguage, string>; groups: Group[] }[] = [
  {
    label: { en: 'Old Testament', fi: 'Vanha testamentti' },
    groups: [
      {
        name: { en: 'Law', fi: 'Laki' },
        bookIds: ['GEN', 'EXO', 'LEV', 'NUM', 'DEU'],
      },
      {
        name: { en: 'History', fi: 'Historia' },
        bookIds: ['JOS', 'JDG', 'RUT', '1SA', '2SA', '1KI', '2KI', '1CH', '2CH', 'EZR', 'NEH', 'EST'],
      },
      {
        name: { en: 'Wisdom & Poetry', fi: 'Viisaus ja runous' },
        bookIds: ['JOB', 'PSA', 'PRO', 'ECC', 'SNG'],
      },
      {
        name: { en: 'Major Prophets', fi: 'Suuret profeetat' },
        bookIds: ['ISA', 'JER', 'LAM', 'EZK', 'DAN'],
      },
      {
        name: { en: 'Minor Prophets', fi: 'Pienet profeetat' },
        bookIds: ['HOS', 'JOL', 'AMO', 'OBA', 'JON', 'MIC', 'NAH', 'HAB', 'ZEP', 'HAG', 'ZEC', 'MAL'],
      },
    ],
  },
  {
    label: { en: 'New Testament', fi: 'Uusi testamentti' },
    groups: [
      { name: { en: 'Gospels', fi: 'Evankeliumit' }, bookIds: ['MAT', 'MRK', 'LUK', 'JHN'] },
      { name: { en: 'History', fi: 'Historia' }, bookIds: ['ACT'] },
      {
        name: { en: "Paul's Letters", fi: 'Paavalin kirjeet' },
        bookIds: [
          'ROM',
          '1CO',
          '2CO',
          'GAL',
          'EPH',
          'PHP',
          'COL',
          '1TH',
          '2TH',
          '1TI',
          '2TI',
          'TIT',
          'PHM',
        ],
      },
      {
        name: { en: 'General Letters', fi: 'Yleiskirjeet' },
        bookIds: ['HEB', 'JAS', '1PE', '2PE', '1JN', '2JN', '3JN', 'JUD'],
      },
      { name: { en: 'Prophecy', fi: 'Profetia' }, bookIds: ['REV'] },
    ],
  },
];

interface BookPickerModalProps {
  uiLanguage: UILanguage;
  onSelect: (bookId: string) => void;
  onClose: () => void;
}

export function BookPickerModal({ uiLanguage, onSelect, onClose }: BookPickerModalProps) {
  const lng = uiLanguage;
  const m = t(lng);

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-[var(--surface)] rounded-2xl shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">{m.bookPickerTitle}</h3>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded-full hover:bg-[var(--surface-2)]"
            aria-label={m.bookPickerClose}
          >
            <X size={18} />
          </button>
        </div>
        {BOOK_GROUPS.map((testament) => (
          <div key={testament.label[lng]} className="mb-6">
            <h4 className="text-xs font-bold uppercase tracking-widest text-[var(--muted)] mb-3">
              {testament.label[lng]}
            </h4>
            {testament.groups.map((group) => (
              <div key={group.name[lng]} className="mb-3">
                <p className="text-xs text-[var(--muted)] mb-1">{group.name[lng]}</p>
                <div className="flex flex-wrap gap-1.5">
                  {group.bookIds.map((bookId) => (
                    <button
                      key={bookId}
                      type="button"
                      onClick={() => {
                        onSelect(bookId);
                        onClose();
                      }}
                      className="px-2.5 py-1 text-sm rounded-lg border border-[var(--border)]
                                 hover:bg-[var(--accent)] hover:text-white hover:border-[var(--accent)]
                                 transition-all"
                    >
                      {bookNameLocalized(bookId, lng)}
                    </button>
                  ))}
                </div>
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
