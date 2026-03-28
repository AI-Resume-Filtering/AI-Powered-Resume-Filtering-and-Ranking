import "../styles/style.css";
import { useNavigate } from "react-router-dom";
import logo from "../assets/project-logo.svg";

function Index() {
  const navigate = useNavigate();

  return (
    <div className="landing-page">
      <div className="landing-container">
        <div className="brand-header">
          <img src={logo} alt="AI Resume Filter logo" className="brand-logo" />
          <div>
            <p className="brand-tag">AI Recruitment Platform</p>
            <h2>AI-Powered Resume Filtering and Ranking</h2>
          </div>
        </div>

        <p className="project-summary">
          Upload resumes, match candidates with job requirements, and shortlist top
          profiles using explainable AI scoring.
        </p>

        <p className="choose-role">Select your role to continue:</p>

        <div className="role-buttons">
          <button onClick={() => navigate("/jobs")}>
            Candidate / Recruiter
          </button>

          <button onClick={() => navigate("/company-login")}>
            Company Login
          </button>
        </div>

        <button
          className="about-button"
          onClick={() => navigate("/about-project")}
        >
          About Project and Contact Us
        </button>

        <div className="footer-text">
          © 2026 Resume Parsing System
        </div>
      </div>
    </div>
  );
}

export default Index;
