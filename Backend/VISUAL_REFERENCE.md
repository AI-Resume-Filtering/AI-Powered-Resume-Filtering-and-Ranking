# 🚀 Backend System - Visual Reference Guide

## System Status Board

```
┌─────────────────────────────────────────────────────────┐
│                    SYSTEM STATUS                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ✅ BACKEND RUNNING                                    │
│     Status: http://localhost:5000/api/health           │
│     Response: {"status": "ok"}                          │
│                                                         │
│  ✅ MONGODB READY                                      │
│     Connection: mongodb://localhost:27017              │
│     Database: resume_filtering                         │
│     Collections: companies, jobs, applications         │
│                                                         │
│  ✅ FLASK APP INITIALIZED                              │
│     Version: Flask 2.3.0+                              │
│     Mode: Development (debug can be enabled)           │
│     Port: 5000                                         │
│                                                         │
│  ✅ ENVIRONMENT CONFIGURED                             │
│     Config File: Backend/.env                          │
│     SMTP: Configured (emails will send when score>=70) │
│     Secret Key: Loaded from .env                       │
│                                                         │
│  ✅ ROUTES REGISTERED                                  │
│     Health: /api/health                               │
│     Company: /api/company/*                            │
│     Jobs: /api/jobs*                                   │
│     Applications: /api/apply (PIPELINE)                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Architecture Quick Reference

### High-Level Layer Diagram

```
        FRONTEND (React)
              │ HTTP
              ▼
    ┌─────────────────────┐
    │   FLASK ROUTES      │
    │  (Thin Controllers) │
    │                     │
    │ /api/company/*      │
    │ /api/jobs*          │
    │ /api/apply ⭐       │
    └─────────┬───────────┘
              │ Call
              ▼
    ┌─────────────────────────────────────┐
    │    SERVICE LAYER                    │
    │  (Business Logic)                   │
    │                                     │
    │ ⭐ PipelineService                  │
    │    ├─ Resume Parser                 │
    │    ├─ NLP Engine                    │
    │    ├─ AI Scoring                    │
    │    ├─ Email Service                 │
    │    └─ Storage Service               │
    │                                     │
    │ + CompanyService                    │
    │ + JobService                        │
    │ + ApplicationService                │
    │ + AuthService                       │
    └────────────┬────────────┬───────────┘
                 │            │
                 ▼            ▼
             MONGODB      SMTP SERVER
          (Persistence)  (Notifications)
```

### Request-Response Flow

```
INCOMING REQUEST
    │
    ├─→ Route Handler (validation)
    │      │
    │      ├─→ Service Layer (logic)
    │      │      │
    │      │      ├─→ Database (read/write)
    │      │      │
    │      │      └─→ External Services (email, storage)
    │      │
    │      └─→ Return response dict
    │
    └─→ JSON Response (status 200/400/500)
```

---

## API Endpoint Map

```
                    /api (BASE)
                        │
        ┌───────────────┼───────────────┐
        │               │               │
    HEALTH          COMPANY          JOBS          APPLICATION
    ------          -------          ----          -----------
    GET /           │               │              POST /apply
    health          │               │              ↓
    (heartbeat)     │               │              [FULL PIPELINE]
                    │               │              │
                ┌─POST /register     GET /          ├─Resume Parse
                │                   (all jobs)      ├─NLP Extract
            ┌─POST /login/           │              ├─AI Score
            │                    GET /{id}          ├─Save MongoDB
            │                    (job details)      └─Send Email
            │                        │
            │                    POST /company/post-job
            │                    (create job with PDF)
            │                        │
            │                    DELETE /company/delete-job
            │
            └─ POST /logout (future)
```

---

## Data Model

```
COMPANIES
┌─────────────────────────────────────┐
│ companyId (PK)                      │
│ name                                │
│ registrationNo (UNIQUE)             │
│ email (UNIQUE)                      │
│ passwordHash (bcrypt)               │
│ createdAt (ISO timestamp)           │
└─────────────────────────────────────┘
          │ (1:N)
          ↓
        JOBS
    ┌──────────────────────────────────┐
    │ jobId (PK)                       │
    │ companyId (FK) ← Company         │
    │ title                            │
    │ description (from PDF)           │
    │ descriptionPdfPath               │
    │ postDate (ISO timestamp)         │
    └──────────────────────────────────┘
             │ (1:N)
             ↓
        APPLICATIONS ⭐
    ┌─────────────────────────────────────┐
    │ applicationId (PK)                  │
    │ jobId (FK) ← Job                    │
    │ companyId (FK) ← Company            │
    │ candidateName                       │
    │ email                               │
    │ resumePdfPath                       │
    │ nlpOutputPath (← NLP Engine)        │
    │ score (0-100, from AI Scoring)      │
    │ rank (1, 2, 3, ...)                 │
    │ status ("Selected" or "Rejected")   │
    │ emailSent (boolean)                 │
    │ createdAt (ISO timestamp)           │
    └─────────────────────────────────────┘
```

---

## Processing Pipeline Sequence

```
┌─ Application Submit ─────────────────────────────┐
│ POST /api/apply                                 │
│ {jobId, resume.pdf, candidate.email, ...}      │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
        ┌────────────────────┐
        │ VALIDATION LAYER   │
        ├────────────────────┤
        │ ✓ File format OK   │
        │ ✓ Job exists       │
        │ ✓ Required fields  │
        └────────┬───────────┘
                 │
                 ▼
        ┌─────────────────────────┐
        │ STORAGE PHASE           │
        ├─────────────────────────┤
        │ 1. Save resumePDF       │ → /uploads/resumes/
        │ 2. Save JD text to tmp  │ → /tmp/job_xxx.txt
        │ 3. Save Resume text     │ → /tmp/resume_xxx.txt
        └────────┬────────────────┘
                 │
                 ▼
        ┌──────────────────────────┐
        │ PIPELINE EXECUTION       │
        ├──────────────────────────┤
        │                          │
        │ A) RESUME PARSER         │
        │    Input: resume.pdf     │
        │    Output: resume_text   │
        │    Module: Resume_Parser │
        │                          │
        │ B) NLP ENGINE            │
        │    Input: [resume.txt,   │
        │            job.txt]      │
        │    Output: NLP JSON      │
        │    {skills, exp, edu}    │
        │    Module: Nlp_Engine    │
        │                          │
        │ C) AI SCORING            │
        │    Input: NLP JSON       │
        │    Output: score (0-100) │
        │    Module: Ai_Scoring    │
        │                          │
        └────────┬─────────────────┘
                 │
                 ▼
        ┌────────────────────────┐
        │ EVALUATION              │
        ├────────────────────────┤
        │ IF score >= 70:         │
        │   status = "Selected"   │
        │ ELSE:                   │
        │   status = "Rejected"   │
        └────────┬───────────────┘
                 │
                 ▼
        ┌────────────────────────────┐
        │ EMAIL SERVICE              │
        ├────────────────────────────┤
        │ TO: candidate.email        │
        │ SUBJECT: Application Status│
        │ BODY: {score, status}      │
        │ (Only if SMTP configured)  │
        └────────┬───────────────────┘
                 │
                 ▼
        ┌───────────────────────────────────┐
        │ DATABASE SAVE                     │
        ├───────────────────────────────────┤
        │ INSERT into applications:         │
        │ {                                 │
        │   applicationId, jobId,           │
        │   candidateName, email,           │
        │   resumePdfPath,                  │
        │   nlpOutputPath,                  │
        │   score, rank, status,            │
        │   emailSent, createdAt            │
        │ }                                 │
        └────────┬────────────────────────┘
                 │
                 ▼
        ┌─────────────────────────────┐
        │ RESPONSE                    │
        ├─────────────────────────────┤
        │ {                           │
        │   "success": true,          │
        │   "message": "...",         │
        │   "applicationId": "...",   │
        │   "status": "Selected",     │
        │   "score": 87.5             │
        │ }                           │
        └─────────────────────────────┘
```

---

## File System Layout

```
PROJECT ROOT (AI-Powered-Resume-Filtering-and-Ranking/)
│
├── Backend/ ⭐ NEW
│   ├── app/
│   │   ├── __init__.py              ← Flask app factory
│   │   ├── config.py                ← Env configuration
│   │   ├── extensions.py            ← MongoDB setup
│   │   │
│   │   ├── routes/                  ← HTTP layer (thin)
│   │   │   ├── __init__.py
│   │   │   ├── health_routes.py
│   │   │   ├── company_routes.py
│   │   │   ├── job_routes.py
│   │   │   └── application_routes.py
│   │   │
│   │   ├── services/                ← Logic layer (thick)
│   │   │   ├── pipeline_service.py  ⭐ CORE
│   │   │   ├── application_service.py
│   │   │   ├── job_service.py
│   │   │   ├── company_service.py
│   │   │   ├── email_service.py
│   │   │   ├── storage_service.py
│   │   │   └── auth_service.py
│   │   │
│   │   └── utils/
│   │       └── logging.py           ← Logging setup
│   │
│   ├── instance/
│   │   └── storage/
│   │       ├── uploads/             ← Resume & JD PDFs
│   │       │   ├── jobs/
│   │       │   └── resumes/
│   │       └── tmp/                 ← Text files (NLP input)
│   │
│   ├── run.py                       ← Start here! Entry point
│   ├── requirements.txt              ← Dependencies
│   ├── .env                          ← Secrets (local)
│   ├── .env.example                  ← Template
│   ├── README.md                     ← Quick start
│   ├── ARCHITECTURE.md               ← Deep dive
│   ├── TESTING_GUIDE.md              ← Step-by-step tests
│   └── SUMMARY.md                    ← This overview
│
├── Resume_Parser/                   ← UNTOUCHED
│   └── resume_parser.py
│
├── Nlp_Engine/                      ← UNTOUCHED
│   └── Nlp_service.py
│
├── Ai_Scoring/                      ← UNTOUCHED
│   └── scorer.py
│
└── Frontend/                        ← COMPATIBLE
    └── react-project/
        └── src/api/index.js         ← Already configured
```

---

## Service Dependency Graph

```
                    HTTP Request
                         │
                         ▼
                 ┌──────────────────┐
                 │  ROUTE HANDLER   │
                 └────────┬─────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
          ▼               ▼               ▼
    CompanyService    JobService    ApplicationService
          │               │               │
          │               │               ├─→ PipelineService ⭐
          │               │               │   ├─→ ResumeParser
          │               │               │   ├─→ NLPEngine
          │               │               │   ├─→ AIScoringModule
          │               │               │   └─→ EmailService
          │               │               │
          │               │               ├─→ StorageService
          │               │               │
          │               │               └─→ AuthService
          │               │
          └───────────────┼───────────────┘
                          │
                          ▼
                   MongoDB Database
                   (Collections)
```

---

## Configuration Hierarchy

```
DEFAULT (Hardcoded in config.py)
    ↓
ENVIRONMENT VARIABLES (.env file)
    ↓
RUNTIME CONFIG (app.config object)

Example:
1. Default: SCORE_THRESHOLD = 70
2. .env: SCORE_THRESHOLD=80
3. Runtime: app.config["SCORE_THRESHOLD"] = 80
```

---

## Error Handling Flow

```
                    Request
                        │
                        ▼
            ┌───────────────────────┐
            │ Route Handler Try/Catch│
            └───────────┬───────────┘
                        │
            ┌───────────┴───────────┐
            │                       │
            ▼                       ▼
        Success              Exception Caught
            │                       │
            │                  ┌────▼────────┐
            │                  │ Log Error   │
            │                  │ (traceback) │
            │                  └────┬────────┘
            │                       │
            ▼                       ▼
        Response:           Response:
        {"success": true}   {"success": false,
                            "message": "..."}
        Status: 200         Status: 500
```

---

## Environment Configuration

```
┌─────────────────────────────────────┐
│  Backend/.env (Local Development)   │
├─────────────────────────────────────┤
│                                     │
│ SECRET_KEY=dev-key                  │
│ │                                   │
│ ├─ MONGO_URI=mongodb://localhost    │
│ ├─ MONGO_DB=resume_filtering        │
│ │                                   │
│ ├─ SMTP_HOST=smtp.gmail.com         │
│ ├─ SMTP_PORT=587                    │
│ ├─ SMTP_USER=your-email@gmail.com   │
│ ├─ SMTP_PASSWORD=your-app-pass      │
│ ├─ SMTP_FROM=your-email@gmail.com   │
│ ├─ SMTP_TLS=true                    │
│ │                                   │
│ ├─ SCORE_THRESHOLD=70               │
│ └─ MAX_CONTENT_LENGTH=20971520(20MB)│
│                                     │
└─────────────────────────────────────┘
        ↓ load_dotenv()
┌─────────────────────────────────────┐
│  app.config (Runtime Config)        │
│  (Used throughout application)      │
└─────────────────────────────────────┘
```

---

## Testing Workflow

```
1. HEALTH CHECK
   GET /api/health
   ✓ Backend running?

2. COMPANY SETUP
   POST /api/company/register
   ✓ Company created?
   ✓ Password hashed?

3. JOB POSTING
   POST /api/company/post-job (with PDF)
   ✓ PDF stored?
   ✓ Text extracted?
   ✓ Job saved to DB?

4. APPLICATION PIPELINE ⭐
   POST /api/apply (with resume PDF)
   ✓ Resume stored?
   ✓ Parser extracted text?
   ✓ NLP processed?
   ✓ AI scored (15-30 seconds)?
   ✓ Email sent?
   ✓ Application saved?

5. VIEW RESULTS
   GET /api/company/{id}/resumes
   ✓ Application visible?
   ✓ Correct status/score?

6. DATABASE CHECK
   mongosh: db.applications.find({})
   ✓ All data persisted?
```

---

## Performance Expectations

```
ENDPOINT                Time      Bottleneck
────────────────────────────────────────────
/api/health             <10ms     None
/api/company/register   <50ms     Password hash
/api/company/login      <50ms     Password verify
POST /api/company/      <200ms    PDF to text
post-job                          parsing
──────────────────────────────────────────── ⭐
POST /api/apply         15-30sec  Full pipeline:
                                  - Parser: 2-5sec
                                  - NLP: 5-10sec
                                  - Scoring: 1-3sec  
                                  - Email: <1sec
                                  - DB save: <100ms
────────────────────────────────────────────
/api/company/{id}/      <100ms    DB query +
resumes                           JSON format
/api/company/{id}/      <100ms    DB query +
history                           JSON format
────────────────────────────────────────────
```

---

## Security Checklist

```
INPUT VALIDATION
  ✓ File extension check (PDF only)
  ✓ File size limit (config: 20MB)
  ✓ Required field validation
  
AUTHENTICATION
  ✓ Passwords hashed (werkzeug bcrypt)
  ✓ Secrets in environment (.env)
  ✓ No sensitive data in logs
  
DATABASE SECURITY
  ✓ Input sanitization (MongoDB driver)
  ✓ Connection string from env
  ✓ Database name from env
  
ERROR HANDLING
  ✓ Generic 500 errors (no internals leaked)
  ✓ Exception logging with traceback
  ✓ Graceful fallbacks (e.g., skip email)
  
FUTURE (Not implemented yet)
  - CORS headers (if cross-domain)
  - Rate limiting
  - Request timeout
  - HTTPS/SSL
```

---

## Quick Commands

### Start Backend
```bash
cd AI-Powered-Resume-Filtering-and-Ranking
python Backend/run.py
```

### Install Dependencies
```bash
pip install -r Backend/requirements.txt
```

### View Logs
```bash
# Real-time logs (if running in terminal)
# Logs appear in the terminal where you ran Backend/run.py

# Or save to file
python Backend/run.py > backend.log 2>&1 &
tail -f backend.log
```

### Check Endpoints
```powershell
# Health
curl http://localhost:5000/api/health

# All jobs
curl http://localhost:5000/api/jobs
```

### Database Access
```bash
mongosh
use resume_filtering
db.applications.find({}).pretty()
```

---

## Status Indicators

```
🟢 GREEN  = Running normally
🟡 YELLOW = Warning (non-blocking)
🔴 RED    = Error (blocking)

CURRENT STATUS:
🟢 Backend      Running on port 5000
🟢 Flask App    Initialized
🟢 MongoDB      Connected (if running)
🟢 Routes       All registered
🟢 Services     All loaded
🟢 Email        Ready (if SMTP configured)
```

---

## Support Resources

| Topic | File |
|-------|------|
| Quick overview | [SUMMARY.md](SUMMARY.md) |
| Architecture deep dive | [ARCHITECTURE.md](ARCHITECTURE.md) |
| Step-by-step testing | [TESTING_GUIDE.md](TESTING_GUIDE.md) |
| Getting started | [README.md](README.md) |
| This visual guide | This file |

---

**Last Updated:** February 16, 2026  
**Backend Status:** ✅ Running  
**Ready for:** Development & Testing
