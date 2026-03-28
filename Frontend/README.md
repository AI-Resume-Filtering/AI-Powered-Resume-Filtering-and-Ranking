# Frontend Module

Frontend provides the user interface for both recruiter and candidate flows.

It is built with React and talks to Backend APIs for authentication, jobs, applications, results, and feedback.

## 1. Goals of this module

1. Provide simple recruiter workflows.
2. Provide candidate application workflow.
3. Show async processing states clearly.
4. Show ranked candidates and score breakdown.
5. Keep API integration environment-configurable.

## 2. Directory structure and sub-file guide

Main app root:
1. `Frontend/react-project/package.json`
Purpose: project scripts and dependencies.
2. `Frontend/react-project/vite.config.js`
Purpose: Vite dev/build configuration.
3. `Frontend/react-project/index.html`
Purpose: app host HTML.
4. `Frontend/react-project/.env` and `.env.example`
Purpose: frontend environment configuration.

App bootstrap:
1. `Frontend/react-project/src/main.jsx`
Purpose: React app boot entrypoint.
2. `Frontend/react-project/src/App.jsx`
Purpose: top-level route/app shell.

API layer:
1. `Frontend/react-project/src/api/index.js`
Purpose: central API calls and base URL usage.

Pages:
1. `src/pages/Index.jsx`
Purpose: landing/start page.
2. `src/pages/CompanyRegister.jsx`
Purpose: recruiter registration flow.
3. `src/pages/CompanyLogin.jsx`
Purpose: recruiter login flow.
4. `src/pages/ForgotPassword.jsx`
Purpose: password reset initiation.
5. `src/pages/ResetPassword.jsx`
Purpose: complete password reset via token.
6. `src/pages/JobList.jsx`
Purpose: list available jobs for candidates.
7. `src/pages/ApplyJob.jsx`
Purpose: candidate application form and upload flow.

Dashboard pages:
1. `src/pages/dashboard/CompanyDashboard.jsx`
Purpose: recruiter control panel container.
2. `src/pages/dashboard/Home.jsx`
Purpose: dashboard overview and key counts.
3. `src/pages/dashboard/PostJob.jsx`
Purpose: create new job postings.
4. `src/pages/dashboard/Resumes.jsx`
Purpose: view applications, scores, and statuses.
5. `src/pages/dashboard/History.jsx`
Purpose: historical application data.
6. `src/pages/dashboard/EmailTemplate.jsx`
Purpose: customize selection email template.
7. `src/pages/dashboard/ScoreThreshold.jsx`
Purpose: configure selection threshold.
8. `src/pages/dashboard/AuditLogs.jsx`
Purpose: view audit-style activity records.
9. `src/pages/dashboard/Delete.jsx`
Purpose: controlled deletion flows.
10. `src/pages/dashboard/Sidebar.jsx`
Purpose: dashboard navigation.

Styling:
1. `src/styles/*.css`
Purpose: per-page and shared UI styles.

## 3. User journeys in detail

Recruiter journey:
1. Register/login.
2. Create job with description.
3. Monitor incoming applications.
4. Review scores and ranking.
5. Mark selected/rejected and submit feedback.
6. Tune threshold/email template where needed.

Candidate journey:
1. Browse job list.
2. Open apply page.
3. Fill details and upload resume PDF.
4. Submit application.
5. Wait while backend processes asynchronously.

## 4. Frontend-backend interaction pattern

1. UI action triggers API call.
2. Frontend sends payload or multipart file upload.
3. Backend returns immediate state.
4. For async flows, frontend polls status endpoint.
5. UI updates status/results once processing completes.

## 5. Async UX behavior

Apply flow should never freeze the UI.

Expected behavior:
1. Show processing state immediately after submit.
2. Poll for status updates.
3. Render final score/status once backend updates application.
4. Show clear error message if API call fails.

## 6. Environment configuration

Key variable:
1. `VITE_API_BASE_URL`

Examples:
1. Local proxy style: `/api`
2. Direct backend URL: `http://localhost:5000/api`

## 7. Troubleshooting checklist

If API calls fail in browser:
1. Verify backend is running.
2. Verify `VITE_API_BASE_URL` value.
3. Verify CORS settings on backend.

If apply form uploads fail:
1. Confirm multipart request is being sent.
2. Confirm PDF file validation rules.
3. Check backend response body and status code.

If dashboard data does not refresh:
1. Check polling/refresh trigger logic.
2. Inspect network tab for failing endpoints.
3. Check token validity and auth headers.

## 8. Build and run

From `Frontend/react-project/`:
1. Install dependencies with npm install.
2. Run dev server with npm run dev.
3. Build production bundle with npm run build.

## 9. Extension points

1. Add route guards and role-based screens.
2. Add reusable API error interceptor layer.
3. Add form schema validation library.
4. Add table pagination/filtering for large datasets.

## 10. Interview questions and answers

1. Why polling for application status?
Answer: pipeline work is asynchronous and may finish after initial submit response.

2. Why keep API base URL in environment?
Answer: the same code can run in local, staging, and production with config-only changes.

3. How do you handle long-running operations in UX?
Answer: show intermediate states, avoid blocking UI, and update incrementally.
