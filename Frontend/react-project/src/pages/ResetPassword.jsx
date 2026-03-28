import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useSearchParams } from "react-router-dom";
import API from "../api";
import "../styles/passwordForgot.css";

function ResetPassword() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const token = useMemo(() => (searchParams.get("token") || "").trim(), [searchParams]);

  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [validating, setValidating] = useState(true);
  const [isTokenValid, setIsTokenValid] = useState(false);
  const [message, setMessage] = useState("");
  const [isError, setIsError] = useState(false);

  useEffect(() => {
    let active = true;

    const validateToken = async () => {
      if (!token) {
        if (!active) return;
        setIsTokenValid(false);
        setValidating(false);
        setIsError(true);
        setMessage("Reset link is invalid or missing token.");
        return;
      }

      try {
        const res = await API.validateResetToken(token);
        if (!active) return;
        setIsTokenValid(Boolean(res.success));
        setIsError(!res.success);
        setMessage(res.success ? "Reset link verified. Set your new password." : (res.message || "Reset link is invalid or expired."));
      } catch {
        if (!active) return;
        setIsTokenValid(false);
        setIsError(true);
        setMessage("Unable to validate reset link right now. Please try again.");
      } finally {
        if (active) {
          setValidating(false);
        }
      }
    };

    validateToken();
    return () => {
      active = false;
    };
  }, [token]);

  const handleReset = async () => {
    if (!token || !isTokenValid) {
      setIsError(true);
      setMessage("Reset link is invalid or expired.");
      return;
    }

    if (!password || !confirmPassword) {
      setIsError(true);
      setMessage("Please fill both password fields.");
      return;
    }

    if (password.length < 8) {
      setIsError(true);
      setMessage("Password must be at least 8 characters.");
      return;
    }

    if (!/[A-Z]/.test(password)) {
      setIsError(true);
      setMessage("Password must include at least one uppercase letter.");
      return;
    }

    if (!/[a-z]/.test(password)) {
      setIsError(true);
      setMessage("Password must include at least one lowercase letter.");
      return;
    }

    if (!/\d/.test(password)) {
      setIsError(true);
      setMessage("Password must include at least one number.");
      return;
    }

    if (!/[^A-Za-z0-9]/.test(password)) {
      setIsError(true);
      setMessage("Password must include at least one special character.");
      return;
    }

    if (password !== confirmPassword) {
      setIsError(true);
      setMessage("Passwords do not match.");
      return;
    }

    try {
      setLoading(true);
      const res = await API.resetPassword(token, password, confirmPassword);
      if (res.success) {
        setIsError(false);
        setMessage("Password reset successful. Redirecting to login...");
        setTimeout(() => navigate("/company-login"), 1400);
      } else {
        setIsError(true);
        setMessage(res.message || "Password reset failed.");
      }
    } catch (error) {
      setIsError(true);
      setMessage("Unable to reset password right now. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="forgot-page">
      <div className="forgot-container">
        <div className="forgot-left">
          <div className="logo-box">🔐</div>
          <h1>Create New Password</h1>
          <p>Set a strong password to secure your company account.</p>
        </div>

        <div className="forgot-right">
          <div className="forgot-card">
            <h2>Reset Password</h2>

            <label>New Password</label>
            <input
              type="password"
              placeholder="Enter new password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              disabled={validating || !isTokenValid || loading}
            />

            <label>Confirm Password</label>
            <input
              type="password"
              placeholder="Confirm new password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              disabled={validating || !isTokenValid || loading}
            />

            <button onClick={handleReset} className="primary" disabled={loading || validating || !isTokenValid}>
              {validating ? "Verifying link..." : (loading ? "Updating..." : "Update Password")}
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

export default ResetPassword;
