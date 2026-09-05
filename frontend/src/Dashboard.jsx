import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useAuth } from "./AuthContext";

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || "ws://localhost:8000";
const MAX_RECONNECT_DELAY_MS = 15000;
const PAGE_SIZE = 8;
const VIEW_NAMES = ["Live feed", "Situation room", "Watchlists"];
const severityMeta = {
  5: { label: "Critical", className: "critical" },
  4: { label: "High", className: "high" },
  3: { label: "Elevated", className: "elevated" },
  2: { label: "Guarded", className: "guarded" },
  1: { label: "Low", className: "low" },
};

function formatTime(timestamp) { return new Intl.DateTimeFormat("en", { hour: "numeric", minute: "2-digit" }).format(new Date(timestamp)); }
function formatDate(timestamp) { return new Intl.DateTimeFormat("en", { month: "short", day: "numeric", year: "numeric" }).format(new Date(timestamp)); }
function getSeverity(level) { return severityMeta[level] || severityMeta[1]; }

function ThreatRow({ threat, onSelect, selected }) {
  const severity = getSeverity(threat.threat_level);
  return <button className={`threat-row ${selected ? "selected" : ""}`} onClick={() => onSelect(threat)}>
    <div className="signal-cell"><span className={`severity-bar ${severity.className}`} /><div><h3>{threat.content.replace(/^\[DEMO\]\s*/, "")}</h3><span className="signal-id">Signal {String(threat.id).slice(-8).toUpperCase()}</span></div></div>
    <div className="source-cell"><span className="source-icon">{threat.platform?.[0]?.toUpperCase()}</span><span>{threat.platform}</span></div>
    <div className="assessment-cell"><span className={`severity-badge ${severity.className}`}>{severity.label}</span><span className="panic-value">{threat.panic_score} panic</span></div>
    <div className="received-cell"><span>{formatTime(threat.timestamp)}</span><small>{formatDate(threat.timestamp)}</small></div>
  </button>;
}

