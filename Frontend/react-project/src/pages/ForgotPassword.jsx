import { useState } from "react";
import { Link } from "react-router-dom";
import API from "../api";
import "../styles/passwordForgot.css";

function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [focused, setFocused] = useState(false);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    const normalizedEmail = email.trim();
    if (!normalizedEmail) {
      setIsError(true);
      setMessage("Please enter your registered email.");
      return;
    }

    try {
      setLoading(true);
      const currentOrigin = typeof window !== "undefined" ? window.location.origin : "";
      const res = await API.requestPasswordReset(normalizedEmail, currentOrigin);
      if (res.success) {
        setIsError(false);
        setMessage(res.message || "If this email is registered, a password reset link has been sent.");
      } else {
        setIsError(true);
        if (res.status === 503) {
          setMessage("Database service is currently unavailable. Start MongoDB and retry.");
        } else if (res.status === 0) {
          setMessage("Backend server is unreachable. Start Backend on port 5000 and retry.");
        } else {
          setMessage(res.message || "Unable to process request right now.");
        }
      }
    } catch (error) {
      setIsError(true);
      setMessage("Unable to process request right now. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="forgot-page">
      <div className="forgot-container">

        <div className="forgot-left">
          <div className="logo-box">🔒</div>
          <h1>Reset Password</h1>
          <p>Enter your registered email to receive a secure password reset link.</p>
        </div>

        <div className="forgot-right">
          <div className="forgot-card">
            <h2>Forgot Password</h2>

            <label className={focused ? "focused" : ""}>Email</label>
            <input
              type="email"
              placeholder="Enter registered email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              onFocus={() => setFocused(true)}
              onBlur={() => setFocused(false)}
            />

            <button onClick={handleSubmit} className="primary" disabled={loading}>
              {loading ? "Sending..." : "Send Reset Link"}
            </button>

            {message && <p className={`forgot-msg ${isError ? "error" : "success"}`}>{message}</p>}

            <div className="links">
              <Link to="/company-login">Back to Login</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ForgotPassword;