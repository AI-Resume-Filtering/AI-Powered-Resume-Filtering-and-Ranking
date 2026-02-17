import { useState } from "react";
import Sidebar from "./Sidebar";
import History from "./History";
import Resumes from "./Resumes";
import Delete from "./Delete";
import Home from "./Home";

import PostJob from "./PostJob";
import "../../styles/dashboard.css";

function CompanyDashboard() {
  const [active, setActive] = useState("home");
  
  // company object from localStorage
  const company = JSON.parse(localStorage.getItem("company"));

  return (
    <div className="dashboard">
      {/* Sidebar */}
      <Sidebar active={active} setActive={setActive} />

      {/* Right Content */}
      <div className="dashboard-content">
        {active === "history" && <History company={company} />}
        {active === "resumes" && <Resumes company={company} setActive={setActive} />}
        {active === "postjob" && <PostJob company={company} />}
        {active === "home" && <Home company={company} />}
        {active=="delete"&& <Delete company={company}/>}
      </div>
    </div>
  );
}

export default CompanyDashboard;