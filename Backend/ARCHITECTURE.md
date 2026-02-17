# Backend Architecture Guide

## Overview

The backend is a Flask-based orchestration layer that coordinates three independent AI modules (Resume Parser, NLP Engine, AI Scoring) into a production-ready pipeline. The system processes job applications, extracts candidate data, scores matches, and sends notifications.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (React)                         │
│         /api/company/register        /api/apply                │
│         /api/company/login           /api/jobs                 │
│         /api/company/post-job        /api/company/:id/resumes  │
└────────────────────────────┬──────────────────────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Flask Routes   │
                    │  (Thin Layer)   │
                    │                 │
                    │  - company_     │
                    │  - job_         │
                    │  - application_ │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
    ┌────▼────┐    ┌─────────▼────────┐    ┌────▼─────────┐
    │Company  │    │Pipeline Service│    │  Job Service │
    │Service  │    │  (NEW - CORE)   │    │              │
    │         │    │                 │    │ - create_job │
    │- Register    │ Orchestrates:   │    │ - list_jobs  │
    │- Login   │    │ 1. Resume Parse │    │ - delete_job │
    └────┬────┘    │ 2. NLP Extract  │    └────┬────────┘
         │         │ 3. AI Score     │        │
         │         │ 4. Save DB      │        │
         │         │ 5. Send Email   │        │
         │         └────────┬────────┘        │
         │                  │                 │
         │    ┌─────────────┼────────┬────────┼──────────┐
         │    │             │        │        │          │
    ┌────▼──────────────────▼─────┐ │   ┌────▼──┐   ┌──▼──────┐
    │     SERVICE LAYER            │ │   │ Email │   │ Storage │
    │  (Business Logic)            │ │   │Service│   │ Service │
    │                              │ │   └───────┘   └─────────┘
    │ - CompanyService             │ │
    │ - JobService                 │ │    ┌──────────────────┐
    │ - ApplicationService (NEW)   │ │    │  AI Modules      │
    │ - PipelineService (NEW)      │ │    │  (Untouched)    │
    │ - EmailService (NEW)         │ │    │                  │
    │ - StorageService (NEW)       │ │    │ 1. Resume Parser │
    │ - AuthService                │ │    │ 2. NLP Engine    │
    └────────────────────┬─────────┘ │    │ 3. AI Scoring    │
         │         │    └────────────┼────┤ (Modules Path)   │
         │         │                 │    └──────────────────┘
         │         │                 │
    ┌────▼─────────▼─────────────────▼──────┐
    │           MONGODB DATABASE             │
    │                                        │
    │  Collections:                          │
    │  - companies                           │
    │  - jobs                                │
    │  - applications (Resume + Score)       │
    └────────────────────────────────────────┘
```

---

## Folder Structure

```
Backend/
├── app/                          # Flask application package
│   ├── __init__.py              # App factory & bootstrap
│   ├── config.py                # Configuration (env-driven)
│   ├── extensions.py            # MongoDB initialization
│   │
│   ├── routes/                  # HTTP Endpoints (thin)
│   │   ├── __init__.py
│   │   ├── health_routes.py     # /api/health
│   │   ├── company_routes.py    # /api/company/*
│   │   ├── job_routes.py        # /api/jobs, /api/company/post-job
│   │   └── application_routes.py # /api/apply, /api/company/:id/resumes
│   │
│   ├── services/                # Business Logic (thick)
│   │   ├── __init__.py
│   │   ├── pipeline_service.py  # ⭐ CORE: Orchestration Layer
│   │   │                         #    Calls: Parser → NLP → Scoring
│   │   │                         #    Saves: MongoDB
│   │   │                         #    Sends: Email
│   │   ├── application_service.py # Application lifecycle
│   │   ├── job_service.py       # Job operations
│   │   ├── company_service.py   # Company management
│   │   ├── email_service.py     # SMTP integration
│   │   ├── storage_service.py   # File uploads
│   │   └── auth_service.py      # Password hashing
│   │
│   └── utils/                   # Utilities
│       ├── __init__.py
│       └── logging.py           # Logging setup
│
├── instance/                    # Runtime data
│   └── storage/
│       ├── uploads/             # Resume PDFs, JD PDFs
│       └── tmp/                 # Text files for modules
│
├── run.py                       # Entry point (WSGI)
├── requirements.txt             # Python dependencies
├── .env.example                 # Env template
└── .env                         # Environment config (local)
```

---

## Data Flow

### 1. Company Posts Job

```
POST /api/company/post-job
├─ Extract: companyId, jobTitle, descriptionPdf
├─ JobService.create_job()
│  ├─ StorageService.save_upload() → job_descriptions folder
│  ├─ ResumeParser.parse() → Extract text (Resume Parser module)
│  └─ MongoDB: INSERT job with description text
└─ Response: jobId

