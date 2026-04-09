import { useEffect, useState, useRef } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import API from "../api";
import { useBackgroundTasks } from "../context/BackgroundTasksContext";
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
  const [hasResumeError, setHasResumeError] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const mountedRef = useRef(true);
  const { runTask } = useBackgroundTasks();

  const updateFormMessage = (title, body = "", tone = "info") => {
    setFormMsg({ title, body, tone });
  };

  useEffect(() => {
    mountedRef.current = true;
    if (!jobId) return;

    API.getJobDetails(jobId)
      .then((data) => setJobData(data))
      .catch(() =>
        setJobData({ description: "Unable to load job details" })
      );
  }, [jobId]);

  const handleResumeChange = () => {
    setHasResumeError(false);
  };

    const handleSubmit = async (e) => {
      e.preventDefault();
      if (isSubmitting || isProcessing) return;

      const resumeFile = e.target.aj_resume.files[0];
      if (resumeFile && resumeFile.size > 5 * 1024 * 1024) {
        setHasResumeError(true);
        updateFormMessage(
          "Resume file is too large",
          "Please upload a resume that is 5 MB or smaller.",
          "error"
        );
        alert("Resume file must be 5 MB or smaller.");
        return;
      }

      setHasResumeError(false);
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
        const companyName = jobData.companyName || "this company";
        const jobTitle = jobData.title || "this position";

        const successMessage = `Completed. ${companyName} will contact you if shortlisted.`;

        const { promise } = runTask(
          {
            type: "job-application",
            title: `Application: ${jobTitle}`,
            message: "Submitting your application...",
          },
          async ({ taskId, update, sleep }) => {
            const data = await API.applyForJob(formData);

            if (!data?.success) {
              throw new Error(
                data?.message ||
                  "Application could not be submitted. Please check your details and try again."
              );
            }

            if (data.status === 202 && data.applicationId) {
              update({
                message: "Application submitted. AI analysis is running...",
                resume: {
                  kind: "application-status",
                  taskId,
                  applicationId: data.applicationId,
                  successMessage,
                },
              });

              for (;;) {
                const result = await API.getApplicationStatus(data.applicationId);
                if (result?.status === "processing") {
                  await sleep(3000);
                  continue;
                }
                if (result?.status === "error") {
                  throw new Error("Resume processing failed. Please try again.");
                }
                break;
              }
            }

            update({
              message: successMessage,
            });

            return data;
          }
        );

        const data = await promise;

        if (!mountedRef.current) {
          return;
        }

        if (!data?.success) {
          const message =
            data?.message ||
            "Application could not be submitted. Please check your details and try again.";
          const invalidResume = /does not appear to be a resume|proper resume pdf|resume/i.test(
            message
          );

          setHasResumeError(invalidResume);

          updateFormMessage(
            invalidResume ? "Invalid document" : "Application could not be submitted",
            message,
            "error"
          );
          return;
        }

        updateFormMessage(
          "Application submitted successfully",
          data.message ||
            `Thank you for applying to ${companyName} for the ${jobTitle} position. Your profile is under review, and if you are selected, our team will contact you soon.`,
          "success"
        );
        setTimeout(redirectToPreviousPage, 3000);
      } catch (err) {
        console.error(err);
        if (mountedRef.current) {
          updateFormMessage(
            "Application could not be submitted",
            err?.message || "Please make sure the backend is running and try again.",
            "error"
          );
        }
      } finally {
        if (mountedRef.current) {
          setIsSubmitting(false);
          setIsProcessing(false);
        }
      }
    };

    useEffect(() => {
      return () => {
        mountedRef.current = false;
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
            className={`aj-file-input${hasResumeError ? " aj-file-input-error" : ""}`}
            type="file"
            name="aj_resume"
            accept=".pdf,.doc,.docx"
            onChange={handleResumeChange}
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