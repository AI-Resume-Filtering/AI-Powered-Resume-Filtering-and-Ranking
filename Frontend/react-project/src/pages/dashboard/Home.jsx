import React, { useEffect, useState } from "react";
import API from "../../api";
import "../../styles/home.css";

function Home({ company }) {
  const [jobStats, setJobStats] = useState([]);
  const [totalJobs, setTotalJobs] = useState(true);

  const formatDate = (value) => {
    if (!value) return "-";
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? "-" : parsed.toLocaleDateString();
  };

  useEffect(() => {
    if (!company) return;

    API.getCompanyJobs(company.companyId)
      .then(data => {
        setJobStats(data || []);
        setTotalJobs(data.length);
      })
      .catch(err => console.error(err));
  }, [company]);

  return (
    <div className="home-page">
      <div className="home-inner">

        <h2>Welcome, {company?.name || "Company"}</h2>

        {/* Total Jobs Card */}
        <div className="home-cards">
          <div className="home-card">
            <h3>Total Jobs Posted</h3>
            <p>{totalJobs}</p>
          </div>
        </div>

        {/* Jobs Table */}
        <div className="table-wrapper">
          <h3>Job Posted List</h3>

          <table className="history-table">
            <thead>
              <tr>
                <th>Sr. No</th>
                <th>Job Position</th>
                <th>Description</th>
                <th>Post Date</th>
                <th>Total Resumes</th>
              </tr>
            </thead>

            <tbody>
              {jobStats.length === 0 && (
                <tr>
                  <td colSpan="5">No jobs posted yet</td>
                </tr>
              )}

              {jobStats.map((job, idx) => (
                <tr key={job.jobId}>
                  <td>{idx + 1}</td>
                  <td>{job.title}</td>
                  <td>{job.description || "-"}</td>
                  <td>{formatDate(job.postDate || job.createdAt)}</td>
                  <td>{job.totalApplications ?? 0}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

      </div>
    </div>
  );
}

export default Home;
