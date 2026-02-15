# Resume Parser - Backend Developer Guide

## 🎯 What This Module Does

**Input:** PDF files (resumes + job descriptions)  
**Output:** Text files (cleaned and formatted)  
**Next:** Text files go to NLP Engine

---

## 📦 Installation

```bash
pip install pdfplumber
```

---

## 💻 Basic Usage

```python
from Resume_Parser import BatchParser

# Initialize
parser = BatchParser()

# Parse all PDFs from Samples folder
result = parser.parse_all()

# Check result
if result["success"]:
    print(f"Resumes: {result['resumes']['parsed']}")
    print(f"JDs: {result['jds']['parsed']}")
    
    # Get output folders
    resume_folder = result['resumes']['output_folder']
    jd_folder = result['jds']['output_folder']
```

**That's it!**

---

## 📤 What You Get Back

```python
{
    "success": True,
    "resumes": {
        "total": 5,
        "parsed": 5,
        "failed": 0,
        "output_folder": "Resume_Parser/parsed_resumes",
        "files": ["resume1.txt", "resume2.txt", "resume3.txt"]
    },
    "jds": {
        "total": 2,
        "parsed": 2,
        "output_folder": "Resume_Parser/Parsed_JD",
        "files": ["jd1.txt", "jd2.txt"]
    }
}
```

---

## 📁 Default Setup (Local Files)

**Folder structure:**
```
Samples/                        ← Put your PDFs here
├── Resumes/
│   ├── resume1.pdf
│   ├── resume2.pdf
│   └── resume3.pdf
└── Job_Descriptions/
    ├── jd1.pdf
    └── jd2.pdf

Resume_Parser/                  ← Output goes here (auto-created)
├── parsed_resumes/
│   ├── resume1.txt
│   ├── resume2.txt
│   └── resume3.txt
└── Parsed_JD/
    ├── jd1.txt
    └── jd2.txt
```

**Code:**
```python
from Resume_Parser import BatchParser

parser = BatchParser()
result = parser.parse_all()
```

---

## 🗄️ Storage Options

### Option 1: Custom Local Folder

**Your folder structure:**
```
data/
├── uploaded_resumes/
│   └── resume1.pdf
└── job_postings/
    └── jd1.pdf
```

**Backend code:**
```python
from Resume_Parser import BatchParser

# Initialize with custom folder
parser = BatchParser(samples_folder="data")

# Set custom input folders
parser.resumes_folder = "data/uploaded_resumes"
parser.jd_folder = "data/job_postings"

# Parse
result = parser.parse_all()
```

---

### Option 2: Database Storage

**Flow:** DB → Temp PDFs → Parser → Text → DB

**Backend code:**
```python
import tempfile
import os
from Resume_Parser import ResumeParser

def parse_from_database(resume_id):
    parser = ResumeParser()
    
    # 1. Fetch PDF from database
    pdf_data = db.query("SELECT pdf_content FROM resumes WHERE id=?", resume_id)
    
    # 2. Save to temp file
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        tmp.write(pdf_data)
        tmp_path = tmp.name
    
    try:
        # 3. Parse PDF
        text = parser.parse(tmp_path)
        
        # 4. Store text in database
        db.execute("""
            UPDATE resumes 
            SET parsed_text = ?, parsed_at = NOW() 
            WHERE id = ?
        """, text, resume_id)
        
        return text
        
    finally:
        # 5. Cleanup temp file
        os.unlink(tmp_path)
```

**Database schema:**
```sql
CREATE TABLE resumes (
    id INT PRIMARY KEY AUTO_INCREMENT,
    filename VARCHAR(255),
    pdf_content LONGBLOB,      -- Original PDF
    parsed_text LONGTEXT,       -- Parsed text
    uploaded_at TIMESTAMP,
    parsed_at TIMESTAMP
);
```

---

### Option 3: Cloud Storage (AWS S3)

**Flow:** S3 → Temp PDF → Parser → Text → S3

**Backend code:**
```python
import boto3
import tempfile
import os
from Resume_Parser import ResumeParser

def parse_from_s3(bucket, pdf_key):
    s3 = boto3.client('s3')
    parser = ResumeParser()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # 1. Download PDF from S3
        pdf_path = os.path.join(tmpdir, "resume.pdf")
        s3.download_file(bucket, pdf_key, pdf_path)
        
        # 2. Parse
        text = parser.parse(pdf_path)
        
        # 3. Save text to S3
        text_path = os.path.join(tmpdir, "resume.txt")
        with open(text_path, 'w', encoding='utf-8') as f:
            f.write(text)
        
        text_key = pdf_key.replace('.pdf', '.txt')
        s3.upload_file(text_path, bucket, text_key)
        
        return text
```

---

### Option 4: File Upload API

**Flow:** Upload → Temp File → Parser → Text

**Backend code (FastAPI):**
```python
from fastapi import FastAPI, UploadFile, File
import tempfile
import os
from Resume_Parser import ResumeParser

app = FastAPI()

@app.post("/api/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    parser = ResumeParser()
    
    # Save uploaded file to temp
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    
    try:
        # Parse
        text = parser.parse(tmp_path)
        
        return {
            "success": True,
            "filename": file.filename,
            "text": text
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
        
    finally:
        os.unlink(tmp_path)

# Run: uvicorn main:app --reload
```

