import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Sidebar from "./Sidebar";
import History from "./History";
import Resumes from "./Resumes";
import Delete from "./Delete";
import Home from "./Home";
import PostJob from "./PostJob";
import EmailTemplate from "./EmailTemplate";

// ✅ Import dashboard CSS
import "../../styles/dashboard.css";

function CompanyDashboard() {
  const [active, setActive] = useState("home");
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("authToken");
    if (!token) {
      navigate("/company-login", { replace: true });
    }
  }, [navigate]);

  const company = JSON.parse(localStorage.getItem("company"));

  return (
    <div className="dashboard-container">
      {/* Sidebar */}
      <Sidebar active={active} setActive={setActive} />

      {/* Main Content */}
      <div className="main-content">
        {active === "home" && <Home company={company} />}
        {active === "resumes" && <Resumes company={company} setActive={setActive} />}
        {active === "postjob" && <PostJob company={company} />}
        {active === "delete" && <Delete company={company} />}
        {active === "history" && <History company={company} />}
        {active === "emailtemplate" && <EmailTemplate company={company} />}
      </div>
    </div>
  );
}

export default CompanyDashboard;