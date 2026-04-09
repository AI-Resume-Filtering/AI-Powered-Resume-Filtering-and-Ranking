import { useState, useEffect, useRef } from "react";
import API from "../../api";
import { useBackgroundTasks } from "../../context/BackgroundTasksContext";
import "../../styles/EmailTemplate.css";

const PLACEHOLDERS = [
  { token: "{candidateName}", desc: "Candidate's full name" },
  { token: "{jobTitle}",      desc: "Job position title" },
  { token: "{companyName}",   desc: "Your company name" },
  { token: "{score}",         desc: "AI match score (0–100)" },
  { token: "{contactEmail}",  desc: "Your company contact email" },
];

function EmailTemplate({ company }) {
  const [subject, setSubject]   = useState("");
  const [body, setBody]         = useState("");
  const [loading, setLoading]   = useState(true);
  const [saving, setSaving]     = useState(false);
  const [message, setMessage]   = useState("");
  const [msgType, setMsgType]   = useState("info");
  const [preview, setPreview]   = useState(false);
  const mountedRef = useRef(true);
  const { runTask } = useBackgroundTasks();

  // Load existing template on mount
  useEffect(() => {
    mountedRef.current = true;
    if (!company?.companyId) return;
    API.getEmailTemplate(company.companyId)
      .then((data) => {
        if (data.success && data.template) {
          setSubject(data.template.subject || "");
          setBody(data.template.body || "");
        }
      })
      .catch(() => {
        if (mountedRef.current) setMessage("Could not load saved template.");
      })
      .finally(() => {
        if (mountedRef.current) setLoading(false);
      });

    return () => {
      mountedRef.current = false;
    };
  }, [company]);

  const handleSave = async () => {
    if (!subject.trim() || !body.trim()) {
      setMsgType("error");
      setMessage("Subject and message body are required.");
      return;
    }
    setSaving(true);
    setMessage("");
    try {
      const { promise } = runTask(
        {
          type: "email-template-save",
          title: "Saving email template",
          message: "Updating selection notification template...",
          resume: {
            kind: "api-call",
            action: "saveEmailTemplate",
            payload: {
              companyId: company.companyId,
              subject,
              body,
            },
            successMessage: "Email template saved",
          },
        },
        async ({ update }) => {
          const data = await API.saveEmailTemplate(company.companyId, subject, body);
          if (!data?.success) {
            throw new Error(data?.message || "Failed to save template.");
          }
          update({ message: "Email template saved" });
          return data;
        }
      );

      const data = await promise;

      if (!mountedRef.current) {
        return;
      }

      if (data.success) {
        setMsgType("success");
        setMessage("✅ Email template saved! Selected candidates will now receive this message.");
      } else {
        setMsgType("error");
        setMessage(data.message || "Failed to save template.");
      }
    } catch (error) {
      if (mountedRef.current) {
        setMsgType("error");
        setMessage(error?.message || "Network error. Make sure the backend is running.");
      }
    } finally {
      if (mountedRef.current) {
        setSaving(false);
      }
    }
  };

  const insertToken = (token) => {
    setBody((prev) => prev + token);
  };

  // Generate a preview with sample values
  const previewSubject = subject
    .replace("{candidateName}", "Rahul Sharma")
    .replace("{jobTitle}", "Software Engineer")
    .replace("{companyName}", company?.name || "Acme Corp")
    .replace("{score}", "87.5")
    .replace("{contactEmail}", company?.email || "hr@acme.com");

  const previewBody = body
    .replace("{candidateName}", "Rahul Sharma")
    .replace("{jobTitle}", "Software Engineer")
    .replace("{companyName}", company?.name || "Acme Corp")
    .replace("{score}", "87.5")
    .replace("{contactEmail}", company?.email || "hr@acme.com")
    .replace("{contactLine}", `For any enquiries, contact us at: ${company?.email || "hr@acme.com"}\n\n`);

  if (loading) {
    return <div className="et-wrapper"><p className="et-loading">Loading template…</p></div>;
  }

  return (
    <div className="et-wrapper">
      <div className="et-card">
        <h2 className="et-title">✉️ Selection Notification Email</h2>
        <p className="et-subtitle">
          This message is automatically sent to every candidate who is <strong>selected</strong> by
          the AI. Use the placeholders below to personalise it.
        </p>

        {/* Placeholder chips */}
        <div className="et-placeholders">
          <span className="et-ph-label">Insert placeholder →</span>
          {PLACEHOLDERS.map(({ token, desc }) => (
            <button
              key={token}
              className="et-chip"
              title={desc}
              onClick={() => insertToken(token)}
              type="button"
            >
              {token}
            </button>
          ))}
        </div>

        {/* Subject */}
        <label className="et-label">Email Subject</label>
        <input
          className="et-input"
          type="text"
          placeholder="e.g. Congratulations! You have been shortlisted for {jobTitle}"
          value={subject}
          onChange={(e) => setSubject(e.target.value)}
          maxLength={300}
        />
        <span className="et-charcount">{subject.length}/300</span>

        {/* Body */}
        <label className="et-label">Email Body</label>
        <textarea
          className="et-textarea"
          placeholder={
            "Dear {candidateName},\n\nYou have been shortlisted for {jobTitle} at {companyName}.\n\n..."
          }
          value={body}
          onChange={(e) => setBody(e.target.value)}
          rows={14}
          maxLength={5000}
        />
        <span className="et-charcount">{body.length}/5000</span>

        {/* Action row */}
        <div className="et-actions">
          <button
            className="et-btn-preview"
            type="button"
            onClick={() => setPreview((p) => !p)}
          >
            {preview ? "Hide Preview" : "👁 Preview"}
          </button>
          <button
            className="et-btn-save"
            type="button"
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? "Saving…" : "💾 Save Template"}
          </button>
        </div>

        {message && (
          <p className={`et-message et-message--${msgType}`}>{message}</p>
        )}

        {/* Live preview panel */}
        {preview && (
          <div className="et-preview-box">
            <h4 className="et-preview-title">📧 Preview (sample values)</h4>
            <div className="et-preview-subject">
              <strong>Subject:</strong> {previewSubject || "(empty)"}
            </div>
            <pre className="et-preview-body">{previewBody || "(empty)"}</pre>
          </div>
        )}
      </div>
    </div>
  );
}

export default EmailTemplate;