function ThreatDetail({ threat, apiBaseUrl, token, onUpdated }) {
  const [isUpdating, setIsUpdating] = useState(false);
  if (!threat) return <aside className="detail-panel empty-detail"><p className="eyebrow">Signal detail</p><h2>Select a signal</h2><p>Choose an item from the feed to inspect its source, assessment, and resolution state.</p></aside>;
  const severity = getSeverity(threat.threat_level);
  const markResolved = async () => {
    setIsUpdating(true);
    try {
      const response = await fetch(`${apiBaseUrl}/threats/${threat.id}`, { method: "PATCH", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` }, body: JSON.stringify({ is_resolved: !threat.is_resolved }) });
      if (!response.ok) throw new Error("Unable to update signal");
      onUpdated(await response.json());
    } finally { setIsUpdating(false); }
  };
  return <aside className="detail-panel"><div className="detail-header"><div><p className="eyebrow">Signal detail</p><h2>{severity.label} priority</h2></div><span className={`detail-status ${threat.is_resolved ? "resolved" : "open"}`}>{threat.is_resolved ? "Resolved" : "Open"}</span></div><p className="detail-content">{threat.content.replace(/^\[DEMO\]\s*/, "")}</p><div className="detail-facts"><div><span>Source</span><strong>{threat.platform}</strong></div><div><span>Threat level</span><strong>{threat.threat_level} of 5</strong></div><div><span>Panic score</span><strong>{threat.panic_score} of 100</strong></div><div><span>Received</span><strong>{formatDate(threat.timestamp)} · {formatTime(threat.timestamp)}</strong></div></div><button className="review-button" onClick={markResolved} disabled={isUpdating}>{isUpdating ? "Updating..." : threat.is_resolved ? "Reopen signal" : "Mark as reviewed"}</button></aside>;
}

export default function Dashboard() {
  const { token, officer, logout, apiBaseUrl } = useAuth();
  const [threats, setThreats] = useState([]);
  const [connectionStatus, setConnectionStatus] = useState("connecting");
  const [activeView, setActiveView] = useState("Live feed");
  const [channel, setChannel] = useState("All channels");
  const [watchFilter, setWatchFilter] = useState("Priority");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedId, setSelectedId] = useState(null);
  const wsRef = useRef(null);
  const reconnectAttemptRef = useRef(0);
  const reconnectTimeoutRef = useRef(null);
  const isUnmountingRef = useRef(false);

  useEffect(() => {
    if (!token) return;
    fetch(`${apiBaseUrl}/threats?limit=200`, { headers: { Authorization: `Bearer ${token}` } }).then((response) => { if (!response.ok) throw new Error("Unable to load threat history"); return response.json(); }).then((data) => setThreats(data.items ?? [])).catch(() => setThreats([]));
  }, [apiBaseUrl, token]);

  const connect = useCallback(() => {
    if (!token) return;
    setConnectionStatus("connecting");
    const ws = new WebSocket(`${WS_BASE_URL}/ws/live-feed?token=${encodeURIComponent(token)}`);
    wsRef.current = ws;
    ws.onopen = () => { reconnectAttemptRef.current = 0; setConnectionStatus("open"); };
    ws.onmessage = (event) => { try { setThreats((previous) => [JSON.parse(event.data), ...previous].slice(0, 200)); } catch { /* Ignore malformed feed messages. */ } };
    ws.onerror = () => setConnectionStatus("error");
    ws.onclose = (event) => { setConnectionStatus("closed"); if (event.code === 1008) { logout(); return; } if (isUnmountingRef.current) return; const delay = Math.min(1000 * 2 ** reconnectAttemptRef.current, MAX_RECONNECT_DELAY_MS); reconnectAttemptRef.current += 1; reconnectTimeoutRef.current = setTimeout(connect, delay); };
  }, [logout, token]);

  useEffect(() => { isUnmountingRef.current = false; connect(); return () => { isUnmountingRef.current = true; clearTimeout(reconnectTimeoutRef.current); wsRef.current?.close(); }; }, [connect]);

  const channels = useMemo(() => ["All channels", ...new Set(threats.map((threat) => threat.platform))], [threats]);
  const filteredThreats = useMemo(() => threats.filter((threat) => channel === "All channels" || threat.platform === channel), [channel, threats]);
  const watchlistThreats = threats.filter((threat) => watchFilter === "Priority" ? threat.threat_level >= 4 : !threat.is_resolved);
  const feedPageCount = Math.max(1, Math.ceil(filteredThreats.length / PAGE_SIZE));
  const watchPageCount = Math.max(1, Math.ceil(watchlistThreats.length / PAGE_SIZE));
  const visibleThreats = filteredThreats.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);
  const visibleWatchlistThreats = watchlistThreats.slice((currentPage - 1) * PAGE_SIZE, currentPage * PAGE_SIZE);
  const selectedThreat = threats.find((threat) => threat.id === selectedId) || null;
  const criticalCount = threats.filter((threat) => threat.threat_level >= 4).length;
  const openCount = threats.filter((threat) => !threat.is_resolved).length;
  const resolvedCount = threats.length - openCount;
  const averagePanic = threats.length ? Math.round(threats.reduce((total, threat) => total + Number(threat.panic_score || 0), 0) / threats.length) : 0;
  const updateThreat = (updated) => setThreats((previous) => previous.map((threat) => threat.id === updated.id ? updated : threat));
  const connectionLabel = connectionStatus === "open" ? "Live connection" : "Reconnecting";

  useEffect(() => { setCurrentPage(1); }, [activeView, channel, watchFilter]);

  const Pagination = ({ pageCount }) => <div className="pagination"><span>Page {Math.min(currentPage, pageCount)} of {pageCount}</span><div><button disabled={currentPage <= 1} onClick={() => setCurrentPage((page) => Math.max(1, page - 1))}>Previous</button><button disabled={currentPage >= pageCount} onClick={() => setCurrentPage((page) => Math.min(pageCount, page + 1))}>Next</button></div></div>;

  const renderStats = () => <section className="stat-grid" aria-label="Threat summary"><article className="stat-card stat-primary"><span className="stat-label">Signals indexed</span><strong>{threats.length.toString().padStart(2, "0")}</strong><span className="stat-note">Across monitored channels</span></article><article className="stat-card"><span className="stat-label">Open incidents</span><strong>{openCount.toString().padStart(2, "0")}</strong><span className="stat-note">Requiring review</span></article><article className="stat-card"><span className="stat-label">Priority signals</span><strong>{criticalCount.toString().padStart(2, "0")}</strong><span className="stat-note">High or critical</span></article><article className="stat-card"><span className="stat-label">Mean panic score</span><strong>{averagePanic}<small> /100</small></strong><span className="stat-note">Current feed average</span></article></section>;

  const renderFeed = (items) => <div className="feed-panel"><div className="panel-heading"><div><p className="eyebrow">Incoming signals</p><h2>Latest intelligence</h2></div><label className="channel-select"><span>Channel</span><select value={channel} onChange={(event) => setChannel(event.target.value)}>{channels.map((item) => <option key={item}>{item}</option>)}</select></label></div>{items.length === 0 ? <div className="empty-state"><h3>No matching signals</h3><p>Try another channel or wait for the next ingestion event.</p></div> : <><div className="threat-table"><div className="table-head"><span>Signal</span><span>Source</span><span>Assessment</span><span>Received</span></div>{items.map((threat) => <ThreatRow key={threat.id} threat={threat} selected={selectedId === threat.id} onSelect={(item) => setSelectedId(item.id)} />)}</div><Pagination pageCount={feedPageCount} /></>}</div>;

  const renderSituationRoom = () => <><section className="analysis-hero"><div><p className="eyebrow">Operational analysis</p><h2>What needs attention now?</h2><p>Priority is determined by threat level, panic score, and whether a signal has been reviewed.</p></div><div className="analysis-callout"><strong>{criticalCount}</strong><span>priority signals open</span></div></section><section className="analysis-grid"><article className="analysis-card"><p className="eyebrow">Resolution progress</p><div className="progress-number"><strong>{threats.length ? Math.round((resolvedCount / threats.length) * 100) : 0}%</strong><span>reviewed</span></div><div className="progress-track"><span style={{ width: `${threats.length ? (resolvedCount / threats.length) * 100 : 0}%` }} /></div><p className="analysis-note">{resolvedCount} reviewed · {openCount} still open</p></article><article className="analysis-card"><p className="eyebrow">Channel volume</p>{channels.slice(1).map((item) => { const count = threats.filter((threat) => threat.platform === item).length; return <div className="channel-row" key={item}><span>{item}</span><div className="channel-bar"><i style={{ width: `${Math.max(8, (count / Math.max(threats.length, 1)) * 100)}%` }} /></div><strong>{count}</strong></div>; })}</article><article className="analysis-card"><p className="eyebrow">Risk mix</p>{[5, 4, 3, 2, 1].map((level) => <div className="mix-row" key={level}><span className={`legend-dot ${getSeverity(level).className}`} /><span>{getSeverity(level).label}</span><strong>{threats.filter((threat) => threat.threat_level === level).length}</strong></div>)}</article></section></>;

  const renderWatchlists = () => <section className="watchlist-layout"><div className="feed-panel"><div className="panel-heading"><div><p className="eyebrow">Saved review queue</p><h2>Watchlist signals</h2></div><div className="watch-tabs">{["Priority", "Open"].map((item) => <button className={watchFilter === item ? "active" : ""} onClick={() => setWatchFilter(item)} key={item}>{item}</button>)}</div></div><div className="watchlist-copy">Signals in this queue are selected for a second look by the operations team.</div>{visibleWatchlistThreats.map((threat) => <ThreatRow key={threat.id} threat={threat} selected={selectedId === threat.id} onSelect={(item) => setSelectedId(item.id)} />)}{watchlistThreats.length === 0 ? <div className="empty-state"><h3>Watchlist is clear</h3><p>No signals match this review filter.</p></div> : <Pagination pageCount={watchPageCount} />}</div><ThreatDetail threat={selectedThreat} apiBaseUrl={apiBaseUrl} token={token} onUpdated={updateThreat} /></section>;

  return <div className="console-shell"><aside className="sidebar"><div className="brand-lockup"><div className="brand-mark"><span /></div><div><p className="brand-name">OSNIT</p><p className="brand-caption">Operational intelligence</p></div></div><div className="sidebar-section-label">Workspace</div><nav className="main-nav" aria-label="Primary navigation">{VIEW_NAMES.map((item, index) => <button className={`nav-item ${activeView === item ? "active" : ""}`} key={item} onClick={() => setActiveView(item)}><span className="nav-glyph">{["◈", "⊞", "⌁"][index]}</span><span>{item}</span>{item === "Live feed" && <span className="nav-count">{threats.length}</span>}</button>)}</nav><div className="sidebar-section-label">System</div><div className="system-card"><div className="system-card-header"><span className="connection-mark" /><span>{connectionLabel}</span></div><p>Ingestion and alert channels are being monitored.</p><div className="system-line"><span>WebSocket</span><strong>{connectionStatus === "open" ? "ONLINE" : "PENDING"}</strong></div><div className="system-line"><span>Last sync</span><strong>{threats[0] ? formatTime(threats[0].timestamp) : "--:--"}</strong></div></div><div className="sidebar-footer"><div className="profile-chip"><div className="profile-avatar">{officer?.email?.[0]?.toUpperCase() || "O"}</div><div className="profile-copy"><strong>{officer?.email || "Officer"}</strong><span>Clearance L{officer?.clearanceLevel || 1}</span></div></div><button className="logout-button" onClick={logout} aria-label="Log out">Log out</button></div></aside><main className="main-panel"><header className="topbar"><div className="breadcrumb"><span>Workspace</span><strong>{activeView}</strong></div><div className="topbar-meta"><span className="date-stamp">{formatDate(new Date())}</span><span className="live-pill">{connectionLabel}</span></div></header><div className="content-wrap"><section className="page-heading"><div><p className="eyebrow">{activeView}</p><h1>{activeView === "Live feed" ? "Live threat feed" : activeView}</h1><p className="heading-copy">{activeView === "Live feed" ? "Review incoming intelligence and act on the signals that matter." : activeView === "Situation room" ? "A clear view of volume, risk, and operational follow-through." : "Keep priority signals close until they are fully reviewed."}</p></div></section>{activeView === "Live feed" && <>{renderStats()}<section className="feed-layout">{renderFeed(visibleThreats)}<ThreatDetail threat={selectedThreat} apiBaseUrl={apiBaseUrl} token={token} onUpdated={updateThreat} /></section></>}{activeView === "Situation room" && <>{renderStats()}{renderSituationRoom()}</>}{activeView === "Watchlists" && renderWatchlists()}</div></main></div>;
}
