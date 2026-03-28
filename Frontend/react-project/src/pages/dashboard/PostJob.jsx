import { useState } from "react";
import API from "../../api";
import "../../styles/PostJob.css";

function PostJob({ company, onJobPosted }) {

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
        // Trigger refresh in parent component
        if (onJobPosted) {
          onJobPosted();
        }
        // Also dispatch event for Home component listener
        window.dispatchEvent(new Event("jobPosted"));
      } 
      else {
        setMessageType("error");
        setMessage(data.message || "Failed to post job");
      }

    } 
    catch (err) {
      console.error(err);
      setMessageType("error");
      setMessage("Error posting job. Make sure backend is running.");
    } 
    finally {
      setLoading(false);
    }

  };

  return (

    <div className="pj-wrapper">

      {/* POST JOB CARD */}

      <div className="pj-card">

        <h2 className="pj-title">Post Job</h2>

        <input
          className="pj-input"
          type="text"
          placeholder="Job Title"
          value={jobTitle}
          onChange={(e) => setJobTitle(e.target.value)}
        />

        <label className="pj-file-label">
          Upload Job Description (PDF)
        </label>

        <div
          className="pj-upload-box"
          onClick={() => document.getElementById("pjFileInput").click()}
        >

          <p className="pj-upload-text">
            Drag & Drop PDF Here
          </p>

          <p className="pj-upload-subtext">
            or click to upload
          </p>

          <input
            id="pjFileInput"
            className="pj-hidden-input"
            type="file"
            accept="application/pdf"
            onChange={(e) => setPdfFile(e.target.files[0])}
          />

        </div>

        {pdfFile && (
          <p className="pj-file-name">
            📄 {pdfFile.name}
          </p>
        )}

        <button
          className="pj-btn-primary"
          onClick={handleSubmit}
          disabled={loading}
        >
          {loading ? "Posting..." : "Post Job"}
        </button>

        {message && (
          <div className={`pj-status-msg pj-${messageType}`}>
            {message}
          </div>
        )}

      </div>


      {/* INFO PANEL */}

      <div className="pj-info-panel">

        <h3 className="pj-info-title">📄 Accepted File Type</h3>

        <p className="pj-info-text">
          Only PDF files are allowed for job description upload.
        </p>

        <h3 className="pj-info-title">📌 Instructions</h3>

        <ul className="pj-info-list">
          <li>Use a clear job title</li>
          <li>Upload detailed job description</li>
          <li>Include required skills</li>
          <li>Provide company information</li>
        </ul>

      </div>

    </div>

  );
}

export default PostJob;