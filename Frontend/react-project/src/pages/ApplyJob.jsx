import { useEffect, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import API from "../api";
import "../styles/apply-job.css";

function ApplyJob() {
  const [params] = useSearchParams();
  const navigate = useNavigate();

  const jobId = params.get("jobId");
  const companyRegNo = params.get("companyRegNo");

  const [job, setJob] = useState({});
  const [msg, setMsg] = useState("Apply for the selected job");
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!jobId) return;

    API.getJobDetails(jobId)
      .then(data => setJob(data))
      .catch(() => setJob({ description: "Unable to load job details" }));
  }, [jobId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (submitting) return;
    setSubmitting(true);

    const formData = new FormData();
    formData.append("jobId", jobId);
    formData.append("companyRegNo", companyRegNo);
    formData.append("fullName", e.target.fullName.value);
    formData.append("email", e.target.email.value);
    formData.append("phone", e.target.phone.value);
    formData.append("degree", e.target.degree.value);
    formData.append("branch", e.target.branch.value);
    formData.append("resume", e.target.resume.files[0]);

    try {
      const data = await API.applyForJob(formData);
      const companyName = job.companyName || "the company";
      const jobTitle = job.title || "this role";
      const successMessage = data.message || (
        `Application submitted successfully for ${jobTitle} at ${companyName}. ` +
        "We are reviewing your profile. If you are shortlisted, we will contact you by email with the next steps."
      );
      setMsg(successMessage);
      alert(successMessage);

      setTimeout(() => navigate("/jobs"), 3000);
    } catch (err) {
      console.error(err);
      const errorMessage = "Error submitting resume. Make sure backend is running.";
      setMsg(errorMessage);
      alert(errorMessage);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="addcase">
      <h2>{job.title || "Apply For Job"}</h2>

      <label>Job Description</label>
      <textarea value={job.description || ""} disabled />

      <form onSubmit={handleSubmit}>
        <label>Full Name</label>
        <input name="fullName" required />

        <label>Email</label>
        <input type="email" name="email" required />

        <label>Phone Number</label>
        <input name="phone" required />

        <label>Degree</label>
        <input name="degree" required />

        <label>Branch</label>
        <input name="branch" required />

        <label>Upload Resume</label>
        <input type="file" name="resume" accept=".pdf,.doc,.docx" required />

        <div className="btn-group">
          <button className={`btn ${submitting ? "loading" : ""}`} disabled={submitting}>
            {submitting ? "Submitting..." : "Submit Details"}
          </button>
          <button
            type="button"
            className="back-btn"
            onClick={() => navigate(-1)}
          >
            Back
          </button>
        </div>
      </form>

      <div className="msg">{msg}</div>
    </div>
  );
}

export default ApplyJob;
