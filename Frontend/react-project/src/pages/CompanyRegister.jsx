import { useState } from "react";
import { useNavigate } from "react-router-dom";
import API from "../api";
import "../styles/company-register.css";

function CompanyRegister() {
  const navigate = useNavigate();
  const [form, setForm] = useState({
    companyName: "",
    regNo: "",
    email: "",
    password: "",
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [focused, setFocused] = useState({
    companyName: false,
    regNo: false,
    email: false,
    password: false,
  });

  const handleChange = (e) => {
    setForm({ ...form, [e.target.id]: e.target.value });
  };

  const handleFocus = (e) => {
    setFocused({ ...focused, [e.target.id]: true });
  };

  const handleBlur = (e) => {
    setFocused({ ...focused, [e.target.id]: false });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    const passRegex =
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&]).{8,}$/;

    if (!passRegex.test(form.password)) {
      setError(
        "Password must contain uppercase, lowercase, number, special character & min 8 characters"
      );
      return;
    }

    try {
      const data = await API.registerCompany({
        companyName: form.companyName,
        registrationNo: form.regNo,
        email: form.email,
        password: form.password,
      });

      if (data.success) {
        setSuccess("Registration successful! Redirecting to login...");
        setTimeout(() => navigate("/company-login"), 2000);
      } else if (data.status === 503) {
        setError("Database service is currently unavailable. Start MongoDB and retry.");
      } else if (data.status === 0) {
        setError("Backend server is unreachable. Start Backend on port 5000 and retry.");
      } else {
        setError(data.message || "Company already exists or server error");
      }
    } catch (err) {
      console.error(err);
      setError("Server error. Please try again.");
    }
  };

  return (
    <div className="register-page">
      <div className="register-container">
        <div className="register-left">
          <div className="logo-box">🏢</div>
          <h1>Join Our Platform</h1>
          <p>Securely register your company and start posting jobs today!</p>
        </div>

        <div className="register-right">
          <div className="register-card">
            <h2>Company Registration</h2>

            <form onSubmit={handleSubmit}>
              <label className={focused.companyName ? "focused" : ""}>Company Name</label>
              <input
                id="companyName"
                value={form.companyName}
                onChange={handleChange}
                onFocus={handleFocus}
                onBlur={handleBlur}
                required
              />

              <label className={focused.regNo ? "focused" : ""}>Company Registration No</label>
              <input
                id="regNo"
                value={form.regNo}
                onChange={handleChange}
                onFocus={handleFocus}
                onBlur={handleBlur}
                required
              />

              <label className={focused.email ? "focused" : ""}>Company Email</label>
              <input
                id="email"
                type="email"
                value={form.email}
                onChange={handleChange}
                onFocus={handleFocus}
                onBlur={handleBlur}
                required
              />

              <label className={focused.password ? "focused" : ""}>Password</label>
              <input
                id="password"
                type="password"
                value={form.password}
                onChange={handleChange}
                onFocus={handleFocus}
                onBlur={handleBlur}
                required
              />

              <button type="submit" className="primary">Register</button>
            </form>

            {error && <div className="msg error">{error}</div>}
            {success && <div className="msg success">{success}</div>}

            <div className="login-link">
              Already Registered?
              <a href="/company-login"> Login</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CompanyRegister;