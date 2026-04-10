import { X } from 'lucide-react';
import { motion } from 'motion/react';
import { InstalledTranslation } from '../types/bible';

interface TranslationModalProps {
  installedTranslations: InstalledTranslation[];
  translationsLoadError: string | null;
  activeTranslation: string | null;
  onSelect: (id: string) => void;
  onClose: () => void;
}

export function TranslationModal({
  installedTranslations,
  translationsLoadError,
  activeTranslation,
  onSelect,
  onClose,
}: TranslationModalProps) {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-[100] bg-[var(--overlay)] backdrop-blur-sm flex items-center justify-center p-6"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-[var(--surface)] text-[var(--text)] w-full max-w-lg rounded-3xl shadow-2xl overflow-hidden border border-[var(--border)]"
      >
        <div className="p-6 border-b border-[var(--border-soft)] flex justify-between items-center">
          <h3 className="text-lg font-semibold">Select Translation</h3>
          <button onClick={onClose}><X size={20} /></button>
        </div>
        <div className="p-6 max-h-[60vh] overflow-y-auto grid grid-cols-1 sm:grid-cols-2 gap-3">
          {translationsLoadError && (
            <p className="col-span-full text-sm text-red-600" role="alert">
              {translationsLoadError}
            </p>
          )}
          {!translationsLoadError && installedTranslations.length === 0 && (
            <p className="col-span-full text-sm text-[var(--muted)]">
              No translations installed. On the machine or container where Clible runs, install
              one with:{' '}
              <code className="font-mono text-[var(--text)]">clible seed install &lt;id&gt;</code>
              . Then refresh this page.
            </p>
          )}
          {installedTranslations.map((t) => (
            <button
              key={t.id}
              onClick={() => onSelect(t.id)}
              className={`px-4 py-3 rounded-xl text-left border-2 transition-all ${
                activeTranslation === t.id
                  ? 'border-[var(--text)] bg-[var(--surface-2)]'
                  : 'border-[var(--border)] hover:border-[var(--text)]'
              }`}
            >
              <span className="uppercase font-bold text-sm block">{t.id}</span>
              <span className="text-xs text-[var(--muted)] block mt-1">{t.name}</span>
              <span className="text-[10px] text-[var(--muted)] uppercase tracking-wide">
                {t.language} · {t.format}
              </span>
            </button>
          ))}
        </div>
        <div className="p-6 bg-[var(--surface-2)] text-xs text-[var(--muted)] border-t border-[var(--border-soft)]">
          <p>
            Only translations installed in this environment appear here. Use{' '}
            <code className="font-mono text-[var(--text)]">clible seed list</code> in the terminal to
            verify.
          </p>
        </div>
      </motion.div>
    </motion.div>
  );
}
