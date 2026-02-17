import { useState } from "react";
import "../styles/company-login.css";

function ForgotPassword() {
  const [email, setEmail] = useState("");

  const handleSubmit = () => {
    if (!email) {
      alert("Enter registered email");
      return;
    }

    // Later: API call for reset link
    alert("Password reset link sent to your email");
  };

  return (
    <div className="login-box">
      <h2>Forgot Password</h2>

      <label>Email</label>
      <input
        type="email"
        placeholder="Enter registered email"
        value={email}
        onChange={e => setEmail(e.target.value)}
      />

      <button onClick={handleSubmit} className="primary">Send Reset Link</button>

      <div className="links">
        <a href="/company-login">Back to Login</a>
      </div>
    </div>
  );
}

export default ForgotPassword;
