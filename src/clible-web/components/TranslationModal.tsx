import { X } from 'lucide-react';
import { motion } from 'motion/react';
import { AvailableTranslation, InstalledTranslation } from '../types/bible';

interface TranslationModalProps {
  installedTranslations: InstalledTranslation[];
  availableTranslations: AvailableTranslation[];
  loadingAvailableTranslations: boolean;
  translationsLoadError: string | null;
  installError: string | null;
  installSuccess: string | null;
  installingTranslationId: string | null;
  activeTranslation: string | null;
  onSelect: (id: string) => void;
  onInstall: (id: string) => void;
  onClose: () => void;
}

export function TranslationModal({
  installedTranslations,
  availableTranslations,
  loadingAvailableTranslations,
  translationsLoadError,
  installError,
  installSuccess,
  installingTranslationId,
  activeTranslation,
  onSelect,
  onInstall,
  onClose,
}: TranslationModalProps) {
  const installedIds = new Set(installedTranslations.map((t) => t.id));

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
          {installError && (
            <p className="col-span-full text-sm text-red-600" role="alert">
              {installError}
            </p>
          )}
          {installSuccess && (
            <p className="col-span-full text-sm text-emerald-700" role="status">
              {installSuccess}
            </p>
          )}
          {!translationsLoadError && installedTranslations.length === 0 && !loadingAvailableTranslations && (
            <p className="col-span-full text-sm text-[var(--muted)]">
              No translations are installed on this server yet. Use Install to fetch one from the
              catalog.
            </p>
          )}

          {loadingAvailableTranslations && (
            <p className="col-span-full text-sm text-[var(--muted)]">Loading translation catalog...</p>
          )}

          {availableTranslations.map((t) => {
            const isInstalled = installedIds.has(t.id);
            const isInstalling = installingTranslationId === t.id;
            return (
              <div
                key={t.id}
                className="px-4 py-3 rounded-xl text-left border-2 transition-all border-[var(--border)]"
              >
                <span className="uppercase font-bold text-sm block">{t.id}</span>
                <span className="text-xs text-[var(--muted)] block mt-1">{t.name}</span>
                <span className="text-[10px] text-[var(--muted)] uppercase tracking-wide">
                  {t.language} · {t.format}
                  {typeof t.size_mb === "number" ? ` · ${t.size_mb} MB` : ""}
                </span>
                <div className="mt-3 flex gap-2">
                  <button
                    onClick={() => onSelect(t.id)}
                    disabled={!isInstalled}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition ${
                      isInstalled
                        ? "border-[var(--text)] text-[var(--text)] hover:bg-[var(--surface-2)]"
                        : "border-[var(--border)] text-[var(--muted)] cursor-not-allowed"
                    }`}
                  >
                    {activeTranslation === t.id ? "Selected" : "Use"}
                  </button>
                  <button
                    onClick={() => onInstall(t.id)}
                    disabled={isInstalled || isInstalling}
                    className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition ${
                      isInstalled
                        ? "border-[var(--border)] text-[var(--muted)] cursor-not-allowed"
                        : "border-[var(--text)] text-[var(--text)] hover:bg-[var(--surface-2)]"
                    }`}
                  >
                    {isInstalled ? "Installed" : isInstalling ? "Installing..." : "Install"}
                  </button>
                </div>
              </div>
            );
          })}

          {!loadingAvailableTranslations && availableTranslations.length === 0 && !translationsLoadError && (
            <p className="col-span-full text-sm text-[var(--muted)]">
              No translations found in the catalog.
            </p>
          )}
        </div>
        <div className="p-6 bg-[var(--surface-2)] text-xs text-[var(--muted)] border-t border-[var(--border-soft)]">
          <p>
            Installable translations come from the shared catalog. Installed translations are
            specific to this server environment.
          </p>
        </div>
      </motion.div>
    </motion.div>
  );
}
