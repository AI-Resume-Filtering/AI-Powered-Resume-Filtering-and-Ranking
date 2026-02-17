import { useState } from "react";
import API from "../../api";
import "../../styles/postjob.css";

function PostJob({ company }) {
  const [jobTitle, setJobTitle] = useState("");
  const [pdfFile, setPdfFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState("info");

  const handleSubmit = async () => {
    if (!jobTitle.trim()) {
      setMessageType("error");
      setMessage("Please enter job title");
      return;
    }

    if (!pdfFile) {
      setMessageType("error");
      setMessage("Please upload job description PDF");
      return;
    }

    if (!company || !company.companyId) {
      setMessageType("error");
      setMessage("Company information not found. Please login again.");
      return;
    }

    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("companyId", company.companyId);
      formData.append("jobTitle", jobTitle);
      formData.append("descriptionPdf", pdfFile);

      const data = await API.postJob(formData);

      if (data.success) {
        setMessageType("success");
        setMessage("Job posted successfully!");
        setJobTitle("");
        setPdfFile(null);
      } else {
        setMessageType("error");
        setMessage(data.message || "Failed to post job");
      }
    } catch (err) {
      console.error(err);
      setMessageType("error");
      setMessage("Error posting job. Make sure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="post-job-wrapper">
      <div className="card">
        <h2>Post Job</h2>

      {/* Job Title */}
      <input
        type="text"
        placeholder="Job Title"
        value={jobTitle}
        onChange={(e) => setJobTitle(e.target.value)}
      />

      {/* PDF Upload */}
      <label className="file-label">
        Upload Job Description (PDF)
      </label>

      <input
        type="file"
        accept="application/pdf"
        onChange={(e) => setPdfFile(e.target.files[0])}
      />

      {/* Show selected PDF */}
      {pdfFile && (
        <p className="file-name">
          Selected File: {pdfFile.name}
        </p>
      )}

        <button className="primary" onClick={handleSubmit} disabled={loading}>
          {loading ? "Posting..." : "Post Job"}
        </button>

        {message && (
          <div className={`status-msg ${messageType}`}>
            {message}
          </div>
        )}
      </div>
    </div>
  );
}

export default PostJob;