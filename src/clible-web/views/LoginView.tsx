import { useState, FormEvent } from 'react';

type Props = {
  onSuccess: (user: { id: string; username: string; aiAccess: boolean; isAdmin: boolean }) => void;
};

export function LoginView({ onSuccess }: Props) {
    const [mode, setMode] = useState<"login" | "register">("login");
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState<string | null>(null);
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        setError(null);
        setLoading(true);

        const endpoint = mode === "login" ? "/api/auth/login" : "/api/auth/register";
        const res = await fetch(endpoint, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ username, password }),
        });

        const data = await res.json();
        setLoading(false);

        if (!res.ok) {
            setError(data.error || "Failed to authenticate.");
            return;
        }

        onSuccess(data);
    }

    return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--bg)] text-[var(--text)]">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-sm space-y-4 p-8 bg-[var(--surface)] rounded-2xl shadow-sm border border-[var(--border)]"
      >
        <h2 className="text-xl font-semibold">{mode === "login" ? "Sign in" : "Create account"}</h2>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full border border-[var(--border)] bg-transparent rounded-xl px-4 py-2 outline-none focus:border-[var(--text)]"
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full border border-[var(--border)] bg-transparent rounded-xl px-4 py-2 outline-none focus:border-[var(--text)]"
          required
        />
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-[var(--text)] text-[var(--surface)] rounded-xl py-2 font-medium hover:opacity-90 transition-colors disabled:opacity-50"
        >
          {loading ? "..." : mode === "login" ? "Sign in" : "Register"}
        </button>
        <button
          type="button"
          onClick={() => setMode(mode === "login" ? "register" : "login")}
          className="w-full text-sm text-[var(--muted)] hover:text-[var(--text)] transition-colors"
        >
          {mode === "login" ? "No account? Register" : "Have an account? Sign in"}
        </button>
      </form>
    </div>
  );
}