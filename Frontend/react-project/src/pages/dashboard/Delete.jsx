import { useState, useEffect } from "react";
import API from "../../api";
import "../../styles/DeleteJob.css";

function DeleteJob({ company }) {
  const [jobs, setJobs] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  // Fetch company jobs on component load
  useEffect(() => {
    if (!company) return;

    const fetchJobs = async () => {
      try {
        const response = await API.getCompanyJobs(company.companyId);
        if (response.success && Array.isArray(response.data)) {
          setJobs(response.data);
          setError("");
        } else {
          setError(response.message || "Failed to load jobs");
          setJobs([]);
        }
      } catch (err) {
        console.error("Error fetching jobs:", err);
        setError("Failed to load jobs");
        setJobs([]);
      }
    };

    fetchJobs();
  }, [company]);

  const handleDelete = async () => {
    if (!selectedJobId) {
      alert("Please select a job to delete");
      return;
    }

    const confirmDelete = window.confirm(
      "Are you sure you want to delete this job?"
    );
    if (!confirmDelete) return;

    setLoading(true);
    setError("");
    setMessage("");

    try {
      const data = await API.deleteJob(selectedJobId);

      if (data.success) {
        setMessage("Job deleted successfully!");
        setJobs(jobs.filter((job) => job.jobId !== selectedJobId));
        setSelectedJobId("");
      } else {
        setError(data.message || "Failed to delete job");
      }
    } catch (err) {
      console.error("Error deleting job:", err);
      setError("Error deleting job. Make sure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dj-wrapper">

      {/* Delete Card */}
      <div className="dj-card">
        <h2 className="dj-title">Delete Job Post</h2>

        {error && <div className="dj-error-msg">{error}</div>}
        {message && <div className="dj-success-msg">{message}</div>}

        {jobs.length === 0 ? (
          <p className="dj-no-job">No jobs posted yet</p>
        ) : (
          <>
            <label className="dj-label">Select Job to Delete:</label>
            <select
              className="dj-select"
              value={selectedJobId}
              onChange={(e) => setSelectedJobId(e.target.value)}
            >
              <option value="">-- Choose a job --</option>
              {jobs.map((job) => (
                <option key={job.jobId} value={job.jobId}>
                  {job.title}
                </option>
              ))}
            </select>

            {selectedJobId && (
              <div className="dj-job-details">
                <p>
                  <strong>Selected:</strong>{" "}
                  {jobs.find((j) => j.jobId === selectedJobId)?.title}
                </p>
                <p>
                  <strong>Applications:</strong>{" "}
                  {jobs.find((j) => j.jobId === selectedJobId)?.totalApplications || 0}
                </p>
              </div>
            )}

            <button
              className="dj-btn-primary"
              onClick={handleDelete}
              disabled={loading || !selectedJobId}
            >
              {loading ? "Deleting..." : "Delete Job Post"}
            </button>
          </>
        )}
      </div>

      {/* Instructions / Accepted File Type */}
      <div className="dj-info-panel">
        <h3 className="dj-info-title">📄 Accepted File Type</h3>
        <p className="dj-info-text">Only PDF files are accepted for job description uploads.</p>

        <h3 className="dj-info-title">📌 Instructions</h3>
        <p className="dj-info-text">
          1. Select the job you want to delete from the dropdown.<br/>
          2. Ensure you have no ongoing applications before deleting.<br/>
          3. Click the "Delete Job Post" button to remove the job permanently.
        </p>
      </div>

    </div>
  );
}

export default DeleteJob;