import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api";
import "../styles/joblist.css"; // dark theme css

function JobList() {
  const [allJobs, setAllJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchText, setSearchText] = useState("");
  const [searchValue, setSearchValue] = useState("");
  const [dateFilter, setDateFilter] = useState("all");
  const [sortBy, setSortBy] = useState("newest");
  const [visibleCount, setVisibleCount] = useState(9);

  const navigate = useNavigate();

  useEffect(() => {
    setLoading(true);
    setError("");

    API.getAllJobs({
      q: searchValue,
      sort: sortBy,
      postedWithinDays: dateFilter === "all" ? "" : dateFilter,
      limit: 100,
      page: 1,
    })
      .then(data => setAllJobs(data || []))
      .catch(err => {
        console.error(err);
        setError("Failed to load jobs. Please refresh.");
        setAllJobs([]);
      })
      .finally(() => setLoading(false));
  }, [searchValue, sortBy, dateFilter]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setSearchValue(searchText.trim());
      setVisibleCount(9);
    }, 350);

    return () => clearTimeout(timer);
  }, [searchText]);

  useEffect(() => {
    setVisibleCount(9);
  }, [sortBy, dateFilter]);

  const latestJobs = useMemo(() => {
    return [...allJobs]
      .sort((a, b) => new Date(b.postDate || b.createdAt || 0) - new Date(a.postDate || a.createdAt || 0))
      .slice(0, 5);
  }, [allJobs]);

  const visibleJobs = allJobs.slice(0, visibleCount);
  const canLoadMore = visibleCount < allJobs.length;

  const formatPostedDate = (isoDate) => {
    if (!isoDate) return "Posted recently";
    const date = new Date(isoDate);
    if (Number.isNaN(date.getTime())) return "Posted recently";

    const diffMs = Date.now() - date.getTime();
    const diffDays = Math.max(0, Math.floor(diffMs / 86400000));
    if (diffDays === 0) return "Posted today";
    if (diffDays === 1) return "Posted 1 day ago";
    if (diffDays < 30) return `Posted ${diffDays} days ago`;
    return `Posted on ${date.toLocaleDateString()}`;
  };

  const isNewJob = (isoDate) => {
    if (!isoDate) return false;
    const posted = new Date(isoDate);
    if (Number.isNaN(posted.getTime())) return false;
    return (Date.now() - posted.getTime()) / 86400000 <= 7;
  };

  return (
    <div className="jl-page-wrapper">

      <header className="jl-header">
        <h2 className="jl-title">Job Listings – Candidate View</h2>
        <button className="jl-back-btn" onClick={() => navigate("/")}>
          ⬅ Back
        </button>
      </header>

      <section className="jl-discovery-bar">
        <input
          className="jl-search-input"
          type="text"
          placeholder="Search by role or company..."
          value={searchText}
          onChange={(e) => setSearchText(e.target.value)}
        />

        <select
          className="jl-select"
          value={dateFilter}
          onChange={(e) => setDateFilter(e.target.value)}
        >
          <option value="all">All dates</option>
          <option value="1">Last 24 hours</option>
          <option value="7">Last 7 days</option>
          <option value="30">Last 30 days</option>
        </select>

        <select
          className="jl-select"
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
        >
          <option value="newest">Sort: Newest first</option>
          <option value="oldest">Sort: Oldest first</option>
          <option value="company">Sort: Company A-Z</option>
        </select>
      </section>

      <section className="jl-latest-strip">
        <h3>Latest Jobs</h3>
        <p>{latestJobs.length} most recent openings</p>
        <div className="jl-latest-list">
          {latestJobs.map((job) => (
            <button
              type="button"
              key={`latest-${job.id}`}
              className="jl-latest-pill"
              onClick={() =>
                navigate(`/apply-job?jobId=${job.id}&companyRegNo=${job.companyRegNo}`)
              }
            >
              <span>{job.title}</span>
              <small>{job.companyName}</small>
            </button>
          ))}
        </div>
      </section>

      <div className="jl-grid-wrapper">
        {loading && <p className="jl-no-jobs">Loading jobs...</p>}

        {!loading && error && (
          <p className="jl-no-jobs">{error}</p>
        )}

        {!loading && !error && allJobs.length === 0 && (
          <p className="jl-no-jobs">No jobs available</p>
        )}

        {!loading && !error && visibleJobs.map((job, index) => (
          <div className="jl-job-card" key={`jl-job-${index}`} id={`jl-job-${job.id}`}>
            
            <div className="jl-job-header">
              <h3 className="jl-job-title">{job.title}</h3>
              <span className="jl-company-name">{job.companyName}</span>
            </div>

            <div className="jl-meta-row">
              {isNewJob(job.postDate || job.createdAt) && <span className="jl-new-badge">NEW</span>}
              <span className="jl-posted-text">{formatPostedDate(job.postDate || job.createdAt)}</span>
            </div>

            <div className="jl-job-details">
              <p><strong>Location:</strong> {job.location}</p>
              <p><strong>Experience:</strong> {job.experience}</p>
            </div>

            <button
              className="jl-apply-btn"
              onClick={() =>
                navigate(
                  `/apply-job?jobId=${job.id}&companyRegNo=${job.companyRegNo}`
                )
              }
            >
              Apply Now
            </button>
          </div>
        ))}
      </div>

      {!loading && !error && canLoadMore && (
        <button
          type="button"
          className="jl-load-more-btn"
          onClick={() => setVisibleCount((count) => count + 9)}
        >
          Load More Jobs
        </button>
      )}

    </div>
  );
}

export default JobList;