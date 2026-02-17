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
    password: ""
  });

  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const handleChange = (e) => {
    setForm({ ...form, [e.target.id]: e.target.value });
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
        password: form.password
      });

      if (data.success) {
        setSuccess("Registration successful! Redirecting to login...");
        setTimeout(() => navigate("/company-login"), 2000);
      } else {
        setError(data.message || "Company already exists or server error");
      }

    } catch (err) {
      console.error(err);
      setError("Server error. Make sure backend is running on http://localhost:5000");
    }
  };

  return (
    <div className="register-box">
      <h2>Company Registration</h2>

      <form onSubmit={handleSubmit}>
        <label>Company Name</label>
        <input id="companyName" onChange={handleChange} required />

        <label>Company Registration No</label>
        <input id="regNo" onChange={handleChange} required />

        <label>Company Email</label>
        <input id="email" type="email" onChange={handleChange} required />

        <label>Password</label>
        <input id="password" type="password" onChange={handleChange} required />

        <button type="submit" className="primary">Register</button>
      </form>

      {error && <div className="msg error">{error}</div>}
      {success && <div className="msg success">{success}</div>}

      <div className="login-link">
        Already Registered?
        <a href="/company-login"> Login</a>
      </div>
    </div>
  );
}

export default CompanyRegister;
