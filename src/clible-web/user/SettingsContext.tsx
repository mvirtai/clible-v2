import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { useAuth } from "../AuthContext";

export type Theme = "light" | "dark" | "system";

export type UserSettings = {
  translationId: string | null;
  theme: Theme;
};

export type SettingsPatch = Partial<UserSettings>;

type SettingsContextType = {
  settings: UserSettings | null;
  loading: boolean;
  error: string | null;
  reload: () => Promise<void>;
  updateSettings: (patch: SettingsPatch) => Promise<void>;
};

const SettingsContext = createContext<SettingsContextType | null>(null);

async function readErrorMessage(resp: Response): Promise<string | null> {
  const body = (await resp.json().catch(() => ({}))) as { error?: string };
  return typeof body.error === "string" ? body.error : null;
}

export function SettingsProvider({ children }: { children: ReactNode }) {
  const { user, loading: authLoading } = useAuth();
  const [settings, setSettings] = useState<UserSettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = async () => {
    if (!user) return;
    setLoading(true);
    setError(null);

    const res = await fetch("/api/user/settings");
    if (!res.ok) {
      const msg = (await readErrorMessage(res)) ?? "Failed to load user settings.";
      setLoading(false);
      setError(msg);
      throw new Error(msg);
    }

    const data = (await res.json()) as UserSettings;
    setSettings(data);
    setLoading(false);
  };

  useEffect(() => {
    if (authLoading) return;

    if (!user) {
      setSettings(null);
      setLoading(false);
      setError(null);
      return;
    }

    const ac = new AbortController();
    setLoading(true);
    setError(null);

    fetch("/api/user/settings", { signal: ac.signal })
      .then(async (res) => {
        if (!res.ok) {
          const msg =
            (await readErrorMessage(res)) ?? "Failed to load user settings.";
          throw new Error(msg);
        }
        return (await res.json()) as UserSettings;
      })
      .then((data) => {
        setSettings(data);
        setLoading(false);
      })
      .catch((e: unknown) => {
        if (ac.signal.aborted) return;
        setError(e instanceof Error ? e.message : "Failed to load user settings.");
        setLoading(false);
      });

    return () => ac.abort();
  }, [user, authLoading]);

  const updateSettings = async (patch: SettingsPatch) => {
    if (!user) throw new Error("Not authenticated.");

    const previous = settings;
    const optimistic: UserSettings = {
      translationId: patch.translationId ?? previous?.translationId ?? null,
      theme: patch.theme ?? previous?.theme ?? "system",
    };

    setSettings(optimistic);
    setError(null);

    const resp = await fetch("/api/user/settings", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(patch),
    });

    if (!resp.ok) {
      const msg = (await readErrorMessage(resp)) ?? "Failed to update settings.";
      setSettings(previous);
      setError(msg);
      throw new Error(msg);
    }

    const data = (await resp.json()) as UserSettings;
    setSettings(data);
  };

  const value = useMemo<SettingsContextType>(
    () => ({ settings, loading, error, reload, updateSettings }),
    [settings, loading, error]
  );

  return <SettingsContext.Provider value={value}>{children}</SettingsContext.Provider>;
}

export function useSettings(): SettingsContextType {
  const ctx = useContext(SettingsContext);
  if (!ctx) {
    throw new Error("useSettings must be used within a SettingsProvider");
  }
  return ctx;
}