import { useEffect, useState } from "react";
import API, { API_BASE_URL } from "../../api";
import "../../styles/history.css";

function History({ company }) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [jobStats, setJobStats] = useState([]);
  const [latestResumes, setLatestResumes] = useState([]);
  const [selectedJobId, setSelectedJobId] = useState("all");

  useEffect(() => {
    if (!company) return;

    API.getCompanyHistory(company.companyId)
      .then(data => {
        setHistory(data || []);

        const stats = [];
        const jobsMap = {};

        data.forEach(item => {
          const key = item.jobId || item.jobTitle;
          if (!jobsMap[key]) {
            jobsMap[key] = {
              jobId: item.jobId,
              jobTitle: item.jobTitle,
              total: 0,
              selected: 0,
              rejected: 0,
            };
          }

          jobsMap[key].total += 1;
          if (item.status.toLowerCase() === "selected")
            jobsMap[key].selected += 1;
          if (item.status.toLowerCase() === "rejected")
            jobsMap[key].rejected += 1;
        });

        for (let job in jobsMap) stats.push(jobsMap[job]);
        setJobStats(stats);

        const sortedByDate = [...data].sort(
          (a, b) => new Date(b.date) - new Date(a.date)
        );
        setLatestResumes(sortedByDate.slice(0, 5));

        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [company]);

  if (!company)
    return <div className="empty-state">Company not found</div>;

  const jobOptions = Array.from(
    new Map(
      history
        .filter(h => h.jobId && h.jobTitle)
        .map(h => [h.jobId, h.jobTitle])
    )
  ).map(([jobId, jobTitle]) => ({ jobId, jobTitle }));

  const filteredHistory = selectedJobId === "all"
    ? history
    : history.filter(h => h.jobId === selectedJobId);

  const sortedHistory = [...filteredHistory].sort((a, b) => {
    const rankA = a.rank ?? Number.POSITIVE_INFINITY;
    const rankB = b.rank ?? Number.POSITIVE_INFINITY;
    if (rankA !== rankB) return rankA - rankB;
    const scoreA = a.score ?? Number.NEGATIVE_INFINITY;
    const scoreB = b.score ?? Number.NEGATIVE_INFINITY;
    return scoreB - scoreA;
  });

  const filteredStats = selectedJobId === "all"
    ? jobStats
    : jobStats.filter(stat => stat.jobId === selectedJobId);

  const filteredLatest = selectedJobId === "all"
    ? latestResumes
    : latestResumes.filter(r => r.jobId === selectedJobId);

  const resolveResumeUrl = (url) => {
    if (!url) return "";
    if (url.startsWith("http")) return url;
    const base = API_BASE_URL.replace(/\/api$/, "");
    return `${base}${url}`;
  };

  return (
    <div className="history-wrapper">
      <div className="history-header">
        <h2 className="history-title">Candidate History & Job Analytics</h2>
        <select
          value={selectedJobId}
          onChange={(e) => setSelectedJobId(e.target.value)}
        >
          <option value="all">All Jobs</option>
          {jobOptions.map(job => (
            <option key={job.jobId} value={job.jobId}>
              {job.jobTitle}
            </option>
          ))}
        </select>
      </div>

      {loading && <div className="empty-state">Loading...</div>}

      {/* Job Analytics Cards */}
      {!loading && filteredStats.length > 0 && (
        <div className="job-cards">
          {filteredStats.map((job, i) => (
            <div key={i} className="job-card">
              <h3>{job.jobTitle}</h3>
              <p>Total Applications: {job.total}</p>
              <p>Selected: {job.selected}</p>
              <p>Rejected: {job.rejected}</p>
            </div>
          ))}
        </div>
      )}

      {/* Latest 5 Resumes Uploaded */}
      {!loading && filteredLatest.length > 0 && (
        <div className="latest-resumes">
          <h3>Latest Resumes Uploaded</h3>
          <div className="resume-cards">
            {filteredLatest.map((r, idx) => (
              <div key={idx} className="resume-card">
                <p><strong>Candidate:</strong> {r.candidateName}</p>
                <p><strong>Job:</strong> {r.jobTitle}</p>
                <p><strong>Email:</strong> {r.email}</p>
                <p><strong>Score:</strong> {r.score ?? "-"}</p>
                <p><strong>Rank:</strong> {r.rank ?? "-"}</p>
                <a href={resolveResumeUrl(r.resumeUrl)} target="_blank" rel="noreferrer">Download</a>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Full History Table */}
      {!loading && sortedHistory.length > 0 && (
        <div className="table-wrapper">
          <table className="history-table">
            <thead>
              <tr>
                <th>Candidate Name</th>
                <th>Job Title</th>
                <th>Score</th>
                <th>Rank</th>
                <th>Status</th>
                <th>Date</th>
                <th>Resume</th>
              </tr>
            </thead>
            <tbody>
              {sortedHistory.map((h, idx) => (
                <tr key={idx}>
                  <td>{h.candidateName}</td>
                  <td>{h.jobTitle}</td>
                  <td>{h.score ?? "-"}</td>
                  <td>{h.rank ?? "-"}</td>
                  <td className={h.status.toLowerCase()}>{h.status}</td>
                  <td>{h.date}</td>
                  <td>
                    {h.resumeUrl ? (
                      <a href={resolveResumeUrl(h.resumeUrl)} target="_blank" rel="noreferrer">
                        Download
                      </a>
                    ) : (
                      "-"
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {!loading && sortedHistory.length === 0 && (
        <div className="empty-state">
          <p>No history available</p>
          <span>Data not loaded yet</span>
        </div>
      )}
    </div>
  );
}

export default History;