# 🧠 NLP ENGINE - COMPLETE TECHNICAL GUIDE
## Resume & Job Description Data Extraction Module

**Date:** February 17, 2026  
**Purpose:** Extract structured data from resumes and job descriptions  
**Technology:** Python NLP, Regular Expressions, Pattern Matching  
**Integration:** Backend → NLP Engine → AI Scoring

---

## 📋 TABLE OF CONTENTS
1. [System Overview](#1-system-overview)
2. [How NLP Engine Works](#2-how-nlp-engine-works)
3. [Module-by-Module Explanation](#3-module-by-module-explanation)
4. [Complete Data Flow](#4-complete-data-flow)
5. [Configuration](#5-configuration)
6. [Integration with Backend](#6-integration-with-backend)
7. [Input/Output Examples](#7-inputoutput-examples)
8. [How to Run](#8-how-to-run)
9. [Common Issues & Solutions](#9-common-issues--solutions)
10. [Interview Q&A](#10-interview-qa)

---

# 1. SYSTEM OVERVIEW

## 🎯 What Does NLP Engine Do?

The NLP Engine is a **data extraction module** that:
1. **Parses Job Descriptions** → Extracts requirements (skills, experience, education)
2. **Parses Resumes** → Extracts candidate data (skills, experience, education)
3. **Matches Resume to Job** → Calculates match percentage
4. **Ranks Candidates** → Orders by match quality
5. **Outputs JSON** → Ready for AI Scoring

## ⚙️ It's NOT for Ranking!

**Important:** NLP Engine does **NOT rank or score** candidates. That's done by AI Scoring module.

- **NLP Engine:** Extract data ✅
- **AI Scorer:** Score and rank ✅

## 🔄 Architecture Position

```
Backend (Flask)
    ↓ (calls)
Nlp_service.py (entry point)
    ↓ (calls)
NLPBatchProcessor (orchestrates extraction)
    ↓ (calls in sequence)
├─ text_normalizer.py (clean text)
├─ section_detector.py (find sections)
├─ contact_extractor.py (get email/phone)
├─ skill_extractor.py (extract skills)
├─ experience_calculator.py (years worked)
├─ education_detector.py (degree level)
├─ job_description_parser.py (parse JD)
└─ output_formatter.py (format JSON)
    ↓ (returns)
JSON Output File
    ↓ (consumed by)
AI Scoring Module
```

---

# 2. HOW NLP ENGINE WORKS

## 📊 Complete Processing Pipeline

### **Step-by-Step Process**

```
INPUT:
- job_description.txt (job requirements)
- resume_1.txt, resume_2.txt, ... (candidates)

PROCESSING:
Step 1: Parse Job Description
        ├─ Normalize text (clean encoding issues)
        ├─ Detect sections (skills, experience, education)
        ├─ Extract required skills
        ├─ Extract preferred skills
        ├─ Extract minimum experience
        ├─ Extract required education
        ├─ Extract job title
        └─ Store as job_requirements

Step 2: Process Each Resume
        For each resume file:
        ├─ Read file
        ├─ Normalize text (clean bullets, whitespace)
        ├─ Detect sections (same as JD)
        ├─ Extract contact info (email, phone)
        ├─ Extract skills list
        ├─ Extract experience years
        ├─ Extract education level
        ├─ Calculate match with job_requirements
        └─ Store as resume_data

Step 3: Calculate Job Match
        For each resume:
        ├─ Compare resume skills vs job required skills
        ├─ Check if experience >= minimum
        ├─ Check if education >= minimum
        ├─ Calculate match percentage
        └─ Flag as "scoring_ready": true

Step 4: Rank Results
        ├─ Sort by match percentage (highest first)
        ├─ Assign ranks (1, 2, 3, ...)
        └─ Generate output JSON

OUTPUT:
- Nlp_Engine/output/REQ_YYYYMMDD_HHMMSS_nlp_output.json
  {
    "job_requirements": {...},
    "resumes": {
      "resume_001": {..., "scoring_ready": true},
      "resume_002": {..., "scoring_ready": true},
      ...
    }
  }
```

---

# 3. MODULE-BY-MODULE EXPLANATION

## 3.1 Nlp_service.py - Entry Point

**Location:** `Nlp_Engine/Nlp_service.py`

**Purpose:** Microservice interface for backend

**Code:**
```python
"""
NLP Engine Microservice API
Extracts data from resumes - NO RANKING
Ranking is done by AI Scoring Module
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict


class NLPMicroservice:
    """
    NLP Extraction Service
    - Extracts skills, experience, education
    - Matches against job requirements
    - Stores data in output folder
    - NO RANKING (AI module handles that)
    """

    def __init__(self):
        """Initialize with internal output directory"""
        self.package_dir = os.path.dirname(os.path.abspath(__file__))
        self.output_dir = os.path.join(self.package_dir, "output")
        os.makedirs(self.output_dir, exist_ok=True)

    def process_request(self,
                       jd_path: str,
                       resume_paths: List[str],
                       request_id: str = None) -> Dict:
        """
        Extract data from resumes (NO RANKING)

        Args:
            jd_path: Path to job description file
            resume_paths: List of resume file paths
            request_id: Optional request ID

        Returns:
            {
                "success": True,
                "request_id": "REQ_xxx",
                "total_resumes": 5,
                "successfully_parsed": 5,
                "output_path": "Nlp_Engine/output/REQ_xxx_nlp_output.json",
                "message": "Data extracted. Ready for AI Scoring."
            }
        """

        request_id = request_id or f"REQ_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        print(f"\n{'='*70}")
        print(f"🚀 NLP EXTRACTION - REQUEST: {request_id}")
        print(f"{'='*70}")

        try:
            # Step 1: Parse JD
            jd_data = self._parse_job_description(jd_path)
            if not jd_data:
                return self._error_response("Failed to parse job description")

            # Step 2: Process all resumes
            results = {}
            stats = {"total": 0, "success": 0, "failed": 0}

            for idx, resume_path in enumerate(resume_paths, 1):
                resume_id = f"resume_{str(idx).zfill(3)}"

                try:
                    resume_data = self._process_single_resume(
                        resume_path,
                        resume_id,
                        jd_data
                    )
                    results[resume_id] = resume_data
                    stats["success"] += 1

                except Exception as e:
                    stats["failed"] += 1

                stats["total"] += 1

            # Step 3: Save output
            output_file = self._save_output(request_id, jd_data, results, stats)

            # Step 4: Return response
            return self._create_response(request_id, stats, output_file)

        except Exception as e:
            return self._error_response(str(e))
```

**How Backend Calls It:**
```python
# Backend/app/services/pipeline_service.py
from Nlp_Engine.Nlp_service import process_resumes

# Call NLP
nlp_response = process_resumes(jd_txt_path, [resume_txt_path])

# Response:
# {
#     "success": True,
#     "request_id": "REQ_20260217_103022",
#     "total_resumes": 1,
#     "successfully_parsed": 1,
#     "output_path": "Nlp_Engine/output/REQ_20260217_103022_nlp_output.json"
# }
```

---

## 3.2 text_normalizer.py - Clean & Standardize

**Purpose:** Clean messy resume text for parsing

**Why Needed:**
- PDFs create encoding issues (â€", Ã¢)
- Bullets render differently (•, ➢, ○, ●)
- Extra whitespace and line breaks

**Code:**
```python
"""
Text Normalizer
Cleans and standardizes resume text for accurate parsing
"""

import re


def normalize_text(text: str) -> str:
    """
    Normalize resume text

    Steps:
    1. Replace bullets with newlines
    2. Fix encoding issues
    3. Normalize whitespace
    4. Remove extra line breaks
    """
    if not text:
        return ""

    # Step 1: Replace all bullet types with newlines
    bullet_chars = ["•", "➢", "○", "●", "■", "□", "▪", "▫", "→", "➤"]
    for bullet in bullet_chars:
        text = text.replace(bullet, "\n")

    # Step 2: Fix line endings
    text = re.sub(r'\r\n', '\n', text)  # Windows → Unix
    text = re.sub(r'\r', '\n', text)     # Old Mac → Unix

    # Step 3: Fix encoding issues (PDF artifacts)
    encoding_fixes = {
        'â€"': '-',      # Em dash
        'â€™': "'",      # Apostrophe
        'â€œ': '"'       # Quote
    }
    for old, new in encoding_fixes.items():
        text = text.replace(old, new)

    # Step 4: Normalize whitespace
    text = re.sub(r'\t', ' ', text)     # Tabs → Spaces
    text = re.sub(r' +', ' ', text)     # Multiple spaces → Single
    text = re.sub(r'\n+', '\n', text)   # Multiple newlines → Single

    # Step 5: Clean up lines
    lines = text.split('\n')
    cleaned_lines = [line.strip() for line in lines if line.strip()]

    return '\n'.join(cleaned_lines)


# EXAMPLE:
# Input:  "SKILLS\n•Python  •Java    •ML\n\nExp â€" 2 years"
# Output: "SKILLS\nPython\nJava\nML\nExp - 2 years"
```

**Why This Matters:**
- ❌ Poor normalization → Skills not detected
- ✅ Good normalization → Accurate extraction

---

## 3.3 section_detector.py - Find Resume Sections

**Purpose:** Locate different sections (Skills, Experience, Education)

**Sections It Finds:**
- **Skills:** Technical skills, core competencies
- **Experience:** Work experience, employment
- **Education:** Academic background, qualifications
- **Projects:** Academic/work projects
- **Summary:** Professional summary, objective

**Code:**
```python
"""
Section Detector
Finds resume sections using pattern matching
"""

import re


SECTION_PATTERNS = {
    "skills": [r"technical\s+skills", r"skills", r"competencies"],
    "experience": [r"experience", r"work\s+experience", r"employment"],
    "education": [r"education", r"academic\s+background"],
    "projects": [r"projects", r"key\s+projects"],
    "summary": [r"professional\s+summary", r"summary", r"profile"]
}


def detect_sections(text: str) -> dict:
    """
    Detect and extract sections from resume

    Returns:
        {
            "skills": ["Python, Java, ML"],
            "experience": ["Developer - 2 years"],
            "education": ["B.E. IT"],
            "projects": ["Smart Attendance"],
            "unknown": ["Header"]
        }
    """
    sections = {}
    current_section = "unknown"
    sections[current_section] = []

    lines = text.split('\n')

    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue

        clean_lower = clean_line.lower()
        matched = False

        # Try to match section headers
        for section_name, patterns in SECTION_PATTERNS.items():
            for pattern in patterns:
                if re.search(f'^{pattern}:?$', clean_lower):
                    current_section = section_name
                    if current_section not in sections:
                        sections[current_section] = []
                    matched = True
                    break
            if matched:
                break

        # Add line to current section
        if not matched:
            sections[current_section].append(clean_line)

    return sections
```

---

## 3.4 contact_extractor.py - Get Email & Phone

**Purpose:** Extract contact information

**Regex Patterns:**
- **Email:** `user@domain.com`
- **Phone:** `+91 9356736650`, `9356736650`

**Code:**
```python
"""
Contact Information Extractor
"""

import re


def extract_contact_info(text: str) -> dict:
    """Extract email and phone"""
    return {
        "email": extract_email(text),
        "phone": extract_phone(text)
    }


def extract_email(text: str) -> str:
    """Extract email address"""
    pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    matches = re.findall(pattern, text)
    return matches[0] if matches else ""


def extract_phone(text: str) -> str:
    """Extract phone number (10+ digits)"""
    pattern = r'[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{3,6}[-\s\.]?[0-9]{4,6}'
    matches = re.findall(pattern, text)
    
    for match in matches:
        digits = re.sub(r'\D', '', match)
        if len(digits) >= 10:
            return match
    
    return ""
```

---

## 3.5 skill_extractor.py - Extract Technical Skills

**Purpose:** Identify technical skills

**Method:**
1. **Exact match:** "Python" in text
2. **Synonym match:** "Py" → "Python"
3. **Fuzzy match:** "Pytho" → "Python" (86% similar)

**Code:**
```python
"""
Skill Extractor
Extracts skills using fuzzy matching and synonyms
"""

import re
from difflib import SequenceMatcher
from .skill_database import SKILL_DATABASE
from .config import MIN_CONFIDENCE, USE_FUZZY_MATCHING, FUZZY_THRESHOLD


def extract_skills(text: str) -> dict:
    """
    Extract all skills from text

    Returns:
        {
            "skills_list": ["python", "java", "ml"],
            "skills_by_category": {"programming_language": 2, "ai_ml": 1},
            "skill_details": {"python": {"confidence": 0.95, "category": "programming_language"}}
        }
    """
    text_lower = text.lower()
    found_skills = {}

    # Check each skill in database
    for skill_name, skill_data in SKILL_DATABASE.items():
        matched, confidence = _match_skill(
            text_lower,
            skill_name,
            skill_data["synonyms"]
        )

        if matched and confidence >= MIN_CONFIDENCE:
            found_skills[skill_name] = {
                "confidence": confidence,
                "category": skill_data["category"]
            }

    # Categorize skills
    skills_by_category = {}
    for skill_name, skill_info in found_skills.items():
        category = skill_info["category"]
        skills_by_category[category] = skills_by_category.get(category, 0) + 1

    return {
        "skills_list": list(found_skills.keys()),
        "skills_by_category": skills_by_category,
        "skill_details": found_skills
    }


def _match_skill(text: str, skill: str, synonyms: list) -> tuple:
    """
    Match skill using methods:
    1. Exact match → confidence 1.0
    2. Synonym match → confidence 0.95
    3. Fuzzy match → confidence = similarity score
    """
    # Method 1: Exact
    if skill.lower() in text:
        return True, 1.0

    # Method 2: Synonym
    for synonym in synonyms:
        if synonym.lower() in text:
            return True, 0.95

    # Method 3: Fuzzy (if enabled)
    if USE_FUZZY_MATCHING:
        words = re.findall(r'\b\w+\b', text)
        for word in words:
            similarity = SequenceMatcher(None, skill.lower(), word).ratio()
            if similarity >= FUZZY_THRESHOLD:
                return True, round(similarity, 2)

    return False, 0.0
```

---

## 3.6 experience_calculator.py - Calculate Work Experience

**Purpose:** Calculate total years of experience

**Methods (Priority):**
1. Explicit mention: "5 years of experience"
2. Date calculation: "2021-2025" = 4 years
3. Position counting: Count job titles
4. Default: 0 years

**Code:**
```python
"""
Experience Calculator
Calculates total years of work experience
"""

import re
from datetime import datetime


def calculate_experience_years(text: str) -> int:
    """
    Calculate total years of experience using multiple methods
    """
    # Method 1: Explicit mentions
    pattern = r'(\d+)\s*(?:year|yr)s?'
    matches = re.findall(pattern, text.lower())
    
    if matches:
        return max(map(int, matches))

    # Method 2: Calculate from year ranges
    current_year = datetime.now().year
    year_mentions = re.findall(r'\b(20\d{2})\b', text)
    
    if year_mentions:
        years = [int(y) for y in year_mentions]
        earliest = min(years)
        
        if current_year - earliest < 50:  # Sanity check
            return current_year - earliest

    # Method 3: Count positions
    position_keywords = ['intern', 'developer', 'engineer', 'analyst']
    count = 0
    for keyword in position_keywords:
        count += len(re.findall(keyword, text.lower()))
    
    return min(count, 10)  # Cap at 10


# EXAMPLE:
# Input: "Developer (2023-2026), Intern (2022)"
# Output: 4 years
```

---

## 3.7 education_detector.py - Identify Education Level

**Purpose:** Detect highest education degree

**Hierarchy:**
1. PhD (level 5)
2. Masters (level 4)
3. Bachelors (level 3)
4. Diploma (level 2)
5. High School (level 1)

**Code:**
```python
"""
Education Detector
Detects highest education level
"""

import re


DEGREE_LEVELS = {
    "phd": {"patterns": ["phd", "doctorate"], "level": 5},
    "masters": {"patterns": ["master", "mtech", "mba"], "level": 4},
    "bachelors": {"patterns": ["bachelor", "btech", "bsc"], "level": 3},
    "diploma": {"patterns": ["diploma"], "level": 2},
    "high_school": {"patterns": ["hsc", "12th", "ssc"], "level": 1}
}


def detect_education_level(text: str) -> str:
    """
    Detect highest education level

    Returns:
        "phd" | "masters" | "bachelors" | "diploma" | "high_school"
    """
    text_lower = text.lower()
    highest_degree = None
    highest_level = 0

    for degree_name, degree_info in DEGREE_LEVELS.items():
        for pattern in degree_info["patterns"]:
            if pattern in text_lower:
                if degree_info["level"] > highest_level:
                    highest_level = degree_info["level"]
                    highest_degree = degree_name
                break

    return highest_degree or "unknown"


# EXAMPLE:
# Input: "B.E. Information Technology 2024"
# Output: "bachelors"
```

---

## 3.8 job_description_parser.py - Parse Job Requirements

**Purpose:** Extract job requirements from JD

**Extracts:**
- Job title
- Required skills
- Preferred skills
- Minimum experience
- Required education

**Code:**
```python
"""
Job Description Parser
Extracts requirements from job descriptions
"""

import re
from .text_normalizer import normalize_text
from .section_detector import detect_sections, get_section_text
from .skill_extractor import extract_skills
from .education_detector import DEGREE_LEVELS


def parse_job_description(jd_text: str) -> dict:
    """
    Parse job description and extract requirements

    Returns:
        {
            "job_title": "Full Stack Developer",
            "required_skills": ["python", "java", "react"],
            "preferred_skills": ["docker", "aws"],
            "minimum_experience": 2,
            "required_education": "bachelors"
        }
    """
    normalized = normalize_text(jd_text)
    sections = detect_sections(normalized)

    job_title = _extract_job_title(normalized, sections)
    skills_data = _extract_jd_skills(normalized, sections)
    min_experience = _extract_experience_requirement(normalized)
    required_education = _extract_education_requirement(normalized)

    return {
        "job_title": job_title,
        "required_skills": skills_data["required"],
        "preferred_skills": skills_data["preferred"],
        "minimum_experience": min_experience,
        "required_education": required_education
    }


def _extract_job_title(text: str, sections: dict) -> str:
    """Extract job title (usually in first lines)"""
    lines = text.split('\n')
    for line in lines[:5]:
        if any(word in line.lower() for word in ['position', 'role', 'engineer']):
            return line.strip()
    return "Unspecified Position"


def _extract_experience_requirement(text: str) -> int:
    """Extract minimum experience years"""
    patterns = [
        r'(\d+)\s*(?:years?|yrs?)\s*(?:of|experience)',
        r'(?:at\s+least|minimum)\s*(\d+)\s*(?:years?|yrs?)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return int(match.group(1))
    
    return 0


def _extract_education_requirement(text: str) -> str:
    """Extract required education"""
    for degree in DEGREE_LEVELS:
        if degree in text.lower():
            return degree
    return "bachelors"


def _extract_jd_skills(text: str, sections: dict) -> dict:
    """Extract required and preferred skills"""
    skills_section = get_section_text(sections, "skills")
    all_skills = extract_skills(skills_section)["skills_list"]
    
    # Simple split: first half required, second half preferred
    split_point = len(all_skills) // 2
    return {
        "required": all_skills[:split_point],
        "preferred": all_skills[split_point:]
    }
```

---

## 3.9 output_formatter.py - Format JSON Output

**Purpose:** Format extracted data for AI Scorer

**Code:**
```python
"""
Output Formatter
Formats extracted data into scoring-ready structure
"""


def format_resume_data(
    resume_id: str,
    filename: str,
    contact_info: dict,
    skills_data: dict,
    experience_years: int,
    education_level: str,
    job_requirements: dict
) -> dict:
    """
    Format extracted data
    """

    job_match = calculate_job_match(
        skills_data,
        experience_years,
        education_level,
        job_requirements
    )

    return {
        "resume_filename": filename,
        "contact_info": contact_info,
        "skills": skills_data["skills_list"],
        "experience_years": experience_years,
        "education_level": education_level,
        "job_match": job_match,
        "scoring_ready": True
    }


def calculate_job_match(
    skills_data: dict,
    experience_years: int,
    education_level: str,
    job_requirements: dict
) -> dict:
    """
    Calculate match percentage with job requirements

    Returns:
        {
            "matched_skills": ["python", "java"],
            "missing_skills": ["aws"],
            "match_percentage": 85.0,
            "meets_requirements": True
        }
    """
    candidate_skills = set([s.lower() for s in skills_data["skills_list"]])
    required_skills = set([s.lower() for s in job_requirements.get("required_skills", [])])

    matched = candidate_skills.intersection(required_skills)
    missing = required_skills - candidate_skills

    match_percentage = (len(matched) / len(required_skills) * 100) if required_skills else 100.0

    min_exp = job_requirements.get("minimum_experience", 0)
    experience_match = experience_years >= min_exp

    return {
        "matched_skills": list(matched),
        "missing_skills": list(missing),
        "match_percentage": round(match_percentage, 2),
        "experience_match": experience_match,
        "meets_requirements": experience_match and len(missing) == 0
    }
```

---

# 4. COMPLETE DATA FLOW

## Input → Processing → Output

```
INPUT:
├─ job_description.txt
│  "Senior Python Developer
│   5+ years with Django
│   Required: Python, Django, PostgreSQL"
│
└─ resume_1.txt
   "John Doe
    Email: john@example.com
    SKILLS: Python, Django, PostgreSQL, JavaScript
    EXPERIENCE: 4 years
    EDUCATION: B.Tech"

PROCESSING:

1. Normalize both texts (fix encoding, bullets)
2. Detect sections (Skills, Experience, Education)
3. Parse Job Description → job_requirements
4. For each resume:
   - Extract contact info
   - Extract skills
   - Extract experience
   - Extract education
   - Calculate match vs job_requirements
5. Format output JSON
6. Save to Nlp_Engine/output/REQ_xxx_nlp_output.json

OUTPUT JSON:
{
  "request_id": "REQ_20260217_103022",
  "job_requirements": {
    "job_title": "Senior Python Developer",
    "required_skills": ["python", "django", "postgresql"],
    "minimum_experience": 5
  },
  "resumes": {
    "resume_001": {
      "resume_filename": "john_resume.txt",
      "contact_info": {"email": "john@example.com", "phone": ""},
      "skills": ["python", "django", "postgresql", "javascript"],
      "experience_years": 4,
      "education_level": "bachelors",
      "job_match": {
        "matched_skills": ["python", "django", "postgresql"],
        "missing_skills": [],
        "match_percentage": 100.0,
        "experience_match": false,
        "meets_requirements": false
      },
      "scoring_ready": true
    }
  }
}
```

---

# 5. CONFIGURATION

**File:** `Nlp_Engine/config.py`

```python
# PATH CONFIGURATIONS
INPUT_FOLDER = ".../Resume_Parser/parsed_resumes"
JOB_DESCRIPTION_FILE = ".../Resume_Parser/Parsed_JD"
OUTPUT_FOLDER = ".../Nlp_Engine/output"

# SKILL EXTRACTION
MIN_CONFIDENCE = 0.75          # 75% confidence threshold
USE_SYNONYM_MATCHING = True
USE_FUZZY_MATCHING = True
FUZZY_THRESHOLD = 0.85

# JOB MATCHING
MINIMUM_MATCH_PERCENTAGE = 50  # 50% skills must match

# ERROR HANDLING
CONTINUE_ON_ERROR = True
ERROR_LOG_FILE = ".../Nlp_Engine/output/errors.log"
```

---

# 6. INTEGRATION WITH BACKEND

## How Backend Calls NLP Engine

```python
# Backend/app/services/pipeline_service.py

from Nlp_Engine.Nlp_service import process_resumes

# Create text files
resume_txt_path = "/tmp/resume_app123.txt"
jd_txt_path = "/tmp/job_xyz789.txt"

# Call NLP
nlp_response = process_resumes(jd_txt_path, [resume_txt_path])

# Response contains request_id and output_path
# Read the output file
with open(os.path.join(project_root, nlp_response["output_path"])) as f:
    nlp_data = json.load(f)

# Extract job requirements for AI Scorer
job_requirements = nlp_data.get("job_requirements", {})

# Pass to AI Scorer
from Ai_Scoring.Ai_Scoring.scorer import process_resume_batch
scored_results = process_resume_batch(output_file, job_requirements)
```

---

# 7. INPUT/OUTPUT EXAMPLES

## Example 1: Simple Resume

**Input Resume:**
```
MAHESH NIKAS
Email: mahesh@example.com | Phone: +91 9356736650

TECHNICAL SKILLS
Python, Java, Machine Learning, Django

EXPERIENCE
Software Intern - 2025
Data Analyst - 2024

EDUCATION
B.E. Information Technology
```

**NLP Output:**
```json
{
  "resume_filename": "mahesh_resume.txt",
  "contact_info": {
    "email": "mahesh@example.com",
    "phone": "+91 9356736650"
  },
  "skills": ["python", "java", "machine learning", "django"],
  "experience_years": 1,
  "education_level": "bachelors",
  "job_match": {
    "matched_skills": ["python"],
    "missing_skills": ["aws", "kubernetes"],
    "match_percentage": 25.0,
    "meets_requirements": false
  },
  "scoring_ready": true
}
```

---

# 8. HOW TO RUN

## Backend Integration (Main Way)

```bash
# From Backend folder
cd Backend

# Start Flask server
python run.py

# When candidate applies at /api/apply:
# ✅ Backend calls PipelineService
# ✅ PipelineService calls NLP Engine
# ✅ NLP Engine extracts data and saves JSON
# ✅ Backend reads JSON and calls AI Scorer
```

---

# 9. COMMON ISSUES & SOLUTIONS

| Issue | Cause | Solution |
|-------|-------|----------|
| "Skills not detected" | Poor text normalization | Check normalize_text() patterns |
| "Wrong section" | Pattern doesn't match | Add to SECTION_PATTERNS |
| "Experience wrong" | Multiple date formats | Update regex patterns |
| "Missing skills" | Not in database | Add to SKILL_DATABASE with synonyms |

---

# 10. INTERVIEW Q&A

## Q1: What does NLP Engine do?
**A:** Extracts structured data (skills, experience, education) from resumes and job descriptions, then calculates match percentages.

## Q2: Why three skill matching methods?
**A:** 
- Exact (Python) handles normal mentions
- Synonym (Py) handles abbreviations
- Fuzzy (Pytho) handles typos/misspellings

## Q3: How are resumes ranked in NLP?
**A:** NOT ranked in NLP! NLP only extracts data. AI Scorer ranks resumes by score.

## Q4: What if experience is "2021-2025"?
**A:** Calculates as 2025 - 2021 = 4 years.

## Q5: Why normalize text?
**A:** PDFs create encoding issues (â€") and bullets (•) that break parsing.

---

**THIS NLP ENGINE GUIDE IS READY FOR PRESENTATIONS!**

Use this to explain:
✅ Complete architecture
✅ File-by-file breakdown  
✅ Code with explanations
✅ Data flow with examples
✅ Integration with backend
✅ Common issues
✅ Interview Q&A

Good luck! 🚀
