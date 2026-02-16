# NLP Engine - Backend Developer Guide

## 🎯 What This Module Does

**Input:** Job Description (text) + Resumes (text files)  
**Output:** Extracted data (skills, experience, education, job match %)  
**Does NOT:** Ranking (your AI module does that)

---

## 📦 Installation

```bash
pip install tqdm
```

---

## 💻 Basic Usage

```python
from Nlp_Engine import process_resumes

# Call with paths
result = process_resumes(
    jd_path="/path/to/job_description.txt",
    resume_paths=["/path/resume1.txt", "/path/resume2.txt"]
)

# Check result
if result["success"]:
    output_file = result["output_path"]  # Pass this to AI Scoring
    print(f"Processed {result['successfully_parsed']} resumes")
else:
    print(f"Error: {result['error']}")
```

**That's it!**

---

## 📤 What You Get Back

```python
{
    "success": True,
    "request_id": "REQ_20260214_143022",
    "total_resumes": 5,
    "successfully_parsed": 5,
    "failed": 0,
    "output_path": "Nlp_Engine/output/REQ_xxx.json",
    "message": "NLP extraction complete."
}
```

**Important:** Use `output_path` for next module (AI Scoring)

---

## 📄 Output File Structure

File location: `Nlp_Engine/output/REQ_xxx.json`

```json
{
  "metadata": {
    "total_resumes": 3,
    "successfully_parsed": 3
  },
  "job_requirements": {
    "job_title": "Full Stack Developer",
    "required_skills": ["python", "java", "react"],
    "minimum_experience": 2
  },
  "resumes": {
    "resume_001": {
      "resume_filename": "john_doe.txt",
      "contact_info": {
        "email": "john@email.com",
        "phone": "+91 9876543210"
      },
      "skills": ["python", "java", "react", "mysql"],
      "experience_years": 3,
      "education_level": "bachelors",
      "job_match": {
        "match_percentage": 100.0,
        "meets_requirements": true
      },
      "scoring_ready": true
    }
  }
}
```

---

## 🗄️ Storage Options

### Option 1: Local Files (Simplest)

**Your setup:**
```
data/
├── jobs/
│   └── jd_123.txt
└── resumes/
    ├── resume1.txt
    └── resume2.txt
```

**Backend code:**
```python
from Nlp_Engine import process_resumes

jd_path = "data/jobs/jd_123.txt"
resume_paths = ["data/resumes/resume1.txt", "data/resumes/resume2.txt"]

result = process_resumes(jd_path, resume_paths)
```

---

### Option 2: Database Storage

**Flow:** DB → Temp Files → NLP → DB

**Backend code:**
```python
import tempfile
import os
from Nlp_Engine import process_resumes

def process_from_database(job_id):
    # 1. Fetch from database
    jd_text = db.query("SELECT description FROM jobs WHERE id=?", job_id)
    resumes = db.query("SELECT id, text FROM resumes WHERE job_id=?", job_id)
    
    # 2. Save to temp files
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save JD
        jd_path = os.path.join(tmpdir, "jd.txt")
        with open(jd_path, 'w', encoding='utf-8') as f:
            f.write(jd_text)
        
        # Save resumes
        resume_paths = []
        for resume in resumes:
            resume_path = os.path.join(tmpdir, f"resume_{resume['id']}.txt")
            with open(resume_path, 'w', encoding='utf-8') as f:
                f.write(resume['text'])
            resume_paths.append(resume_path)
        
        # 3. Process with NLP
        result = process_resumes(jd_path, resume_paths)
        
        # 4. Save to database
        if result["success"]:
            import json
            with open(result["output_path"], 'r') as f:
                nlp_data = json.load(f)
            
            # Store in DB
            for resume_id, data in nlp_data['resumes'].items():
                db.execute("""
                    INSERT INTO nlp_results (job_id, resume_id, skills, match_percentage)
                    VALUES (?, ?, ?, ?)
                """, job_id, resume_id, json.dumps(data['skills']), data['job_match']['match_percentage'])
        
        return result
    # Temp files deleted automatically
```

**Database schema:**
```sql
CREATE TABLE nlp_results (
    id INT PRIMARY KEY AUTO_INCREMENT,
    job_id INT,
    resume_id VARCHAR(50),
    skills JSON,
    experience_years INT,
    education_level VARCHAR(50),
    match_percentage DECIMAL(5,2),
    processed_at TIMESTAMP
);
```

---

### Option 3: Cloud Storage (AWS S3)

**Flow:** S3 → Temp Files → NLP → S3

**Backend code:**
```python
import boto3
import tempfile
import os
from Nlp_Engine import process_resumes

def process_from_s3(bucket, jd_key, resume_keys):
    s3 = boto3.client('s3')
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Download JD from S3
        jd_path = os.path.join(tmpdir, "jd.txt")
        s3.download_file(bucket, jd_key, jd_path)
        
        # 2. Download resumes from S3
        resume_paths = []
        for i, key in enumerate(resume_keys):
            resume_path = os.path.join(tmpdir, f"resume_{i}.txt")
            s3.download_file(bucket, key, resume_path)
            resume_paths.append(resume_path)
        
        # 3. Process
        result = process_resumes(jd_path, resume_paths)
        
        # 4. Upload result to S3
        if result["success"]:
            s3.upload_file(
                result["output_path"],
                bucket,
                f"nlp_results/{result['request_id']}.json"
            )
        
        return result
```

