// Dashboard.jsx
import { useEffect, useRef, useState, useCallback } from "react";
import { useAuth } from "./AuthContext";

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || "ws://localhost:8000";
const MAX_RECONNECT_DELAY_MS = 15000;

export default function Dashboard() {
  const { token, officer, logout, apiBaseUrl } = useAuth();
  const [threats, setThreats] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState("connecting"); // connecting | open | closed | error

  const wsRef = useRef(null);
  const reconnectAttemptRef = useRef(0);
  const reconnectTimeoutRef = useRef(null);
  const isUnmountingRef = useRef(false);

  useEffect(() => {
    if (!token) return;

    fetch(`${apiBaseUrl}/threats?limit=200`, {
      headers: { Authorization: `Bearer ${token}` },
    })
      .then((response) => {
        if (!response.ok) throw new Error("Unable to load threat history");
        return response.json();
      })
      .then((data) => setThreats(data.items ?? []))
      .catch(() => setThreats([]));
  }, [apiBaseUrl, token]);

  const connect = useCallback(() => {
    if (!token) return;

    setConnectionStatus("connecting");

    // Token passed as query param; auth.py/main.py validate it server-side
    // before accepting the handshake.
    const ws = new WebSocket(
      `${WS_BASE_URL}/ws/live-feed?token=${encodeURIComponent(token)}`
    );
    wsRef.current = ws;

    ws.onopen = () => {
      reconnectAttemptRef.current = 0;
      setConnectionStatus("open");
    };

    ws.onmessage = (event) => {
      try {
        const threatPost = JSON.parse(event.data);
        setThreats((prev) => [threatPost, ...prev].slice(0, 200));
      } catch {
        // Malformed payload from the feed — drop it, don't crash the UI.
      }
    };

    ws.onerror = () => {
      setConnectionStatus("error");
    };

    ws.onclose = (event) => {
      setConnectionStatus("closed");

      // 1008 = policy violation (server rejected the token). Don't
      // reconnect in a loop against a dead credential — force re-login.
      if (event.code === 1008) {
        logout();
        return;
      }

      if (isUnmountingRef.current) return;

      const delay = Math.min(
        1000 * 2 ** reconnectAttemptRef.current,
        MAX_RECONNECT_DELAY_MS
      );
      reconnectAttemptRef.current += 1;
      reconnectTimeoutRef.current = setTimeout(connect, delay);
    };
  }, [token, logout]);

  useEffect(() => {
    isUnmountingRef.current = false;
    connect();

    return () => {
      isUnmountingRef.current = true;
      clearTimeout(reconnectTimeoutRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  const statusColor = {
    connecting: "bg-amber-500",
    open: "bg-emerald-500",
    closed: "bg-slate-500",
    error: "bg-red-500",
  }[connectionStatus];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold tracking-tight">Live Threat Feed</h1>
          <p className="text-slate-500 text-xs mt-0.5">
            Signed in as {officer?.email} · Clearance L{officer?.clearanceLevel}
          </p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span className={`w-2 h-2 rounded-full ${statusColor}`} />
            {connectionStatus}
          </div>
          <button
            onClick={logout}
            className="text-xs font-medium text-slate-400 hover:text-slate-200 border border-slate-700 rounded-md px-3 py-1.5 transition"
          >
            Log Out
          </button>
        </div>
      </header>

      <main className="p-6">
        {threats.length === 0 ? (
          <p className="text-slate-600 text-sm">
            Awaiting incoming threat data...
          </p>
        ) : (
          <ul className="space-y-3">
            {threats.map((threat) => (
              <li
                key={threat.id}
                className="rounded-lg border border-slate-800 bg-slate-900/60 px-4 py-3"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="text-xs font-medium uppercase tracking-wide text-slate-500">
                    {threat.platform}
                  </span>
                  <span className="text-xs text-slate-600">
                    {new Date(threat.timestamp).toLocaleTimeString()}
                  </span>
                </div>
                <p className="text-sm text-slate-200 truncate">{threat.content}</p>
                <div className="flex gap-4 mt-2 text-xs">
                  <span className="text-slate-400">
                    Threat Level:{" "}
                    <span className="font-semibold text-slate-200">
                      {threat.threat_level}
                    </span>
                  </span>
                  <span className="text-slate-400">
                    Panic Score:{" "}
                    <span className="font-semibold text-slate-200">
                      {threat.panic_score}
                    </span>
                  </span>
                </div>
              </li>
            ))}
          </ul>
        )}
      </main>
    </div>
  );
}