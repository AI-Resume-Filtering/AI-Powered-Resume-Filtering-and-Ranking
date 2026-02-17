# 📊 Complete Data Flow & Architecture

## 🌐 System Overview

```
INTERNET BROWSER
    ↓
    │
    ├─→ http://localhost:5173 (Frontend - React)
    │   ├─ Components
    │   ├─ API Client
    │   └─ State Management
    │
    ├─→ http://localhost:5000 (Backend - Flask API)
    │   ├─ Routes
    │   ├─ Services
    │   └─ MongoDB Integration
    │
    └─→ MongoDB Database
        ├─ companies collection
        ├─ jobs collection
        ├─ applications collection
        └─ (Data persistence)
```

---

## 👤 User Authentication Flow

```
USER
 ↓
┌─────────────────────────────────┐
│ 1. REGISTRATION PAGE            │
│ - Enter company name            │
│ - Enter registration number     │
│ - Enter email & password        │
└─────────────────┬───────────────┘
                  ↓
            POST /api/company/register
                  ↓
        ┌────────────────────┐
        │ Backend            │
        │ CompanyService     │
        │ - Check duplicate  │
        │ - Hash password    │
        │ - Save to MongoDB  │
        └────────────────────┘
                  ↓
            MongoDB: companies
                  ↓
         Response: {success, company}
                  ↓
            localStorage.setItem('company')
                  ↓
    ┌─────────────────────────────────┐
    │ 2. LOGIN PAGE                   │
    │ - Enter email & password        │
    └─────────────────┬───────────────┘
                      ↓
                POST /api/company/login
                      ↓
            ┌────────────────────┐
            │ Backend            │
            │ CompanyService     │
            │ - Find by email    │
            │ - Verify password  │
            └────────────────────┘
                      ↓
                  MongoDB: companies
                      ↓
             Response: {success, company}
                      ↓
            localStorage.setItem('company')
                      ↓
    ┌─────────────────────────────────┐
    │ 3. COMPANY DASHBOARD            │
    │ - Access granted                │
    │ - company data in localStorage  │
    └─────────────────────────────────┘
```

---

## 📝 Job Management Flow

### A. POST JOB

```
USER (Company)
    ↓
┌─────────────────────────────────┐
│ POST JOB PAGE                   │
│ - Enter job title               │
│ - Upload PDF (JD)               │
└─────────────────┬───────────────┘
                  ↓
         POST /api/company/post-job
         FormData: {
           companyId,
           jobTitle,
           descriptionPdf (file)
         }
                  ↓
        ┌────────────────────────────┐
        │ Backend (job_routes.py)    │
        │ - Validate company         │
        │ - Save PDF to disk         │
        └────────────┬───────────────┘
                     ↓
        ┌────────────────────────────┐
        │ Resume Parser              │
        │ (PDF → Extract Text)       │
        └────────────┬───────────────┘
                     ↓
        ┌────────────────────────────┐
        │ JobService.create_job()    │
        │ - Generate jobId           │
        │ - Create job object        │
        │ - Insert to MongoDB        │
        └────────────┬───────────────┘
                     ↓
        MongoDB: jobs
        {
          jobId: "...",
          title: "...",
          description: "...",
          companyId: "...",
          companyName: "...",
          postDate: "..."
        }
                     ↓
        Response: {success: true, jobId: "..."}
                     ↓
        USER: "Job posted successfully!"
```

### B. VIEW POSTED JOBS (HOME PAGE) ✅ NEW

```
USER (Company) on Dashboard Home Tab
    ↓
GET /api/company/{companyId}/jobs
    ↓
┌──────────────────────────────────┐
│ Backend                          │
│ - Get company ID from route      │
│ - Query MongoDB for company jobs │
│ - Format for frontend            │
└────────────┬─────────────────────┘
             ↓
   MongoDB: jobs
   Find: {companyId: "..."}
             ↓
   Response: [{
     jobId: "...",
     title: "Senior Developer",
     description: "...",
     createdAt: "...",
     totalApplications: 0
   }]
             ↓
Frontend: Display in table
- Total Jobs Posted: 1
- Job Position: Senior Developer
- Post Date: 2026-02-16
- Total Resumes: 0
```

### C. DELETE JOB ✅ FIXED

