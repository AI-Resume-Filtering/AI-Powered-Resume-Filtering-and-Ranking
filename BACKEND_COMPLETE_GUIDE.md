# 🚀 COMPLETE BACKEND INTEGRATION GUIDE
## Resume Filtering & Ranking System

**Date:** February 17, 2026  
**Technology Stack:** Flask, MongoDB, RESTful API, CORS  
**Purpose:** Complete explanation of backend architecture, integration, and data flow

---

## 📋 TABLE OF CONTENTS
1. [System Architecture Overview](#1-system-architecture-overview)
2. [Database Schema & Collections](#2-database-schema--collections)
3. [Backend Folder Structure](#3-backend-folder-structure)
4. [Core Services (Business Logic)](#4-core-services-business-logic)
5. [API Routes & Endpoints](#5-api-routes--endpoints)
6. [Frontend-Backend Integration](#6-frontend-backend-integration)
7. [AI Model Integration](#7-ai-model-integration)
8. [Complete Data Flow](#8-complete-data-flow)
9. [Environment Configuration](#9-environment-configuration)
10. [How to Run & Test](#10-how-to-run--test)

---

# 1. SYSTEM ARCHITECTURE OVERVIEW

## 🏗️ High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                              │
│                   http://localhost:5173                          │
│  ┌─────────────┐  ┌────────────┐  ┌─────────────┐              │
│  │ Register    │  │ Dashboard  │  │ Apply Job   │              │
│  │ Login       │  │ Post Job   │  │ My Profile  │              │
│  │ Company     │  │ Delete Job │  │ History     │              │
│  └──────┬──────┘  └─────┬──────┘  └──────┬──────┘              │
└─────────┼────────────────┼────────────────┼──────────────────────┘
          │                │                │
          └────────────────┼────────────────┘
                           │
                ┌──────────▼──────────┐
                │   FRONTEND API      │
                │   (HTTP Client)     │
                │   Makes requests    │
                │   to /api/*         │
                └──────────┬──────────┘
                           │
        ┌──────────────────▼──────────────────┐
        │  CORS Enabled on Backend            │
        │  Allows requests from localhost:5173│
        │  Methods: GET, POST, PUT, DELETE    │
        └──────────────────┬──────────────────┘
                           │
    ┌──────────────────────▼──────────────────────┐
    │    BACKEND (Flask) - ORCHESTRATION LAYER    │
    │         http://localhost:5000               │
    │                                             │
    │  ┌──────────────────────────────────────┐  │
    │  │ Routes (Thin Layer)                  │  │
    │  │ - company_routes.py                  │  │
    │  │ - job_routes.py                      │  │
    │  │ - application_routes.py              │  │
    │  │ - health_routes.py                   │  │
    │  └──────────────────┬───────────────────┘  │
    │                     │                       │
    │  ┌──────────────────▼───────────────────┐  │
    │  │ Services (Business Logic - THICK)    │  │
    │  │ ┌─ CompanyService ──────────────┐   │  │
    │  │ │ ├─ register_company()         │   │  │
    │  │ │ ├─ login_company()            │   │  │
    │  │ │ └─ Authentication logic       │   │  │
    │  │ └───────────────────────────────┘   │  │
    │  │                                       │  │
    │  │ ┌─ JobService ──────────────────┐   │  │
    │  │ │ ├─ create_job()               │   │  │
    │  │ │ ├─ list_jobs()                │   │  │
    │  │ │ ├─ delete_job()               │   │  │
    │  │ │ └─ list_company_jobs()        │   │  │
    │  │ └───────────────────────────────┘   │  │
    │  │                                       │  │
    │  │ ┌─ ApplicationService ──────────┐   │  │
    │  │ │ ├─ create_application()       │   │  │
    │  │ │ ├─ list_company_resumes()     │   │  │
    │  │ │ └─ list_company_history()     │   │  │
    │  │ └───────────────────────────────┘   │  │
    │  │                                       │  │
    │  │ ┌─ PipelineService ⭐ CORE ────┐   │  │
    │  │ │ Orchestrates:                 │   │  │
    │  │ │ 1. Resume Parser (PDF→Text)   │   │  │
    │  │ │ 2. NLP Engine (Extract data)  │   │  │
    │  │ │ 3. AI Scorer (Score resume)   │   │  │
    │  │ │ 4. MongoDB (Save results)     │   │  │
    │  │ │ 5. Email Service (Notify)     │   │  │
    │  │ └───────────────────────────────┘   │  │
    │  │                                       │  │
    │  │ ┌─ StorageService ──────────────┐   │  │
    │  │ │ ├─ save_upload()              │   │  │
    │  │ │ └─ write_text()               │   │  │
    │  │ └───────────────────────────────┘   │  │
    │  │                                       │  │
    │  │ ┌─ EmailService ────────────────┐   │  │
    │  │ │ └─ send_email()               │   │  │
    │  │ └───────────────────────────────┘   │  │
    │  └───────────────────────────────────────┘  │
    └────────┬─────────────────────┬──────────────┘
             │                     │
    ┌────────▼────────┐  ┌────────▼──────────┐
    │  AI MODULES     │  │  MONGODB DATABASE │
    │  (Untouched)    │  │  (Data Storage)   │
    │                 │  │                   │
    │ 1. Resume Parser│  │ Collections:      │
    │ 2. NLP Engine   │  │ - companies       │
    │ 3. AI Scorer    │  │ - jobs            │
    │                 │  │ - applications    │
    └─────────────────┘  └───────────────────┘
```

## 🔄 Key Concept: Orchest ration Layer

The backend is **NOT** a microservice. It's an **orchestration layer** that:

1. **Receives requests** from frontend
2. **Validates input** (user, job, file)
3. **Calls AI modules** in sequence:
   - Resume Parser (PDF → plain text)
   - NLP Engine (extract skills, experience, education)
   - AI Scorer (score resume vs job description)
4. **Stores results** in MongoDB
5. **Sends notifications** via email
6. **Returns response** to frontend

---

# 2. DATABASE SCHEMA & COLLECTIONS

## MongoDB Collections & Documents

### ✅ COLLECTIONS COLLECTION (Companies)

```javascript
// Collection: "companies"
// Purpose: Store company registration & login credentials

{
  "_id": ObjectId("..."),                          // MongoDB auto ID (hidden)
  "companyId": "a1b2c3d4e5f6...",                 // Our unique ID (hex)
  "name": "Acme Corporation",
  "registrationNo": "ABC123456",
  "email": "hr@acme.com",
  "passwordHash": "$2b$12$KIXxP...",              // bcrypt hashed (never store plain!)
  "createdAt": "2026-02-15T10:30:00"
}
```

**Fields Explained:**
- `companyId`: Unique identifier (UUID hex) - use this in routes
- `passwordHash`: Bcrypt encrypted password - verified during login
- `_id`: Automatically created by MongoDB - not used in API

---

### 📝 JOBS COLLECTION

```javascript
// Collection: "jobs"
// Purpose: Store job postings with descriptions

{
  "_id": ObjectId("..."),
  "jobId": "job_abc123...",                        // Our unique ID
  "title": "Senior Full Stack Developer",
  "description": "We are looking for a developer...",  // Extracted from PDF
  "descriptionPdfPath": "/uploads/job_descriptions/abc123_job.pdf",
  "companyId": "a1b2c3d4e5f6...",                 // Links to company
  "companyName": "Acme Corporation",
  "companyRegNo": "ABC123456",
  "companyEmail": "hr@acme.com",
  "location": "New York, NY",
  "experience": "2-5 years",
  "postDate": "2026-02-16T14:45:00"
}
```

**Key Relationships:**
- `companyId` → links to "companies" collection
- `description` → extracted from PDF using Resume Parser
- All JD data used by NLP Engine to extract requirements

---

### 💼 APPLICATIONS COLLECTION

```javascript
// Collection: "applications"
// Purpose: Store candidate applications with scores

{
  "_id": ObjectId("..."),
  "applicationId": "app_xyz789...",                // Our unique ID
  
  // Job Reference
  "jobId": "job_abc123...",
  "jobTitle": "Senior Full Stack Developer",
  "companyId": "a1b2c3d4e5f6...",
  "companyRegNo": "ABC123456",
  
  // Candidate Details
  "candidateName": "John Doe",
  "email": "john@example.com",
  "phone": "+1-555-1234",
  "degree": "B.Tech",
  "branch": "Computer Science",
  "resumeName": "John_Doe_Resume.pdf",
  
  // File Paths
  "resumePdfPath": "/uploads/resumes/abc123_John_Doe_Resume.pdf",
  "resumeTextPath": "/tmp/resume_app_xyz789.txt",
  "nlpOutputPath": "Nlp_Engine/output/REQ_20260217_143022_nlp_output.json",
  
  // Scoring Results
  "score": 82.5,                                   // Final score (0-100)
  "rank": 1,                                       // Rank among applications for this job
  "status": "Selected",                            // "Selected" or "Rejected"
  
  // Notification
  "emailSent": true,
  "createdAt": "2026-02-17T14:30:22"
}
```

**Scoring Breakdown:**
- `score`: Sum of 4 metrics:
  - Skill Match (40-70%)
  - Experience (5-45%)
  - Education (5-20%)
  - Preferred Skills (5-10%)
- `rank`: Auto-assigned based on score for each job
- `status`: Determined by `score >= SCORE_THRESHOLD`

---

# 3. BACKEND FOLDER STRUCTURE

```
Backend/
├── run.py                              # ⭐ ENTRY POINT
│   └─ Imports: app = create_app()
│   └─ Runs: app.run(host="0.0.0.0", port=5000)
│
├── app/                                # Flask application package
│   │
│   ├── __init__.py                     # ⭐ APP FACTORY
│   │   ├─ load_dotenv() → reads .env file
│   │   ├─ create_app() → initializes Flask
│   │   ├─ CORS configuration → allows frontend requests
│   │   ├─ init_mongo() → connects to MongoDB
│   │   └─ register_blueprints() → registers all routes
│   │
│   ├── config.py                       # Configuration
│   │   ├─ BASE_DIR, BACKEND_ROOT, PROJECT_ROOT paths
│   │   ├─ MONGO_URI, MONGO_DB names
│   │   ├─ SMTP_HOST, SMTP_PORT (email)
│   │   ├─ SCORE_THRESHOLD (70 by default)
│   │   ├─ MAX_CONTENT_LENGTH (file size limit)
│   │   └─ UPLOADS_DIR, TMP_DIR paths
│   │
│   ├── extensions.py                   # MongoDB initialization
│   │   ├─ init_mongo(app) → connects MongoClient
│   │   └─ get_db(app) → returns database instance
│   │
│   ├── routes/                         # HTTP Endpoints (THIN LAYER)
│   │   ├── __init__.py → register_blueprints()
│   │   ├── health_routes.py → /api/health
│   │   ├── company_routes.py → /api/company/*
│   │   ├── job_routes.py → /api/jobs, /api/company/*
│   │   └── application_routes.py → /api/apply, /api/resumes/*
│   │
│   ├── services/                       # Business Logic (THICK LAYER)
│   │   ├── __init__.py
│   │   ├── pipeline_service.py         # ⭐ ORCHESTRATION CORE
│   │   ├── application_service.py
│   │   ├── job_service.py
│   │   ├── company_service.py
│   │   ├── email_service.py
│   │   ├── storage_service.py
│   │   └── auth_service.py
│   │
│   ├── utils/
│   │   └── logging.py → configure logging
│   │
│   └── __pycache__/
│
├── instance/                           # Runtime files
│   └── storage/
│       ├── uploads/ → saved PDFs
│       │   ├── resumes/ → candidate resumes
│       │   └── job_descriptions/ → job description PDFs
│       └── tmp/ → temporary text files
│
├── .env                                # Environment variables (not in git)
├── requirements.txt                    # Python dependencies
└── run.py → Entry point
```

---

# 4. CORE SERVICES - BUSINESS LOGIC

## 4.1 PipelineService ⭐ (The Core Orchestrator)

**Location:** `Backend/app/services/pipeline_service.py`

**Purpose:** Orchestrates the entire processing pipeline

**Code:**
```python
class PipelineService:
    def __init__(self, storage_service, email_service, project_root: str, score_threshold: float):
        self.storage = storage_service          # File handling
        self.email = email_service              # Email sending
        self.project_root = project_root        # Root directory path
        self.score_threshold = score_threshold  # Score cutoff (70)
        self.parser = ResumeParser()            # PDF parser

    def run(self, job: dict, candidate: dict, resume_file) -> dict:
        """
        Main orchestration method
        
        Flow:
        1. Save resume PDF to disk
        2. Parse resume PDF → extract text
        3. Write text to temporary file
        4. Create job description text file
        5. Call NLP Engine → extract skills, experience, education
        6. Call AI Scorer → calculate score
        7. Send email if selected
        8. Return results
        """
        
        # Step 1: Save uploaded resume PDF
        resume_pdf_path = self.storage.save_upload(resume_file, "resumes")
        
        # Step 2: Parse PDF → extract plain text
        resume_text = self.parser.parse(resume_pdf_path)
        
        # Step 3: Get job description (already extracted from PDF)
        jd_text = job.get("description", "")
        
        # Step 4: Write text files for NLP processing
        resume_txt_path = self.storage.write_text(
            resume_text, 
            f"resume_{candidate['applicationId']}.txt"
        )
        jd_txt_path = self.storage.write_text(
            jd_text, 
            f"job_{job['jobId']}.txt"
        )
        
        # Step 5: Call NLP Engine (from Nlp_Engine folder)
        from Nlp_Engine.Nlp_service import process_resumes
        nlp_response = process_resumes(jd_txt_path, [resume_txt_path])
        
        if not nlp_response.get("success"):
            raise RuntimeError(nlp_response.get("error"))
        
        # Get NLP output file path
        output_path = nlp_response.get("output_path")
        output_file = os.path.join(self.project_root, output_path)
        
        # Step 6: Read NLP output
        with open(output_file, "r", encoding="utf-8") as f:
            nlp_data = json.load(f)
        
        # Extract job requirements for scoring
        job_requirements = nlp_data.get("job_requirements", {})
        scoring_metadata = {"job_requirements": job_requirements}
        
        # Step 7: Call AI Scorer (from Ai_Scoring folder)
        from Ai_Scoring.Ai_Scoring.scorer import process_resume_batch
        scored_results = process_resume_batch(Path(output_file).name, scoring_metadata)
        
        # Get score from results
        result = scored_results[0] if scored_results else {}
        score = float(result.get("total_score", 0))
        
        # Step 8: Determine status based on score threshold
        status = "Selected" if score >= self.score_threshold else "Rejected"
        
        # Step 9: Send email if selected
        email_sent = False
        if status == "Selected" and candidate.get("email"):
            subject = f"Shortlisted: {job.get('title', 'Your application')}"
            body = f"""Hello {candidate.get('fullName')},

Great news — your application for {job.get('title')} at {job.get('companyName')} 
has been shortlisted.

Your Score: {score}/100

Thank you for applying!
Best regards,
{job.get('companyName')} Hiring Team"""
            
            self.email.send_email(candidate["email"], subject, body)
            email_sent = True
        
        # Step 10: Return all results
        return {
            "resumePdfPath": resume_pdf_path,
            "resumeTextPath": resume_txt_path,
            "nlpOutputPath": output_path,
            "score": score,
            "rank": result.get("rank"),
            "status": status,
            "emailSent": email_sent,
        }
```

**Key Points:**
- **Integration Point:** Connects Resume Parser → NLP Engine → AI Scorer
- **Error Handling:** Raises exceptions if any step fails
- **Database:** Returns data (not saves) - ApplicationService handles DB
- **Email:** Sends selection notification to candidate
- **Configuration:** Uses score_threshold from .env

---

## 4.2 ApplicationService

**Location:** `Backend/app/services/application_service.py`

**Code:**
```python
class ApplicationService:
    def __init__(self, db, pipeline_service=None):
        self.collection = db["applications"]  # MongoDB "applications" collection
        self.pipeline = pipeline_service       # Uses pipeline to process resume

    def create_application(self, job: dict, candidate: dict, resume_file) -> dict:
        """
        Creates an application record:
        1. Generate unique applicationId
        2. Call pipeline to process resume
        3. Store everything in MongoDB
        4. Return complete application object
        """
        application_id = uuid.uuid4().hex  # Generate unique ID
        candidate["applicationId"] = application_id
        
        # Run the pipeline (orchestrates everything)
        pipeline_result = self.pipeline.run(job, candidate, resume_file)
        
        # Create application document for MongoDB
        application = {
            "applicationId": application_id,
            "jobId": job.get("jobId"),
            "jobTitle": job.get("title"),
            "companyId": job.get("companyId"),
            "candidateName": candidate.get("fullName"),
            "email": candidate.get("email"),
            "score": pipeline_result.get("score"),
            "status": pipeline_result.get("status"),  # "Selected" or "Rejected"
            "emailSent": pipeline_result.get("emailSent"),
            "createdAt": datetime.utcnow().isoformat(),
            # ... other fields
        }
        
        # Save to MongoDB
        self.collection.insert_one(application)
        return application

    def list_company_resumes(self, company_id: str) -> list:
        """Returns all applications/resumes for a company"""
        return list(self.collection.find(
            {"companyId": company_id},
            {"_id": 0}  # Exclude MongoDB's _id field
        ))

    def list_company_history(self, company_id: str) -> list:
        """Returns historical applications/resumes"""
        return list(self.collection.find(
            {"companyId": company_id},
            {"_id": 0}
        ))
```

---

## 4.3 JobService

**Location:** `Backend/app/services/job_service.py`

**Code:**
```python
class JobService:
    def __init__(self, db, storage_service=None):
        self.collection = db["jobs"]      # MongoDB "jobs" collection
        self.storage = storage_service     # File storage service
        self.parser = ResumeParser()       # PDF parser

    def create_job(self, company: dict, job_title: str, jd_file) -> dict:
        """
        Creates a job posting:
        1. Save PDF to disk
        2. Parse PDF → extract text
        3. Create job document
        4. Store in MongoDB
        """
        # Save PDF file
        pdf_path = self.storage.save_upload(jd_file, "job_descriptions")
        
        # Extract text from PDF
        description_text = self.parser.parse(pdf_path)
        
        # Create job document
        job_id = uuid.uuid4().hex
        job = {
            "jobId": job_id,
            "title": job_title,
            "description": description_text,        # Extracted text
            "descriptionPdfPath": pdf_path,         # Original PDF
            "companyId": company.get("companyId"),
            "companyName": company.get("name"),
            "companyEmail": company.get("email"),
            "postDate": datetime.utcnow().isoformat(),
        }
        
        # Save to MongoDB
        self.collection.insert_one(job)
        return job

    def get_job(self, job_id: str) -> dict:
        """Get single job by ID"""
        return self.collection.find_one({"jobId": job_id})

    def list_jobs(self) -> list:
        """Get all jobs"""
        return list(self.collection.find({}, {"_id": 0}))

    def list_company_jobs(self, company_id: str) -> list:
        """Get all jobs for a specific company"""
        return list(self.collection.find(
            {"companyId": company_id}, 
            {"_id": 0}
        ))

    def delete_job(self, job_id: str) -> bool:
        """Delete a job"""
        result = self.collection.delete_one({"jobId": job_id})
        return result.deleted_count > 0
```

---

## 4.4 CompanyService

**Location:** `Backend/app/services/company_service.py`

**Code:**
```python
class CompanyService:
    def __init__(self, db):
        self.collection = db["companies"]  # MongoDB "companies" collection

    def register_company(self, company_name: str, registration_no: str, 
                        email: str, password: str) -> dict:
        """
        Register a new company:
        1. Check if email already exists
        2. Hash password (bcrypt)
        3. Create company document
        4. Store in MongoDB
        """
        # Check for duplicates
        existing = self.collection.find_one({"email": email})
        if existing:
            return {"success": False, "message": "Company already exists"}
        
        # Generate unique ID
        company_id = uuid.uuid4().hex
        
        # Create company document
        company = {
            "companyId": company_id,
            "name": company_name,
            "registrationNo": registration_no,
            "email": email,
            "passwordHash": hash_password(password),  # Never store plain!
            "createdAt": datetime.utcnow().isoformat(),
        }
        
        # Save to MongoDB
        self.collection.insert_one(company)
        return {"success": True, "company": self._public_company(company)}

    def login_company(self, email: str, password: str) -> dict:
        """
        Login company:
        1. Find company by email
        2. Verify password hash
        3. Return company data
        """
        company = self.collection.find_one({"email": email})
        if not company:
            return {"success": False, "message": "Invalid email or password"}
        
        # Verify password (compares plain text with bcrypt hash)
        if not verify_password(password, company.get("passwordHash", "")):
            return {"success": False, "message": "Invalid email or password"}
        
        return {"success": True, "company": self._public_company(company)}

    @staticmethod
    def _public_company(company: dict) -> dict:
        """Return only non-sensitive fields"""
        return {
            "companyId": company.get("companyId"),
            "name": company.get("name"),
            "registrationNo": company.get("registrationNo"),
            "email": company.get("email"),
        }
```

---

## 4.5 StorageService

**Purpose:** File upload and temporary file management

**Code:**
```python
class StorageService:
    def __init__(self, uploads_dir: str, tmp_dir: str):
        self.uploads_dir = uploads_dir
        self.tmp_dir = tmp_dir
        Path(self.uploads_dir).mkdir(parents=True, exist_ok=True)
        Path(self.tmp_dir).mkdir(parents=True, exist_ok=True)

    def save_upload(self, file_storage, subdir: str) -> str:
        """
        Save uploaded file (resume PDF, job description PDF)
        
        Workflow:
        1. Get filename from upload
        2. Make it safe (remove ../, etc.)
        3. Generate unique prefix (UUID)
        4. Save to disk
        5. Return full path
        
        Example Output:
        /uploads/resumes/a1b2c3d4_John_Doe_Resume.pdf
        """
        safe_name = secure_filename(file_storage.filename or "upload.bin")
        unique_prefix = uuid.uuid4().hex
        target_dir = Path(self.uploads_dir) / subdir
        target_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"{unique_prefix}_{safe_name}"
        target_path = target_dir / filename
        file_storage.save(str(target_path))
        return str(target_path)

    def write_text(self, text: str, filename: str) -> str:
        """
        Write text to temporary file (for NLP processing)
        
        Example:
        - Input: resume text, "resume_app123.txt"
        - Output: /tmp/resume_app123.txt
        """
        target_path = Path(self.tmp_dir) / filename
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(text or "")
        return str(target_path)
```

---

## 4.6 EmailService

**Purpose:** Send SMTP emails to candidates

**Code:**
```python
class EmailService:
    def __init__(self, host: str, port: int, user: str, password: str, 
                 sender: str, use_tls: bool):
        self.host = host           # e.g., "smtp.gmail.com"
        self.port = port           # e.g., 587
        self.user = user           # email username
        self.password = password   # email password
        self.sender = sender       # from address
        self.use_tls = use_tls     # use TLS encryption

    def send_email(self, to_address: str, subject: str, body: str) -> None:
        """
        Send email via SMTP
        
        Note: SMTP settings come from .env file
        If not configured, logs warning and skips
        """
        if not self.host or not self.sender:
            logger.warning("SMTP settings missing, skipping email")
            return
        
        # Create email message
        message = EmailMessage()
        message["From"] = self.sender
        message["To"] = to_address
        message["Subject"] = subject
        message.set_content(body)
        
        try:
            # Connect to SMTP server
            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls()  # Encrypt connection
                if self.user and self.password:
                    server.login(self.user, self.password)  # Authenticate
                server.send_message(message)  # Send
            logger.info(f"Email sent to {to_address}")
        except Exception as e:
            logger.exception(f"Email failed: {str(e)}")
```

---

# 5. API ROUTES & ENDPOINTS

## 5.1 Company Routes

**File:** `Backend/app/routes/company_routes.py`

### **Endpoint 1: Register Company**
```
POST /api/company/register
```

**Frontend Request:**
```javascript
const response = await fetch("http://localhost:5000/api/company/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
        companyName: "Acme Corporation",
        registrationNo: "ABC123456",
        email: "hr@acme.com",
        password: "SecurePass123"
    })
});
const data = await response.json();
```

**Backend Code:**
```python
@company_bp.route("/company/register", methods=["POST"])
def register_company():
    payload = request.get_json() or {}
    
    # Validate required fields
    required = ["companyName", "registrationNo", "email", "password"]
    missing = [f for f in required if not payload.get(f)]
    if missing:
        return jsonify({"success": False, "message": f"Missing: {', '.join(missing)}"}), 400
    
    # Call service
    service = CompanyService(current_app.mongo_db)
    result = service.register_company(
        company_name=payload["companyName"],
        registration_no=payload["registrationNo"],
        email=payload["email"],
        password=payload["password"]
    )
    
    # Return response
    status = 200 if result.get("success") else 400
    return jsonify(result), status
```

**Backend Response (Success):**
```json
{
    "success": true,
    "company": {
        "companyId": "a1b2c3d4e5f6...",
        "name": "Acme Corporation",
        "registrationNo": "ABC123456",
        "email": "hr@acme.com"
    }
}
```

**Backend Response (Error):**
```json
{
    "success": false,
    "message": "Company already exists"
}
```

**What Happens:**
1. Route receives JSON payload
2. Validates all required fields
3. Calls CompanyService.register_company()
4. Service checks for duplicate email
5. Service hashes password using bcrypt
6. Service saves company to MongoDB "companies" collection
7. Route returns response (with/without company data)

---

### **Endpoint 2: Login Company**
```
POST /api/company/login
```

**Frontend Request:**
```javascript
const response = await fetch("http://localhost:5000/api/company/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
        email: "hr@acme.com",
        password: "SecurePass123"
    })
});
const data = await response.json();
// If success, save to localStorage:
localStorage.setItem("company", JSON.stringify(data.company));
```

**Backend Code:**
```python
@company_bp.route("/company/login", methods=["POST"])
def login_company():
    payload = request.get_json() or {}
    
    # Validate fields
    if not payload.get("email") or not payload.get("password"):
        return jsonify({"success": False, "message": "Email and password required"}), 400
    
    # Call service
    service = CompanyService(current_app.mongo_db)
    result = service.login_company(payload["email"], payload["password"])
    
    # Return response
    status = 200 if result.get("success") else 401
    return jsonify(result), status
```

**What Happens:**
1. Route receives email and password
2. Calls CompanyService.login_company()
3. Service queries MongoDB for company by email
4. Service calls verify_password() which:
   - Takes plain password
   - Takes bcrypt hash from database
   - Compares them (returns true/false)
5. If verified, returns company data
6. Frontend stores company in localStorage for future requests

---

## 5.2 Job Routes

**File:** `Backend/app/routes/job_routes.py`

### **Endpoint 3: Post Job**
```
POST /api/company/post-job
```

**Frontend Request (FormData):**
```javascript
const formData = new FormData();
formData.append("companyId", "a1b2c3d4...");
formData.append("jobTitle", "Senior Developer");
formData.append("descriptionPdf", pdfFile);  // File object

const response = await fetch("http://localhost:5000/api/company/post-job", {
    method: "POST",
    body: formData  // Note: FormData, not JSON
});
```

**Backend Code:**
```python
@job_bp.route("/company/post-job", methods=["POST"])
def post_job():
    # Get form data (not JSON!)
    company_id = request.form.get("companyId")
    job_title = request.form.get("jobTitle")
    jd_file = request.files.get("descriptionPdf")
    
    if not company_id or not job_title or not jd_file:
        return jsonify({"success": False, "message": "Missing required fields"}), 400
    
    # Validate file extension
    ext = os.path.splitext(jd_file.filename or "")[1].lower()
    if ext not in current_app.config["ALLOWED_JD_EXTENSIONS"]:  # {.pdf}
        return jsonify({"success": False, "message": "Only PDF job descriptions supported"}), 400
    
    # Get company from database
    company_service = CompanyService(current_app.mongo_db)
    company = company_service.collection.find_one({"companyId": company_id})
    if not company:
        return jsonify({"success": False, "message": "Company not found"}), 404
    
    # Create job
    storage = StorageService(current_app.config["UPLOADS_DIR"], current_app.config["TMP_DIR"])
    service = JobService(current_app.mongo_db, storage)
    job = service.create_job(company, job_title, jd_file)
    
    return jsonify({"success": True, "jobId": job.get("jobId")})
```

**What Happens:**
1. Route receives FormData with file
2. Validates company exists
3. Calls JobService.create_job() which:
   - Calls StorageService.save_upload() → saves PDF to disk
   - Calls ResumeParser.parse() → extracts text from PDF
   - Creates job document with extracted text
   - Saves job to MongoDB "jobs" collection
4. Returns jobId to frontend

---

### **Endpoint 4: List Company Jobs**
```
GET /api/company/{companyId}/jobs
```

**Frontend Request:**
```javascript
const response = await fetch("http://localhost:5000/api/company/a1b2c3d4.../jobs");
const jobs = await response.json();
```

**Backend Code:**
```python
@job_bp.route("/company/<company_id>/jobs", methods=["GET"])
def list_company_jobs(company_id):
    job_service = JobService(current_app.mongo_db, None)
    jobs = job_service.list_company_jobs(company_id)  # Query MongoDB
    
    # Count applications for each job
    applications = current_app.mongo_db["applications"]
    formatted = []
    for job in jobs:
        total_apps = applications.count_documents({"jobId": job.get("jobId")})
        formatted.append({
            "jobId": job.get("jobId"),
            "title": job.get("title"),
            "description": job.get("description"),
            "postDate": job.get("postDate"),
            "totalApplications": total_apps
        })
    
    return jsonify(formatted)
```

**What Happens:**
1. Route receives companyId
2. Calls JobService.list_company_jobs() → queries MongoDB
3. For each job, counts applications in "applications" collection
4. Returns formatted list to frontend

---

### **Endpoint 5: Delete Job**
```
DELETE /api/company/delete-job
```

**Frontend Request:**
```javascript
const response = await fetch("http://localhost:5000/api/company/delete-job", {
    method: "DELETE",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ jobId: "job_abc123..." })
});
```

**Backend Code:**
```python
@job_bp.route("/company/delete-job", methods=["DELETE"])
def delete_job():
    payload = request.get_json() or {}
    job_id = payload.get("jobId")
    
    if not job_id:
        return jsonify({"success": False, "message": "jobId required"}), 400
    
    service = JobService(current_app.mongo_db, None)
    deleted = service.delete_job(job_id)
    
    if not deleted:
        return jsonify({"success": False, "message": "Job not found"}), 404
    
    return jsonify({"success": True})
```

---

## 5.3 Application Routes (THE MAIN PIPELINE)

**File:** `Backend/app/routes/application_routes.py`

### **Endpoint 6: Apply for Job ⭐ (CORE)**
```
POST /api/apply
```

This is the **most important endpoint** - it triggers the entire pipeline.

**Frontend Request (FormData):**
```javascript
const formData = new FormData();
formData.append("jobId", "job_abc123...");
formData.append("resume", resumeFile);  // PDF file
formData.append("fullName", "John Doe");
formData.append("email", "john@example.com");
formData.append("phone", "+1-555-1234");
formData.append("degree", "B.Tech");
formData.append("branch", "Computer Science");

const response = await fetch("http://localhost:5000/api/apply", {
    method: "POST",
    body: formData
});
const result = await response.json();
// Result includes: success, status, score, applicationId
```

**Backend Code (Full Flow):**
```python
@application_bp.route("/apply", methods=["POST"])
def apply_for_job():
    # 1. EXTRACT FORM DATA
    form = request.form
    job_id = form.get("jobId")
    resume_file = request.files.get("resume")
    
    # Validate required fields
    if not job_id or not resume_file:
        return jsonify({"success": False, "message": "jobId and resume required"}), 400
    
    # Validate file type
    ext = os.path.splitext(resume_file.filename or "")[1].lower()
    if ext not in current_app.config["ALLOWED_RESUME_EXTENSIONS"]:  # {.pdf}
        return jsonify({"success": False, "message": "Only PDF resumes supported"}), 400
    
    # 2. GET CANDIDATE DATA
    candidate = {
        "fullName": form.get("fullName", ""),
        "email": form.get("email", ""),
        "phone": form.get("phone", ""),
        "degree": form.get("degree", ""),
        "branch": form.get("branch", ""),
    }
    
    # 3. CREATE SERVICES
    storage = StorageService(
        current_app.config["UPLOADS_DIR"],
        current_app.config["TMP_DIR"]
    )
    email = EmailService(
        current_app.config["SMTP_HOST"],
        current_app.config["SMTP_PORT"],
        current_app.config["SMTP_USER"],
        current_app.config["SMTP_PASSWORD"],
        current_app.config["SMTP_FROM"],
        current_app.config["SMTP_TLS"]
    )
    pipeline = PipelineService(
        storage,
        email,
        project_root=current_app.config["PROJECT_ROOT"],
        score_threshold=current_app.config["SCORE_THRESHOLD"]  # 70 by default
    )
    app_service = ApplicationService(current_app.mongo_db, pipeline)
    
    # 4. GET JOB FROM DATABASE
    job_service = JobService(current_app.mongo_db, None)
    job = job_service.get_job(job_id)
    if not job:
        return jsonify({"success": False, "message": "Job not found"}), 404
    
    # 5. TRIGGER PIPELINE (the main orchestration)
    try:
        application = app_service.create_application(job, candidate, resume_file)
        
        # Return success response
        return jsonify({
            "success": True,
            "message": f"Application submitted for {job.get('title')}. Score: {application.get('score')}",
            "applicationId": application.get("applicationId"),
            "status": application.get("status"),  # "Selected" or "Rejected"
            "score": application.get("score")
        })
    except Exception as exc:
        logger.exception("Application processing failed")
        return jsonify({"success": False, "message": str(exc)}), 500
```

**What Happens (Complete Pipeline):**
```
1. Route receives FormData with jobId and resume PDF
   ↓
2. Route creates all services (Storage, Email, Pipeline, Application)
   ↓
3. Route calls ApplicationService.create_application()
   ↓
4. ApplicationService calls PipelineService.run()
   ↓
5. PipelineService:
   a. Saves resume PDF → /uploads/resumes/abc123_John_Doe_Resume.pdf
   b. Parses PDF → extracts text
   c. Writes text to /tmp/resume_app123.txt
   d. Writes job description to /tmp/job_abc123.txt
   ↓
6. PipelineService calls NLP Engine (from Nlp_Engine folder):
   - Extracts skills from resume
   - Extracts experience years
   - Extracts education level
   - Extracts job requirements
   - Returns JSON: Nlp_Engine/output/REQ_20260217_143022_nlp_output.json
   ↓
7. PipelineService calls AI Scorer (from Ai_Scoring folder):
   - Reads NLP output
   - Scores resume vs job requirements
   - Calculates: Skill Match + Experience + Education + Preferred Skills
   - Returns score (0-100)
   ↓
8. PipelineService determines status:
   if score >= 70: status = "Selected"
   else: status = "Rejected"
   ↓
9. PipelineService sends email (if selected):
   - Subject: "Shortlisted: Senior Developer"
   - Body: Congratulations email with score
   ↓
10. PipelineService returns results to ApplicationService
    ↓
11. ApplicationService saves complete application to MongoDB:
    - applicationId, jobId, candidateName, email, score, status, etc.
    ↓
12. ApplicationService returns application object
    ↓
13. Route returns success response to frontend with score and status
```

---

### **Endpoint 7: List Company Resumes**
```
GET /api/company/{companyId}/resumes
```

**Purpose:** Show all resumes submitted to company's jobs

**Frontend Request:**
```javascript
const response = await fetch("http://localhost:5000/api/company/a1b2c3d4.../resumes");
const resumes = await response.json();
```

**Backend Code:**
```python
@application_bp.route("/company/<company_id>/resumes", methods=["GET"])
def list_company_resumes(company_id):
    app_service = ApplicationService(current_app.mongo_db)
    resumes = app_service.list_company_resumes(company_id)  # Query MongoDB
    
    # Format for frontend
    formatted = [
        {
            "jobId": item.get("jobId"),
            "candidateName": item.get("candidateName"),
            "email": item.get("email"),
            "jobTitle": item.get("jobTitle"),
            "status": item.get("status"),  # "Selected" or "Rejected"
            "score": item.get("score"),
            "resumeUrl": f"/api/resumes/{item.get('applicationId')}"
        }
        for item in resumes
    ]
    
    # Assign ranks (Rank 1 = highest score per job)
    _assign_ranks(formatted)
    
    return jsonify(formatted)
```

**Response:**
```json
[
    {
        "jobId": "job_abc123",
        "candidateName": "John Doe",
        "email": "john@example.com",
        "jobTitle": "Senior Developer",
        "status": "Selected",
        "score": 85.5,
        "rank": 1,
        "resumeUrl": "/api/resumes/app_xyz789"
    },
    {
        "jobId": "job_abc123",
        "candidateName": "Jane Smith",
        "email": "jane@example.com",
        "jobTitle": "Senior Developer",
        "status": "Selected",
        "score": 78.2,
        "rank": 2,
        "resumeUrl": "/api/resumes/app_xyz790"
    },
    {
        "jobId": "job_abc123",
        "candidateName": "Bob Johnson",
        "email": "bob@example.com",
        "jobTitle": "Senior Developer",
        "status": "Rejected",
        "score": 45.0,
        "rank": null,
        "resumeUrl": "/api/resumes/app_xyz791"
    }
]
```

---

### **Endpoint 8: Download Resume**
```
GET /api/resumes/{applicationId}
```

**Purpose:** Download resume PDF

**Frontend Code:**
```javascript
// Make a link click to download
const link = document.createElement("a");
link.href = "/api/resumes/app_xyz789";
link.download = "resume.pdf";
link.click();
```

**Backend Code:**
```python
@application_bp.route("/resumes/<application_id>", methods=["GET"])
def download_resume(application_id):
    # Get application from MongoDB
    app_doc = current_app.mongo_db["applications"].find_one(
        {"applicationId": application_id}
    )
    if not app_doc:
        return jsonify({"message": "Resume not found"}), 404
    
    resume_path = app_doc.get("resumePdfPath")
    if not resume_path or not os.path.exists(resume_path):
        return jsonify({"message": "Resume file missing"}), 404
    
    # Send file as download
    return send_file(resume_path, as_attachment=True)
```

---

# 6. FRONTEND-BACKEND INTEGRATION

## 6.1 How Frontend Calls Backend

**Frontend Setup (React):**

```javascript
// Frontend/react-project/src/api/index.js

const API_BASE = "http://localhost:5000/api";

// Function: Call backend API
async function apiCall(endpoint, options = {}) {
    const url = `${API_BASE}${endpoint}`;
    try {
        const response = await fetch(url, {
            headers: {
                "Content-Type": "application/json",
                ...options.headers
            },
            ...options
        });
        return await response.json();
    } catch (error) {
        console.error(`API Error (${endpoint}):`, error);
        throw error;
    }
}

// Company APIs
export const API = {
    // Register
    registerCompany: (companyName, regNo, email, password) =>
        apiCall("/company/register", {
            method: "POST",
            body: JSON.stringify({ companyName, registrationNo: regNo, email, password })
        }),
    
    // Login
    loginCompany: (email, password) =>
        apiCall("/company/login", {
            method: "POST",
            body: JSON.stringify({ email, password })
        }),
    
    // Post Job
    postJob: (companyId, jobTitle, pdfFile) => {
        const formData = new FormData();
        formData.append("companyId", companyId);
        formData.append("jobTitle", jobTitle);
        formData.append("descriptionPdf", pdfFile);
        
        return fetch(`${API_BASE}/company/post-job`, {
            method: "POST",
            body: formData
        }).then(r => r.json());
    },
    
    // Get Company Jobs
    getCompanyJobs: (companyId) =>
        apiCall(`/company/${companyId}/jobs`),
    
    // Delete Job
    deleteJob: (jobId) =>
        apiCall("/company/delete-job", {
            method: "DELETE",
            body: JSON.stringify({ jobId })
        }),
    
    // Get All Jobs (for job seeker)
    getJobs: () =>
        apiCall("/jobs"),
    
    // Apply for Job
    applyForJob: (jobId, resumeFile, fullName, email, phone, degree, branch) => {
        const formData = new FormData();
        formData.append("jobId", jobId);
        formData.append("resume", resumeFile);
        formData.append("fullName", fullName);
        formData.append("email", email);
        formData.append("phone", phone);
        formData.append("degree", degree);
        formData.append("branch", branch);
        
        return fetch(`${API_BASE}/apply`, {
            method: "POST",
            body: formData
        }).then(r => r.json());
    },
    
    // Get Company Resumes
    getCompanyResumes: (companyId) =>
        apiCall(`/company/${companyId}/resumes`),
    
    // Download Resume
    downloadResume: (applicationId) =>
        `${API_BASE}/resumes/${applicationId}`
};
```

---

## 6.2 Frontend Components Using Backend

### **Component 1: Company Registration**
```jsx
import { API } from "../api";

export default function CompanyRegister() {
    const [formData, setFormData] = useState({
        companyName: "",
        registrationNo: "",
        email: "",
        password: ""
    });
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const result = await API.registerCompany(
                formData.companyName,
                formData.registrationNo,
                formData.email,
                formData.password
            );
            
            if (result.success) {
                alert("Registration successful! Redirecting to login...");
                navigate("/company/login");
            } else {
                alert(result.message);
            }
        } catch (error) {
            alert("Error: " + error.message);
        }
    };
    
    return (
        <form onSubmit={handleSubmit}>
            <input
                type="text"
                placeholder="Company Name"
                value={formData.companyName}
                onChange={(e) => setFormData({...formData, companyName: e.target.value})}
            />
            {/* Other fields... */}
            <button type="submit">Register</button>
        </form>
    );
}
```

**What Happens:**
1. User fills form and clicks Register
2. Component calls `API.registerCompany()`
3. API makes POST to `/api/company/register`
4. Backend validates, hashes password, saves to MongoDB
5. Backend returns response
6. Frontend shows success/error
7. On success, redirects to login

---

### **Component 2: Post Job**
```jsx
export default function PostJob() {
    const company = JSON.parse(localStorage.getItem("company"));
    const [jobTitle, setJobTitle] = useState("");
    const [pdfFile, setPdfFile] = useState(null);
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const result = await API.postJob(company.companyId, jobTitle, pdfFile);
            
            if (result.success) {
                alert("Job posted successfully!");
                setJobTitle("");
                setPdfFile(null);
            } else {
                alert(result.message);
            }
        } catch (error) {
            alert("Error: " + error.message);
        }
    };
    
    return (
        <form onSubmit={handleSubmit}>
            <input
                type="text"
                placeholder="Job Title"
                value={jobTitle}
                onChange={(e) => setJobTitle(e.target.value)}
            />
            <input
                type="file"
                accept=".pdf"
                onChange={(e) => setPdfFile(e.target.files[0])}
            />
            <button type="submit">Post Job</button>
        </form>
    );
}
```

**What Happens:**
1. User uploads job description PDF and enters title
2. Component calls `API.postJob()` with companyId, title, PDF
3. API creates FormData and POSTs to `/api/company/post-job`
4. Backend saves PDF, parses text, creates job document, saves to MongoDB
5. Backend returns jobId
6. Frontend shows success

---

### **Component 3: Apply for Job**
```jsx
export default function ApplyJob({ jobId }) {
    const [formData, setFormData] = useState({
        fullName: "",
        email: "",
        phone: "",
        degree: "",
        branch: ""
    });
    const [resumeFile, setResumeFile] = useState(null);
    const [loading, setLoading] = useState(false);
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        
        try {
            const result = await API.applyForJob(
                jobId,
                resumeFile,
                formData.fullName,
                formData.email,
                formData.phone,
                formData.degree,
                formData.branch
            );
            
            if (result.success) {
                alert(`Application submitted!\nScore: ${result.score}\nStatus: ${result.status}`);
            } else {
                alert(result.message);
            }
        } catch (error) {
            alert("Error: " + error.message);
        } finally {
            setLoading(false);
        }
    };
    
    return (
        <form onSubmit={handleSubmit}>
            {/* Form fields... */}
            <input
                type="file"
                accept=".pdf"
                onChange={(e) => setResumeFile(e.target.files[0])}
                required
            />
            <button type="submit" disabled={loading}>
                {loading ? "Processing..." : "Submit Application"}
            </button>
        </form>
    );
}
```

**What Happens (COMPLETE PIPELINE):**
1. User fills form and uploads resume PDF
2. Component calls `API.applyForJob()` with all data
3. API creates FormData and POSTs to `/api/apply`
4. Backend PipelineService starts orchestration:
   - Saves resume PDF
   - Parses PDF → text
   - Calls NLP Engine → extracts data
   - Calls AI Scorer → calculates score
   - Sends email (if selected)
5. Backend saves application to MongoDB
6. Backend returns score and status
7. Frontend shows result to user

---

# 7. AI MODEL INTEGRATION

## 7.1 How Backend Calls AI Models

**PipelineService Integration:**

```python
# Backend/app/services/pipeline_service.py

import sys
import os
from pathlib import Path

# Add project root to path so we can import AI modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

class PipelineService:
    def run(self, job: dict, candidate: dict, resume_file) -> dict:
        
        # ... Step 1-4: Save files ...
        
        # STEP 5: CALL NLP ENGINE
        # ========================
        from Nlp_Engine.Nlp_service import process_resumes
        
        nlp_response = process_resumes(
            jd_txt_path,           # Job description text file path
            [resume_txt_path]      # List of resume text file paths
        )
        
        # Check if NLP succeeded
        if not nlp_response.get("success"):
            raise RuntimeError(f"NLP failed: {nlp_response.get('error')}")
        
        # Get output file path from NLP response
        output_path = nlp_response.get("output_path")
        # output_path = "Nlp_Engine/output/REQ_20260217_143022_nlp_output.json"
        
        # Load NLP output from disk
        output_file = os.path.join(self.project_root, output_path)
        with open(output_file, "r", encoding="utf-8") as f:
            nlp_data = json.load(f)
        
        # Extract job requirements from NLP output
        job_requirements = nlp_data.get("job_requirements", {})
        scoring_metadata = {"job_requirements": job_requirements}
        
        # ========================
        # STEP 6: CALL AI SCORER
        # ========================
        from Ai_Scoring.Ai_Scoring.scorer import process_resume_batch
        
        scored_results = process_resume_batch(
            Path(output_file).name,    # Filename: "REQ_20260217_143022_nlp_output.json"
            scoring_metadata           # Job requirements for scoring
        )
        
        # Check if scoring succeeded
        if scored_results and "error" in scored_results[0]:
            raise RuntimeError(f"Scoring failed: {scored_results[0].get('error')}")
        
        # Get score from result
        result = scored_results[0] if scored_results else {}
        score = float(result.get("total_score", 0))
        
        # ... Determine status, send email, etc ...
```

---

## 7.2 Data Flow Between Backend and AI Models

```
┌─────────────────────────────────────────────────────┐
│ CANDIDATE APPLICATION                               │
│ Resume PDF + Candidate Info + Job ID                │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │ BACKEND - Step 1,2,3    │
        │ - Save PDF              │
        │ - Parse PDF → text      │
        │ - Create TXT files      │
        └────────────┬────────────┘
                     │
        ┌────────────▼─────────────────────────────┐
        │ NLP_ENGINE - process_resumes()           │
        │                                          │
        │ INPUT:                                   │
        │ - job_description.txt                   │
        │ - resume.txt                            │
        │                                          │
        │ OUTPUT: JSON File                        │
        │ {                                        │
        │   "success": true,                      │
        │   "output_path": "Nlp_Engine/output/...",│
        │   "job_requirements": {                 │
        │     "required_skills": ["python", ...],│
        │     "minimum_experience": 3,             │
        │     "required_education": "bachelors"   │
        │   },                                    │
        │   "resumes": {                          │
        │     "resume_001": {                     │
        │       "skills": ["python", "java", ...],│
        │       "experience_years": 5,             │
        │       "education_level": "bachelors",   │
        │       "job_match": {                    │
        │         "match_percentage": 85          │
        │       },                                │
        │       "scoring_ready": true             │
        │     }                                   │
        │   }                                     │
        │ }                                        │
        └────────────┬──────────────────────────────┘
                     │
        ┌────────────▼────────────────────────────┐
        │ BACKEND - Step 5,6                      │
        │ - Read NLP output JSON                  │
        │ - Extract job_requirements              │
        │ - Call AI Scorer                        │
        └────────────┬────────────────────────────┘
                     │
        ┌────────────▼──────────────────────────────┐
        │ AI_SCORING - process_resume_batch()      │
        │                                          │
        │ INPUT:                                   │
        │ - NLP output filename                    │
        │ - job_requirements (metadata)            │
        │                                          │
        │ OUTPUT: List of scored results           │
        │ [                                        │
        │   {                                      │
        │     "resume_id": "resume_001",          │
        │     "total_score": 82.5,                │
        │     "rank": 1,                          │
        │     "details": {                        │
        │       "experience_years": 5,            │
        │       "skills_match": 85                │
        │     }                                   │
        │   }                                     │
        │ ]                                       │
        └────────────┬──────────────────────────────┘
                     │
        ┌────────────▼────────────────────────┐
        │ BACKEND - Final Steps               │
        │ - Determine status (Selected/Rejected)
        │ - Send email notification           │
        │ - Save to MongoDB                   │
        │ - Return response to frontend       │
        └────────────┬────────────────────────┘
                     │
        ┌────────────▼──────────────────────────┐
        │ FRONTEND                             │
        │ Shows: Score, Status, Confirmation   │
        └──────────────────────────────────────┘
```

---

# 8. COMPLETE DATA FLOW

## End-to-End User Journey

### **Scenario: Company Posts Job + Candidate Applies**

```
╔═══════════════════════════════════════════════════════════════════════╗
║ DAY 1: COMPANY POSTS JOB                                              ║
╚═══════════════════════════════════════════════════════════════════════╝

1. COMPANY VISITS FRONTEND (http://localhost:5173)
   ├─ Sees: Company Dashboard
   └─ Clicks: "Register"

2. COMPANY REGISTRATION
   ├─ Fills: Name="Acme Corp", RegNo="ABC123", Email="hr@acme.com", Password="***"
   ├─ Clicks: "Register"
   ├─ Frontend calls: POST /api/company/register
   ├─ Backend:
   │   ├─ Validates all fields
   │   ├─ Checks duplicate email
   │   ├─ Hashes password: "***" → "$2b$12$KIXxP..."
   │   ├─ Creates document:
   │   │   {
   │   │     "companyId": "a1b2c3d4...",
   │   │     "name": "Acme Corp",
   │   │     "email": "hr@acme.com",
   │   │     "passwordHash": "$2b$12$KIXxP..."
   │   │   }
   │   ├─ Saves to MongoDB: companies collection
   │   └─ Returns: {"success": true, "company": {...}}
   └─ Frontend: Redirects to login

3. COMPANY LOGIN
   ├─ Fills: Email="hr@acme.com", Password="***"
   ├─ Clicks: "Login"
   ├─ Frontend calls: POST /api/company/login
   ├─ Backend:
   │   ├─ Queries MongoDB for email
   │   ├─ Compares plain password with bcrypt hash
   │   ├─ Returns: {"success": true, "company": {...}}
   │   └─ (No session/token - stateless!)
   └─ Frontend: Saves company to localStorage, shows dashboard

4. COMPANY POSTS JOB
   ├─ Fills: Job Title = "Senior Python Developer"
   ├─ Uploads: job_description.pdf
   ├─ Clicks: "Post Job"
   ├─ Frontend calls: POST /api/company/post-job (FormData)
   ├─ Backend:
   │   ├─ Receives FormData with companyId, jobTitle, PDF
   │   ├─ StorageService.save_upload():
   │   │   ├─ Generates UUID: abc123def456
   │   │   ├─ Saves to disk: /uploads/job_descriptions/abc123_job_description.pdf
   │   │   └─ Returns path
   │   ├─ ResumeParser.parse(pdf_path):
   │   │   ├─ Reads PDF
   │   │   ├─ Extracts text: "We are looking for a Senior Python Developer with 5+ years..."
   │   │   └─ Returns text
   │   ├─ JobService.create_job():
   │   │   ├─ Generates jobId: xyz789abc123
   │   │   ├─ Creates document:
   │   │   │   {
   │   │   │     "jobId": "xyz789abc123",
   │   │   │     "title": "Senior Python Developer",
   │   │   │     "description": "We are looking for...",
   │   │   │     "descriptionPdfPath": "/uploads/job_descriptions/abc123_job_description.pdf",
   │   │   │     "companyId": "a1b2c3d4...",
   │   │   │     "companyName": "Acme Corp",
   │   │   │     "companyEmail": "hr@acme.com",
   │   │   │     "postDate": "2026-02-17T10:00:00"
   │   │   │   }
   │   │   └─ Saves to MongoDB: jobs collection
   │   └─ Returns: {"success": true, "jobId": "xyz789abc123"}
   ├─ Frontend: Shows success, "Job posted!"
   └─ Company sees job in dashboard

╔═══════════════════════════════════════════════════════════════════════╗
║ DAY 2: CANDIDATE APPLIES FOR JOB                                      ║
╚═══════════════════════════════════════════════════════════════════════╝

1. CANDIDATE VISITS FRONTEND (http://localhost:5173)
   ├─ Sees: "Available Jobs"
   ├─ Searches and finds: "Senior Python Developer at Acme Corp"
   └─ Clicks: "Apply"

2. CANDIDATE FILLS APPLICATION FORM
   ├─ Fills:
   │   Name: "John Doe"
   │   Email: "john@example.com"
   │   Phone: "+1-555-1234"
   │   Degree: "B.Tech"
   │   Branch: "Computer Science"
   ├─ Uploads: John_Doe_Resume.pdf
   ├─ Clicks: "Submit Application"
   ├─ Frontend calls: POST /api/apply (FormData)
   │
   └─ BACKEND PIPELINE STARTS ⭐
      │
      ├─ Step 1: VALIDATION
      │   ├─ Check jobId exists
      │   ├─ Check resume is PDF
      │   └─ Get job from MongoDB: {...full job document...}
      │
      ├─ Step 2: CREATE SERVICES
      │   ├─ StorageService (for files)
      │   ├─ EmailService (for notifications)
      │   ├─ PipelineService (orchestration)
      │   └─ ApplicationService (database)
      │
      ├─ Step 3: SAVE FILES
      │   ├─ StorageService.save_upload(John_Doe_Resume.pdf, "resumes"):
      │   │   └─ Saves to: /uploads/resumes/def456ghi789_John_Doe_Resume.pdf
      │   │
      │   ├─ ResumeParser.parse(resume_path):
      │   │   ├─ Reads PDF
      │   │   └─ Extracts text:
      │   │       "John Doe
      │   │        john@example.com
      │   │        EXPERIENCE:
      │   │        Senior Developer at TechCorp (2023-2026)
      │   │        - Python, Django, PostgreSQL
      │   │        - Led team of 5 developers
      │   │        ..."
      │   │
      │   ├─ StorageService.write_text(resume_text, "resume_app_xyz.txt"):
      │   │   └─ Saves to: /tmp/resume_app_xyz.txt
      │   │
      │   └─ StorageService.write_text(jd_text, "job_xyz789.txt"):
      │       └─ Saves to: /tmp/job_xyz789.txt
      │
      ├─ Step 4: NLP EXTRACTION
      │   ├─ Call: process_resumes("/tmp/job_xyz789.txt", ["/tmp/resume_app_xyz.txt"])
      │   │
      │   ├─ NLP Engine processes:
      │   │   ├─ Parses job description:
      │   │   │   ├─ Extracts required skills: ["Python", "Django", "PostgreSQL", "AWS"]
      │   │   │   ├─ Extracts minimum experience: 5 years
      │   │   │   ├─ Extracts required education: "Bachelors"
      │   │   │   └─ Stores in job_requirements
      │   │   │
      │   │   └─ Parses resume:
      │   │       ├─ Extracts skills: ["Python", "Django", "PostgreSQL", "JavaScript", "React"]
      │   │       ├─ Extracts experience: 3 years
      │   │       ├─ Extracts education: "Bachelors"
      │   │       ├─ Calculates match: 4 skills match out of 5 = 80% match
      │   │       └─ Stores in scoring_ready: true
      │   │
      │   └─ NLP output saved to: Nlp_Engine/output/REQ_20260217_103022_nlp_output.json
      │       {
      │         "job_requirements": {
      │           "required_skills": ["Python", "Django", "PostgreSQL", "AWS"],
      │           "minimum_experience": 5,
      │           "required_education": "Bachelors"
      │         },
      │         "resumes": {
      │           "resume_001": {
      │             "skills": ["Python", "Django", "PostgreSQL", "JavaScript", "React"],
      │             "experience_years": 3,
      │             "education_level": "Bachelors",
      │             "job_match": {"match_percentage": 80},
      │             "scoring_ready": true
      │           }
      │         }
      │       }
      │
      ├─ Step 5: AI SCORING
      │   ├─ Call: process_resume_batch("REQ_20260217_103022_nlp_output.json", job_requirements)
      │   │
      │   ├─ AI Scorer calculates metrics:
      │   │   ├─ Metric 1: Skill Match
      │   │   │   └─ 80% match * 60 weight = 48 points
      │   │   │
      │   │   ├─ Metric 2: Experience
      │   │   │   ├─ Required: 5 years
      │   │   │   ├─ Candidate: 3 years
      │   │   │   ├─ Ratio: 3/5 = 0.6
      │   │   │   └─ 0.6 * 25 weight = 15 points
      │   │   │
      │   │   ├─ Metric 3: Education
      │   │   │   ├─ Required: Bachelors
      │   │   │   ├─ Candidate: Bachelors
      │   │   │   └─ Match = 10 points
      │   │   │
      │   │   └─ Metric 4: Preferred Skills
      │   │       └─ 0 extra points
      │   │
      │   ├─ FINAL SCORE: 48 + 15 + 10 + 0 = 73 points
      │   │
      │   └─ Result: [{"resume_id": "resume_001", "total_score": 73, "rank": 1}]
      │
      ├─ Step 6: DETERMINE STATUS
      │   ├─ Score: 73
      │   ├─ Threshold: 70 (from .env)
      │   ├─ 73 >= 70? YES
      │   └─ Status: "Selected"
      │
      ├─ Step 7: SEND EMAIL
      │   ├─ Since status is "Selected", send email to candidate
      │   ├─ EmailService.send_email():
      │   │   ├─ Connect to SMTP: smtp.gmail.com:587
      │   │   ├─ Authenticate
      │   │   ├─ Send email:
      │   │   │   From: noreply@company.com
      │   │   │   To: john@example.com
      │   │   │   Subject: "Shortlisted: Senior Python Developer"
      │   │   │   Body: "Hello John,
      │   │   │          Great news — your application for Senior Python Developer 
      │   │   │          at Acme Corp has been shortlisted.
      │   │   │          Your Score: 73.0/100
      │   │   │          ..."
      │   │   └─ Email sent successfully
      │   └─ emailSent = true
      │
      ├─ Step 8: SAVE TO DATABASE
      │   ├─ ApplicationService.create_application():
      │   │   ├─ Generate applicationId: app_123xyz456
      │   │   ├─ Create document:
      │   │   │   {
      │   │   │     "applicationId": "app_123xyz456",
      │   │   │     "jobId": "xyz789abc123",
      │   │   │     "jobTitle": "Senior Python Developer",
      │   │   │     "companyId": "a1b2c3d4...",
      │   │   │     "candidateName": "John Doe",
      │   │   │     "email": "john@example.com",
      │   │   │     "score": 73.0,
      │   │   │     "rank": 1,
      │   │   │     "status": "Selected",
      │   │   │     "emailSent": true,
      │   │   │     "createdAt": "2026-02-17T10:30:22"
      │   │   │   }
      │   │   └─ Save to MongoDB: applications collection
      │   └─ Return application object
      │
      └─ Step 9: RETURN TO FRONTEND
          └─ Frontend receives:
              {
                "success": true,
                "message": "Application submitted successfully! Score: 73 Status: Selected",
                "applicationId": "app_123xyz456",
                "status": "Selected",
                "score": 73.0
              }

3. FRONTEND SHOWS RESULT TO CANDIDATE
   └─ Alert: "Success! Score: 73/100 Status: Selected"

4. COMPANY SEES NEW RESUME
   ├─ Company views dashboard
   ├─ Clicks: "Resumes" tab
   ├─ Frontend calls: GET /api/company/a1b2c3d4.../resumes
   ├─ Backend:
   │   ├─ ApplicationService.list_company_resumes("a1b2c3d4..."):
   │   │   └─ Queries MongoDB applications collection
   │   │       Returns: [
   │   │         {
   │   │           "jobId": "xyz789abc123",
   │   │           "candidateName": "John Doe",
   │   │           "email": "john@example.com",
   │   │           "jobTitle": "Senior Python Developer",
   │   │           "status": "Selected",
   │   │           "score": 73.0,
   │   │           "rank": 1,
   │   │           "resumeUrl": "/api/resumes/app_123xyz456"
   │   │         }
   │   │       ]
   │   └─ Returns formatted response
   └─ Frontend: Shows table with John Doe, Score: 73, Status: Selected, Rank: 1

5. COMPANY DOWNLOADS RESUME
   ├─ Company clicks: "Resume" link
   ├─ Frontend calls: GET /api/resumes/app_123xyz456
   ├─ Backend:
   │   ├─ Queries MongoDB for applicationId
   │   ├─ Gets resumePdfPath: /uploads/resumes/def456ghi789_John_Doe_Resume.pdf
   │   ├─ Sends file as download
   │   └─ Browser saves: John_Doe_Resume.pdf
   └─ Company can review the PDF

╔═══════════════════════════════════════════════════════════════════════╗
║ SUMMARY                                                              ║
╚═══════════════════════════════════════════════════════════════════════╝

Data Journey:
Frontend (React) 
  ↓ (HTTP API calls)
Backend (Flask - Orchestration)
  ├─ Service Layer (Business Logic)
  │   ├─ CompanyService (Auth)
  │   ├─ JobService (Job Management)
  │   ├─ ApplicationService (Applications)
  │   ├─ PipelineService ⭐ (Orchestration)
  │   ├─ StorageService (Files)
  │   └─ EmailService (Notifications)
  ↓
AI Modules (Independent)
  ├─ Resume Parser (PDF → TEXT)
  ├─ NLP Engine (Extract Data)
  └─ AI Scorer (Score & Rank)
  ↓
MongoDB Database
  ├─ companies collection
  ├─ jobs collection
  └─ applications collection
```

---

# 9. ENVIRONMENT CONFIGURATION

**File:** `Backend/.env`

```bash
# MongoDB Connection
MONGO_URI=mongodb://localhost:27017
MONGO_DB=resume_filtering

# SMTP (Email) Configuration
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-specific-password
SMTP_FROM=noreply@yourcompany.com
SMTP_TLS=true

# Scoring Configuration
SCORE_THRESHOLD=70  # Minimum score to be "Selected"

# File Size Limit
MAX_CONTENT_LENGTH=20971520  # 20MB

# Flask Configuration
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
```

**What Each Setting Does:**

| Setting | Purpose | Example |
|---------|---------|---------|
| `MONGO_URI` | Connection to MongoDB | `mongodb://localhost:27017` |
| `MONGO_DB` | Database name | `resume_filtering` |
| `SMTP_HOST` | Email server | `smtp.gmail.com` |
| `SMTP_PORT` | Email server port | `587` |
| `SMTP_USER` | Email username | `your-email@gmail.com` |
| `SMTP_PASSWORD` | Email app password | From Gmail app-specific passwords |
| `SMTP_FROM` | From address in emails | `noreply@company.com` |
| `SCORE_THRESHOLD` | Min score to select candidate | `70` (0-100) |
| `MAX_CONTENT_LENGTH` | Max file upload size | `20971520` (bytes, ~20MB) |

---

# 10. HOW TO RUN & TEST

## 10.1 Prerequisites

```bash
# Install Python 3.9+
python --version

# Install MongoDB (or use MongoDB Atlas cloud)
# Download from: https://www.mongodb.com/try/download/community

# Navigate to Backend folder
cd Backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 10.2 Start Backend

```bash
# Make sure you're in Backend folder
cd Backend

# Check .env file exists and is configured
# Required: MONGO_URI, MONGO_DB, SMTP settings

# Run the server
python run.py

# Expected output:
# * Serving Flask app 'app'
# * Debug mode: on
# * Running on http://0.0.0.0:5000
```

---

## 10.3 Test Endpoints

### **Test 1: Health Check**
```bash
curl http://localhost:5000/api/health
# Expected: {"status": "ok"}
```

### **Test 2: Register Company**
```bash
curl -X POST http://localhost:5000/api/company/register \
  -H "Content-Type: application/json" \
  -d '{
    "companyName": "Tech Corp",
    "registrationNo": "REG123",
    "email": "hr@techcorp.com",
    "password": "TestPass123"
  }'

# Expected: {"success": true, "company": {...}}
```

### **Test 3: Login Company**
```bash
curl -X POST http://localhost:5000/api/company/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "hr@techcorp.com",
    "password": "TestPass123"
  }'

# Expected: {"success": true, "company": {...}}
```

---

## 10.4 Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| "Connection refused" | MongoDB not running; start with: `mongod` |
| "CORS error" | Ensure CORS is enabled in app.__init__.py |
| "Email not sending" | Check SMTP_HOST, SMTP_PORT, credentials in .env |
| "File not found" | Check UPLOADS_DIR, TMP_DIR paths in config.py |
| "Module not found" | Ensure project root is in sys.path in services |

---

## 10.5 Database Inspection

```bash
# Start MongoDB shell
mongo

# or (newer versions):
mongosh

# Select database
use resume_filtering

# View collections
show collections

# Check companies
db.companies.find()

# Check jobs
db.jobs.find()

# Check applications
db.applications.find()

# Delete a collection (for testing)
db.companies.deleteMany({})
```

---

# KEY TAKEAWAYS FOR YOUR SIR

## 🎯 Architecture Philosophy

**Backend is an ORCHESTRATION LAYER**, not a microservice:
- ✅ Routes are THIN (just receive and return)
- ✅ Services are THICK (contain business logic)
- ✅ AI Modules are UNTOUCHED (independent)
- ✅ Pipeline orchestrates all components

## 🔄 Data Flow

```
Frontend (React)
    ↓ HTTP Request
Backend (Flask)
    ├─ Validate
    ├─ Call Services
    │   ├─ JobService, CompanyService, ApplicationService
    │   └─ PipelineService (CORE)
    ├─ Call AI Modules
    │   ├─ Resume Parser (PDF → TEXT)
    │   ├─ NLP Engine (Extract)
    │   └─ AI Scorer (Score)
    ├─ Save to MongoDB
    └─ Return Response
    ↓ HTTP Response
Frontend (React)
```

## 💾 Database Collections

| Collection | Purpose | Key Fields |
|-----------|---------|-----------|
| companies | Company accounts | companyId, email, passwordHash |
| jobs | Job postings | jobId, companyId, title, description |
| applications | Candidate applications | applicationId, jobId, companyId, score, status |

## 🔐 Key Features

1. **CORS Enabled** → Frontend can call backend
2. **Password Hashing** → Bcrypt (never plain text)
3. **File Uploads** → Secure file handling with UUID
4. **Email Notifications** → SMTP for candidate updates
5. **AI Pipeline** → Orchestrated sequence (Parser → NLP → Scorer)
6. **Stateless** → No sessions needed (frontend stores company data)
7. **Error Handling** → Try-catch in all services

## 🚀 How It All Works Together

When candidate applies:
1. Form data comes to `/api/apply`
2. Route creates services and calls ApplicationService
3. ApplicationService calls PipelineService.run()
4. PipelineService orchestrates:
   - Save resume PDF to disk
   - Parse PDF → extract text
   - Call NLP Engine → extract skills, experience, education
   - Call AI Scorer → calculate score (0-100)
   - Determine if Selected (score ≥ 70) or Rejected
   - Send email notification
5. ApplicationService saves application to MongoDB
6. Route returns result to frontend
7. Frontend shows success/rejection to candidate

---

**THIS DOCUMENT IS READY FOR YOUR SIR PRESENTATION!**

Use this to explain:
- ✅ Complete system architecture
- ✅ How frontend and backend communicate
- ✅ How AI models integrate
- ✅ Complete data flow with examples
- ✅ All APIs with code
- ✅ Database schema
- ✅ Configuration and setup

Good luck with your presentation! 🚀
