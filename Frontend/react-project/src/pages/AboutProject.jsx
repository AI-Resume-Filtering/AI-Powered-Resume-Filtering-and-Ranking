import { Link } from "react-router-dom";
import logo from "../assets/project-logo.svg";
import "../styles/about-project.css";

function AboutProject() {
  return (
    <div className="about-page">
      <div className="about-card">
        <header className="about-header">
          <img src={logo} alt="AI Resume Filter logo" className="about-logo" />
          <div>
            <p className="eyebrow">About This Software</p>
            <h1>AI-Powered Resume Filtering and Ranking</h1>
            <p className="intro">
              This platform helps recruiters quickly shortlist the best candidates by
              combining resume parsing, NLP feature extraction, and AI-based scoring.
            </p>
          </div>
        </header>

        <section className="about-section">
          <h2>What This Software Does</h2>
          <ul>
            <li>Lets companies post jobs and define hiring requirements.</li>
            <li>Allows candidates to apply by uploading resume PDFs.</li>
            <li>Parses each resume and extracts skills, experience, and education.</li>
            <li>Matches resumes with job requirements using semantic AI similarity.</li>
            <li>Generates explainable scores and ranking for recruiter review.</li>
            <li>Improves future ranking quality from recruiter feedback.</li>
          </ul>
        </section>

        <section className="about-section">
          <h2>Why It Is Useful</h2>
          <ul>
            <li>Reduces manual resume screening time.</li>
            <li>Improves consistency in candidate evaluation.</li>
            <li>Provides transparent score breakdown for decisions.</li>
            <li>Supports self-learning improvement over time.</li>
          </ul>
        </section>

        <section className="about-section contact-box">
          <h2>Contact Us</h2>
          <p>If you need support, feature requests, or setup help, contact us here:</p>
          <p>
            Email: <a href="mailto:hackmking4646@gmail.com">hackmking4646@gmail.com</a>
          </p>
          <p>
            Phone: <a href="tel:+919356736650">+91 93567 36650</a>
          </p>
          <p>Support Hours: Mon-Sat, 10:00 AM to 7:00 PM IST</p>
        </section>

        <footer className="about-footer">
          <Link to="/" className="about-link">Back to Home</Link>
          <Link to="/jobs" className="about-link secondary">Explore Jobs</Link>
        </footer>
      </div>
    </div>
  );
}

export default AboutProject;
