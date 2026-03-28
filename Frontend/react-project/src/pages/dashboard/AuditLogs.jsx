import { useState, useCallback } from "react";
import API from "../../api";
import "../../styles/AuditLogs.css";

const OUTCOMES = [
  "", "success", "email-sent", "email-send-failed", "rate-limited",
  "token-invalid-or-expired", "token-not-found", "account-not-found",
  "password-reused", "account-locked", "password-policy-failed",
  "password-mismatch", "missing-token",
];

const EVENTS = [
  "", "password_reset_requested", "password_reset_completed",
];

function AuditLogs() {
  const [adminKey, setAdminKey] = useState("");
  const [keyEntered, setKeyEntered] = useState(false);
  const [keyError, setKeyError] = useState("");

  // filters
  const [dateFrom, setDateFrom] = useState("");
  const [dateTo, setDateTo]     = useState("");
  const [ip, setIp]             = useState("");
  const [email, setEmail]       = useState("");
  const [outcome, setOutcome]   = useState("");
  const [event, setEvent]       = useState("");

  // results + pagination
  const [logs, setLogs]         = useState([]);
  const [total, setTotal]       = useState(0);
  const [page, setPage]         = useState(1);
  const [limit]                 = useState(50);
  const [loading, setLoading]   = useState(false);
  const [error, setError]       = useState("");

  // metrics
  const [metrics, setMetrics]   = useState(null);
  const [metricsLoading, setMetricsLoading] = useState(false);

  const handleKeySubmit = () => {
    if (!adminKey.trim()) {
      setKeyError("Admin key is required.");
      return;
    }
    setKeyError("");
    setKeyEntered(true);
    fetchMetrics(adminKey.trim());
  };

  const fetchLogs = useCallback(async (pageNum = 1, key = adminKey) => {
    setLoading(true);
    setError("");
    try {
      const res = await API.getAuditLogs(
        { dateFrom: dateFrom || undefined, dateTo: dateTo || undefined, ip: ip || undefined,
          email: email || undefined, outcome: outcome || undefined, event: event || undefined },
        pageNum, limit, key.trim(),
      );
      if (!res.success) {
        if (res.status === 403) {
          setKeyEntered(false);
          setKeyError("Invalid admin key.");
          return;
        }
        setError(res.message || "Failed to load audit logs.");
        return;
      }
      setLogs(res.logs || []);
      setTotal(res.total || 0);
      setPage(pageNum);
    } catch {
      setError("Unable to reach the server.");
    } finally {
      setLoading(false);
    }
  }, [dateFrom, dateTo, ip, email, outcome, event, limit, adminKey]);

  const fetchMetrics = async (key) => {
    setMetricsLoading(true);
    try {
      const res = await API.getAdminMetrics(key);
      if (res.success) setMetrics(res.metrics);
    } catch { /* silent */ } finally {
      setMetricsLoading(false);
    }
  };

  const handleSearch = () => {
    fetchLogs(1, adminKey);
  };

  const handleExport = async () => {
    const filters = new URLSearchParams();
    if (dateFrom)  filters.set("dateFrom", dateFrom);
    if (dateTo)    filters.set("dateTo", dateTo);
    if (ip)        filters.set("ip", ip);
    if (email)     filters.set("email", email);
    if (outcome)   filters.set("outcome", outcome);
    if (event)     filters.set("event", event);

    const url = `${import.meta.env.VITE_API_BASE_URL || "/api"}/admin/audit-logs/export?${filters}`;
    const a = document.createElement("a");
    a.href = url;
    a.download = `audit_logs_${new Date().toISOString().slice(0,10)}.csv`;
    // Attach admin key via a fetch-download approach
    try {
      const resp = await fetch(url, { headers: { "X-Admin-Key": adminKey.trim() } });
      if (!resp.ok) { alert("Export failed — check admin key."); return; }
      const blob = await resp.blob();
      const blobUrl = URL.createObjectURL(blob);
      a.href = blobUrl;
      document.body.appendChild(a); a.click(); document.body.removeChild(a);
      URL.revokeObjectURL(blobUrl);
    } catch { alert("Export request failed."); }
  };

  const handleCleanup = async () => {
    if (!window.confirm("Delete old records per the configured TTL? This cannot be undone.")) return;
    try {
      const res = await API.adminCleanup(adminKey.trim());
      if (res.success) {
        const d = res.deleted;
        alert(`Cleanup: ${d.deletedAuditLogs} audit logs, ${d.deletedRateLimitRecords} rate-limit buckets, ${d.deletedEmailEvents} email events deleted.`);
        fetchLogs(1, adminKey);
        fetchMetrics(adminKey);
      } else {
        alert(res.message || "Cleanup failed.");
      }
    } catch { alert("Cleanup request failed."); }
  };

  const totalPages = Math.max(1, Math.ceil(total / limit));

  const outcomeClass = (o) => {
    if (!o) return "";
    if (o === "success" || o === "email-sent") return "outcome-success";
    if (o.includes("rate-limited") || o.includes("locked")) return "outcome-warn";
    return "outcome-fail";
  };

  // ── admin key gate ────────────────────────────────────────────────────────
  if (!keyEntered) {
    return (
      <div className="auditlogs-gate">
        <div className="auditlogs-gate-card">
          <h2>🔐 Admin Access</h2>
          <p>Enter your admin API key to access audit logs and security metrics.</p>
          <input
            type="password"
            placeholder="Admin API key"
            value={adminKey}
            onChange={e => setAdminKey(e.target.value)}
            onKeyDown={e => e.key === "Enter" && handleKeySubmit()}
          />
          {keyError && <p className="auditlogs-error">{keyError}</p>}
          <button className="al-btn al-btn-primary" onClick={handleKeySubmit}>
            Unlock Admin Panel
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="auditlogs-container">
      <div className="auditlogs-header">
        <h2>🔍 Audit Logs</h2>
        <div className="auditlogs-header-actions">
          <button className="al-btn al-btn-sm" onClick={() => fetchMetrics(adminKey)} disabled={metricsLoading}>
            {metricsLoading ? "Loading…" : "↻ Refresh Metrics"}
          </button>
          <button className="al-btn al-btn-danger al-btn-sm" onClick={() => { setKeyEntered(false); setAdminKey(""); setLogs([]); setMetrics(null); }}>
            Lock
          </button>
        </div>
      </div>

      {/* ── metrics strip ─────────────────────────────────────────────── */}
      {metrics && (
        <div className="auditlogs-metrics">
          <div className="al-metric"><span>{metrics.companies?.total ?? "–"}</span><label>Companies</label></div>
          <div className="al-metric"><span>{metrics.applications?.total ?? "–"}</span><label>Applications</label></div>
          <div className="al-metric accent-green"><span>{metrics.applications?.selected ?? "–"}</span><label>Selected</label></div>
          <div className="al-metric accent-red"><span>{metrics.applications?.rejected ?? "–"}</span><label>Rejected</label></div>
          <div className="al-metric"><span>{metrics.security?.auditLogs24h ?? "–"}</span><label>Audits (24 h)</label></div>
          <div className="al-metric accent-yellow"><span>{metrics.security?.rateLimitHits24h ?? "–"}</span><label>Rate-limit hits</label></div>
          <div className="al-metric accent-red"><span>{metrics.security?.failedPasswordResets24h ?? "–"}</span><label>Failed resets (24 h)</label></div>
          <div className="al-metric accent-green"><span>{metrics.security?.successfulPasswordResets24h ?? "–"}</span><label>Success resets (24 h)</label></div>
        </div>
      )}

      {/* ── filter bar ────────────────────────────────────────────────── */}
      <div className="auditlogs-filters">
        <div className="al-filter-row">
          <div className="al-field">
            <label>From date</label>
            <input type="date" value={dateFrom} onChange={e => setDateFrom(e.target.value)} />
          </div>
          <div className="al-field">
            <label>To date</label>
            <input type="date" value={dateTo} onChange={e => setDateTo(e.target.value)} />
          </div>
          <div className="al-field">
            <label>IP address</label>
            <input type="text" placeholder="e.g. 192.168." value={ip} onChange={e => setIp(e.target.value)} />
          </div>
          <div className="al-field">
            <label>Email (masked)</label>
            <input type="text" placeholder="e.g. te**@" value={email} onChange={e => setEmail(e.target.value)} />
          </div>
          <div className="al-field">
            <label>Event</label>
            <select value={event} onChange={e => setEvent(e.target.value)}>
              {EVENTS.map(v => <option key={v} value={v}>{v || "— any —"}</option>)}
            </select>
          </div>
          <div className="al-field">
            <label>Outcome</label>
            <select value={outcome} onChange={e => setOutcome(e.target.value)}>
              {OUTCOMES.map(v => <option key={v} value={v}>{v || "— any —"}</option>)}
            </select>
          </div>
        </div>
        <div className="al-filter-actions">
          <button className="al-btn al-btn-primary" onClick={handleSearch} disabled={loading}>
            {loading ? "Searching…" : "Search"}
          </button>
          <button className="al-btn" onClick={handleExport}>Export CSV</button>
          <button className="al-btn al-btn-danger" onClick={handleCleanup}>Cleanup Old Records</button>
        </div>
      </div>

      {/* ── error ─────────────────────────────────────────────────────── */}
      {error && <p className="auditlogs-error">{error}</p>}

      {/* ── results ───────────────────────────────────────────────────── */}
      <div className="auditlogs-results-header">
        <span>{total} result{total !== 1 ? "s" : ""}</span>
        <span>Page {page} / {totalPages}</span>
      </div>

      <div className="auditlogs-table-wrapper">
        <table className="auditlogs-table">
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>Event</th>
              <th>Outcome</th>
              <th>Email</th>
              <th>IP Address</th>
              <th>User Agent</th>
              <th>Metadata</th>
            </tr>
          </thead>
          <tbody>
            {logs.length === 0 && !loading && (
              <tr><td colSpan={7} className="al-empty">No records found. Run a search above.</td></tr>
            )}
            {logs.map((log, i) => (
              <tr key={i}>
                <td className="al-mono al-nowrap">{(log.createdAt || "").slice(0, 19).replace("T", " ")}</td>
                <td><span className="al-tag">{log.event || "–"}</span></td>
                <td><span className={`al-badge ${outcomeClass(log.outcome)}`}>{log.outcome || "–"}</span></td>
                <td className="al-mono">{log.emailMasked || "–"}</td>
                <td className="al-mono al-nowrap">{log.ipAddress || "–"}</td>
                <td className="al-ua" title={log.userAgent}>{(log.userAgent || "–").slice(0, 48)}</td>
                <td className="al-meta">
                  {log.metadata && Object.keys(log.metadata).length > 0
                    ? Object.entries(log.metadata).map(([k, v]) => (
                        <span key={k} className="al-meta-item"><b>{k}:</b> {String(v)}</span>
                      ))
                    : "–"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* ── pagination ────────────────────────────────────────────────── */}
      <div className="auditlogs-pagination">
        <button className="al-btn al-btn-sm" onClick={() => fetchLogs(page - 1)} disabled={page <= 1 || loading}>
          ← Prev
        </button>
        <span>{page} / {totalPages}</span>
        <button className="al-btn al-btn-sm" onClick={() => fetchLogs(page + 1)} disabled={page >= totalPages || loading}>
          Next →
        </button>
      </div>
    </div>
  );
}

export default AuditLogs;
