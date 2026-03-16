import { useEffect, useState } from "react";
import API, { API_BASE_URL } from "../../api";
import "../../styles/CompanyHistory.css";

const getJobKey = (item) => String(item?.jobId || item?.jobTitle || "");

function CompanyHistory({ company }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedJobId, setSelectedJobId] = useState("all");

  useEffect(() => {
    if (!company) return;

    const fetchData = async () => {
      try {
        const data = await API.getCompanyHistory(company.companyId);
        setHistory(data || []);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [company]);

  const jobOptions = Array.from(
    history.reduce((jobsMap, item) => {
      const key = getJobKey(item);
      if (!key || jobsMap.has(key)) return jobsMap;

      jobsMap.set(key, {
        jobId: key,
        jobTitle: item.jobTitle || item.jobId || "Untitled Job",
      });
      return jobsMap;
    }, new Map())
  ).map(([, job]) => job);

  const isAllJobsSelected = selectedJobId === "all";
  const selectedJobKey = String(selectedJobId);

  const matchesSelectedJob = (item) => {
    if (isAllJobsSelected) return true;
    return getJobKey(item) === selectedJobKey;
  };

  const filteredHistory = history.filter(matchesSelectedJob);
  const filteredJobStats = Array.from(
    filteredHistory.reduce((jobsMap, item) => {
      const key = getJobKey(item);
      if (!key) return jobsMap;

      if (!jobsMap.has(key)) {
        jobsMap.set(key, {
          jobId: key,
          jobTitle: item.jobTitle || item.jobId || "Untitled Job",
          total: 0,
          selected: 0,
          rejected: 0,
        });
      }

      const stats = jobsMap.get(key);
      const status = (item.status || "unknown").toLowerCase();

      stats.total += 1;
      if (status === "selected") stats.selected += 1;
      if (status === "rejected") stats.rejected += 1;

      return jobsMap;
    }, new Map())
  ).map(([, stats]) => stats);

  const filteredLatestResumes = [...filteredHistory]
    .sort((a, b) => new Date(b.date) - new Date(a.date))
    .slice(0, 5);

  const resolveResumeUrl = (url) => {
    if (!url) return "";
    if (url.startsWith("http")) return url;
    return `${API_BASE_URL.replace(/\/api$/, "")}${url}`;
  };

  return (
    <div className="ch-wrapper">
      <h2 className="ch-main-title">Candidate History & Job Analytics</h2>

      {/* Job Filter */}
      <div className="ch-filter">
        <select value={selectedJobId} onChange={e => setSelectedJobId(e.target.value)}>
          <option value="all">All Jobs</option>
          {jobOptions.map(job => (
            <option key={job.jobId} value={job.jobId}>{job.jobTitle}</option>
          ))}
        </select>
      </div>

      {/* Job Stats */}
      <div className="ch-job-cards">
        {!loading && filteredJobStats.length > 0
          ? filteredJobStats.map((job, idx) => (
              <div key={idx} className="ch-job-card">
                <h3>{job.jobTitle}</h3>
                <p>Total: {job.total}</p>
                <p>Selected: {job.selected}</p>
                <p>Rejected: {job.rejected}</p>
              </div>
            ))
          : Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="ch-job-card placeholder"></div>
            ))
        }
      </div>

      {/* Latest Resumes */}
      <div className="ch-latest-resumes">
        <h3>Latest Resumes</h3>
        <div className="ch-resume-cards">
          {!loading && filteredLatestResumes.length > 0
            ? filteredLatestResumes.map((r, idx) => (
                <div key={idx} className="ch-resume-card">
                  <p><strong>Candidate:</strong> {r.candidateName}</p>
                  <p><strong>Job:</strong> {r.jobTitle}</p>
                  <p><strong>Email:</strong> {r.email}</p>
                  <p><strong>Score:</strong> {r.score ?? "-"}</p>
                  <p><strong>Rank:</strong> {r.rank ?? "-"}</p>
                  <a href={resolveResumeUrl(r.resumeUrl)} target="_blank" rel="noreferrer">Download</a>
                </div>
              ))
            : Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="ch-resume-card placeholder"></div>
              ))
          }
        </div>
      </div>

      {/* History Table */}
      <div className="ch-table-wrapper">
        <table className="ch-history-table">
          <thead>
            <tr>
              <th>Candidate</th>
              <th>Job</th>
              <th>Score</th>
              <th>Rank</th>
              <th>Status</th>
              <th>Date</th>
              <th>Resume</th>
            </tr>
          </thead>
          <tbody>
            {!loading && filteredHistory.length > 0
              ? filteredHistory.map((h, idx) => (
                  <tr key={idx}>
                    <td>{h.candidateName}</td>
                    <td>{h.jobTitle}</td>
                    <td>{h.score ?? "-"}</td>
                    <td>{h.rank ?? "-"}</td>
                    <td className={`ch-status-${(h.status || "unknown").toLowerCase()}`}>{h.status || "unknown"}</td>
                    <td>{h.date}</td>
                    <td>
                      {h.resumeUrl ? <a href={resolveResumeUrl(h.resumeUrl)} target="_blank" rel="noreferrer">Download</a> : "-"}
                    </td>
                  </tr>
                ))
              : (
                  <tr>
                    <td colSpan="7" className="ch-loading-row">Loading or no data available</td>
                  </tr>
                )
            }
          </tbody>
        </table>
      </div>
    </div>
  );
}

export default CompanyHistory;