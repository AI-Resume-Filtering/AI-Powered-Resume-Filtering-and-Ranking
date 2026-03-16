import { useEffect, useState } from "react";
import API, { API_BASE_URL } from "../../api";
import "../../styles/Resume.css";

function Resumes({ company, setActive }) {
  const [resumes, setResumes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedJobId, setSelectedJobId] = useState("all");
  const [searchTerm, setSearchTerm] = useState("");

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

  const visibleResumes =
    selectedJobId === "all"
      ? resumes
      : resumes.filter(r => r.jobId === selectedJobId);

  const normalizedSearch = searchTerm.trim().toLowerCase();

  const filteredResumes = normalizedSearch
    ? visibleResumes.filter((resume) => {
        const candidateName = (resume.candidateName || "").toLowerCase();
        const email = (resume.email || "").toLowerCase();
        return candidateName.includes(normalizedSearch) || email.includes(normalizedSearch);
      })
    : visibleResumes;

  const sortedResumes = [...filteredResumes].sort((a, b) => {
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

  const formatScore = (score) => {
    if (score == null) return "-";
    return Number(score).toFixed(2);
  };

  return (
    <div className="resumes-page"> {/* NEW FULL WIDTH WRAPPER */}

      <div className="resumes-section">

        <div className="resumes-header">
          <h2>Uploaded Resumes</h2>

          <div className="resumes-actions">
            <input
              className="resumes-search-input"
              type="search"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by candidate name or email"
            />

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
              className="resumes-back-btn"
              onClick={() => setActive && setActive("home")}
            >
              Back to Dashboard
            </button>
          </div>
        </div>

        <div className="resumes-table-wrapper">

          <div className="resumes-table-meta">
            <span>{sortedResumes.length} resume{sortedResumes.length === 1 ? "" : "s"} found</span>
          </div>

          <table className="resumes-table">

            <colgroup>
              <col className="resumes-col-candidate" />
              <col className="resumes-col-file" />
              <col className="resumes-col-email" />
              <col className="resumes-col-job" />
              <col className="resumes-col-score" />
              <col className="resumes-col-rank" />
              <col className="resumes-col-status" />
              <col className="resumes-col-action" />
            </colgroup>

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

              {loading && (
                <tr>
                  <td colSpan="8">Loading...</td>
                </tr>
              )}

              {!loading && sortedResumes.length === 0 && (
                <tr>
                  <td colSpan="8">
                    {normalizedSearch
                      ? "No resumes match the current search."
                      : "No resumes available"}
                  </td>
                </tr>
              )}

              {!loading &&
                sortedResumes.map((r, idx) => (
                  <tr key={idx}>

                    <td className="resumes-cell resumes-cell-wrap">{r.candidateName}</td>
                    <td className="resumes-cell resumes-cell-file">
                      <span className="resumes-file-name" data-tooltip={r.resumeName}>
                        {r.resumeName}
                      </span>
                    </td>
                    <td className="resumes-cell resumes-cell-email" title={r.email}>{r.email}</td>
                    <td className="resumes-cell resumes-cell-wrap">{r.jobTitle}</td>
                    <td className="resumes-cell resumes-cell-center">{formatScore(r.score)}</td>
                    <td className="resumes-cell resumes-cell-center">{r.rank ?? "-"}</td>

                    <td className={`resumes-cell resumes-cell-center status-${(r.status || "unknown").toLowerCase()}`}>
                      {r.status || "unknown"}
                    </td>

                    <td className="resumes-cell resumes-cell-center">
                      {r.resumeUrl ? (
                        <a
                          className="resumes-download-link"
                          href={resolveResumeUrl(r.resumeUrl)}
                          target="_blank"
                          rel="noreferrer"
                        >
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

    </div>
  );
}

export default Resumes;