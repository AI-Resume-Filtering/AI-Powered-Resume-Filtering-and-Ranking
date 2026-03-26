# AI-Powered Resume Filtering and Ranking — Detailed Technical Overview (March 2026)

## 1. System Architecture & Technology Stack

### 1.1 Overview
The system is a hybrid AI/NLP platform for automated resume filtering and ranking. It combines advanced semantic AI (SBERT sentence-transformers) with rule-based NLP, heuristic scoring, and a modern web frontend.

### 1.2 Backend
- **Language:** Python 3.x
- **Framework:** Flask
- **Database:** MongoDB
- **AI/NLP Libraries:**
  - sentence-transformers (SBERT)
  - numpy, joblib
  - pdfplumber, PyMuPDF, pytesseract (for PDF extraction)
  - fuzzywuzzy/SequenceMatcher (for fuzzy matching)

### 1.3 Frontend
- **Framework:** React
- **Styling:** CSS modules (dashboard.css, CompanyHistory.css)
- **Features:**
  - Dark theme support
  - Status color coding (red/green)
  - Visual separation of job stats
  - Blue table headers

---

## 2. End-to-End Flow

### 2.1 Resume Upload & Validation
- User uploads a PDF resume via the frontend.
- Backend saves the file and immediately validates it:
  - **BOTH email and phone number are required.**
  - **At least 3 out of 4 core sections** (education, experience, skills, projects) must be present.
  - **Candidate name must appear at the top** (first 5 lines, 2–5 words, mostly alphabetic).
  - Non-resume documents (reports, analysis, etc.) are rejected before any scoring.

### 2.2 Text Extraction & Normalization
- PDF text is extracted using pdfplumber and PyMuPDF, with OCR fallback for image-based resumes.
- Text is normalized (whitespace, encoding, bullet glyphs) for stable downstream processing.

### 2.3 NLP Extraction Pipeline
- **Section Segmentation:**
  - Detects sections using regex header patterns (skills, experience, education, projects).
- **Contact Extraction:**
  - Regex for email and phone (both now required).
- **Skill Extraction:**
  - Uses a skill database, synonym mapping, and fuzzy matching.
  - Confidence thresholding (configurable).
- **Experience Extraction:**
  - Sums all year ranges and explicit mentions.
  - Fallback: keyword count of job titles.
- **Education Extraction:**
  - Maps detected degrees to a hierarchy (PhD > Masters > Bachelors > Diploma > High School).
- **Job Description Parsing:**
  - Extracts required/preferred skills, minimum experience, required education, responsibilities.
  - Generates semantic embedding for SBERT comparison.

---

## 3. Semantic Matching (SBERT)

### 3.1 Model
- **Sentence-BERT (SBERT):** Used for encoding resumes and job descriptions into semantic embeddings.

### 3.2 Usage
- **Resume-JD Matching:**
  - Embeddings are compared using cosine similarity.
  - Used as a core feature in candidate-job matching.
- **JD Deduplication:**
  - Embeddings are used to detect and prevent duplicate job descriptions.

### 3.3 Impact
- Enables true meaning-based matching, not just keyword overlap.
- Reduces false positives from unrelated resumes.

---

## 4. Scoring Logic

### 4.1 Adaptive Profile Selection
- Scoring weights adapt based on job level (fresher, mid, senior) using config profiles.

### 4.2 Score Formula
- **Skill Score:** Based on required skill match percentage and weight.
- **Experience Score:** Ratio of candidate years to required years, capped by experience weight.
- **Education Score:** Full weight if candidate rank >= required rank, else 0.
- **Preferred Skill Score:** 2 points per preferred skill match, capped by preferred skill weight.
- **Skill-Experience Bonus:** Up to 5 bonus points for years of experience on required skills.
- **Semantic Score:** SBERT similarity is weighted and combined with rule-based scores.
- **Penalties:** For missing required skills.
- **Capping:** Final score capped at 100.

### 4.3 Batch Processing & Ranking
- Only resumes marked as scoring_ready are processed.
- Batch scoring sorts by total_score desc, then experience_years desc.
- Ranks are assigned dynamically.

---

## 5. Validation Pipeline (Strict Resume Filtering)

### 5.1 Contact Information
- BOTH email and phone number are required. If either is missing, the document is rejected.

### 5.2 Resume Sections
- At least 3 out of 4 core sections (education, experience, skills, projects) must be present.

### 5.3 Candidate Name at the Top
- First 5 lines must contain a plausible candidate name (2–5 words, mostly alphabetic).

### 5.4 Removed Checks
- No longer requires “resume” or “CV” keywords on the first page.

### 5.5 Effect
- Non-resume documents (such as technical reports, analysis documents, or project documentation) are rejected and not scored.
- Only genuine resumes with clear structure and contact details are accepted for further processing.

---

## 6. Deduplication

### 6.1 Job Description Deduplication
- Uses SBERT embeddings to detect and prevent duplicate JDs.
- Only unique JDs are stored; similar ones are referenced.

---

## 7. Frontend & UI Improvements

### 7.1 Visibility & Usability
- White text for dark themes.
- Status colors: red for rejected, green for selected.
- Job stats visually separated, table headers styled in blue.

---

## 8. Known Limitations & Next Steps

### 8.1 Skill Matching
- Substring and fuzzy matching can still produce some false positives.

### 8.2 Experience Calculation
- Overlapping roles may be double-counted.

### 8.3 Future Improvements
- Boundary-aware skill matching.
- Overlap-aware experience calculation.
- Potential for a learned ranking layer on top of current features.

---

## 9. Change Log (Recent Major Changes)

- Added SBERT-based semantic matching for resumes and JDs.
- Enforced strict resume validation (email, phone, sections, name at top).
- Improved frontend for dark theme and status clarity.
- Enhanced JD deduplication using semantic embeddings.
- Removed requirement for resume-specific keywords on first page.
- Refined scoring logic for stricter required skill enforcement and penalties.

---

## 10. References & Further Reading
- [SBERT: Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks](https://www.sbert.net/)
- [pdfplumber Documentation](https://github.com/jsvine/pdfplumber)
- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/en/latest/)
- [FuzzyWuzzy Documentation](https://github.com/seatgeek/fuzzywuzzy)

---

*This document reflects the current state of the project as of March 2026. For further details or code-level documentation, see the project repository files and inline comments.*
