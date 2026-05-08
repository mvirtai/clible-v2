import { X } from 'lucide-react';
import { motion } from 'motion/react';
import { AvailableTranslation, InstalledTranslation } from '../types/bible';
import type { UILanguage } from '../utils/bookNames';
import { t } from '../utils/i18n';

interface TranslationModalProps {
  installedTranslations: InstalledTranslation[];
  availableTranslations: AvailableTranslation[];
  loadingAvailableTranslations: boolean;
  translationsLoadError: string | null;
  installError: string | null;
  installSuccess: string | null;
  installingTranslationId: string | null;
  activeTranslation: string | null;
  uiLanguage: UILanguage;
  query: string;
  onQueryChange: (value: string) => void;
  onSelect: (id: string) => void;
  onInstall: (id: string) => void;
  onClose: () => void;
}

const FEATURED_TRANSLATION_IDS = [
  // EN
  'web',
  'kjv',
  'eng-us-oeb',
  // FI
  'fin-1992',
  'fin-biblia-33-38',
  'fin-stlk',
  // Original languages
  'greeksblgnt',
  'hebrewaleppocodex',
] as const;

const DEFAULT_BROWSE_LIMIT = 50;

const HIDDEN_TRANSLATION_IDS = new Set<string>(['heb-leningrad']);

function normalize(s: string): string {
  return s.toLowerCase().trim();
}

function sortByUiPreference(uiLanguage: UILanguage, a: AvailableTranslation, b: AvailableTranslation): number {
  const al = normalize(a.language ?? '');
  const bl = normalize(b.language ?? '');
  const pref = normalize(uiLanguage);
  const aPref = al === pref ? 1 : 0;
  const bPref = bl === pref ? 1 : 0;
  if (aPref !== bPref) return bPref - aPref;
  return normalize(a.id).localeCompare(normalize(b.id));
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
  uiLanguage,
  query,
  onQueryChange,
  onSelect,
  onInstall,
  onClose,
}: TranslationModalProps) {
  const m = t(uiLanguage);
  const installedIds = new Set(installedTranslations.map((x) => x.id));
  const featuredSet = new Set<string>(FEATURED_TRANSLATION_IDS);

  const visibleAvailable = availableTranslations.filter((tr) => !HIDDEN_TRANSLATION_IDS.has(tr.id));

  const byId = new Map<string, AvailableTranslation>();
  for (const tr of visibleAvailable) byId.set(tr.id, tr);

  const featured = FEATURED_TRANSLATION_IDS.map((id) => byId.get(id)).filter(
    (x): x is AvailableTranslation => x != null,
  );

  const installedOther = visibleAvailable
    .filter((tr) => installedIds.has(tr.id) && !featuredSet.has(tr.id))
    .sort((a, b) => sortByUiPreference(uiLanguage, a, b));

  const browseCandidates = visibleAvailable
    .filter((tr) => !featuredSet.has(tr.id) && !installedIds.has(tr.id))
    .sort((a, b) => sortByUiPreference(uiLanguage, a, b));

  const browse = query.trim() ? browseCandidates : browseCandidates.slice(0, DEFAULT_BROWSE_LIMIT);

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
          <h3 className="text-lg font-semibold">{m.translationModalTitle}</h3>
          <button
            type="button"
            onClick={onClose}
            aria-label={m.settingsClose}
            disabled={installingTranslationId != null}
            className={installingTranslationId != null ? 'opacity-50 cursor-not-allowed' : undefined}
          >
            <X size={20} />
          </button>
        </div>
        <div className="p-6 border-b border-[var(--border-soft)]">
          <input
            value={query}
            onChange={(e) => onQueryChange(e.target.value)}
            placeholder={m.translationSearchPlaceholder}
            className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface)] px-4 py-2.5 text-sm outline-none focus:ring-2 focus:ring-[#D4A373]/40"
          />
          <p className="mt-2 text-xs text-[var(--muted)]">{m.translationSearchHint}</p>
        </div>

        <div className="p-6 max-h-[60vh] overflow-y-auto space-y-5">
          {translationsLoadError && (
            <p className="text-sm text-red-600" role="alert">
              {translationsLoadError}
            </p>
          )}
          {installError && (
            <p className="text-sm text-red-600" role="alert">
              {installError}
            </p>
          )}
          {installSuccess && (
            <p className="text-sm text-emerald-700" role="status">
              {installSuccess}
            </p>
          )}
          {!translationsLoadError && installedTranslations.length === 0 && !loadingAvailableTranslations && (
            <p className="text-sm text-[var(--muted)]">
              {m.translationNoneInstalled}
            </p>
          )}

          {loadingAvailableTranslations && (
            <p className="text-sm text-[var(--muted)]">{m.translationCatalogLoading}</p>
          )}

          <section className="space-y-2">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">
              {m.translationFeaturedLabel}
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {featured.map((tr) => (
                <TranslationCard
                  key={tr.id}
                  tr={tr}
                  isInstalled={installedIds.has(tr.id)}
                  isInstalling={installingTranslationId === tr.id}
                  activeTranslation={activeTranslation}
                  m={m}
                  onSelect={onSelect}
                  onInstall={onInstall}
                />
              ))}
            </div>
          </section>

          {installedOther.length > 0 && (
            <section className="space-y-2">
              <h4 className="text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">
                {m.translationInstalledSectionLabel}
              </h4>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {installedOther.map((tr) => (
                  <TranslationCard
                    key={tr.id}
                    tr={tr}
                    isInstalled={true}
                    isInstalling={false}
                    activeTranslation={activeTranslation}
                    m={m}
                    onSelect={onSelect}
                    onInstall={onInstall}
                  />
                ))}
              </div>
            </section>
          )}

          <section className="space-y-2">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-[var(--muted)]">
              {m.translationBrowseLabel}
            </h4>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {browse.map((tr) => (
                <TranslationCard
                  key={tr.id}
                  tr={tr}
                  isInstalled={installedIds.has(tr.id)}
                  isInstalling={installingTranslationId === tr.id}
                  activeTranslation={activeTranslation}
                  m={m}
                  onSelect={onSelect}
                  onInstall={onInstall}
                />
              ))}
            </div>
            {!query.trim() && browseCandidates.length > DEFAULT_BROWSE_LIMIT && (
              <p className="text-xs text-[var(--muted)]">{m.translationBrowseLimitedHint}</p>
            )}
          </section>

          {!loadingAvailableTranslations && availableTranslations.length === 0 && !translationsLoadError && (
            <p className="text-sm text-[var(--muted)]">{m.translationCatalogEmpty}</p>
          )}
        </div>
        <div className="p-6 bg-[var(--surface-2)] text-xs text-[var(--muted)] border-t border-[var(--border-soft)]">
          <p>{m.translationFooter}</p>
        </div>
      </motion.div>
    </motion.div>
  );
}

