/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import { X } from 'lucide-react';

const BOOK_GROUPS = [
  {
    label: 'Old Testament',
    groups: [
      {
        name: 'Law',
        books: ['Genesis', 'Exodus', 'Leviticus', 'Numbers', 'Deuteronomy'],
      },
      {
        name: 'History',
        books: [
          'Joshua',
          'Judges',
          'Ruth',
          '1 Samuel',
          '2 Samuel',
          '1 Kings',
          '2 Kings',
          '1 Chronicles',
          '2 Chronicles',
          'Ezra',
          'Nehemiah',
          'Esther',
        ],
      },
      {
        name: 'Wisdom & Poetry',
        books: ['Job', 'Psalms', 'Proverbs', 'Ecclesiastes', 'Song of Solomon'],
      },
      {
        name: 'Major Prophets',
        books: ['Isaiah', 'Jeremiah', 'Lamentations', 'Ezekiel', 'Daniel'],
      },
      {
        name: 'Minor Prophets',
        books: [
          'Hosea',
          'Joel',
          'Amos',
          'Obadiah',
          'Jonah',
          'Micah',
          'Nahum',
          'Habakkuk',
          'Zephaniah',
          'Haggai',
          'Zechariah',
          'Malachi',
        ],
      },
    ],
  },
  {
    label: 'New Testament',
    groups: [
      { name: 'Gospels', books: ['Matthew', 'Mark', 'Luke', 'John'] },
      { name: 'History', books: ['Acts'] },
      {
        name: "Paul's Letters",
        books: [
          'Romans',
          '1 Corinthians',
          '2 Corinthians',
          'Galatians',
          'Ephesians',
          'Philippians',
          'Colossians',
          '1 Thessalonians',
          '2 Thessalonians',
          '1 Timothy',
          '2 Timothy',
          'Titus',
          'Philemon',
        ],
      },
      {
        name: 'General Letters',
        books: [
          'Hebrews',
          'James',
          '1 Peter',
          '2 Peter',
          '1 John',
          '2 John',
          '3 John',
          'Jude',
        ],
      },
      { name: 'Prophecy', books: ['Revelation'] },
    ],
  },
];

interface BookPickerModalProps {
  onSelect: (book: string) => void;
  onClose: () => void;
}

export function BookPickerModal({ onSelect, onClose }: BookPickerModalProps) {
  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 p-4">
      <div className="bg-[var(--surface)] rounded-2xl shadow-xl max-w-2xl w-full max-h-[80vh] overflow-y-auto p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Choose a Book</h3>
          <button
            type="button"
            onClick={onClose}
            className="p-1 rounded-full hover:bg-[var(--surface-2)]"
            aria-label="Close"
          >
            <X size={18} />
          </button>
        </div>
        {BOOK_GROUPS.map((testament) => (
          <div key={testament.label} className="mb-6">
            <h4 className="text-xs font-bold uppercase tracking-widest text-[var(--muted)] mb-3">
              {testament.label}
            </h4>
            {testament.groups.map((group) => (
              <div key={group.name} className="mb-3">
                <p className="text-xs text-[var(--muted)] mb-1">{group.name}</p>
                <div className="flex flex-wrap gap-1.5">
                  {group.books.map((book) => (
                    <button
                      key={book}
                      type="button"
                      onClick={() => {
                        onSelect(book);
                        onClose();
                      }}
                      className="px-2.5 py-1 text-sm rounded-lg border border-[var(--border)]
                                 hover:bg-[var(--accent)] hover:text-white hover:border-[var(--accent)]
                                 transition-all"
                    >
                      {book}
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