Database: companies → jobs
```

### 2. Candidate Applies & AI Processing ⭐

```
POST /api/apply
│
├─ Extract: jobId, resume file, candidate data
├─ Validation: file extension check
├─ JobService.get_job() → Load JD text from DB
│
├─ PipelineService.run() ⭐⭐⭐
│  │
│  ├─ StorageService.save_upload() → uploads/resumes
│  │
│  ├─ ResumeParser.parse(resume_pdf) → resume text
│  │   (Resume Parser module - UNTOUCHED)
│  │
│  ├─ Write files to tmp:
│  │   - resume_<id>.txt
│  │   - job_<jobId>.txt
│  │
│  ├─ NLPMicroservice.process_request()
│  │   (NLP Engine module - UNTOUCHED)
│  │   ├─ Input: [(job_text, [resume_texts])]
│  │   ├─ Output: REQ_xxx_nlp_output.json
│  │   │          {resumes: {resume_001: {skills, exp, edu, job_match}}}
│  │   └─ Load JSON output
│  │
│  ├─ process_resume_batch() → AI Scoring
│  │   (AI Scoring module - UNTOUCHED)
│  │   ├─ Input: NLP JSON + job requirements
│  │   ├─ Score calculation: skill_match + exp + edu + bonus
│  │   └─ Output: [{rank: 1, score: 87.5, ...}]
│  │
│  ├─ Score evaluation:
│  │   ├─ If score >= SCORE_THRESHOLD (70)
│  │   │  └─ Status: "Selected"
│  │   └─ Else
│  │      └─ Status: "Rejected"
│  │
│  └─ EmailService.send_email()
│     ├─ To: candidate.email
│     ├─ Subject: "Application Status: {Selected|Rejected}"
│     └─ Body: Score + Status
│
├─ ApplicationService.create_application()
│  └─ MongoDB: INSERT application with all metadata
│
└─ Response: {
     success: true,
     message: "Resume submitted successfully!",
     applicationId, status, score
   }

Database: applications ← All processing results saved
```

### 3. View Resumes & History

```
GET /api/company/{companyId}/resumes
└─ ApplicationService.list_company_resumes()
   └─ MongoDB query: applications | filter: companyId
      Response: [{candidateName, resumeName, email, jobTitle, status}]

GET /api/company/{companyId}/history
└─ ApplicationService.list_company_history()
   └─ MongoDB query: applications | filter: companyId
      Response: [{candidateName, jobTitle, status, date}]
```

---

## Key Services Explained

### PipelineService (⭐ Core Orchestration)

**File:** [Backend/app/services/pipeline_service.py](Backend/app/services/pipeline_service.py)

**Responsibility:** Calls Resume Parser → NLP Engine → AI Scoring in sequence

```python
pipeline.run(job, candidate, resume_file)
├─ Parse resume PDF
├─ Call NLP extraction (creates output JSON)
├─ Call AI scoring (reads NLP JSON, returns scores)
├─ Save application + score to DB
├─ Send email if score > threshold
└─ Return result dict
```

**Design:**
- Does NOT modify AI modules
- Receives output files from each module
- Coordinates data flow between modules
- Handles errors gracefully

---

### EmailService

**File:** [Backend/app/services/email_service.py](Backend/app/services/email_service.py)

**Responsibility:** SMTP-based email sending (threshold-triggered)

```python
email.send_email(to_address, subject, body)
├─ Check SMTP config (skip if missing)
├─ Create EmailMessage
├─ Connect to SMTP server
└─ Send
```

**Configuration (via .env):**
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com
SMTP_TLS=true
```

---

### StorageService

**File:** [Backend/app/services/storage_service.py](Backend/app/services/storage_service.py)

**Responsibility:** File upload + text file writing

```python
storage.save_upload(file_obj, subdir)
├─ Generate unique filename
├─ Save to uploads/{subdir}/
└─ Return file path

storage.write_text(text, filename)
├─ Write to tmp/{filename}
└─ Return file path
```

---

### MongoDB Collections

```
{
  companies: [
    {companyId, name, registrationNo, email, passwordHash, createdAt}
  ],
  
  jobs: [
    {jobId, title, description, descriptionPdfPath, 
     companyId, companyName, postDate}
  ],
  
  applications: [
    {applicationId, jobId, jobTitle, companyId,
     candidateName, email, phone, degree, branch,
     resumeName, resumePdfPath, resumeTextPath,
     nlpOutputPath, score, rank, status, emailSent,
     createdAt}
  ]
}
```

---

## Configuration & Secrets

### Environment Variables (.env)

