# Resume Parser Package

Parse PDF resumes and job descriptions from either the existing Samples folder layout or the updated data folder layout.

---

## 📁 Supported Folder Structures

```
Project/
├── Samples/                      ← Existing layout
│   ├── Resumes/
│   └── Job_Descriptions/
│
├── data/                         ← Updated layout also supported
│   ├── resumes/
│   └── job_descriptions/
│
├── Resume_Parser/                 ← This package
│   ├── __init__.py
│   ├── resume_parser.py          # PDF parser
│   ├── text_cleaner.py           # Text cleaning
│   ├── batch_parser.py           # Batch processing
│   ├── parsed_resumes/           # Output (auto-created)
│   │   ├── resume1.txt
│   │   └── resume2.txt
│   └── Parsed_JD/                # Output (auto-created)
│       ├── jd1.txt
│       └── jd2.txt
│
└── Nlp_Engine/                    ← Next module
```

---

## 🚀 Usage

### Option 1: Parse Only

```python
from Resume_Parser import BatchParser

parser = BatchParser()

# Parse all resumes and JDs
result = parser.parse_all()

print(f"Parsed {result['resumes']['parsed']} resumes")
print(f"Parsed {result['jds']['parsed']} JDs")
```

### Option 2: Complete Pipeline

```bash
python run_complete_pipeline.py
```

This will:
1. Parse PDFs from `Samples/` folder
2. Extract data with NLP Engine
3. Output ready for AI Scoring

---

## 📦 Package Contents

| File | Purpose |
|------|---------|
| `resume_parser.py` | Core PDF parser |
| `text_cleaner.py` | Clean extracted text |
| `batch_parser.py` | Process multiple files |
| `__init__.py` | Package initialization |

---

## ⚙️ How It Works

1. **Reads PDFs** from `Samples/Resumes` + `Samples/Job_Descriptions` or `data/resumes` + `data/job_descriptions`
2. **Extracts text** using pdfplumber for text PDFs and tables
3. **Falls back to OCR** using PyMuPDF + OpenCV + Tesseract for scanned pages and embedded images
4. **Cleans text** (removes artifacts, normalizes)
5. **Saves as .txt** in `Resume_Parser/parsed_resumes/` and `Resume_Parser/Parsed_JD/`

---

## 🔧 Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create one of the supported input layouts:**
   ```bash
   mkdir -p Samples/Resumes
   mkdir -p Samples/Job_Descriptions
   ```

   Or:

   ```bash
   mkdir -p data/resumes
   mkdir -p data/job_descriptions
   ```

3. **Add PDF files:**
   - Put resume PDFs in `Samples/Resumes/` or `data/resumes/`
   - Put JD PDFs in `Samples/Job_Descriptions/` or `data/job_descriptions/`

4. **Run:**
   ```bash
   python run_complete_pipeline.py
   ```

---

## 📊 Output Format

**Parsed resume (text file):**
```
JOHN DOE
Email: john@example.com
Phone: 9876543210

TECHNICAL SKILLS
Python, Java, React, MySQL

EXPERIENCE
Software Developer - ABC Corp (2021-2024)
Developed web applications
```

**Parsed JD (text file):**
```
Job Title: Full Stack Developer

Required Skills:
Python, Java, React, MySQL, Spring Boot

Minimum Experience: 2 years
Education: Bachelor's degree
```

---

## ✅ Verification

Check parsed files:

```bash
# Check parsed resumes
ls Resume_Parser/parsed_resumes/

# Check parsed JDs
ls Resume_Parser/Parsed_JD/

# View a parsed file
cat Resume_Parser/parsed_resumes/resume1.txt
```

---

## 🔗 Integration

Parsed files are automatically used by NLP Engine:

```python
from Resume_Parser import BatchParser
from Nlp_Engine import process_resumes

# Step 1: Parse
parser = BatchParser()
parse_result = parser.parse_all()

# Step 2: Get paths
jd_path = f"{parse_result['jds']['output_folder']}/{parse_result['jds']['files'][0]}"
resume_paths = [
    f"{parse_result['resumes']['output_folder']}/{f}"
    for f in parse_result['resumes']['files']
]

# Step 3: NLP Extract
nlp_result = process_resumes(jd_path, resume_paths)
```

---

## 🐛 Troubleshooting

**Error: input folder not found**
```bash
# Create one supported layout
mkdir -p Samples/Resumes
mkdir -p Samples/Job_Descriptions
```

**Error: No PDF files found**
- Add PDF files to the detected input folders shown by `BatchParser`

**Error: OCR dependencies missing**
```bash
pip install -r requirements.txt
```

**Error: Tesseract not found**
- Install Tesseract OCR and ensure `tesseract.exe` is on PATH, or set `pytesseract.pytesseract.tesseract_cmd`

---

## 📝 Notes

- Only PDF files are supported currently
- Output text files are UTF-8 encoded
- Cleaned text removes artifacts and normalizes formatting
- Scanned PDFs no longer require Poppler because OCR uses PyMuPDF rendering
- Output folders are auto-created inside Resume_Parser package