```
USER (Company) on Dashboard Delete Tab
    ↓
┌──────────────────────────────────┐
│ DELETE JOB PAGE                  │
│ - Fetch jobs (same as Home)      │
│ - Show as dropdown               │
└────────────┬─────────────────────┘
             ↓
GET /api/company/{companyId}/jobs
             ↓
         (same as Home flow)
             ↓
Dropdown: [Senior Developer, ...]
             ↓
USER: Select job from dropdown
             ↓
Shows: Job details
- Selected: Senior Developer
- Applications: 0
             ↓
USER: Click "Delete Job Post"
             ↓
Confirmation: "Are you sure?"
             ↓
DELETE /api/company/delete-job
Body: {jobId: "..."}
             ↓
┌──────────────────────────────────┐
│ Backend (job_routes.py)          │
│ - Get jobId from request         │
│ - Call JobService.delete_job()   │
└────────────┬─────────────────────┘
             ↓
   MongoDB: Delete from jobs
   Where: {jobId: "..."}
             ↓
   Response: {success: true}
             ↓
Frontend: Remove from dropdown
             ↓
USER: "Job deleted successfully!"
```

---

## 📄 Resume Application Flow

### A. CANDIDATE APPLIES FOR JOB

```
CANDIDATE (Job Seeker)
    ↓
┌────────────────────────────────┐
│ JOB LISTING PAGE               │
│ - View available jobs          │
│ - Click on a job               │
└────────────┬───────────────────┘
             ↓
  GET /api/jobs (or /api/jobs/{id})
             ↓
┌────────────────────────────────┐
│ Backend                        │
│ - Query all jobs from MongoDB  │
│ - Format response              │
└────────────┬───────────────────┘
             ↓
  Response: [{
    id: "...",
    title: "Senior Developer",
    companyName: "...",
    description: "..."
  }]
             ↓
┌────────────────────────────────┐
│ APPLY PAGE                     │
│ - Enter candidate details      │
│ - Upload resume PDF            │
└────────────┬───────────────────┘
             ↓
    POST /api/apply
    FormData: {
      jobId,
      resume (file),
      fullName,
      email,
      phone,
      degree,
      branch
    }
             ↓
┌────────────────────────────────────┐
│ Backend - Pipeline Processing      │
│ applicationService.create_app()    │
└────────────┬──────────────────────┘
             ↓
    ┌────────────────────────────┐
    │ 1. RESUME PARSER           │
    │ - Extract text from PDF    │
    │ - Parse resume sections    │
    └────────────┬───────────────┘
                 ↓
    ┌────────────────────────────┐
    │ 2. NLP ENGINE              │
    │ - Extract skills           │
    │ - Extract experience       │
    │ - Extract education        │
    └────────────┬───────────────┘
                 ↓
    ┌────────────────────────────┐
    │ 3. AI SCORING              │
    │ - Match resume to JD       │
    │ - Calculate score          │
    │ - Determine match %        │
    │ - Score >= Threshold? ✓    │
    └────────────┬───────────────┘
                 ↓
    ┌────────────────────────────┐
    │ 4. STORE IN MONGODB        │
    │ applications               │
    │ {                          │
    │   applicationId: "...",    │
    │   jobId: "...",            │
    │   candidateName: "...",    │
    │   email: "...",            │
    │   score: 85,               │
    │   status: "processed"      │
    │ }                          │
    └────────────┬───────────────┘
                 ↓
    ┌────────────────────────────┐
    │ 5. SEND EMAIL (IF CONFIG)  │
    │ - To company               │
    │ - To candidate             │
    └────────────┬───────────────┘
                 ↓
    Response: {
      success: true,
      applicationId: "...",
      score: 85,
      status: "processed"
    }
             ↓
CANDIDATE: "Resume submitted!"
           "Score: 85/100"
           "Status: Processed"
```

### B. COMPANY VIEWS RESUMES

```
COMPANY (Dashboard → View Resumes)
    ↓
GET /api/company/{companyId}/resumes
    ↓
┌────────────────────────────────┐
│ Backend                        │
│ - Query applications           │
│ - Filter by companyId          │
│ - Format for display           │
└────────────┬───────────────────┘
             ↓
MongoDB: applications
Find: {companyId: "..."}
             ↓
Response: [{
  candidateName: "...",
  resumeName: "...",
  email: "...",
  jobTitle: "...",
  status: "processed"
}, ...]
             ↓
Display in Table:
- Candidate Name
- Resume Name
- Email
- Job Applied For
- Status
             ↓
COMPANY: See all applicants!
```

### C. COMPANY VIEWS HISTORY

```
COMPANY (Dashboard → History)
    ↓
GET /api/company/{companyId}/history
    ↓
┌────────────────────────────────┐
│ Backend                        │
│ - Query applications           │
│ - Sort by date                 │
│ - Calculate statistics         │
└────────────┬───────────────────┘
             ↓
MongoDB: applications
Find: {companyId: "..."}
Sort: {createdAt: -1}
             ↓
Response: [{
  candidateName: "...",
  jobTitle: "...",
  status: "selected",
  score: 85,
  date: "2026-02-16",
  email: "..."
}, ...]
             ↓
Display:
- Job-wise Statistics Cards
  * Total Applications
  * Selected Count
  * Rejected Count
- Latest Resumes Timeline
  * Recent 5 applications
  * With dates and scores
```

