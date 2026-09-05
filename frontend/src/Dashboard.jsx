import { useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "./AuthContext";

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || "ws://localhost:8000";
const MAX_RECONNECT_DELAY_MS = 15000;

const severityMeta = {
  5: { label: "Critical", className: "critical" },
  4: { label: "High", className: "high" },
  3: { label: "Elevated", className: "elevated" },
  2: { label: "Guarded", className: "guarded" },
  1: { label: "Low", className: "low" },
};

function formatTime(timestamp) {
  return new Intl.DateTimeFormat("en", { hour: "numeric", minute: "2-digit" }).format(new Date(timestamp));
}

function formatDate(timestamp) {
  return new Intl.DateTimeFormat("en", { month: "short", day: "numeric" }).format(new Date(timestamp));
}

function getSeverity(level) {
  return severityMeta[level] || severityMeta[1];
}

export default function Dashboard() {
  const { token, officer, logout, apiBaseUrl } = useAuth();
  const [threats, setThreats] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState("connecting");
  const [activeView, setActiveView] = useState("Live feed");
  const wsRef = useRef(null);
  const reconnectAttemptRef = useRef(0);
  const reconnectTimeoutRef = useRef(null);
  const isUnmountingRef = useRef(false);

  useEffect(() => {
    if (!token) return;
    fetch(`${apiBaseUrl}/threats?limit=200`, { headers: { Authorization: `Bearer ${token}` } })
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
    const ws = new WebSocket(`${WS_BASE_URL}/ws/live-feed?token=${encodeURIComponent(token)}`);
    wsRef.current = ws;
    ws.onopen = () => { reconnectAttemptRef.current = 0; setConnectionStatus("open"); };
    ws.onmessage = (event) => {
      try {
        const threatPost = JSON.parse(event.data);
        setThreats((previous) => [threatPost, ...previous].slice(0, 200));
      } catch { /* Ignore malformed feed messages. */ }
    };
    ws.onerror = () => setConnectionStatus("error");
    ws.onclose = (event) => {
      setConnectionStatus("closed");
      if (event.code === 1008) { logout(); return; }
      if (isUnmountingRef.current) return;
      const delay = Math.min(1000 * 2 ** reconnectAttemptRef.current, MAX_RECONNECT_DELAY_MS);
      reconnectAttemptRef.current += 1;
      reconnectTimeoutRef.current = setTimeout(connect, delay);
    };
  }, [logout, token]);

  useEffect(() => {
    isUnmountingRef.current = false;
    connect();
    return () => {
      isUnmountingRef.current = true;
      clearTimeout(reconnectTimeoutRef.current);
      wsRef.current?.close();
    };
  }, [connect]);

  const criticalCount = threats.filter((threat) => threat.threat_level >= 4).length;
  const openCount = threats.filter((threat) => !threat.is_resolved).length;
  const averagePanic = threats.length ? Math.round(threats.reduce((total, threat) => total + Number(threat.panic_score || 0), 0) / threats.length) : 0;
  const connectionLabel = connectionStatus === "open" ? "Live connection" : "Reconnecting";

  return (
    <div className="console-shell">
      <aside className="sidebar">
        <div className="brand-lockup"><div className="brand-mark"><span /></div><div><p className="brand-name">OSNIT</p><p className="brand-caption">Operational intelligence</p></div></div>
        <div className="sidebar-section-label">Workspace</div>
        <nav className="main-nav" aria-label="Primary navigation">
          {["Live feed", "Situation room", "Watchlists"].map((item, index) => <button className={`nav-item ${activeView === item ? "active" : ""}`} key={item} onClick={() => setActiveView(item)}><span className="nav-glyph">{["◈", "⊞", "⌁"][index]}</span><span>{item}</span>{item === "Live feed" && <span className="nav-count">{threats.length}</span>}</button>)}
        </nav>
        <div className="sidebar-section-label">System</div>
        <div className="system-card"><div className="system-card-header"><span className={`status-dot ${connectionStatus}`} /><span>{connectionLabel}</span></div><p>Ingestion and alert channels are being monitored.</p><div className="system-line"><span>WebSocket</span><strong>{connectionStatus === "open" ? "ONLINE" : "PENDING"}</strong></div><div className="system-line"><span>Last sync</span><strong>{threats[0] ? formatTime(threats[0].timestamp) : "--:--"}</strong></div></div>
        <div className="sidebar-footer"><div className="profile-chip"><div className="profile-avatar">{officer?.email?.[0]?.toUpperCase() || "O"}</div><div className="profile-copy"><strong>{officer?.email || "Officer"}</strong><span>Clearance L{officer?.clearanceLevel || 1}</span></div></div><button className="logout-button" onClick={logout} aria-label="Log out">↗</button></div>
      </aside>

      <main className="main-panel">
        <header className="topbar"><div className="breadcrumb"><span>Workspace</span><b>/</b><strong>{activeView}</strong></div><div className="topbar-meta"><span className="date-stamp">{formatDate(new Date())}</span><span className="live-pill"><i /> Monitoring</span></div></header>
        <div className="content-wrap">
          <section className="page-heading"><div><p className="eyebrow">Situation overview / 01</p><h1>Live threat feed</h1><p className="heading-copy">A real-time view of signals requiring operational attention.</p></div><div className="heading-action"><span className="mini-pulse" />Auto-refreshing</div></section>
          <section className="stat-grid" aria-label="Threat summary">
            <article className="stat-card stat-primary"><span className="stat-label">Signals indexed</span><strong>{threats.length.toString().padStart(2, "0")}</strong><span className="stat-note">Across all monitored channels</span></article>
            <article className="stat-card"><span className="stat-label">Open incidents</span><strong>{openCount.toString().padStart(2, "0")}</strong><span className="stat-note"><em className="trend-up">↗</em> Requiring review</span></article>
            <article className="stat-card"><span className="stat-label">Priority signals</span><strong>{criticalCount.toString().padStart(2, "0")}</strong><span className="stat-note"><em className="trend-alert">!</em> High or critical</span></article>
            <article className="stat-card"><span className="stat-label">Mean panic score</span><strong>{averagePanic}<small>/100</small></strong><span className="stat-note">Current feed average</span></article>
          </section>
          <section className="feed-layout">
            <div className="feed-panel"><div className="panel-heading"><div><p className="eyebrow">Incoming signals</p><h2>Latest intelligence</h2></div><button className="filter-button">All channels <span>⌄</span></button></div>
              {threats.length === 0 ? <div className="empty-state"><span className="empty-icon">⌁</span><h3>Awaiting incoming signals</h3><p>New threat intelligence will appear here as it is ingested.</p></div> : <div className="threat-table"><div className="table-head"><span>Signal</span><span>Source</span><span>Assessment</span><span>Received</span></div>{threats.slice(0, 40).map((threat) => { const severity = getSeverity(threat.threat_level); return <article className="threat-row" key={threat.id}><div className="signal-cell"><span className={`severity-bar ${severity.className}`} /><div><h3>{threat.content.replace(/^\[DEMO\]\s*/, "")}</h3><span className="signal-id">ID / {String(threat.id).slice(-8).toUpperCase()}</span></div></div><div className="source-cell"><span className="source-icon">{threat.platform?.[0]?.toUpperCase()}</span><span>{threat.platform}</span></div><div className="assessment-cell"><span className={`severity-badge ${severity.className}`}>{severity.label}</span><span className="panic-value">{threat.panic_score} panic</span></div><div className="received-cell"><span>{formatTime(threat.timestamp)}</span><small>{formatDate(threat.timestamp)}</small></div></article>; })}</div>}
            </div>
            <aside className="insight-panel"><div className="panel-heading compact"><div><p className="eyebrow">Risk distribution</p><h2>Signal profile</h2></div><span className="panel-index">02</span></div><div className="risk-ring"><div><strong>{averagePanic}</strong><span>avg. panic</span></div></div><div className="risk-legend">{[5, 4, 3, 2, 1].map((level) => <div className="legend-row" key={level}><span><i className={`legend-dot ${getSeverity(level).className}`} />{getSeverity(level).label}</span><strong>{threats.filter((threat) => threat.threat_level === level).length}</strong></div>)}</div><div className="analyst-note"><span className="note-mark">✦</span><div><p>Analyst note</p><strong>Review critical signals first</strong><span>Priority is weighted by threat level and panic score.</span></div></div></aside>
          </section>
        </div>
      </main>
    </div>
  );
}
