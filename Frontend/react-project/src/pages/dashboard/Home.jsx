import { useEffect, useState } from "react";
import API from "../../api";
import "../../styles/dashboard.css";

function Home({ company, refreshTick = 0 }) {

  const [jobs, setJobs] = useState([]);
  const totalApplications = jobs.reduce((sum, j) => sum + (j.totalApplications || 0), 0);

  useEffect(() => {
    if (!company?.companyId) return;

    const loadJobs = () => {
      API.getCompanyJobs(company.companyId)
        .then(response => {
          if (response.success && Array.isArray(response.data)) {
            setJobs(response.data);
          } else {
            console.error('Failed to load jobs:', response.message);
            setJobs([]);
          }
        })
        .catch(err => {
          console.error('Error loading jobs:', err);
          setJobs([]);
        });
    };

    loadJobs();
    window.addEventListener("jobPosted", loadJobs);

    return () => {
      window.removeEventListener("jobPosted", loadJobs);
    };
  }, [company, refreshTick]);

  return (
    <div className="home-container">

      <h2>Welcome {company?.name}</h2>

      {/* Dashboard Cards */}
      <div className="dashboard-cards">

        <div className="card">
          <h3>Total Jobs</h3>
          <p>{jobs.length}</p>
        </div>

        <div className="card">
          <h3>Total Applications</h3>
            <p>{totalApplications}</p>
        </div>

        <div className="card">
          <h3>Active Jobs</h3>
          <p>{jobs.length}</p>
        </div>

        <div className="card">
          <h3>Closed Jobs</h3>
          <p>0</p>
        </div>

      </div>

      {/* Job Table */}

      <div className="table-box">

        <h3>Recent Job Posts</h3>

        <table>

          <thead>
            <tr>
              <th>#</th>
              <th>Position</th>
              <th>Description</th>
              <th>Date</th>
            </tr>
          </thead>

          <tbody>

            {jobs.map((job,index)=>(
              <tr key={job.jobId}>
                <td>{index+1}</td>
                <td>{job.title}</td>
                <td>{job.description}</td>
                <td>{job.postDate}</td>
              </tr>
            ))}

          </tbody>

        </table>

      </div>

    </div>
  );
}

export default Home;