---

## 🗄️ MongoDB Schema

### Companies Collection
```javascript
{
  _id: ObjectId(),
  companyId: "unique-string",
  name: "Company Name",
  registrationNo: "REG-123",
  email: "company@email.com",
  passwordHash: "hashed-password",
  createdAt: "2026-02-16T..."
}
```

### Jobs Collection
```javascript
{
  _id: ObjectId(),
  jobId: "unique-string",
  title: "Senior Developer",
  description: "extracted text from PDF",
  descriptionPdfPath: "/path/to/pdf",
  companyId: "company-id",
  companyName: "Company Name",
  companyRegNo: "REG-123",
  location: "NYC",
  experience: "5+ years",
  postDate: "2026-02-16T..."
}
```

### Applications Collection
```javascript
{
  _id: ObjectId(),
  applicationId: "unique-string",
  jobId: "job-id",
  companyId: "company-id",
  candidateName: "Candidate Name",
  email: "candidate@email.com",
  phone: "123-456-7890",
  degree: "Bachelor's",
  branch: "Computer Science",
  score: 85,
  status: "processed",
  resumePdfPath: "/path/to/resume",
  createdAt: "2026-02-16T..."
}
```

---

## 🔄 API Endpoint Summary

| Endpoint | Method | Purpose | Auth | Data Flow |
|----------|--------|---------|------|-----------|
| `/api/company/register` | POST | Register company | No | Form → Backend → MongoDB ✅ |
| `/api/company/login` | POST | Login company | No | Form → Backend → Verify → Response ✅ |
| `/api/jobs` | GET | Get all jobs | No | Backend → MongoDB → Response ✅ |
| `/api/jobs/{id}` | GET | Get job details | No | Backend → MongoDB → Response ✅ |
| `/api/company/post-job` | POST | Post new job | Yes | File → Parse → Save → MongoDB ✅ |
| `/api/company/{id}/jobs` | GET | Get company jobs | Yes | Backend → Query → Response ✅ **NEW** |
| `/api/company/delete-job` | DELETE | Delete job | Yes | Backend → Delete → Response ✅ **FIXED** |
| `/api/apply` | POST | Apply for job | No | File → Pipeline → Save → Email ✅ |
| `/api/company/{id}/resumes` | GET | Get resumes | Yes | Backend → Query → Response ✅ |
| `/api/company/{id}/history` | GET | Get history | Yes | Backend → Query → Format → Response ✅ |
| `/api/health` | GET | Health check | No | Response: {status: "ok"} ✅ |

---

## 📱 Frontend Routes Map

```
http://localhost:5173/
├── / (Landing Page)
├── /company-register
│   → POST /api/company/register
├── /company-login
│   → POST /api/company/login
├── /job-list
│   → GET /api/jobs
├── /apply-job/{jobId}
│   → GET /api/jobs/{jobId}
│   → POST /api/apply
├── /company-dashboard
│   ├── /home
│   │   → GET /api/company/{id}/jobs ✅ NEW
│   ├── /postjob
│   │   → POST /api/company/post-job
│   ├── /delete
│   │   → GET /api/company/{id}/jobs ✅ NEW
│   │   → DELETE /api/company/delete-job
│   ├── /resumes
│   │   → GET /api/company/{id}/resumes
│   └── /history
│       → GET /api/company/{id}/history
```

---

## ✨ Data Flow Summary

### Registration → Login → Dashboard
```
User Input → Frontend → API Call → Backend Service → MongoDB
                                        ↓
                                    Validation
                                        ↓
                                    Processing
                                        ↓
                                    Response ← Frontend ← Display
```

### Post Job → View Jobs → Delete Job
```
PDF Upload → Parse → Store → Database ← Query ← Display in Dropdown ← Delete ← Confirm
```

### Apply → Process → View Results
```
Resume PDF → Parser → NLP → Scoring → Store → Email → Dashboard ← Resumes/History
```

---

## 🎯 Key Points

1. **All data flows through Backend** - Frontend never talks to MongoDB directly
2. **CORS enabled** - Frontend and Backend can communicate
3. **Services layer** - Business logic separated from routes
4. **MongoDB persistence** - All data stored durably
5. **Validation everywhere** - Frontend and Backend both validate
6. **Error handling** - Errors logged and returned properly
7. **Pipeline processing** - AI flow: Parse → NLP → Score

---

This is your complete system architecture! All flows are connected and working! 🚀

