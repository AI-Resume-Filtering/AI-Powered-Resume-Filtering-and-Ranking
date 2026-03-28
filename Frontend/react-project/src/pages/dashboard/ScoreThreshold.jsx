import { useEffect, useState } from "react";
import API from "../../api";
import "../../styles/dashboard.css";

function normalizeErrorMessage(data, fallback) {
  const raw = (data?.message || "").toLowerCase();
  if (raw.includes("endpoint not found")) {
    return "Backend update not loaded yet. Restart Backend (python run.py) and try again.";
  }
  if (raw.includes("unauthorized") || data?.status === 401) {
    return "Session expired. Please log in again.";
  }
  return data?.message || fallback;
}

function ScoreThreshold({ company }) {
  const [threshold, setThreshold] = useState("70");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    if (!company?.companyId) return;

    API.getCompanyScoreThreshold(company.companyId)
      .then((data) => {
        if (data?.success) {
          setThreshold(String(data.scoreThreshold ?? 70));
        } else {
          setIsError(true);
          setMessage(normalizeErrorMessage(data, "Could not load score threshold."));
        }
      })
      .catch(() => {
        setIsError(true);
        setMessage("Network error while loading threshold.");
      })
      .finally(() => setLoading(false));
  }, [company]);

  const handleSave = async () => {
    setMessage("");
    setIsError(false);

    const numeric = Number(threshold);
    if (!Number.isFinite(numeric) || numeric < 0 || numeric > 100) {
      setIsError(true);
      setMessage("Threshold must be a number between 0 and 100.");
      return;
    }

    setSaving(true);
    try {
      const data = await API.saveCompanyScoreThreshold(company.companyId, numeric);
      if (data?.success) {
        setThreshold(String(data.scoreThreshold));
        setMessage("Threshold saved successfully.");

        const existing = JSON.parse(localStorage.getItem("company") || "{}");
        localStorage.setItem(
          "company",
          JSON.stringify({ ...existing, scoreThreshold: data.scoreThreshold })
        );
      } else {
        setIsError(true);
        setMessage(normalizeErrorMessage(data, "Could not save threshold."));
      }
    } catch {
      setIsError(true);
      setMessage("Network error while saving threshold.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="home-container">
        <h2>Score Threshold</h2>
        <p>Loading threshold...</p>
      </div>
    );
  }

  return (
    <div className="home-container">
      <h2>Score Threshold Settings</h2>
      <div className="table-box score-threshold-card" style={{ maxWidth: 520 }}>
        <h3>Candidate Selection Threshold</h3>
        <p style={{ color: "#cbd5e1", marginBottom: 16 }}>
          Set the minimum AI score required for candidates to be marked as Selected.
        </p>

        <label htmlFor="score-threshold" style={{ display: "block", marginBottom: 8, color: "#e2e8f0" }}>
          Threshold (0-100)
        </label>
        <input
          id="score-threshold"
          type="number"
          min="0"
          max="100"
          step="0.1"
          value={threshold}
          onChange={(e) => setThreshold(e.target.value)}
          className="score-threshold-input"
        />

        <button
          type="button"
          className="score-threshold-save-btn"
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? "Saving..." : "Save Threshold"}
        </button>

        {message ? (
          <p style={{ marginTop: 14, color: isError ? "#f87171" : "#4ade80" }}>{message}</p>
        ) : null}
      </div>
    </div>
  );
}

export default ScoreThreshold;
