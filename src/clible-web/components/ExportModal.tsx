import { X, FileJson, FileText, Code, FileCode, Search, Hash } from 'lucide-react';
import { motion } from 'motion/react';
import type { UILanguage } from '../utils/bookNames';
import { t } from '../utils/i18n';

export type ExportFormat = 'md' | 'html' | 'json' | 'txt' | 'csv' | 'xml';

interface ExportModalProps {
  title: string;
  uiLanguage: UILanguage;
  onExport: (format: ExportFormat) => void;
  onClose: () => void;
  isExporting: boolean;
}

export function ExportModal({ title, uiLanguage, onExport, onClose, isExporting }: ExportModalProps) {
  const m = t(uiLanguage);
  const formats: { id: ExportFormat; name: string; icon: typeof FileText; description: string }[] =
    [
      { id: 'md', name: m.formatMdName, icon: FileText, description: m.formatMdDesc },
      { id: 'html', name: m.formatHtmlName, icon: Code, description: m.formatHtmlDesc },
      { id: 'json', name: m.formatJsonName, icon: FileJson, description: m.formatJsonDesc },
      { id: 'txt', name: m.formatTxtName, icon: Hash, description: m.formatTxtDesc },
      { id: 'csv', name: m.formatCsvName, icon: Search, description: m.formatCsvDesc },
      { id: 'xml', name: m.formatXmlName, icon: FileCode, description: m.formatXmlDesc },
    ];

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-[110] bg-[var(--overlay)] backdrop-blur-sm flex items-center justify-center p-6"
    >
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="bg-[var(--surface)] text-[var(--text)] w-full max-w-md rounded-3xl shadow-2xl overflow-hidden border border-[var(--border)]"
      >
        <div className="p-6 border-b border-[var(--border-soft)] flex justify-between items-center">
          <div>
            <h3 className="text-lg font-semibold">{m.exportModalTitle}</h3>
            <p className="text-xs text-[var(--muted)] truncate max-w-[200px]">{title}</p>
          </div>
          <button type="button" onClick={onClose} disabled={isExporting} aria-label={m.settingsClose}>
            <X size={20} />
          </button>
        </div>

        <div className="p-6 space-y-3">
          <div className="grid grid-cols-1 gap-3">
            {formats.map((f) => (
              <button
                key={f.id}
                type="button"
                onClick={() => onExport(f.id)}
                disabled={isExporting}
                className="flex items-center gap-4 p-4 rounded-2xl border border-[var(--border)] hover:border-[var(--text)] hover:bg-[var(--surface-2)] transition-all group disabled:opacity-50"
              >
                <div className="w-10 h-10 rounded-xl bg-[var(--surface-2)] group-hover:bg-[var(--surface)] flex items-center justify-center text-[var(--accent)] transition-colors">
                  <f.icon size={20} />
                </div>
                <div className="text-left">
                  <span className="font-bold text-sm block">{f.name}</span>
                  <span className="text-[10px] text-[var(--muted)] block">{f.description}</span>
                </div>
              </button>
            ))}
          </div>
        </div>

        {isExporting && (
          <div className="px-6 pb-6 text-center">
            <p className="text-xs text-[var(--muted)] animate-pulse">{m.exportPreparing}</p>
          </div>
        )}
      </motion.div>
    </motion.div>
  );
}
