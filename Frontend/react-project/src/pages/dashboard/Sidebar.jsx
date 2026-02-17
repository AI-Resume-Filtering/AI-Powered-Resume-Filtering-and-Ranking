import { useNavigate } from "react-router-dom";

function Sidebar({ active, setActive }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    // Clear login data
    localStorage.removeItem("company");

    // Redirect to Index page
    navigate("/");
  };

  return (
    <div className="sidebar">
      <h2 className="logo">Company</h2>

      <button onClick={() => setActive("home")} >🏠 Home</button>

      <button onClick={() => setActive("resumes")} >
        📄 View Resumes
      </button>

      <button onClick={() => setActive("postjob")}>
        📝 Post Job
      </button>

      <button
        className={active === "delete" ? "active" : ""}
        onClick={() => setActive("delete")}
       
      >
        🗑️ Delete Job Post
      </button>

      <button
        className={active === "history" ? "active" : ""}
        onClick={() => setActive("history")}
      
      >
        📊 History
      </button>

      <button className="primary" onClick={handleLogout}>
        🚪 Logout
      </button>
    </div>
  );
}

export default Sidebar;