import { useNavigate } from "react-router-dom";

function Sidebar({ active, setActive }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("company");
    navigate("/"); // redirect to Index page
  };

  return (
    <div className="sidebar">
      <h2 className="logo">Company</h2>

      <button
        className={active === "home" ? "active" : ""}
        onClick={() => setActive("home")}
      >
        🏠 Home
      </button>

      <button
        className={active === "resumes" ? "active" : ""}
        onClick={() => setActive("resumes")}
      >
        📄 View Resumes
      </button>

      <button
        className={active === "postjob" ? "active" : ""}
        onClick={() => setActive("postjob")}
      >
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

      <button
        className={active === "emailtemplate" ? "active" : ""}
        onClick={() => setActive("emailtemplate")}
      >
        ✉️ Email Settings
      </button>

      <button className="primary" onClick={handleLogout}>
        🚪 Logout
      </button>
    </div>
  );
}

export default Sidebar;