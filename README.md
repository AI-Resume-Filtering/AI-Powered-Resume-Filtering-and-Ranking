# AI-Powered Resume Filtering and Ranking

## 🚀 Recent Upgrades & Features

**1. Multi-Branch/Field Resume Support:**
The skill extraction engine and database now support all major fields (Engineering, Commerce, Law, Medicine, Arts, etc.), not just IT. This enables universal applicability for any job domain.

**2. Semantic (Meaning-Based) Matching:**
The system uses advanced semantic similarity (SBERT) to match resumes and job descriptions based on meaning, not just keywords. This improves ranking quality for diverse writing styles and fields.

**3. Job Description Deduplication:**
When a new job is created, the backend computes a hash of the job description text and checks for duplicates. If a job with the same description already exists for the company, it reuses the existing job instead of storing a duplicate. This saves storage and prevents redundant postings.

**4. Code Cleanup:**
Obsolete IT-only logic has been removed. All modules are now field-agnostic and extensible.

**5. Documentation:**
README and module docs have been updated to reflect these changes. See below for details.

This project is a complete hiring pipeline that converts resume uploads into ranked, explainable candidate recommendations.

It combines:
1. Resume PDF parsing.
2. NLP feature extraction.
3. Semantic and rule-based scoring.
4. Feedback-driven model retraining.
5. Recruiter and candidate web workflows.

## 1. Business problem solved

Manual resume screening is slow and inconsistent.
This platform automates shortlist generation while preserving explainability.

Core outcomes:
1. Faster filtering.
2. More relevant ranking.
3. Transparent score breakdown.
4. Continuous learning from recruiter decisions.

## 2. Complete architecture overview

Main modules:
1. `Frontend/`
Role: recruiter and candidate UI.
2. `Backend/`
Role: API gateway, storage orchestration, async pipeline trigger, feedback APIs.
3. `Resume_Parser/`
Role: PDF to text conversion with OCR fallback.
4. `Nlp_Engine/`
Role: text to structured candidate features.
5. `Ai_Scoring/`
Role: score calculation, ranking logic, model retraining.

Supporting pieces:
1. `start-dev.ps1`
Role: local startup helper and environment bootstrap.
2. `requirements.txt`
Role: central Python dependency install point.

## 3. End-to-end click-to-response flow

### Recruiter setup flow

1. Recruiter registers/logs in from frontend.
2. Frontend calls backend auth endpoints.
3. Backend validates and stores company records.
4. Recruiter creates job with title and description.
5. Backend stores job document and exposes it via job APIs.

### Candidate apply flow

1. Candidate opens a job and submits details plus resume PDF.
2. Frontend sends multipart request to apply endpoint.
3. Backend validates payload and file.
4. Backend saves resume file to storage.
5. Backend inserts initial application record with status `processing`.
6. Backend starts background thread for heavy processing.
7. Backend immediately returns success with processing status.

### AI processing flow

1. Pipeline reads saved resume PDF.
2. Resume Parser extracts and cleans text.
3. Pipeline converts job description to text input.
4. NLP Engine extracts job requirements and resume features.
5. AI Scoring computes semantic and component scores.
6. If trained model exists, ML score is used.
7. Backend updates application with final fields:
8. Total score.
9. Component scores.
10. Rank metadata.
11. Status selected/rejected by threshold.
12. If selected and SMTP is configured, email is sent.

### Recruiter decision feedback flow

1. Recruiter marks selected/rejected manually.
2. Frontend posts feedback payload.
3. Backend stores labeled feedback row.
4. Backend checks retraining threshold and minimum sample requirements.
5. AI model retrains when conditions are met.
6. Future scoring uses improved model behavior.

## 4. Detailed module map with key files

Backend key files:
1. `Backend/app/routes/application_routes.py`
Handles apply endpoint, status polling, and feedback path.
2. `Backend/app/services/pipeline_service.py`
Bridges parser, NLP, and scoring.
3. `Backend/app/services/email_service.py`
SMTP email delivery with retries.
4. `Backend/app/config.py`
Environment-driven configuration.

Resume Parser key files:
1. `Resume_Parser/resume_parser.py`
Main parse orchestration.
2. `Resume_Parser/ocr_parser.py`
OCR fallback for scanned PDFs.
3. `Resume_Parser/text_cleaner.py`
Output text cleanup.
4. `Resume_Parser/batch_parser.py`
Batch parse flow.

NLP Engine key files:
1. `Nlp_Engine/Nlp_service.py`
Main NLP orchestrator.
2. `Nlp_Engine/job_description_parser.py`
JD requirement extraction.
3. `Nlp_Engine/skill_extractor.py`
Skill detection.
4. `Nlp_Engine/experience_calculator.py`
Experience estimates.
5. `Nlp_Engine/output_formatter.py`
Stable output schema.

AI Scoring key files:
1. `Ai_Scoring/Ai_Scoring/scorer.py`
Scoring control and final output assembly.
2. `Ai_Scoring/Ai_Scoring/semantic_matcher.py`
Semantic similarity.
3. `Ai_Scoring/Ai_Scoring/model_trainer.py`
Feedback-based retraining.

Frontend key files:
1. `Frontend/react-project/src/pages/ApplyJob.jsx`
Candidate apply page.
2. `Frontend/react-project/src/pages/dashboard/Resumes.jsx`
Recruiter application review page.
3. `Frontend/react-project/src/api/index.js`
Central API integration.

## 5. Scoring logic summary

Current scoring combines:
1. Semantic match score.
2. Experience score.
3. Education score.

Fallback blended score exists for reliability when no trained model is available.

Explainability fields are returned to backend and frontend for transparency.

## 6. Data persistence summary

Mongo collections include:
1. Company records.
2. Job records.
3. Application records with full score metadata.
4. Feedback records used for retraining.

Stored files include:
1. Uploaded resumes.
2. Temporary text artifacts for pipeline processing.

## 7. Environment and setup details

Prerequisites:
1. Python 3.10+
2. Node.js 18+
3. MongoDB running locally or remotely.
4. Tesseract OCR installed for scanned PDFs.

Primary setup:
1. Install Python dependencies from project root:
`pip install -r requirements.txt`
2. Install frontend dependencies:
`cd Frontend/react-project`
`npm install`
3. Start services from project root:
`./start-dev.ps1`

Environment files:
1. `Backend/.env`
2. `Backend/.env.example`
3. `Frontend/react-project/.env`
4. `Frontend/react-project/.env.example`

## 8. Operational troubleshooting

If applications remain in processing:
1. Check backend logs for parser/NLP/scoring errors.
2. Verify file storage permissions.
3. Verify NLP output generation.

If selection email is not sent:
1. Verify SMTP settings in backend env.
2. Verify `SMTP_HOST` is mail server host, not email address.
3. Verify candidate status reached selected threshold.

If model never retrains:
1. Verify feedback volume.
2. Verify both positive and negative labels exist.
3. Verify retraining thresholds in env config.

## 9. Security and quality notes

1. Keep real secrets out of tracked files.
2. Use `.env.example` templates for portability.
3. Validate all incoming payloads.
4. Preserve explainability in score outputs.

## 10. Detailed module docs

1. `Backend/README.md`
2. `Resume_Parser/README.md`
3. `Nlp_Engine/README.md`
4. `Ai_Scoring/README.md`
5. `Frontend/README.md`

Each module README contains file-level detail, processing flow, troubleshooting, and interview preparation.
