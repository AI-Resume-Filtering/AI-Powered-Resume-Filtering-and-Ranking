import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api";
import "../styles/job-list.css";


function JobList() {
  const [jobs, setJobs] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    API.getAllJobs()
      .then(data => setJobs(data))
      .catch(err => {
        console.error(err);
        setJobs([]);
      });
  }, []);

  return (
    <>
      <h2>Job Listings – Candidate View</h2>

      <div className="addcase">
        <button className="back-btn" onClick={() => navigate("/")}>
          Back
        </button>

        <div id="jobList">
          {jobs.length === 0 && (
            <p style={{ textAlign: "center" }}>No jobs available</p>
          )}

          {jobs.map(job => (
            <div className="job-card" key={job.id}>
              <b>{job.title}</b>
              <p><strong>Company:</strong> {job.companyName}</p>
              <p><strong>Location:</strong> {job.location}</p>
              <p><strong>Experience:</strong> {job.experience}</p>

              <button
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
      </div>
    </>
  );
}

export default JobList;