function TranslationCard({
  tr,
  isInstalled,
  isInstalling,
  activeTranslation,
  m,
  onSelect,
  onInstall,
}: {
  tr: AvailableTranslation;
  isInstalled: boolean;
  isInstalling: boolean;
  activeTranslation: string | null;
  m: ReturnType<typeof t>;
  onSelect: (id: string) => void;
  onInstall: (id: string) => void;
}) {
  const installDisabled = isInstalled || isInstalling;

  return (
    <div className="px-4 py-3 rounded-xl text-left border-2 transition-all border-[var(--border)]">
      <span className="uppercase font-bold text-sm block">{tr.id}</span>
      <span className="text-xs text-[var(--muted)] block mt-1">{tr.name}</span>
      <span className="text-[10px] text-[var(--muted)] uppercase tracking-wide">
        {tr.language} · {tr.format}
        {typeof tr.size_mb === 'number' ? ` · ${tr.size_mb} MB` : ''}
      </span>
      <div className="mt-3 flex gap-2">
        <button
          type="button"
          onClick={() => onSelect(tr.id)}
          disabled={!isInstalled}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition ${
            isInstalled
              ? 'border-[var(--text)] text-[var(--text)] hover:bg-[var(--surface-2)]'
              : 'border-[var(--border)] text-[var(--muted)] cursor-not-allowed'
          }`}
        >
          {activeTranslation === tr.id ? m.translationSelected : m.translationUse}
        </button>
        <button
          type="button"
          onClick={() => onInstall(tr.id)}
          disabled={installDisabled}
          className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition ${
            installDisabled
              ? 'border-[var(--border)] text-[var(--muted)] cursor-not-allowed'
              : 'border-[var(--text)] text-[var(--text)] hover:bg-[var(--surface-2)]'
          }`}
        >
          {isInstalled
            ? m.translationInstalled
            : isInstalling
              ? m.translationInstalling
              : m.translationInstall}
        </button>
      </div>
    </div>
  );
}
