import { createContext, useContext, useEffect, useState, ReactNode } from 'react';

/**
 * Authenticated user information as returned by GET /api/auth/me.
 *
 * Purpose: keep UI decisions (e.g. admin affordances, AI buttons) aligned with
 * server-side authorization while keeping sensitive fields off the client.
 */
type User = {
  id: string;
  username: string;
  aiAccess: boolean;
  isAdmin: boolean;
} | null;

type AuthContextType = {
    user: User;
    loading: boolean;
    login: (user: { id: string; username: string; aiAccess: boolean; isAdmin: boolean }) => void;
    logout: () => Promise<void>;
};

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: ReactNode}) {
    const [user, setUser] = useState<User>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // check if user is already logged in
        fetch("/api/auth/me")
            .then((r) => (r.ok ? r.json() : null))
            .then(setUser)
            .finally(() => setLoading(false))
    }, []);

    const login = (u: { id: string; username: string; aiAccess: boolean; isAdmin: boolean }) => setUser(u);

    const logout = async () => {
        await fetch("/api/auth/logout", { method: "POST" });
        setUser(null);
    }

    return (
        <AuthContext.Provider value={{ user, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}