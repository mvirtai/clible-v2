import { useState, FormEvent } from 'react';

type Props = { onSuccess: (user: { id: string; username: string }) => void };

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
    <div className="min-h-screen flex items-center justify-center bg-[#FDFCFB]">
      <form onSubmit={handleSubmit} className="w-full max-w-sm space-y-4 p-8 bg-white rounded-2xl shadow-sm border border-[#E5E5E5]">
        <h2 className="text-xl font-semibold">{mode === "login" ? "Sign in" : "Create account"}</h2>
        {error && <p className="text-sm text-red-600">{error}</p>}
        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="w-full border border-[#E5E5E5] rounded-xl px-4 py-2 outline-none focus:border-[#1A1A1A]"
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full border border-[#E5E5E5] rounded-xl px-4 py-2 outline-none focus:border-[#1A1A1A]"
          required
        />
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-[#1A1A1A] text-white rounded-xl py-2 font-medium hover:bg-[#333] transition-colors disabled:opacity-50"
        >
          {loading ? "..." : mode === "login" ? "Sign in" : "Register"}
        </button>
        <button
          type="button"
          onClick={() => setMode(mode === "login" ? "register" : "login")}
          className="w-full text-sm text-[#8E8E8E] hover:text-[#1A1A1A] transition-colors"
        >
          {mode === "login" ? "No account? Register" : "Have an account? Sign in"}
        </button>
      </form>
    </div>
  );
}