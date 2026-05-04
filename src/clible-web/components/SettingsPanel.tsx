import { X, User, Paintbrush, Globe2, Languages } from "lucide-react";
import { motion } from "motion/react";
import type { InstalledTranslation } from "../types/bible";
import type { Theme, UserSettings } from "../user/SettingsContext";
import type { UILanguage } from "../utils/bookNames";
import { t } from "../utils/i18n";

type Props = {
  open: boolean;
  onClose: () => void;
  username: string;
  userId: string;
  settings: UserSettings | null;
  loading: boolean;
  error: string | null;
  installedTranslations: InstalledTranslation[];
  onPickTranslation: () => void;
  onSetTheme: (theme: Theme) => void;
  onSetUILanguage: (lang: UILanguage) => void;
  uiLanguage: UILanguage;
};

function ThemeButton({
  active,
  label,
  onClick,
}: {
  active: boolean;
  label: string;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-3 py-2 rounded-xl text-sm font-semibold border transition-colors ${
        active
          ? "bg-[var(--text)] text-[var(--surface)] border-[var(--text)]"
          : "bg-[var(--surface)] text-[var(--text)] border-[var(--border)] hover:border-[var(--text)]"
      }`}
    >
      {label}
    </button>
  );
}

export function SettingsPanel({
  open,
  onClose,
  username,
  userId,
  settings,
  loading,
  error,
  installedTranslations,
  onPickTranslation,
  onSetTheme,
  onSetUILanguage,
  uiLanguage,
}: Props) {
  if (!open) return null;

  const m = t(uiLanguage);
  const activeTheme = settings?.theme ?? "system";
  const activeTranslation = settings?.translationId;
  const activeUILanguage = settings?.uiLanguage ?? "en";

  const translationLabel = activeTranslation
    ? installedTranslations.find((x) => x.id === activeTranslation)?.name ??
      activeTranslation.toUpperCase()
    : null;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 z-[90]"
    >
      <button
        onClick={onClose}
        className="absolute inset-0 bg-[var(--overlay)] backdrop-blur-[2px]"
        aria-label={m.settingsCloseBackdrop}
      />

      <motion.aside
        initial={{ x: 24, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        exit={{ x: 24, opacity: 0 }}
        transition={{ type: "spring", stiffness: 420, damping: 36 }}
        className="absolute top-4 right-4 bottom-4 w-[min(520px,calc(100vw-2rem))] bg-[var(--surface)] rounded-3xl shadow-2xl border border-[var(--border)] overflow-hidden flex flex-col text-[var(--text)]"
        role="dialog"
        aria-modal="true"
        aria-label={m.settingsDialogLabel}
      >
        <div className="p-6 border-b border-[var(--border-soft)] flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold tracking-tight">{m.settingsHeading}</h3>
            <p className="text-xs text-[var(--muted)] mt-1">{m.settingsSubtitle}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-[var(--surface-2)] rounded-full transition-colors"
            aria-label={m.settingsClose}
          >
            <X size={18} />
          </button>
        </div>

        <div className="p-6 space-y-6 overflow-y-auto">
          {error && (
            <p className="text-sm text-red-600" role="alert">
              {error}
            </p>
          )}

          <section className="rounded-2xl border border-[var(--border)] p-4">
            <div className="flex items-center gap-2 text-sm font-semibold">
              <User size={16} />
              {m.settingsProfile}
            </div>
            <div className="mt-3 grid grid-cols-1 gap-3 text-sm">
              <div>
                <div className="text-xs text-[var(--muted)]">{m.settingsUsername}</div>
                <div className="font-medium">{username}</div>
              </div>
              <div>
                <div className="text-xs text-[var(--muted)]">{m.settingsUserId}</div>
                <div className="font-mono text-xs break-all">{userId}</div>
              </div>
            </div>
          </section>

          <section className="rounded-2xl border border-[var(--border)] p-4">
            <div className="flex items-center gap-2 text-sm font-semibold">
              <Paintbrush size={16} />
              {m.settingsTheme}
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              <ThemeButton
                active={activeTheme === "light"}
                label={m.themeLight}
                onClick={() => onSetTheme("light")}
              />
              <ThemeButton
                active={activeTheme === "dark"}
                label={m.themeDark}
                onClick={() => onSetTheme("dark")}
              />
              <ThemeButton
                active={activeTheme === "system"}
                label={m.themeSystem}
                onClick={() => onSetTheme("system")}
              />
            </div>
            {loading && (
              <p className="mt-3 text-xs text-[var(--muted)]">{m.settingsLoading}</p>
            )}
          </section>

          <section className="rounded-2xl border border-[var(--border)] p-4">
            <div className="flex items-center gap-2 text-sm font-semibold">
              <Languages size={16} />
              {m.settingsInterfaceLang}
            </div>
            <p className="mt-2 text-xs text-[var(--muted)]">{m.settingsInterfaceLangHint}</p>
            <div className="mt-3 flex flex-wrap gap-2">
              <ThemeButton
                active={activeUILanguage === "en"}
                label={m.langEnglish}
                onClick={() => onSetUILanguage("en")}
              />
              <ThemeButton
                active={activeUILanguage === "fi"}
                label={m.langFinnish}
                onClick={() => onSetUILanguage("fi")}
              />
            </div>
          </section>

          <section className="rounded-2xl border border-[var(--border)] p-4">
            <div className="flex items-center gap-2 text-sm font-semibold">
              <Globe2 size={16} />
              {m.settingsTranslation}
            </div>
            <div className="mt-3 flex items-center justify-between gap-3">
              <div className="min-w-0">
                <div className="text-xs text-[var(--muted)]">{m.settingsDefaultTranslation}</div>
                <div className="font-medium truncate">
                  {translationLabel ?? m.settingsNotSelected}
                </div>
              </div>
              <button
                onClick={onPickTranslation}
                className="px-3 py-2 rounded-xl text-sm font-semibold border border-[var(--border)] hover:border-[var(--text)] transition-colors"
              >
                {m.settingsChoose}
              </button>
            </div>
            <p className="mt-3 text-xs text-[var(--muted)]">{m.settingsTranslationFootnote}</p>
          </section>
        </div>
      </motion.aside>
    </motion.div>
  );
}