---

## 🌐 REST API Integration

### FastAPI Example

```python
from fastapi import FastAPI, UploadFile, File
from typing import List
import tempfile
import os
from Nlp_Engine import process_resumes

app = FastAPI()

@app.post("/api/nlp/extract")
async def extract_data(
    jd_file: UploadFile = File(...),
    resume_files: List[UploadFile] = File(...)
):
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save JD
        jd_path = os.path.join(tmpdir, jd_file.filename)
        with open(jd_path, 'wb') as f:
            f.write(await jd_file.read())
        
        # Save resumes
        resume_paths = []
        for resume in resume_files:
            resume_path = os.path.join(tmpdir, resume.filename)
            with open(resume_path, 'wb') as f:
                f.write(await resume.read())
            resume_paths.append(resume_path)
        
        # Process
        result = process_resumes(jd_path, resume_paths)
        return result

# Run: uvicorn main:app --reload
```

**API Call:**
```bash
curl -X POST "http://localhost:8000/api/nlp/extract" \
  -F "jd_file=@job_description.txt" \
  -F "resume_files=@resume1.txt" \
  -F "resume_files=@resume2.txt"
```

---

## 🔗 Connect to AI Scoring Module

```python
from Nlp_Engine import process_resumes
from AI_Scoring import score_and_rank  # Your AI module

# Step 1: NLP Extract
nlp_result = process_resumes(jd_path, resume_paths)

# Step 2: AI Score (your module reads the JSON file)
if nlp_result["success"]:
    rankings = score_and_rank(nlp_result["output_path"])
    
    print(f"Top candidate: {rankings[0]}")
```

**Your AI module receives:**
- Path to JSON file with all extracted data
- Reads file, applies AI scoring, returns rankings

---

## 🔄 Complete Pipeline Example

```python
from Nlp_Engine import process_resumes
import database as db

def complete_pipeline(job_id):
    # 1. Get data from database
    jd_text = db.get_job_description(job_id)
    resumes = db.get_resumes_for_job(job_id)
    
    # 2. Save to temp files
    import tempfile, os
    with tempfile.TemporaryDirectory() as tmpdir:
        jd_path = f"{tmpdir}/jd.txt"
        with open(jd_path, 'w') as f: f.write(jd_text)
        
        resume_paths = []
        for r in resumes:
            path = f"{tmpdir}/resume_{r['id']}.txt"
            with open(path, 'w') as f: f.write(r['text'])
            resume_paths.append(path)
        
        # 3. NLP Extract
        nlp_result = process_resumes(jd_path, resume_paths)
        
        if nlp_result["success"]:
            # 4. Store in database
            db.save_nlp_result(job_id, nlp_result)
            
            # 5. Trigger AI Scoring
            from AI_Scoring import score_and_rank
            rankings = score_and_rank(nlp_result["output_path"])
            
            # 6. Save rankings
            db.save_rankings(job_id, rankings)
            
            return rankings
```

---

## ⚠️ Error Handling

```python
result = process_resumes(jd_path, resume_paths)

if result["success"]:
    # Success
    output_file = result["output_path"]
    parsed_count = result["successfully_parsed"]
    
    # Check for partial failures
    if result["failed"] > 0:
        logger.warning(f"{result['failed']} resumes failed")
    
else:
    # Failed
    error = result["error"]
    logger.error(f"NLP extraction failed: {error}")
```

---

## 📊 Quick Reference

| What | How |
|------|-----|
| **Import** | `from Nlp_Engine import process_resumes` |
| **Call** | `result = process_resumes(jd_path, resume_paths)` |
| **Check** | `if result["success"]:` |
| **Get output** | `output_file = result["output_path"]` |
| **Pass to AI** | `ai_module.score(output_file)` |

---

## 🎯 Key Points

1. **Module needs TEXT files** - if you have PDFs, parse them first (use Resume Parser)
2. **Returns file path** - not the data itself
3. **Output inside package** - `Nlp_Engine/output/`
4. **No ranking** - just extraction
5. **Works with any storage** - just convert to temp files first

---

## 💡 Tips

- Use temp files for database/cloud storage
- Always check `result["success"]`
- Pass `output_path` to next module
- Module manages its own output folder
- No need to configure paths (handled internally)

---

## 📞 Common Questions

**Q: Where is output saved?**  
A: `Nlp_Engine/output/REQ_xxx.json`

**Q: Can I change output location?**  
A: Yes, edit `Nlp_Engine/config.py` → `OUTPUT_FOLDER`

**Q: Does it rank candidates?**  
A: No, only extracts data. Your AI module ranks.

**Q: Works with database?**  
A: Yes, fetch data → save to temp files → process → store results

**Q: What if resume parsing fails?**  
A: Module continues, marks resume as failed, processes others

---

**That's everything you need!** 🚀