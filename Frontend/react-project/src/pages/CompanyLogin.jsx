import { useState } from "react";  
import { useNavigate, Link } from "react-router-dom";  
import API from "../api";  
import "../styles/Company-login/company-login-dark.css"; // new CSS

function CompanyLogin() {  
  const navigate = useNavigate();  
  const [email, setEmail] = useState("");  
  const [password, setPassword] = useState("");  
  const [loading, setLoading] = useState(false);  

  const getFriendlyAuthError = (data) => {
    if (!data) return "Login failed. Please try again.";
    if (data.status === 503) {
      return "Database service is currently unavailable. Start MongoDB and retry.";
    }
    if (data.status === 0) {
      return "Backend server is unreachable. Start Backend on port 5000 and retry.";
    }
    return data.message || "Invalid email or password";
  };

  const handleLogin = async () => {  
    if (!email || !password) {  
      alert("Enter email and password");  
      return;  
    }  

    setLoading(true);  

    try {  
      const data = await API.loginCompany(email, password);  

      if (data.success) {  
        localStorage.setItem("authToken", data.token);
        localStorage.setItem("company", JSON.stringify(data.company));
        navigate("/company-dashboard");
      } else {  
        alert(getFriendlyAuthError(data));  
      }  

    } catch (err) {  
      console.error(err);
      alert("Server error. Please try again.");
    } finally {  
      setLoading(false);  
    }  
  };  

  return (
    <div className="main-container">

      {/* LEFT PANEL */}
      <div className="left-panel">
        <div className="logo-box">🛡</div>
        <h1>Secure Enterprise <br/> Access Control</h1>
        <p>Next-generation authentication system for modern company HR portals.</p>
      </div>

      {/* RIGHT PANEL */}
      <div className="right-panel">
        <div className="login-card">
          <h2>Welcome Back</h2>
          <p className="subtitle">Please enter your employee credentials</p>

          <label>Email</label>
          <input
            type="email"
            placeholder="Enter email"
            value={email}
            onChange={e => setEmail(e.target.value)}
          />

          <label>Password</label>
          <input
            type="password"
            placeholder="Enter password"
            value={password}
            onChange={e => setPassword(e.target.value)}
          />

          <button
            onClick={handleLogin}
            className="secure-btn"
            disabled={loading}
          >
            {loading ? "Logging in..." : "Secure Login"}
          </button>

          <div className="links">
            <Link to="/forgot-password">Forgot Password?</Link>
            <Link to="/company-register">Sign Up</Link>
          </div>
        </div>
      </div>

    </div>
  );
}

export default CompanyLogin;