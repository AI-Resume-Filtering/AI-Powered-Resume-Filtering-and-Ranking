import "../styles/style.css";
import { useNavigate } from "react-router-dom";

function Index() {
  const navigate = useNavigate();

  return (
    <div className="container">
      <h2>Welcome to Resume Parsing</h2>

      <p className="choose-role">Select your role to continue:</p>

      <div className="role-buttons">
        <button onClick={() => navigate("/jobs")}>
          Candidate / Recruiter
        </button>

        <button onClick={() => navigate("/company-login")}>
          Company Login
        </button>
      </div>



      <div className="footer-text">
        © 2026 Resume Parsing System
      </div>
    </div>
  );
}

export default Index;
