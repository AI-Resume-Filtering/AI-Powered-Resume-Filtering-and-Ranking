const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

class API {
  static async _requestJson(path, options = {}) {
    try {
      const response = await fetch(`${API_BASE_URL}${path}`, options);
      let payload = {};

      try {
        payload = await response.json();
      } catch {
        payload = {};
      }

      if (!response.ok) {
        return {
          success: false,
          status: response.status,
          message: payload.message || `Request failed (${response.status})`,
          ...payload,
        };
      }

      return { status: response.status, ...payload };
    } catch {
      return {
        success: false,
        status: 0,
        message: 'Cannot reach backend server. Ensure Backend is running on port 5000.',
      };
    }
  }

  /** S4/A1: Return the stored JWT token. */
  static getToken() {
    return localStorage.getItem('authToken');
  }

  /** Build Authorization header for protected company endpoints. */
  static _authHeader() {
    const token = API.getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  static async registerCompany(data) {
    return API._requestJson('/company/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
  }

  static async loginCompany(email, password) {
    return API._requestJson('/company/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });
  }

  static async requestPasswordReset(email, frontendBaseUrl = '') {
    return API._requestJson('/company/forgot-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, frontendBaseUrl }),
    });
  }

  static async resetPassword(token, password, confirmPassword) {
    return API._requestJson('/company/reset-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token, password, confirmPassword }),
    });
  }

  static async validateResetToken(token) {
    return API._requestJson('/company/reset-password/validate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token }),
    });
  }

  static async getAllJobs(params = {}) {
    const query = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null && value !== "") {
        query.set(key, String(value));
      }
    });

    const suffix = query.toString() ? `?${query.toString()}` : "";
    const response = await fetch(`${API_BASE_URL}/jobs${suffix}`);
    return response.json();
  }

  static async getJobDetails(jobId) {
    const response = await fetch(`${API_BASE_URL}/jobs/${jobId}`);
    return response.json();
  }

  /** S4: Sends auth token so backend can verify ownership. */
  static async getCompanyJobs(companyId) {
    const response = await fetch(`${API_BASE_URL}/company/${companyId}/jobs`, {
      headers: { ...API._authHeader() },
    });
    return response.json();
  }

  static async postJob(formData) {
    const response = await fetch(`${API_BASE_URL}/company/post-job`, {
      method: 'POST',
      headers: { ...API._authHeader() },
      body: formData,
    });
    return response.json();
  }

  static async deleteJob(jobId) {
    const response = await fetch(`${API_BASE_URL}/company/delete-job`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json', ...API._authHeader() },
      body: JSON.stringify({ jobId }),
    });
    return response.json();
  }

  static async applyForJob(formData) {
    const response = await fetch(`${API_BASE_URL}/apply`, {
      method: 'POST',
      body: formData,
    });
    return response.json();
  }

  /** A3: Poll the async pipeline status for a submitted application. */
  static async getApplicationStatus(applicationId) {
    const response = await fetch(`${API_BASE_URL}/apply/status/${applicationId}`);
    return response.json();
  }

  static async getCompanyResumes(companyId) {
    const response = await fetch(`${API_BASE_URL}/company/${companyId}/resumes`, {
      headers: { ...API._authHeader() },
    });
    return response.json();
  }

  static async getCompanyHistory(companyId) {
    const response = await fetch(`${API_BASE_URL}/company/${companyId}/history`, {
      headers: { ...API._authHeader() },
    });
    return response.json();
  }

  /** Email template: load the company's saved selection notification template. */
  static async getEmailTemplate(companyId) {
    const response = await fetch(`${API_BASE_URL}/company/${companyId}/email-template`, {
      headers: { ...API._authHeader() },
    });
    return response.json();
  }

  /** Email template: save/update the company's selection notification template. */
  static async saveEmailTemplate(companyId, subject, body) {
    const response = await fetch(`${API_BASE_URL}/company/${companyId}/email-template`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...API._authHeader() },
      body: JSON.stringify({ subject, body }),
    });
    return response.json();
  }

  static async getCompanyScoreThreshold(companyId) {
    const response = await fetch(`${API_BASE_URL}/company/${companyId}/score-threshold`, {
      headers: { ...API._authHeader() },
    });
    return response.json();
  }

  static async saveCompanyScoreThreshold(companyId, scoreThreshold) {
    const response = await fetch(`${API_BASE_URL}/company/${companyId}/score-threshold`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...API._authHeader() },
      body: JSON.stringify({ scoreThreshold }),
    });
    return response.json();
  }

  static async healthCheck() {
    return API._requestJson('/health');
  }
}

export default API;
export { API_BASE_URL };
