/**
 * API Configuration and Helper Functions
 * Centralized API calls for the React frontend
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

/**
 * API Helper Class
 */
class API {
  /**
   * Company Registration
   */
  static async registerCompany(data) {
    const response = await fetch(`${API_BASE_URL}/company/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    return response.json();
  }

  /**
   * Company Login
   */
  static async loginCompany(email, password) {
    const response = await fetch(`${API_BASE_URL}/company/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    return response.json();
  }

  /**
   * Get all jobs (for candidates)
   */
  static async getAllJobs() {
    const response = await fetch(`${API_BASE_URL}/jobs`);
    return response.json();
  }

  /**
   * Get specific job details
   */
  static async getJobDetails(jobId) {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`);
    return response.json();
  }

  /**
   * Get company's posted jobs
   */
  static async getCompanyJobs(companyId) {
    const response = await fetch(`${API_BASE_URL}/company/${companyId}/jobs`);
    return response.json();
  }

  /**
   * Post a new job
   */
  static async postJob(formData) {
    const response = await fetch(`${API_BASE_URL}/company/post-job`, {
      method: 'POST',
      body: formData  // FormData object with file
    });
    return response.json();
  }

  /**
   * Delete a job
   */
  static async deleteJob(jobId) {
    const response = await fetch(`${API_BASE_URL}/company/delete-job`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ jobId })
    });
    return response.json();
  }

  /**
   * Apply for a job (submit resume)
   */
  static async applyForJob(formData) {
    const response = await fetch(`${API_BASE_URL}/apply`, {
      method: 'POST',
      body: formData  // FormData object with resume file
    });
    return response.json();
  }

  /**
   * Get company's received resumes
   */
  static async getCompanyResumes(companyId) {
    const response = await fetch(`${API_BASE_URL}/company/${companyId}/resumes`);
    return response.json();
  }

  /**
   * Get company's application history
   */
  static async getCompanyHistory(companyId) {
    const response = await fetch(`${API_BASE_URL}/company/${companyId}/history`);
    return response.json();
  }

  /**
   * Health check
   */
  static async healthCheck() {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.json();
  }
}

export default API;
export { API_BASE_URL };
