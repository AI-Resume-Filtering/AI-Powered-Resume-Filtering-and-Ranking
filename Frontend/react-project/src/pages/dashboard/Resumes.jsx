import { useEffect, useState } from "react";
import API, { API_BASE_URL } from "../../api";
import "../../styles/table.css";
import "../../styles/resumes.css";

function Resumes({ company, setActive }) {
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedJobId, setSelectedJobId] = useState("all");

  useEffect(() => {
    if (!company) return;

    API.getCompanyResumes(company.companyId)
      .then(data => setResumes(data || []))
      .catch(err => console.error(err))
      .finally(() => setLoading(false));
  }, [company]);

  const jobOptions = Array.from(
    new Map(
      resumes
        .filter(r => r.jobId && r.jobTitle)
        .map(r => [r.jobId, r.jobTitle])
    )
  ).map(([jobId, jobTitle]) => ({ jobId, jobTitle }));

  const visibleResumes = selectedJobId === "all"
    ? resumes
    : resumes.filter(r => r.jobId === selectedJobId);

  const sortedResumes = [...visibleResumes].sort((a, b) => {
    const rankA = a.rank ?? Number.POSITIVE_INFINITY;
    const rankB = b.rank ?? Number.POSITIVE_INFINITY;
    if (rankA !== rankB) return rankA - rankB;
    const scoreA = a.score ?? Number.NEGATIVE_INFINITY;
    const scoreB = b.score ?? Number.NEGATIVE_INFINITY;
    return scoreB - scoreA;
  });

  const resolveResumeUrl = (url) => {
    if (!url) return "";
    if (url.startsWith("http")) return url;
    const base = API_BASE_URL.replace(/\/api$/, "");
    return `${base}${url}`;
  };

  return (
    <div className="section">
      <div className="section-header">
        <h2>Uploaded Resumes</h2>
        <div className="section-actions">
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
          <button
            type="button"
            className="secondary"
            onClick={() => setActive && setActive("home")}
          >
            Back to Dashboard
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="table-wrapper">
        <table className="history-table">
          <thead>
            <tr>
              <th>Candidate Name</th>
              <th>Resume Name</th>
              <th>Email</th>
              <th>Job Applied</th>
              <th>Score</th>
              <th>Rank</th>
              <th>Status</th>
              <th>View Resume</th>
            </tr>
          </thead>
          <tbody>
            {/* Loading state */}
            {loading && (
              <tr>
                <td colSpan="8">Loading...</td>
              </tr>
            )}

            {/* No data */}
            {!loading && visibleResumes.length === 0 && (
              <tr>
                <td colSpan="8">No resumes available</td>
              </tr>
            )}

            {/* Data rows */}
            {!loading &&
              sortedResumes.map((r, idx) => (
                <tr key={idx}>
                  <td>{r.candidateName}</td>
                  <td>{r.resumeName}</td>
                  <td>{r.email}</td>
                  <td>{r.jobTitle}</td>
                  <td>{r.score ?? "-"}</td>
                  <td>{r.rank ?? "-"}</td>
                  <td className={r.status.toLowerCase()}>{r.status}</td>
                  <td>
                    {r.resumeUrl ? (
                      <a href={resolveResumeUrl(r.resumeUrl)} target="_blank" rel="noreferrer">
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
    </div>
  );
}

export default Resumes;