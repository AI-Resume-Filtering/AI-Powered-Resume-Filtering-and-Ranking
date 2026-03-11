# 📄 HOW RESUMES ARE STORED - Complete Mechanism & Interview Guide

**Date:** February 17, 2026

---

# TABLE OF CONTENTS

1. [Quick Answer - For Interviews](#quick-answer---for-interviews)
2. [What Resume Data is Stored](#what-resume-data-is-stored)
3. [Storage Mechanism - Step by Step](#storage-mechanism---step-by-step)
4. [File System Storage](#file-system-storage)
5. [Database Storage (MongoDB)](#database-storage-mongodb)
6. [Complete Architecture Diagram](#complete-architecture-diagram)
7. [Interview Questions & Answers](#interview-questions--answers)

---

# QUICK ANSWER - FOR INTERVIEWS

👤 **Interviewer:** "Tell me, how do you store resumes?"

✅ **Your Answer:**

> "We store resumes in **TWO places**:
>
> **1. File System (Physical Storage)**
> - Original PDF file is saved to disk: `Backend/instance/storage/uploads/resumes/`
> - Text extracted version is saved: `Backend/instance/storage/tmp/`
> - Files are renamed with unique IDs for security
>
> **2. MongoDB Database (Reference Storage)**
> - We store metadata about the resume:
>   - Path to PDF file
>   - Path to extracted text
>   - AI scores and extracted data
>   - Candidate information (name, email, phone)
> - We do NOT store the entire PDF in database (too large)
> - Only store references and metadata
>
> **Why Two Places?**
> - File system: Store large PDF (fast disk storage)
> - Database: Quick lookup and search (MongoDB indexes)
>
> **Security:**
> - Unique IDs: `a1b2c3d4e5f6_resume.pdf`
> - Original names not exposed
> - File permissions restricted"

---

# WHAT RESUME DATA IS STORED

## Two Types of Resume Storage

### 1️⃣ **Resume FILE (Disk/File System)**

```
What's stored:
├── Original PDF file (as-is, unchanged)
├── Extracted text version (.txt)
└── Metadata (creation date, file size)

Where stored:
├── PDF: Backend/instance/storage/uploads/resumes/
└── TXT: Backend/instance/storage/tmp/

Size: 
├── Typical PDF: 200-500 KB
├── Extracted text: 5-50 KB
└── Max allowed: 20 MB per file
```

### 2️⃣ **Resume DATABASE RECORD (MongoDB)**

```
What's stored:
├── Candidate Name
├── Email
├── Phone
├── Degree
├── Branch
├── Resume Filename
├── Resume PDF Path (reference)
├── Resume Text Path (reference)
├── NLP Extracted Data Path (reference)
├── AI Score (0-100)
├── Status (Selected/Rejected)
├── Job Applied For
├── Company Name
└── Application Date

Size:
└── ~2-5 KB per application record
```

---

# STORAGE MECHANISM - STEP BY STEP

## Complete Process Flow

```
┌──────────────────────────────────────────────────────────────────┐
│ STEP 1: User Uploads Resume (Frontend)                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ User clicks "Apply" → Selects PDF file                          │
│ File: resume_john_doe.pdf                                       │
│ Size: 350 KB                                                     │
│                                                                  │
│ Browser sends: POST /api/apply                                  │
│ FormData {                                                       │
│   jobId: "job_xyz123",                                          │
│   fullName: "John Doe",                                         │
│   email: "john@example.com",                                    │
│   phone: "9876543210",                                          │
│   degree: "BTech",                                              │
│   branch: "Computer Science",                                   │
│   resume: <PDF File Object>                                     │
│ }                                                                │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 2: Backend Receives File (application_routes.py)           │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Code:                                                            │
│   resume_file = request.files.get("resume")                     │
│                                                                  │
│ What happens:                                                    │
│   ✓ File is in memory (temporary buffer)                        │
│   ✓ File extension validated (.pdf only)                        │
│   ✓ File size checked (< 20 MB)                                 │
│                                                                  │
│ At this point:                                                   │
│   - File still in memory                                         │
│   - NOT saved to disk yet                                       │
│   - NOT saved to database yet                                   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 3: Application Service Creates ID                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Code (application_service.py):                                  │
│   application_id = uuid.uuid4().hex                             │
│   # Result: "a1b2c3d4e5f6g7h8i9j0k1l2"                          │
│                                                                  │
│ Why unique ID?                                                   │
│   ✓ Security (hide real filename)                               │
│   ✓ Unique identifier for tracking                              │
│   ✓ Deduplication (same file, different ID)                     │
│                                                                  │
│ At this point:                                                   │
│   - ID generated                                                 │
│   - Ready to save file                                          │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 4: Storage Service Saves File to Disk                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Code (storage_service.py):                                      │
│   safe_name = secure_filename(resume_file.filename)             │
│   # resume_john_doe.pdf → resume_john_doe.pdf (safe version)    │
│                                                                  │
│   unique_prefix = uuid.uuid4().hex                              │
│   # "a1b2c3d4e5f6"                                              │
│                                                                  │
│   filename = f"{unique_prefix}_{safe_name}"                     │
│   # "a1b2c3d4e5f6_resume_john_doe.pdf"                          │
│                                                                  │
│   target_path = uploads_dir / subdir / filename                 │
│   # Backend/instance/storage/uploads/resumes/a1b2c3d4e5f6_resume_john_doe.pdf  │
│                                                                  │
│   file_storage.save(target_path)                                │
│   # ✓ FILE NOW SAVED TO DISK                                    │
│                                                                  │
│ At this point:                                                   │
│   ✓ PDF file physically stored on disk                          │
│   ✓ Can be accessed later by path                               │
│   ✓ Cannot be accidentally deleted (versioned)                  │
│                                                                  │
│ Returns: "Backend/instance/storage/uploads/resumes/a1b2c3d4e5f6_resume_john_doe.pdf"  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 5: Resume Parser Extracts Text from PDF                    │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Code (pipeline_service.py):                                     │
│   resume_text = self.parser.parse(resume_pdf_path)              │
│   # Reads PDF → Extracts all text                               │
│                                                                  │
│ What extracted:                                                  │
│   "JOHN DOE                                                       │
│    Email: john@example.com                                      │
│    Phone: 9876543210                                            │
│    Location: Bangalore                                          │
│                                                                  │
│    SUMMARY                                                       │
│    Experienced Python Developer with 3 years...                 │
│                                                                  │
│    SKILLS                                                        │
│    • Python, Java, Django, Flask                                │
│    • REST APIs, SQL, MongoDB                                    │
│    • AWS, Docker, Kubernetes                                     │
│                                                                  │
│    EXPERIENCE                                                    │
│    Senior Developer at Tech Corp (2023-2026)                    │
│    • Led 5-member team                                          │
│    • Reduced response time by 40%                               │
│                                                                  │
│    EDUCATION                                                     │
│    B.Tech Computer Science from XYZ University (2020)           │
│   "                                                              │
│                                                                  │
│ Size: Original PDF 350 KB → Extracted Text 12 KB                │
│                                                                  │
│ At this point:                                                   │
│   ✓ Text extracted from PDF                                     │
│   ✓ Ready for AI processing                                     │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 6: Save Extracted Text to Temp File                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Code:                                                            │
│   resume_txt_path = self.storage.write_text(                    │
│       resume_text,                                              │
│       f"resume_{application_id}.txt"                            │
│   )                                                              │
│   # "Backend/instance/storage/tmp/resume_a1b2c3d4e5f6.txt"      │
│                                                                  │
│ Why temporary file?                                              │
│   ✓ NLP Engine needs text file input                            │
│   ✓ Easier to process than PDF                                  │
│   ✓ Can be deleted after processing                             │
│                                                                  │
│ At this point:                                                   │
│   ✓ Text file saved to temporary storage                        │
│   ✓ Ready for NLP processing                                    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 7: NLP Engine Processes & Outputs Structured Data          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Process:                                                         │
│   NLP Engine:                                                    │
│   ├─ Input 1: resume_a1b2c3d4e5f6.txt (candidate's resume)     │
│   ├─ Input 2: job_xyz123.txt (job description)                  │
│   ├─ Extracts:                                                  │
│   │  ├─ Skills: ["Python", "Java", "Django"]                   │
│   │  ├─ Experience: 3 years                                     │
│   │  ├─ Education: BTech                                        │
│   │  └─ Match score: 85%                                        │
│   └─ Output: JSON file with structured data                     │
│                                                                  │
│ Outputs:                                                         │
│   Path: Nlp_Engine/output/REQ_20260217_010509_nlp_output.json   │
│                                                                  │
│   JSON Content:                                                  │
│   {                                                              │
│     "job_requirements": {                                        │
│       "job_title": "Senior Python Developer",                  │
│       "required_skills": ["python", "django", "rest-api"],      │
│       "minimum_experience": 3,                                   │
│       "required_education": "bachelors"                          │
│     },                                                           │
│     "resumes": {                                                 │
│       "resume_a1b2c3d4e5f6": {                                  │
│         "candidate_name": "John Doe",                           │
│         "email": "john@example.com",                            │
│         "skills": ["python", "java", "django", "flask"],        │
│         "experience_years": 3,                                   │
│         "education_level": "bachelors",                         │
│         "job_match": {                                           │
│           "match_percentage": 85,                               │
│           "matched_skills": ["python", "django"],              │
│           "missing_skills": ["rest-api"]                        │
│         }                                                        │
│       }                                                          │
│     }                                                            │
│   }                                                              │
│                                                                  │
│ At this point:                                                   │
│   ✓ Structured data extracted for AI                            │
│   ✓ Candidate skills identified                                 │
│   ✓ Job match calculated                                        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 8: AI Scorer Calculates Final Score                        │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ AI Scoring:                                                      │
│   Input: nlp_output.json + job requirements                     │
│                                                                  │
│   Calculates:                                                    │
│   • Skill Match: 30 points (3/3 required skills = 30 pts)       │
│   • Experience: 28 points (3 years >= 3 years = 28 pts)         │
│   • Education: 20 points (BTech matches = 20 pts)               │
│   • Extras: 7 points (bonus for additional skills)              │
│   ─────────────────────────────────────────────              │
│   TOTAL SCORE: 85/100                                           │
│                                                                  │
│ Status Decision:                                                 │
│   Threshold: 70                                                  │
│   Score: 85                                                      │
│   Status: 85 >= 70 → "Selected" ✅                              │
│   Action: Send acceptance email                                 │
│                                                                  │
│ At this point:                                                   │
│   ✓ Score calculated (0-100)                                    │
│   ✓ Candidate ranked (1st, 2nd, 3rd)                            │
│   ✓ Status determined (Selected/Rejected)                       │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────────┐
│ STEP 9: Save Everything to MongoDB Database                     │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Code (application_service.py):                                  │
│   application = {                                                │
│     "applicationId": "a1b2c3d4e5f6g7h8i9j0k1l2",               │
│     "jobId": "job_xyz123",                                      │
│     "jobTitle": "Senior Python Developer",                      │
│     "candidateName": "John Doe",                                │
│     "email": "john@example.com",                                │
│     "phone": "9876543210",                                      │
│     "degree": "BTech",                                          │
│     "branch": "Computer Science",                               │
│     "resumeName": "resume_john_doe.pdf",                        │
│     "resumePdfPath": "Backend/instance/storage/uploads/resumes/a1b2c3d4e5f6_resume_john_doe.pdf",  │
│     "resumeTextPath": "Backend/instance/storage/tmp/resume_a1b2c3d4e5f6.txt",  │
│     "nlpOutputPath": "Nlp_Engine/output/REQ_20260217_010509_nlp_output.json",  │
│     "score": 85,                                                │
│     "rank": 1,                                                  │
│     "status": "Selected",                                       │
│     "emailSent": true,                                          │
│     "createdAt": "2026-02-17T10:35:22.123456"                   │
│   }                                                              │
│                                                                  │
│   self.collection.insert_one(application)                       │
│   # ✓ SAVED TO MONGODB!                                         │
│                                                                  │
│ MongoDB Document Saved:                                          │
│ Database: resume_filtering                                       │
│ Collection: applications                                         │
│ {                                                                │
│   "_id": ObjectId("607f1f77bcf86cd799439011"),  ← Auto-generated │
│   "applicationId": "a1b2c3d4e5f6g7h8i9j0k1l2",                 │
│   "jobId": "job_xyz123",                                        │
│   "jobTitle": "Senior Python Developer",                        │
│   "candidateName": "John Doe",                                  │
│   "email": "john@example.com",                                  │
│   "phone": "9876543210",                                        │
│   "degree": "BTech",                                            │
│   "branch": "Computer Science",                                 │
│   "resumeName": "resume_john_doe.pdf",                          │
│   "resumePdfPath": "Backend/instance/storage/uploads/resumes/a1b2c3d4e5f6_resume_john_doe.pdf",  │
│   "resumeTextPath": "Backend/instance/storage/tmp/resume_a1b2c3d4e5f6.txt",  │
│   "nlpOutputPath": "Nlp_Engine/output/REQ_20260217_010509_nlp_output.json",  │
│   "score": 85,                                                  │
│   "rank": 1,                                                    │
│   "status": "Selected",                                         │
│   "emailSent": true,                                            │
│   "createdAt": "2026-02-17T10:35:22.123456"                     │
│ }                                                                │
│                                                                  │
│ At this point:                                                   │
│   ✓ Resume metadata in database                                 │
│   ✓ All extracted data indexed                                  │
│   ✓ Searchable by: applicationId, jobId, candidateName, score  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────────┐
│ FINAL STATE: Resume Data Stored Everywhere                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ Resume Data Now Exists In:                                       │
│                                                                  │
│ 1. FILE SYSTEM (on disk)                                         │
│    └─ Backend/instance/storage/uploads/resumes/                │
│       └─ a1b2c3d4e5f6_resume_john_doe.pdf (350 KB)            │
│                                                                  │
│ 2. TEMP STORAGE (for processing)                                │
│    └─ Backend/instance/storage/tmp/                            │
│       └─ resume_a1b2c3d4e5f6.txt (12 KB)  [can be deleted]     │
│                                                                  │
│ 3. NLP OUTPUT (extracted data)                                   │
│    └─ Nlp_Engine/output/                                        │
│       └─ REQ_20260217_010509_nlp_output.json (2 KB)             │
│                                                                  │
│ 4. MONGODB DATABASE (references + metadata)                      │
│    └─ resume_filtering.applications.insert_one({...})           │
│       └─ Document stored with paths and scores                  │
│                                                                  │
│ All linked by applicationId: "a1b2c3d4e5f6g7h8i9j0k1l2"         │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

# FILE SYSTEM STORAGE

## Directory Structure

```
Backend/
│
└── instance/
    │
    └── storage/
        │
        ├── uploads/                    ← PERMANENT STORAGE
        │   │
        │   └── resumes/                ← PDF Files here
        │       │
        │       ├── a1b2c3d4e5f6_resume_john_doe.pdf (350 KB)
        │       ├── b2c3d4e5f6g7_resume_jane_smith.pdf (420 KB)
        │       ├── c3d4e5f6g7h8_resume_alex_kumar.pdf (280 KB)
        │       └── ...
        │
        └── tmp/                        ← TEMPORARY STORAGE
            │
            ├── resume_a1b2c3d4e5f6.txt (12 KB) → Can delete after NLP
            ├── job_job_xyz123.txt (8 KB) → Can delete after NLP
            ├── resume_b2c3d4e5f6g7.txt (15 KB)
            └── ...


KEY POINTS:
-----------
1. Uploads DIR: Permanent storage for original PDFs
   ✓ Keeps original file safe
   ✓ Can retrieve anytime
   ✓ Backed up

2. Tmp DIR: Temporary, can be cleaned
   ✓ Text versions of PDFs
   ✓ Job description text
   ✓ Cleaned after processing (optional)

3. Naming: Unique ID + Original Name
   ✓ a1b2c3d4e5f6_resume_john_doe.pdf
   ✓ Prevents filename collisions
   ✓ Original name visible for user reference
   ✓ Unique ID for internal tracking
```

## File Naming Convention

```
Formula: {UUID_HEX}_{SAFE_FILENAME}

Example:
--------
Original: resume.pdf → a1b2c3d4e5f6_resume.pdf
Original: "My-Resume(v2).pdf" → b2c3d4e5f6g7_My-Resumev2.pdf
Original: "%#@!.pdf" → c3d4e5f6g7h8_upload.bin

Benefits:
---------
✓ No collisions (UUID globally unique)
✓ Secure (original name sanitized)
✓ Readable (keeps descriptive filename)
✓ Traceable (UUID links to database)
```

---

# DATABASE STORAGE (MONGODB)

## MongoDB Collection Schema

```javascript
// Collection: applications
// Database: resume_filtering

// Single Document Example:
{
  "_id": ObjectId("607f1f77bcf86cd799439011"),           // MongoDB auto-ID
  
  // IDENTIFICATION
  "applicationId": "a1b2c3d4e5f6g7h8i9j0k1l2",          // Our unique ID
  
  // JOB INFORMATION
  "jobId": "job_xyz123",                                // Which job
  "jobTitle": "Senior Python Developer",                // Job title
  "companyId": "comp_abc123",                           // Hiring company
  "companyRegNo": "CIN:U72900KA2022PTC123456",         // Company license
  
  // CANDIDATE INFORMATION
  "candidateName": "John Doe",                          // Full name
  "email": "john@example.com",                          // Contact email
  "phone": "9876543210",                                // Phone number
  "degree": "BTech",                                    // Degree level
  "branch": "Computer Science",                         // Field of study
  
  // RESUME FILES (REFERENCES/PATHS)
  "resumeName": "resume_john_doe.pdf",                  // Original filename
  "resumePdfPath": "Backend/instance/storage/uploads/resumes/a1b2c3d4e5f6_resume_john_doe.pdf",
  "resumeTextPath": "Backend/instance/storage/tmp/resume_a1b2c3d4e5f6.txt",
  "nlpOutputPath": "Nlp_Engine/output/REQ_20260217_010509_nlp_output.json",
  
  // AI RESULTS
  "score": 85,                                          // Final score 0-100
  "rank": 1,                                            // Rank among job applicants
  "status": "Selected",                                 // Selected or Rejected
  "emailSent": true,                                    // Email sent to candidate?
  
  // METADATA
  "createdAt": "2026-02-17T10:35:22.123456",           // Application timestamp
}
```

## What's NOT Stored in Database

```
❌ LARGE FILES (stored on disk instead):
   ├─ PDF files (200-500 KB) ← File system
   ├─ Raw text files (5-50 KB) ← File system
   └─ Images/attachments ← File system

❌ WHY NOT?
   ├─ Database slow for large files
   ├─ Database storage expensive
   ├─ Hard to backup large BLOBs
   └─ File system better optimized

✅ SMALL DATA (stored in database):
   ├─ Paths/references to files ← String (100 bytes)
   ├─ Scores/metadata ← Numbers (8 bytes)
   ├─ Candidate info ← String (500 bytes)
   └─ Timestamps ← ISO string (30 bytes)

✅ WHY DATABASE?
   ├─ Fast queries
   ├─ Indexed search (find by score, name, etc.)
   ├─ ACID compliance
   ├─ Easy backup
   └─ Relationships (link candidate to job)
```

## Query Examples

```javascript
// Find all applications for a job
db.applications.find({ jobId: "job_xyz123" })
// Result: 5 applications

// Find all "Selected" candidates for a company
db.applications.find({ 
  companyId: "comp_abc123", 
  status: "Selected" 
})
// Result: 8 selected candidates

// Find all candidates with score > 80
db.applications.find({ score: { $gt: 80 } })
// Result: 15 high-scoring candidates

// Find candidate by name
db.applications.find({ candidateName: "John Doe" })
// Result: All applications from this person

// Find by rank (top 3 candidates for a job)
db.applications.find({ 
  jobId: "job_xyz123", 
  rank: { $in: [1, 2, 3] } 
})
// Result: Top 3 candidates
```

---

# COMPLETE ARCHITECTURE DIAGRAM

## Data Flow: Where Resume Lives

```
┌────────────────────────────────────────────────────────────────┐
│                     USER UPLOADS RESUME                        │
│                    (Browser/Frontend)                          │
│                  resume_john_doe.pdf                           │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         │ HTTP POST /api/apply
                         │ FormData with file
                         ↓
┌────────────────────────────────────────────────────────────────┐
│              BACKEND ROUTES LAYER                               │
│         (application_routes.py)                                │
│                                                                │
│  1. Receive file in memory                                    │
│  2. Validate (is PDF? < 20 MB?)                              │
│  3. Call services                                             │
└────────────────────────┬───────────────────────────────────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ↓                ↓                ↓
   ┌─────────┐      ┌─────────┐      ┌──────────┐
   │ Storage │      │ Pipeline│      │   Job    │
   │ Service │      │ Service │      │ Service  │
   └────┬────┘      └────┬────┘      └────┬─────┘
        │                │                │
        │ Save PDF       │ Run AI         │ Fetch
        │ to disk        │ pipeline       │ job
        ↓                ↓                │
   ┌──────────────────┐                   │
   │   FILE SYSTEM    │   Extract Text    │
   │   (Hard Disk)    │   from PDF        │
   │                  │                   │
   │  uploads/        │   ┌─────────────┐ │
   │  resumes/        │   │  Text File  │ │
   │                  │   │  (tmp/)     │ │
   │  a1b2c3d4_...pdf │   └─────────────┘ │
   │  (350 KB)        │         │          │
   │                  │         │ NLP      │
   │  [PERMANENT]     │         │ Engine   │
   │                  │         │          │
   └──────────────────┘         ↓          │
                           ┌──────────┐    │
                           │ AI       │    │
                           │ Scorer   │    │
                           └────┬─────┘    │
                                │          │
                   ┌────────────┴┴─────────┘
                   │
                   ↓
          ┌────────────────────┐
          │ APPLICATION SERVICE │─────┐
          └────────────────────┘      │
                   │                  │
                   │ Create record    │
                   │ with all paths   │
                   │                  │
                   ↓                  │
          ┌────────────────────┐      │
          │    MONGODB         │◄─────┘
          │  (Database)        │
          │                    │
          │ resume_filtering   │
          │   ↓               │
          │   applications     │
          │   collection       │
          │                    │
          │ {                  │
          │  applicationId:... │
          │  resumePdfPath:    │
          │   ".../upload/.."  │
          │  resumeTextPath:   │
          │   ".../tmp/.."     │
          │  nlpOutputPath:..  │
          │  score: 85         │
          │  status: Selected  │
          │ }                  │
          │                    │
          │ [PERMANENT]        │
          └────────────────────┘

KEY LOCATIONS:
--------------
✓ Resume PDF: Backend/instance/storage/uploads/resumes/
✓ Temp Text: Backend/instance/storage/tmp/
✓ NLP Output: Nlp_Engine/output/
✓ Database Records: MongoDB (resume_filtering.applications)
✓ Paths Stored In: Database (as strings)
```

---

# INTERVIEW QUESTIONS & ANSWERS

## Question 1: "Where do you store resumes?"

**Answer:**
> "We store resumes in **two layers**:
>
> **Layer 1 - File System (Physical Storage)**
> - Original PDF files are saved to disk
> - Location: `Backend/instance/storage/uploads/resumes/`
> - Files renamed with unique IDs: `a1b2c3d4e5f6_resume.pdf`
> - This is permanent storage
>
> **Layer 2 - Database (Reference Storage)**
> - MongoDB stores metadata about the resume
> - Includes: file paths, candidate info, scores
> - Does NOT store the PDF itself (too large)
> - Stores references to files on disk
>
> **Why Two Places?**
> - File system = cheap, fast storage for large files
> - Database = fast queries, indexing for metadata"

---

## Question 2: "Why don't you store the entire PDF in the database?"

**Answer:**
> "Good question! Even though MongoDB can store large files (using GridFS), we don't because:
>
> **Performance:**
> - File system reads/writes faster than database
> - Database better for small structured data
>
> **Cost:**
> - Database storage is expensive
> - Disk storage is cheap
>
> **Scalability:**
> - File system scales to terabytes easily
> - Database can handle many small documents
>
> **Backup:**
> - Easy to backup just file paths (database)
> - Easy to backup files separately (file system)
>
> **Retrieval:**
> - To show PDF to user → read from disk directly
> - To find candidates by score → query database
>
> **Best Practice:**
> - Files on disk
> - Metadata in database
> - Database has paths to files"

---

## Question 3: "How do you prevent filename collisions?"

**Answer:**
> "We use a **two-part naming convention**:
>
> `{UNIQUE_ID}_{SAFE_FILENAME}`
>
> **Example:**
> - User uploads: `resume.pdf`
> - We generate: UUID hex = `a1b2c3d4e5f6`
> - Final name: `a1b2c3d4e5f6_resume.pdf`
>
> **Benefits:**
> - **Unique:** UUID-32 hex = 4.9 × 10^36 combinations
> - **Safe:** Original name sanitized (removes special chars)
> - **Readable:** Human can still see it was a resume
> - **Traceable:** UUID links to database record
>
> **Why not just UUID?**
> - Could work, but lose original filename info
> - User experiences: `a1b2c3d4e5f6.pdf` (less meaningful)
>
> **Why not just original name?**
> - Two users upload `resume.pdf` same day
> - Second file overwrites first
> - Data loss!
>
> **Why UUID + safe filename?**
> - Best of both: unique + meaningful"

---

## Question 4: "What if someone tries to download another person's resume?"

**Answer:**
> "Good security question! We have multiple protections:
>
> **1. File Path Security:**
> - Resume stored as: `uploads/resumes/a1b2c3d4e5f6_resume.pdf`
> - User doesn't know the UUID
> - Can't guess path (4.9 × 10^36 possibilities)
>
> **2. Database Authentication:**
> - `/api/resumes/{applicationId}` route protected
> - Only company HR can access their own applications
> - Backend verifies: companyId matches logged-in user
>
> **3. Code Example (in application_routes.py):**
>    ```python
>    def get_application(application_id):
>        # Check if user is authorized (added auth check)
>        if current_user.company_id != application.company_id:
>            return 401 Unauthorized
>        return application
>    ```
>
> **4. File System Permissions:**
> - Files on disk have restricted permissions
> - Only Flask process can read them (not public)
>
> **5. No Direct File Access:**
> - Frontend can't call: `http://localhost:5000/uploads/resumes/...`
> - Frontend must use: `GET /api/resumes/{id}`
> - Route verifies permissions before serving file
>
> **If someone tries:**
> ```
> GET /uploads/resumes/a1b2c3d4e5f6_resume.pdf
>    ↓ (Direct access forbidden)
> 404 Not Found
>
> GET /api/resumes/someone_else_id
>    ↓ (Authorization check)
> 401 Unauthorized
> ```"

---

## Question 5: "What data is extracted from the resume and how is it stored?"

**Answer:**
> "From resume, we extract and store:
>
> **Text Extraction (From PDF):**
> - All text converted to readable format
> - Location: `Backend/instance/storage/tmp/resume_id.txt`
> - Temporary (can delete after NLP)
>
> **Structured Data (From NLP Engine):**
> - Skills: ['Python', 'Java', 'Django']
> - Experience: 3 years
> - Education: BTech in CS
> - Contact: john@email.com
> - Location: `Nlp_Engine/output/REQ_xxx_nlp_output.json`
>
> **Metadata (In MongoDB Database):**
> ```javascript
> {
>   \"candidateName\": \"John Doe\",
>   \"email\": \"john@example.com\",
>   \"phone\": \"9876543210\",
>   \"degree\": \"BTech\",
>   \"branch\": \"Computer Science\",
>   \"skills\": [...], (optional, if store)
>   \"experience\": [...], (optional, if store)
>   \"score\": 85,
>   \"status\": \"Selected\"
> }
> ```
>
> **What's NOT stored:**
> - Raw PDF text (stored as temp file only)
> - Full resume document (stored as PDF file)
>
> **Why this split?**
> - Large data (PDF, text) → File system
> - Small data (metadata, scores) → Database
> - Structured data (NLP JSON) → File system (for audit trail)"

---

## Question 6: "How do you handle resume updates?"

**Answer:**
> "Currently, we treat each application as final. However, here's how we handle it:
>
> **Current Design:**
> - Each resume create new application ID
> - Each score/status is separate record
> - User can apply again (new scoresheet)
> - Serves as audit trail (can see all attempts)
>
> **Example:**
> ```
> John Doe applies for Python Job:
> Application 1: Score 75 (Rejected)
> 
> John reapplies (better resume):
> Application 2: Score 88 (Selected)
> 
> Both stored in MongoDB:
> - Different applicationIds
> - Different scores
> - Company can see both
> ```
>
> **If We Need True 'Updates':**
> ```python
> # Current: Insert new record
> collection.insert_one(new_application)
>
> # Future approach: Update existing
> collection.update_one(
>     {\"applicationId\": app_id},
>     {\"$set\": {\"score\": new_score}}
> )
> ```
>
> **Benefits of Current Approach:**
> - Historical record maintained
> - Can see score progression
> - Fair if multiple submissions allowed
> - Audit trail for compliance"

---

## Question 7: "How do you delete resumes?"

**Answer:**
> "Deletion is handled in tiers:
>
> **Immediate Delete (After Processing):**
> ```
> Backend/instance/storage/tmp/resume_id.txt
> └─ Deleted after NLP processing
> └─ Temp file only, not needed anymore
> ```
>
> **On-Demand Delete (Optional):**
> ```python
> # User/Company requests deletion
> def delete_application(app_id):
>     # 1. Delete from database
>     collection.delete_one({\"applicationId\": app_id})
>     
>     # 2. Delete PDF from disk
>     os.remove(application[\"resumePdfPath\"])
>     
>     # 3. Delete NLP output
>     os.remove(application[\"nlpOutputPath\"])
> ```
>
> **Files to Delete:**
> - PDF file: `uploads/resumes/a1b2c3d4_resume.pdf`
> - NLP output: `Nlp_Engine/output/REQ_xxx_nlp_output.json`
> - Database record: `applications` collection
>
> **Retention Policy (Best Practice):**
> ```
> Temporary files (txt): Delete immediately
> Resume files (pdf): Keep 90 days
> NLP output (json): Keep 90 days
> Database records: Keep per policy (7 years for audit)
> ```
>
> **Compliance:**
> - GDPR: User can request data deletion
> - Right to forget: Delete personal data
> - But keep: Anonymized records for analytics"

---

## Question 8: "What happens if a resume is corrupted?"

**Answer:**
> "We have error handling at each stage:
>
> **Stage 1: Upload (Storage Service)**
> ```python
> try:
>     # Save file to disk
>     file_storage.save(path)
> except Exception as e:
>     return error(\"Failed to save resume\", 400)
> ```
>
> **Stage 2: Parse (Resume Parser)**
> ```python
> try:
>     resume_text = parser.parse(pdf_path)
>     if not resume_text.strip():
>         raise ValueError(\"PDF appears empty\")
> except Exception as e:
>     logger.exception(\"PDF parsing failed\")
>     return error(\"Could not extract text from PDF\", 400)
> ```
>
> **Stage 3: NLP (NLP Engine)**
> ```python
> nlp_response = process_resumes(jd_path, [resume_path])
> if not nlp_response.get(\"success\"):
>     raise RuntimeError(nlp_response.get(\"error\"))
> ```
>
> **User Experience:**
> ```
> Upload PDF → Failed to parse
> ↓
> Return error: \"Resume appears corrupted. Please try another file.\"
> ↓
> User gets feedback + can retry
> ```
>
> **Logging:**
> ```
> All errors logged with:
> - applicationId
> - Timestamp
> - Error message
> - Stack trace
> ↓
> Helps debugging later
> ```
>
> **Fallback:**
> If PDF corrupted but already saved:
> - Mark application as \"Failed\"
> - Keep PDF for manual review
> - Notify company admin
> - Log for investigation"

---

## Question 9: "What's the maximum resume size?"

**Answer:**
> "Maximum file size: **20 MB**
>
> **Configuration (in config.py):**
> ```python
> MAX_CONTENT_LENGTH = 20971520  # 20 MB in bytes
> ```
>
> **Why 20 MB?**
> - Typical resume: 200-500 KB
> - 20 MB = 40x buffer for edge cases
> - PDF with many images: ~2-5 MB
> - Prevents abuse: infinite file uploads
> - Balances practicality + security
>
> **If File Too Large:**
> ```
> User uploads 50 MB file
>     ↓
> request.max_content_length check
>     ↓
> HTTP 413 Payload Too Large
>     ↓
> Error: \"File too large. Maximum 20 MB.\"
> ```
>
> **How to Increase:**
> ```python
> # In config.py
> MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB
> ```
>
> **Monitoring:**
> ```python
> # Track uploads
> if file.size > 5_000_000:  # 5 MB
>     logger.warning(f\"Large file upload: {file.size} bytes\")
> ```
>
> **Compression:**
> ```
> If user has large file:
> Recommendation: \"Please compress PDF or remove images\"
> ```"

---

## Question 10: "How do you ensure resume data privacy?"

**Answer:**
> "Privacy protected at multiple levels:
>
> **1. Storage Level:**
> - Files on disk, not accessible via web
> - Only Flask process can read files
> - Encrypted file permissions
>
> **2. Database Level:**
> - MongoDB password protected
> - Only backend can access
> - Connections use TLS encrypted
>
> **3. API Level:**
> - Require authentication token
> - Check user permissions
> - Log all access attempts
>
> **4. Code Example:**
> ```python
> @app.route(\"/api/resumes/<app_id>\", methods=[\"GET\"])
> @login_required  # Must be logged in
> def get_resume(app_id):
>     # Get current user (authenticated)
>     user_id = current_user.id
>     
>     # Fetch application
>     app = db.applications.find_one({\"applicationId\": app_id})
>     
>     # Check owner (privacy check)
>     if app[\"companyId\"] != user_id:
>         return \"Unauthorized\", 401
>     
>     # Serve file
>     return send_file(app[\"resumePdfPath\"])
> ```
>
> **4. Anonymization:**
> - Before sharing reports, remove names
> - Show only: score, rank, skills match
>
> **5. Audit Trail:**
> - Log who accessed which resume
> - Log what operations performed
> - For compliance investigations
>
> **6. GDPR Compliance:**
> - User can request data deletion
> - Auto-delete after retention period
> - Privacy policy transparent
>
> **Summary:**
> - Encrypt at rest (on disk)
> - Encrypt in transit (HTTPS)
> - Authenticate access
> - Authorize by role
> - Log everything
> - Delete on request"

---

# SUMMARY: How to Answer \"Resume Storage\" Question

## Structure Your Answer:

```
START WITH HIGH LEVEL:
├─ "We store resumes in TWO places"
├─ 1. File System (PDFs)
└─ 2. Database (References)

THEN EXPLAIN EACH:
├─ File System:
│  ├─ Where: Backend/instance/storage/uploads/resumes/
│  ├─ What: Original PDF files
│  ├─ How: Saved with unique IDs
│  └─ Why: Cheap, fast, scalable
│
└─ Database:
   ├─ Where: MongoDB (resume_filtering)
   ├─ What: Metadata + file paths
   ├─ How: Insert as document
   └─ Why: Fast queries, indexing

THEN ADD THE FLOW:
├─ Upload → Parse → Extract → Score → Save → Return

THEN HANDLE FOLLOW-UPS:
├─ Security: Multiple auth layers
├─ Privacy: Encryption + Access control
├─ Scalability: File system handles millions
└─ Compliance: Audit trail logged
```

---

**You're now ready to answer ANY resume storage question! 🎯**