**Frontend upload:**
```javascript
const formData = new FormData();
formData.append('file', pdfFile);

const response = await fetch('/api/parse-resume', {
    method: 'POST',
    body: formData
});

const result = await response.json();
console.log(result.text);
```

---

## 🔗 Connect to NLP Engine

**After parsing, pass to NLP Engine:**

```python
from Resume_Parser import BatchParser
from Nlp_Engine import process_resumes

# Step 1: Parse PDFs
parser = BatchParser()
parse_result = parser.parse_all()

if parse_result["success"]:
    # Step 2: Get paths
    jd_path = os.path.join(
        parse_result['jds']['output_folder'],
        parse_result['jds']['files'][0]  # First JD
    )
    
    resume_paths = [
        os.path.join(parse_result['resumes']['output_folder'], f)
        for f in parse_result['resumes']['files']
    ]
    
    # Step 3: NLP Extract
    nlp_result = process_resumes(jd_path, resume_paths)
    
    print(f"NLP output: {nlp_result['output_path']}")
```

---

## 🔄 Complete Pipeline

```python
from Resume_Parser import BatchParser
from Nlp_Engine import process_resumes
import database as db

def complete_pipeline(job_id, uploaded_files):
    # 1. Save uploaded PDFs
    import tempfile, os
    with tempfile.TemporaryDirectory() as tmpdir:
        # Save PDFs
        for file in uploaded_files:
            file_path = os.path.join(tmpdir, file.filename)
            with open(file_path, 'wb') as f:
                f.write(file.read())
        
        # 2. Parse PDFs
        parser = BatchParser(samples_folder=tmpdir)
        parse_result = parser.parse_all()
        
        if not parse_result["success"]:
            return {"error": "Parsing failed"}
        
        # 3. NLP Extract
        jd_path = os.path.join(
            parse_result['jds']['output_folder'],
            parse_result['jds']['files'][0]
        )
        
        resume_paths = [
            os.path.join(parse_result['resumes']['output_folder'], f)
            for f in parse_result['resumes']['files']
        ]
        
        nlp_result = process_resumes(jd_path, resume_paths)
        
        # 4. Save to database
        db.save_parsed_data(job_id, parse_result)
        db.save_nlp_data(job_id, nlp_result)
        
        return nlp_result
```

---

## 📊 Parse Single File

```python
from Resume_Parser import ResumeParser

parser = ResumeParser()

# Parse single PDF
text = parser.parse("path/to/resume.pdf")

# Save to file
with open("output.txt", "w", encoding="utf-8") as f:
    f.write(text)
```

---

## ⚠️ Error Handling

```python
from Resume_Parser import BatchParser

parser = BatchParser()
result = parser.parse_all()

if result["success"]:
    # Success
    parsed_count = result['resumes']['parsed']
    failed_count = result['resumes']['failed']
    
    if failed_count > 0:
        logger.warning(f"{failed_count} resumes failed to parse")
    
else:
    # Failed
    error = result.get('error', 'Unknown error')
    logger.error(f"Parsing failed: {error}")
```

---

## 🎨 Customize Output Location

```python
from Resume_Parser import BatchParser

parser = BatchParser()

# Change output folders
parser.output_resumes = "/custom/path/resumes"
parser.output_jd = "/custom/path/jds"

result = parser.parse_all()
```

---

## 📊 Quick Reference

| What | How |
|------|-----|
| **Import** | `from Resume_Parser import BatchParser` |
| **Initialize** | `parser = BatchParser()` |
| **Parse all** | `result = parser.parse_all()` |
| **Parse resumes only** | `result = parser.parse_all_resumes()` |
| **Parse JDs only** | `result = parser.parse_all_jds()` |
| **Single file** | `text = ResumeParser().parse("file.pdf")` |

---

## 🎯 Key Points

1. **Only parses PDFs** - converts to clean text
2. **Auto-creates output folders** - inside Resume_Parser package
3. **Cleans text** - removes PDF artifacts
4. **Works with any storage** - just provide PDF paths
5. **Output ready for NLP** - text files go directly to NLP Engine

---

## 💡 Tips

- Put PDFs in `Samples/` folder for quick testing
- For production, use database/cloud with temp files
- Always check `result["success"]`
- Parsed text is UTF-8 encoded
- Output folders created automatically

---

## 📞 Common Questions

**Q: Where is output saved?**  
A: `Resume_Parser/parsed_resumes/` and `Resume_Parser/Parsed_JD/`

**Q: Can I parse DOCX files?**  
A: Currently only PDF. Can be extended.

**Q: What if PDF is scanned image?**  
A: Won't work without OCR. Need readable PDFs.

**Q: Can I change output location?**  
A: Yes, set `parser.output_resumes` and `parser.output_jd`

**Q: Works with database?**  
A: Yes, fetch PDF → save temp → parse → store text

---

## 🔗 Integration Summary

```
1. Upload PDF
   ↓
2. Resume Parser → Text
   ↓
3. NLP Engine → Extract data
   ↓
4. AI Scoring → Rankings
   ↓
5. Display to user
```

**That's everything!** 🚀