import { useState, useEffect } from "react";
import API from "../../api";
import "../../styles/delete.css";

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
        const data = await API.getCompanyJobs(company.companyId);
        setJobs(data || []);
        setError("");
      } catch (err) {
        console.error("Error fetching jobs:", err);
        setError("Failed to load jobs");
      }
    };

    fetchJobs();
  }, [company]);

  const handleDelete = async () => {
    if (!selectedJobId) {
      alert("Please select a job to delete");
      return;
    }

    const confirmDelete = window.confirm("Are you sure you want to delete this job?");
    if (!confirmDelete) return;

    setLoading(true);
    setError("");
    setMessage("");

    try {
      const data = await API.deleteJob(selectedJobId);

      if (data.success) {
        setMessage("Job deleted successfully!");
        // Remove from list
        setJobs(jobs.filter(job => job.jobId !== selectedJobId));
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
    <div className="delete-card">
      <h2>Delete Job Post</h2>

      {error && <div className="error-msg">{error}</div>}
      {message && <div className="success-msg">{message}</div>}

      {jobs.length === 0 ? (
        <p>No jobs posted yet</p>
      ) : (
        <>
          <label>Select Job to Delete:</label>
          <select
            value={selectedJobId}
            onChange={(e) => setSelectedJobId(e.target.value)}
          >
            <option value="">-- Choose a job --</option>
            {jobs.map(job => (
              <option key={job.jobId} value={job.jobId}>
                {job.title}
              </option>
            ))}
          </select>

          {selectedJobId && (
            <div className="job-details">
              <p>
                <strong>Selected:</strong> {jobs.find(j => j.jobId === selectedJobId)?.title}
              </p>
              <p>
                <strong>Applications:</strong> {jobs.find(j => j.jobId === selectedJobId)?.totalApplications || 0}
              </p>
            </div>
          )}

          <button
            className="primary delete-btn"
            onClick={handleDelete}
            disabled={loading || !selectedJobId}
          >
            {loading ? "Deleting..." : "Delete Job Post"}
          </button>
        </>
      )}
    </div>
  );
}

export default DeleteJob;