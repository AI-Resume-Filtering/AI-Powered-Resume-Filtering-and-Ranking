import { useEffect, useState, useRef } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import API, { API_BASE_URL } from "../api";
import "../styles/applyjob.css"; // linked CSS file

function ApplyJob() {
  const [params] = useSearchParams();
  const navigate = useNavigate();

  const redirectToPreviousPage = () => {
    if (window.history.length > 1) {
      navigate(-1);
      return;
    }

    navigate("/jobs");
  };

  const jobId = params.get("jobId");
  const companyRegNo = params.get("companyRegNo");

  const [jobData, setJobData] = useState({});
  const [formMsg, setFormMsg] = useState({
    title: "Apply for the selected job",
    body: "Complete the form below and upload your resume to continue.",
    tone: "info",
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const pollRef = useRef(null);

  const updateFormMessage = (title, body = "", tone = "info") => {
    setFormMsg({ title, body, tone });
  };

  useEffect(() => {
    if (!jobId) return;

    API.getJobDetails(jobId)
      .then((data) => setJobData(data))
      .catch(() =>
        setJobData({ description: "Unable to load job details" })
      );
  }, [jobId]);

    const handleSubmit = async (e) => {
      e.preventDefault();
      if (isSubmitting || isProcessing) return;

      const resumeFile = e.target.aj_resume.files[0];
      if (resumeFile && resumeFile.size > 5 * 1024 * 1024) {
        updateFormMessage(
          "Resume file is too large",
          "Please upload a resume that is 5 MB or smaller.",
          "error"
        );
        alert("Resume file must be 5 MB or smaller.");
        return;
      }

      setIsSubmitting(true);

      const formData = new FormData();
      formData.append("jobId", jobId);
      formData.append("companyRegNo", companyRegNo);
      formData.append("fullName", e.target.aj_fullName.value);
      formData.append("email", e.target.aj_email.value);
      formData.append("phone", e.target.aj_phone.value);
      formData.append("degree", e.target.aj_degree.value);
      formData.append("branch", e.target.aj_branch.value);
      formData.append("resume", resumeFile);

      try {
        const response = await fetch(`${API_BASE_URL}/apply`, {
          method: "POST",
          body: formData,
        });

        const data = await response.json();

        if (response.status === 202 && data.applicationId) {
          setIsSubmitting(false);
          setIsProcessing(true);
          updateFormMessage(
            "Application received",
            "Your resume has been submitted successfully and is now being analysed. Please wait a moment.",
            "processing"
          );
          _startPolling(data.applicationId);
          return;
        }

        const companyName = jobData.companyName || "the company";
        const jobTitle = jobData.title || "this role";
        updateFormMessage(
          "Application submitted successfully",
          data.message ||
            `Thank you for applying to ${companyName} for the ${jobTitle} position. Your profile is under review, and if you are selected, our team will contact you soon.` ,
          "success"
        );
        setTimeout(redirectToPreviousPage, 3000);
      } catch (err) {
        console.error(err);
        updateFormMessage(
          "Application could not be submitted",
          "Please make sure the backend is running and try again.",
          "error"
        );
      } finally {
        setIsSubmitting(false);
      }
    };

    const _startPolling = (applicationId) => {
      pollRef.current = setInterval(async () => {
        try {
          const result = await API.getApplicationStatus(applicationId);
          if (!result || result.status === "processing") return;

          clearInterval(pollRef.current);
          setIsProcessing(false);

          if (result.status === "error") {
            updateFormMessage(
              "Resume processing failed",
              "Please try again or contact support if the issue continues.",
              "error"
            );
            return;
          }

          const companyName = jobData.companyName || "this company";
          const jobTitle = jobData.title || "this position";
          updateFormMessage(
            "Application submitted successfully",
            `Thank you for applying to ${companyName} for the ${jobTitle} position. ${companyName} uses AI intelligence to review applications carefully. If you are selected, our team will connect with you soon. Redirecting you back now...`,
            "success"
          );
          setTimeout(redirectToPreviousPage, 4000);
        } catch {
          clearInterval(pollRef.current);
          setIsProcessing(false);
          updateFormMessage(
            "Status check interrupted",
            "Connection was lost while checking your application status. Please contact support.",
            "error"
          );
        }
      }, 3000);
    };

    useEffect(() => {
      return () => {
        if (pollRef.current) clearInterval(pollRef.current);
      };
    }, []);


  return (
    <div className="aj-page-wrapper">
      <div className="aj-card">
        <h2 className="aj-title">{jobData.title || "Apply For Job"}</h2>

        <label className="aj-label">Job Description</label>
        <textarea
          className="aj-textarea"
          value={jobData.description || ""}
          disabled
        />

        <form className="aj-form" onSubmit={handleSubmit}>
          <label className="aj-label">Full Name</label>
          <input
            className="aj-input"
            name="aj_fullName"
            placeholder="Enter your full name"
            required
          />

          <label className="aj-label">Email</label>
          <input
            className="aj-input"
            type="email"
            name="aj_email"
            placeholder="Enter your email"
            required
          />

          <label className="aj-label">Phone Number</label>
          <input
            className="aj-input"
            name="aj_phone"
            placeholder="Enter your phone number"
            required
          />

          <label className="aj-label">Degree</label>
          <input
            className="aj-input"
            name="aj_degree"
            placeholder="Enter your degree"
            required
          />

          <label className="aj-label">Branch</label>
          <input
            className="aj-input"
            name="aj_branch"
            placeholder="Enter your branch"
            required
          />

          <label className="aj-label">Upload Resume</label>
          <input
            className="aj-file-input"
            type="file"
            name="aj_resume"
            accept=".pdf,.doc,.docx"
            required
          />

          <div className="aj-btn-group">
            <button
                className={`aj-btn-submit ${(isSubmitting || isProcessing) ? "loading" : ""}`}
                disabled={isSubmitting || isProcessing}
            >
                {isSubmitting ? "Submitting..." : isProcessing ? "Analysing..." : "Submit Details"}
            </button>

            <button
              type="button"
              className="aj-btn-back"
              onClick={() => navigate(-1)}
            >
              Back
            </button>
          </div>
        </form>

        <div className={`aj-msg aj-msg-${formMsg.tone}`}>
          <div className="aj-msg-title">{formMsg.title}</div>
          {formMsg.body ? <div className="aj-msg-body">{formMsg.body}</div> : null}
        </div>
      </div>
    </div>
  );
}

export default ApplyJob;