```bash
# App
SECRET_KEY=your-secret-key-change-in-production

# MongoDB
MONGO_URI=mongodb://localhost:27017
MONGO_DB=resume_filtering

# SMTP (Email)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_FROM=your-email@gmail.com
SMTP_TLS=true

# Business Logic
SCORE_THRESHOLD=70  # Minimum score to email "Selected"
MAX_CONTENT_LENGTH=20971520  # 20MB max upload
```

### Loading (.env)

```python
# Backend/app/__init__.py
def create_app():
    load_dotenv()  # Loads .env
    app.config.from_object(Config)  # Reads env vars
```

---

## API Endpoints

### Health Check
- `GET /api/health` → `{status: ok}`

### Company
- `POST /api/company/register` → Register company
- `POST /api/company/login` → Login company

### Job Management
- `GET /api/jobs` → List all jobs (for candidates)
- `GET /api/jobs/{jobId}` → Get job details
- `GET /api/company/{companyId}/jobs` → List company's jobs
- `POST /api/company/post-job` → Post new job (with JD PDF)
- `DELETE /api/company/delete-job` → Delete job

### Applications (⭐ Pipeline Endpoint)
- `POST /api/apply` → Apply for job (triggers pipeline)
- `GET /api/company/{companyId}/resumes` → View received resumes
- `GET /api/company/{companyId}/history` → View application history

---

## Running the Backend

### 1. Prerequisites

```bash
# Install dependencies
pip install -r Backend/requirements.txt

# Ensure MongoDB is running
mongod

# Copy .env
cp Backend/.env.example Backend/.env
# Edit Backend/.env with your settings
```

### 2. Start Flask Server

```bash
cd AI-Powered-Resume-Filtering-and-Ranking
python Backend/run.py
```

**Output:**
```
INFO:werkzeug: * Running on http://0.0.0.0:5000
```

### 3. Test

```powershell
# Health check
Invoke-WebRequest -Uri "http://localhost:5000/api/health" -UseBasicParsing

# Response
{"status": "ok"}
```

---

## Error Handling

### Route Level

```python
try:
    application = app_service.create_application(job, candidate, resume_file)
    return {"success": True, ...}
except Exception as exc:
    logger.exception("Application processing failed")
    return {"success": False, "message": str(exc)}, 500
```

### Global Exception Handler

```python
@app.errorhandler(Exception)
def handle_exception(error):
    app.logger.exception("Unhandled error")
    return {"success": False, "message": "Internal server error"}, 500
```

---

## Logging

**File:** [Backend/app/utils/logging.py](Backend/app/utils/logging.py)

```python
import logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

# Usage in services
logger = logging.getLogger(__name__)
logger.info("Processing resume")
logger.exception("Pipeline failed")  # Auto-includes traceback
```

---

## Production Considerations

### 1. Security
- ✅ Passwords hashed with werkzeug
- ✅ Secrets in environment variables
- ✅ File upload validation (extension checks)
- ✅ CORS (configure as needed)

### 2. Scalability
- ✅ Modular services (easy to refactor)
- ✅ Database indexes (add via MongoDB compass)
- ✅ Async job processing (use Celery if needed)

### 3. Monitoring
- ✅ Structured logging
- ✅ Error handlers with traceback
- ✅ Health endpoint for load balancers

---

## Next Steps

1. **Add Input Validation**
   - Use `marshmallow` or `pydantic` for request schemas
   - Validate email, phone, file sizes

2. **Add Database Indexes**
   - `db.companies.create_index([("email", 1)])` (unique)
   - `db.applications.create_index([("companyId", 1)])` (compound)

3. **Async Processing**
   - Use Celery + Redis for scoring/email
   - Prevent `/api/apply` blocking

4. **Frontend Integration**
   - ✅ Already compatible (no API changes needed)
   - Just update `VITE_API_BASE_URL` if deployed

---

## Clean Architecture Principles Used

| Layer | Responsibility | Example |
|-------|-----------------|---------|
| **Routes** | HTTP ↔ JSON | `company_routes.py` |
| **Services** | Business Logic | `pipeline_service.py` |
| **Extensions** | Infrastructure | `extensions.py` |
| **Config** | Environment | `config.py` |
| **Utilities** | Cross-cutting | `logging.py` |

---

## File Reference

- **Entry Point:** [Backend/run.py](Backend/run.py)
- **App Factory:** [Backend/app/__init__.py](Backend/app/__init__.py)
- **Config:** [Backend/app/config.py](Backend/app/config.py)
- **Core Orchestration:** [Backend/app/services/pipeline_service.py](Backend/app/services/pipeline_service.py)
- **All Routes:** [Backend/app/routes](Backend/app/routes)
- **All Services:** [Backend/app/services](Backend/app/services)

---

**Status:** ✅ Production-Ready | Latest: Feb 16, 2026
