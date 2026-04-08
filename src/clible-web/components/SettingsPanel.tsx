import { X, User, Paintbrush, Globe2 } from "lucide-react";
import { motion } from "motion/react";
import type { InstalledTranslation } from "../types/bible";
import type { Theme, UserSettings } from "../user/SettingsContext";

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
          ? "bg-[#1A1A1A] text-white border-[#1A1A1A]"
          : "bg-white text-[#1A1A1A] border-[#E5E5E5] hover:border-[#1A1A1A]"
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
}: Props) {
  if (!open) return null;

  const activeTheme = settings?.theme ?? "system";
  const activeTranslation = settings?.translationId;

  const translationLabel = activeTranslation
    ? installedTranslations.find((t) => t.id === activeTranslation)?.name ??
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
        className="absolute inset-0 bg-black/30 backdrop-blur-[2px]"
        aria-label="Close settings"
      />

      <motion.aside
        initial={{ x: 24, opacity: 0 }}
        animate={{ x: 0, opacity: 1 }}
        exit={{ x: 24, opacity: 0 }}
        transition={{ type: "spring", stiffness: 420, damping: 36 }}
        className="absolute top-4 right-4 bottom-4 w-[min(520px,calc(100vw-2rem))] bg-white rounded-3xl shadow-2xl border border-[#E5E5E5] overflow-hidden flex flex-col"
        role="dialog"
        aria-modal="true"
        aria-label="Settings"
      >
        <div className="p-6 border-b border-[#F5F5F5] flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold tracking-tight">Settings</h3>
            <p className="text-xs text-[#8E8E8E] mt-1">
              User preferences are saved to your account.
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-[#F5F5F5] rounded-full transition-colors"
            aria-label="Close"
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

          <section className="rounded-2xl border border-[#E5E5E5] p-4">
            <div className="flex items-center gap-2 text-sm font-semibold">
              <User size={16} />
              Profile
            </div>
            <div className="mt-3 grid grid-cols-1 gap-3 text-sm">
              <div>
                <div className="text-xs text-[#8E8E8E]">Username</div>
                <div className="font-medium">{username}</div>
              </div>
              <div>
                <div className="text-xs text-[#8E8E8E]">User id</div>
                <div className="font-mono text-xs break-all">{userId}</div>
              </div>
            </div>
          </section>

          <section className="rounded-2xl border border-[#E5E5E5] p-4">
            <div className="flex items-center gap-2 text-sm font-semibold">
              <Paintbrush size={16} />
              Theme
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              <ThemeButton
                active={activeTheme === "light"}
                label="Light"
                onClick={() => onSetTheme("light")}
              />
              <ThemeButton
                active={activeTheme === "dark"}
                label="Dark"
                onClick={() => onSetTheme("dark")}
              />
              <ThemeButton
                active={activeTheme === "system"}
                label="System"
                onClick={() => onSetTheme("system")}
              />
            </div>
            {loading && (
              <p className="mt-3 text-xs text-[#8E8E8E]">Loading settings…</p>
            )}
          </section>

          <section className="rounded-2xl border border-[#E5E5E5] p-4">
            <div className="flex items-center gap-2 text-sm font-semibold">
              <Globe2 size={16} />
              Translation
            </div>
            <div className="mt-3 flex items-center justify-between gap-3">
              <div className="min-w-0">
                <div className="text-xs text-[#8E8E8E]">Default translation</div>
                <div className="font-medium truncate">
                  {translationLabel ?? "Not selected"}
                </div>
              </div>
              <button
                onClick={onPickTranslation}
                className="px-3 py-2 rounded-xl text-sm font-semibold border border-[#E5E5E5] hover:border-[#1A1A1A] transition-colors"
              >
                Choose…
              </button>
            </div>
            <p className="mt-3 text-xs text-[#8E8E8E]">
              Installed translations are environment-wide. Your selection is saved per user.
            </p>
          </section>
        </div>
      </motion.aside>
    </motion.div>
  );
}

