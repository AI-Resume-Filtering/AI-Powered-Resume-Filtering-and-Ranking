import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import API from "../api";
import "../styles/company-login.css";

function CompanyLogin() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  // ✅ Async login function with backend check
  const handleLogin = async () => {
    if (!email || !password) {
      alert("Enter email and password");
      return;
    }

    setLoading(true);

    try {
      const data = await API.loginCompany(email, password);

      if (data.success) {
        // Login successful
        localStorage.setItem("company", JSON.stringify(data.company));
        navigate("/company-dashboard");
      } else {
        // Login failed
        alert(data.message || "Invalid email or password");
      }

    } catch (err) {
      console.error(err);
      alert("Server error. Make sure backend is running on http://localhost:5000");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-box">
      <h2>Company Login</h2>

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

      <button onClick={handleLogin} className="primary" disabled={loading}>
        {loading ? "Logging in..." : "Login"}
      </button>

      <div className="links">
        <Link to="/forgot-password">Forgot Password?</Link>
        <Link to="/company-register">Sign Up</Link>
      </div>
    </div>
  );
}

export default CompanyLogin;