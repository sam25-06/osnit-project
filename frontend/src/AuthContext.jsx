// AuthContext.jsx
import { createContext, useContext, useState, useEffect, useCallback, useMemo } from "react";

const AuthContext = createContext(null);

const TOKEN_KEY = "intel_dashboard_token";
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

function decodeJwtPayload(token) {
  try {
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const json = decodeURIComponent(
      atob(base64)
        .split("")
        .map((c) => "%" + c.charCodeAt(0).toString(16).padStart(2, "0"))
        .join("")
    );
    return JSON.parse(json);
  } catch {
    return null;
  }
}

function isTokenExpired(payload) {
  if (!payload?.exp) return true;
  return Date.now() >= payload.exp * 1000;
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem(TOKEN_KEY));
  const [officer, setOfficer] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  const clearSession = useCallback(() => {
    localStorage.removeItem(TOKEN_KEY);
    setToken(null);
    setOfficer(null);
  }, []);

  const applyToken = useCallback(
    (newToken) => {
      const payload = decodeJwtPayload(newToken);
      if (!payload || isTokenExpired(payload)) {
        clearSession();
        return false;
      }
      localStorage.setItem(TOKEN_KEY, newToken);
      setToken(newToken);
      setOfficer({
        email: payload.sub,
        clearanceLevel: payload.clearance_level,
      });
      return true;
    },
    [clearSession]
  );

  // Rehydrate session on load / hard refresh
  useEffect(() => {
    const stored = localStorage.getItem(TOKEN_KEY);
    if (stored) {
      applyToken(stored);
    }
    setIsLoading(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const login = useCallback(
    async (email, password) => {
      setError(null);

      // Backend uses OAuth2PasswordRequestForm -> requires
      // application/x-www-form-urlencoded, NOT JSON.
      const body = new URLSearchParams();
      body.append("username", email);
      body.append("password", password);

      const response = await fetch(`${API_BASE_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: body.toString(),
      });

      if (!response.ok) {
        const detail = await response
          .json()
          .then((d) => d.detail)
          .catch(() => null);
        const message = detail || "Invalid credentials. Please try again.";
        setError(message);
        throw new Error(message);
      }

      const data = await response.json();
      applyToken(data.access_token);
      return data;
    },
    [applyToken]
  );

  const logout = useCallback(() => {
    clearSession();
  }, [clearSession]);

  const value = useMemo(
    () => ({
      token,
      officer,
      isAuthenticated: Boolean(token && officer),
      isLoading,
      error,
      login,
      logout,
      apiBaseUrl: API_BASE_URL,
    }),
    [token, officer, isLoading, error, login, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return ctx;
}