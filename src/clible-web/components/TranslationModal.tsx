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
      className="fixed inset-0 z-[100] bg-black/40 backdrop-blur-sm flex items-center justify-center p-6"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-white w-full max-w-lg rounded-3xl shadow-2xl overflow-hidden"
      >
        <div className="p-6 border-b border-[#F5F5F5] flex justify-between items-center">
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
            <p className="col-span-full text-sm text-[#8E8E8E]">
              No translations installed. On the machine or container where Clible runs, install
              one with:{' '}
              <code className="font-mono text-[#1A1A1A]">clible seed install &lt;id&gt;</code>
              . Then refresh this page.
            </p>
          )}
          {installedTranslations.map((t) => (
            <button
              key={t.id}
              onClick={() => onSelect(t.id)}
              className={`px-4 py-3 rounded-xl text-left border-2 transition-all ${activeTranslation === t.id ? 'border-[#1A1A1A] bg-[#F5F5F5]' : 'border-[#E5E5E5] hover:border-[#1A1A1A]'}`}
            >
              <span className="uppercase font-bold text-sm block">{t.id}</span>
              <span className="text-xs text-[#8E8E8E] block mt-1">{t.name}</span>
              <span className="text-[10px] text-[#8E8E8E] uppercase tracking-wide">
                {t.language} · {t.format}
              </span>
            </button>
          ))}
        </div>
        <div className="p-6 bg-[#F5F5F5] text-xs text-[#8E8E8E]">
          <p>
            Only translations installed in this environment appear here. Use{' '}
            <code className="font-mono text-[#1A1A1A]">clible seed list</code> in the terminal to
            verify.
          </p>
        </div>
      </motion.div>
    </motion.div>
  );
}
