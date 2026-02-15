# Resume Parser Package

Parse PDF resumes and job descriptions from Samples folder.

---

## 📁 Required Folder Structure

```
Project/
├── Samples/                       ← Create this folder
│   ├── Resumes/                  ← Put resume PDFs here
│   │   ├── resume1.pdf
│   │   ├── resume2.pdf
│   │   └── resume3.pdf
│   └── Job_Descriptions/         ← Put JD PDFs here
│       ├── jd1.pdf
│       └── jd2.pdf
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

1. **Reads PDFs** from `Samples/Resumes` and `Samples/Job_Descriptions`
2. **Extracts text** using pdfplumber
3. **Cleans text** (removes artifacts, normalizes)
4. **Saves as .txt** in `Resume_Parser/parsed_resumes/` and `Resume_Parser/Parsed_JD/`

---

## 🔧 Setup

1. **Install dependencies:**
   ```bash
   pip install pdfplumber
   ```

2. **Create Samples folder:**
   ```bash
   mkdir -p Samples/Resumes
   mkdir -p Samples/Job_Descriptions
   ```

3. **Add PDF files:**
   - Put resume PDFs in `Samples/Resumes/`
   - Put JD PDFs in `Samples/Job_Descriptions/`

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

**Error: Samples folder not found**
```bash
# Create it
mkdir -p Samples/Resumes
mkdir -p Samples/Job_Descriptions
```

**Error: No PDF files found**
- Add PDF files to `Samples/Resumes/` and `Samples/Job_Descriptions/`

**Error: pdfplumber not installed**
```bash
pip install pdfplumber
```

---

## 📝 Notes

- Only PDF files are supported currently
- Output text files are UTF-8 encoded
- Cleaned text removes artifacts and normalizes formatting
- Output folders are auto-created inside Resume_Parser package
