# 🔧 BACKEND संपूर्ण मार्गदर्शक | BACKEND COMPLETE GUIDE
## सर्व कोड कसा जोडला आहे आणि काय काम करतो | How All Code Connects & Works

**Date:** 17 फेब्रुवारी 2026 | February 17, 2026

---

# 📑 सामग्री | TABLE OF CONTENTS

1. [Backend म्हणजे काय? | What is Backend?](#1-backend-म्हणजे-काय--what-is-backend)
2. [फोल्डर स्ट्रक्चर | Folder Structure](#2-फोल्डर-स्ट्रक्चर--folder-structure)
3. [प्रत्येक फाईल काय करते? | What Does Each File Do?](#3-प्रत्येक-फाईल-काय-करते--what-does-each-file-do)
4. [कनेक्शन कसे काम करते? | How Connections Work?](#4-कनेक्शन-कसे-काम-करते--how-connections-work)
5. [संपूर्ण डेटा फ्लो | Complete Data Flow](#5-संपूर्ण-डेटा-फ्लो--complete-data-flow)
6. [कोड एक्सप्लेनेशन | Code Explanation](#6-कोड-एक्सप्लेनेशन--code-explanation)

---

# 1. BACKEND म्हणजे काय? | WHAT IS BACKEND?

## 🇮🇳 मराठी स्पष्टीकरण

**Backend म्हणजे काय?**
- जेव्हा तुम्ही वेबसाईटवर बटन दाबता (जसे "Apply" बटन), तेव्हा तुमचा डेटा कुठेतरी जाऊन प्रोसेस होतो.
- Backend हे "मागे काम करणारा भाग" आहे.
- Frontend (React) वापरकर्त्याला दिसतो, Backend मागे सगळं हँडल करतो.

**Backend काय काय करतो?**
1. **Resume आणि Job Description घेतो** (Frontend पासून)
2. **Database मध्ये माहिती सेव्ह करतो** (MongoDB)
3. **AI Modules ला बोलावतो** (Resume Parser, NLP Engine, AI Scorer)
4. **Email पाठवतो** (Selected candidates ला)
5. **Company login/registration हँडल करतो**

**उदाहरण:**
```
Student वेबसाइट वर जातो
    ↓
Job दिसतो आणि "Apply" वर क्लिक करतो
    ↓
Resume upload करतो
    ↓
Backend: Resume घेतो → AI ला दाखवतो → Score calculate करतो
    ↓
Database मध्ये सेव्ह करतो
    ↓
Email पाठवतो (Score चांगला असेल तर)
```

---

## 🇬🇧 English Explanation

**What is Backend?**
- When you click a button on a website (like "Apply"), your data goes somewhere to be processed.
- Backend is the "behind-the-scenes worker".
- Frontend (React) is what users see, Backend handles everything behind.

**What Does Backend Do?**
1. **Receives Resume & Job Description** (from Frontend)
2. **Saves Information in Database** (MongoDB)
3. **Calls AI Modules** (Resume Parser, NLP Engine, AI Scorer)
4. **Sends Emails** (to Selected candidates)
5. **Handles Company login/registration**

**Example:**
```
Student visits website
    ↓
Sees a job and clicks "Apply"
    ↓
Uploads resume
    ↓
Backend: Takes Resume → Sends to AI → Calculates Score
    ↓
Saves in Database
    ↓
Sends Email (if Score is good)
```

---

# 2. फोल्डर स्ट्रक्चर | FOLDER STRUCTURE

## 🇮🇳 मराठी स्पष्टीकरण

```
Backend/
│
├── run.py                  ← मुख्य फाईल! इथून सर्व सुरू होतं (Entry point)
│
├── requirements.txt        ← कोणती libraries लागतात (Flask, pymongo, etc.)
│
└── app/                    ← सगळा मुख्य कोड इथे
    │
    ├── __init__.py         ← App बनवतो (Flask app initialization)
    ├── config.py           ← सगळी Settings (Database, Email, Paths)
    ├── extensions.py       ← MongoDB connection
    │
    ├── routes/             ← API Endpoints (Frontend इथेच येतो!)
    │   ├── company_routes.py    ← Company login/registration
    │   ├── job_routes.py        ← Job post करणे, jobs list
    │   ├── application_routes.py ← Resume apply (सर्वात महत्त्वाचं!)
    │   └── health_routes.py     ← Check if server चालू आहे
    │
    ├── services/           ← मुख्य Business Logic (काम इथे होतं)
    │   ├── pipeline_service.py      ← मुख्यत्वे! AI modules ला orchestrate करतो
    │   ├── application_service.py   ← Application सेव्ह करतो database मध्ये
    │   ├── job_service.py           ← Jobs handle करतो
    │   ├── company_service.py       ← Company account handle करतो
    │   ├── storage_service.py       ← Files upload/save करतो
    │   ├── email_service.py         ← Email पाठवतो
    │   └── auth_service.py          ← Password encrypt करतो
    │
    └── utils/              ← Helper functions
        ├── logging.py      ← Errors log करतो
        └── validators.py   ← Check करतो data valid आहे का
```

---

## 🇬🇧 English Explanation

```
Backend/
│
├── run.py                  ← Main file! Everything starts here (Entry point)
│
├── requirements.txt        ← Which libraries are needed (Flask, pymongo, etc.)
│
└── app/                    ← All main code is here
    │
    ├── __init__.py         ← Creates the app (Flask app initialization)
    ├── config.py           ← All Settings (Database, Email, Paths)
    ├── extensions.py       ← MongoDB connection
    │
    ├── routes/             ← API Endpoints (Frontend comes here!)
    │   ├── company_routes.py    ← Company login/registration
    │   ├── job_routes.py        ← Post jobs, list jobs
    │   ├── application_routes.py ← Resume apply (Most important!)
    │   └── health_routes.py     ← Check if server is running
    │
    ├── services/           ← Main Business Logic (Work happens here)
    │   ├── pipeline_service.py      ← Main! Orchestrates AI modules
    │   ├── application_service.py   ← Saves application in database
    │   ├── job_service.py           ← Handles jobs
    │   ├── company_service.py       ← Handles company account
    │   ├── storage_service.py       ← Uploads/saves files
    │   ├── email_service.py         ← Sends email
    │   └── auth_service.py          ← Encrypts password
    │
    └── utils/              ← Helper functions
        ├── logging.py      ← Logs errors
        └── validators.py   ← Checks if data is valid
```

---

# 3. प्रत्येक फाईल काय करते? | WHAT DOES EACH FILE DO?

---

## 3.1 run.py - मुख्य प्रवेश बिंदू | Main Entry Point

### 🇮🇳 मराठी

**काय करतो?**
- Backend सर्वर सुरू करतो
- `python run.py` हा command रन केल्यावर हे चालू होतं

**कोड:**
```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
```

**Explanation:**
1. `create_app()` - Flask application तयार करतो
2. `port=5000` - Server 5000 port वर चालतो (म्हणजे `localhost:5000`)
3. `debug=True` - Development mode (errors दिसतात)

**Terminal मध्ये असे दिसेल:**
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

---

### 🇬🇧 English

**What does it do?**
- Starts the Backend server
- Runs when you execute `python run.py` command

**Code:**
```python
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
```

**Explanation:**
1. `create_app()` - Creates Flask application
2. `port=5000` - Server runs on port 5000 (meaning `localhost:5000`)
3. `debug=True` - Development mode (shows errors)

**Terminal will show:**
```
 * Running on http://0.0.0.0:5000
 * Debug mode: on
```

---

## 3.2 app/__init__.py - App Initialization

### 🇮🇳 मराठी

**काय करतो?**
- Flask app तयार करतो आणि सगळं setup करतो

**कोड:**
```python
def create_app():
    load_dotenv()                    # .env फाईल मधून settings वाचतो
    configure_logging()               # Errors log करण्यासाठी
    
    app = Flask(__name__)             # Flask app बनवलं
    app.config.from_object(Config)    # Settings घेतलं
    
    # CORS enable केलं (Frontend ला allow करतो)
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173"],  # React frontend
            "methods": ["GET", "POST", "PUT", "DELETE"]
        }
    })
    
    init_mongo(app)           # MongoDB connect केलं
    register_blueprints(app)  # सगळे routes जोडले
    
    return app
```

**हे इतकं महत्त्वाचं का?**
- CORS: Frontend (React पासून 5173 port वर) Backend (5000 port) ला बोलू शकतो
- MongoDB: Database connection तयार करतो
- Blueprints: सगळे API routes register करतो

---

### 🇬🇧 English

**What does it do?**
- Creates Flask app and sets up everything

**Code:**
```python
def create_app():
    load_dotenv()                    # Reads settings from .env file
    configure_logging()               # For logging errors
    
    app = Flask(__name__)             # Created Flask app
    app.config.from_object(Config)    # Got settings
    
    # Enabled CORS (allows Frontend)
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173"],  # React frontend
            "methods": ["GET", "POST", "PUT", "DELETE"]
        }
    })
    
    init_mongo(app)           # Connected MongoDB
    register_blueprints(app)  # Registered all routes
    
    return app
```

**Why is this important?**
- CORS: Frontend (React from port 5173) can talk to Backend (port 5000)
- MongoDB: Creates database connection
- Blueprints: Registers all API routes

---

## 3.3 app/config.py - सगळी Settings | All Settings

### 🇮🇳 मराठी

**काय करतो?**
- सर्व configuration settings ठेवतो

**कोड:**
```python
class Config:
    # Database Settings
    MONGO_URI = "mongodb://localhost:27017"
    MONGO_DB = "resume_filtering"
    
    # Email Settings (Selected candidates ला email पाठवण्यासाठी)
    SMTP_HOST = "smtp.gmail.com"
    SMTP_PORT = 587
    SMTP_USER = "your-email@gmail.com"
    SMTP_PASSWORD = "your-password"
    
    # Score Settings
    SCORE_THRESHOLD = 70  # 70+ score असेल तर "Selected"
    
    # File Upload
    MAX_CONTENT_LENGTH = 20971520  # Max 20MB files
    ALLOWED_RESUME_EXTENSIONS = {".pdf"}
```

**कुठून येतात values?**
- `.env` फाईल मधून वाचतो
- Environment variables वापरतो

**Example `.env` file:**
```
MONGO_URI=mongodb://localhost:27017
MONGO_DB=resume_filtering
SMTP_USER=myemail@gmail.com
SCORE_THRESHOLD=70
```

---

### 🇬🇧 English

**What does it do?**
- Stores all configuration settings

**Code:**
```python
class Config:
    # Database Settings
    MONGO_URI = "mongodb://localhost:27017"
    MONGO_DB = "resume_filtering"
    
    # Email Settings (for sending email to Selected candidates)
    SMTP_HOST = "smtp.gmail.com"
    SMTP_PORT = 587
    SMTP_USER = "your-email@gmail.com"
    SMTP_PASSWORD = "your-password"
    
    # Score Settings
    SCORE_THRESHOLD = 70  # If score is 70+, then "Selected"
    
    # File Upload
    MAX_CONTENT_LENGTH = 20971520  # Max 20MB files
    ALLOWED_RESUME_EXTENSIONS = {".pdf"}
```

**Where do values come from?**
- Reads from `.env` file
- Uses environment variables

**Example `.env` file:**
```
MONGO_URI=mongodb://localhost:27017
MONGO_DB=resume_filtering
SMTP_USER=myemail@gmail.com
SCORE_THRESHOLD=70
```

---

## 3.4 app/extensions.py - MongoDB Connection

### 🇮🇳 मराठी + 🇬🇧 English

```python
from pymongo import MongoClient

mongo_client = None

def init_mongo(app):
    """MongoDB connect करतो | Connects to MongoDB"""
    global mongo_client
    mongo_client = MongoClient(app.config["MONGO_URI"])
    app.mongo_db = mongo_client[app.config["MONGO_DB"]]
```

**काय होतं? | What happens?**
1. PyMongo वापरून MongoDB शी connect होतो
2. `resume_filtering` database वापरतो
3. सगळ्या services ला database मिळतो

---

# 4. कनेक्शन कसे काम करते? | HOW CONNECTIONS WORK?

## 🇮🇳 मराठी स्पष्टीकरण

### Layer 1: ROUTES (पातळ बाहेरचा थर)

**काय करतो?**
- Frontend चे requests घेतो
- Services ला call करतो
- Response परत पाठवतो

**Example:**
```python
# application_routes.py

@application_bp.route("/apply", methods=["POST"])
def apply_for_job():
    # Step 1: Data घेतो
    job_id = request.form.get("jobId")
    resume_file = request.files.get("resume")
    
    # Step 2: Service बोलावतो
    application = app_service.create_application(job, candidate, resume_file)
    
    # Step 3: Response परत करतो
    return jsonify({"success": True, "applicationId": application["applicationId"]})
```

**म्हणजे:**
- Routes म्हणजे "reception desk" (front desk वाली व्यक्ती)
- तो फक्त request घेतो आणि services ला सांगतो

---

### Layer 2: SERVICES (जाड आतला थर)

**काय करतो?**
- खरंच काम इथे होतं!
- Database operations
- AI modules call करणे
- Business logic

**Example:**
```python
# application_service.py

def create_application(self, job, candidate, resume_file):
    # Step 1: Pipeline run करतो (AI processing)
    pipeline_result = self.pipeline.run(job, candidate, resume_file)
    
    # Step 2: Database मध्ये save करतो
    application = {
        "applicationId": uuid.uuid4().hex,
        "score": pipeline_result["score"],
        "status": pipeline_result["status"]
    }
    self.collection.insert_one(application)
    
    return application
```

**म्हणजे:**
- Services म्हणजे "actual workers"
- सगळं काम हीच करतात

---

### Layer 3: DATABASE (Storage)

**काय करतो?**
- MongoDB मध्ये data save करतो
- 3 collections:
  1. **companies** - Company accounts
  2. **jobs** - Job postings
  3. **applications** - Resumes आणि scores

---

## 🇬🇧 English Explanation

### Layer 1: ROUTES (Thin Outer Layer)

**What does it do?**
- Receives requests from Frontend
- Calls Services
- Sends response back

**Example:**
```python
# application_routes.py

@application_bp.route("/apply", methods=["POST"])
def apply_for_job():
    # Step 1: Get data
    job_id = request.form.get("jobId")
    resume_file = request.files.get("resume")
    
    # Step 2: Call service
    application = app_service.create_application(job, candidate, resume_file)
    
    # Step 3: Return response
    return jsonify({"success": True, "applicationId": application["applicationId"]})
```

**Meaning:**
- Routes are like "reception desk" (front desk person)
- Only receives request and tells services

---

### Layer 2: SERVICES (Thick Inner Layer)

**What does it do?**
- Real work happens here!
- Database operations
- Calling AI modules
- Business logic

**Example:**
```python
# application_service.py

def create_application(self, job, candidate, resume_file):
    # Step 1: Run pipeline (AI processing)
    pipeline_result = self.pipeline.run(job, candidate, resume_file)
    
    # Step 2: Save in database
    application = {
        "applicationId": uuid.uuid4().hex,
        "score": pipeline_result["score"],
        "status": pipeline_result["status"]
    }
    self.collection.insert_one(application)
    
    return application
```

**Meaning:**
- Services are the "actual workers"
- They do all the work

---

### Layer 3: DATABASE (Storage)

**What does it do?**
- Saves data in MongoDB
- 3 collections:
  1. **companies** - Company accounts
  2. **jobs** - Job postings
  3. **applications** - Resumes and scores

---

# 5. संपूर्ण डेटा फ्लो | COMPLETE DATA FLOW

## 🇮🇳 मराठी - पूर्ण प्रवास

```
STEP 1: Student Apply करतो
════════════════════════════════
Frontend (React):
- Student form भरतो (name, email, resume upload)
- "Apply" button दाबतो
- POST request पाठवतो: /api/apply

↓↓↓

STEP 2: Backend Request घेतो
════════════════════════════════
application_routes.py (@application_bp.route("/apply")):
- Form data घेतो: jobId, fullName, email, resume file
- Validate करतो: resume PDF आहे का?
- Services बोलावतो

↓↓↓

STEP 3: Application Service
════════════════════════════════
application_service.py (create_application):
- UUID generate करतो (unique ID)
- Pipeline Service ला बोलावतो
- Result database मध्ये save करतो

↓↓↓

STEP 4: Pipeline Service (मुख्य!)
════════════════════════════════
pipeline_service.py (run):

4.1 Resume PDF सेव्ह करतो:
    - storage_service वापरतो
    - uploads/ folder मध्ये save करतो

4.2 Resume PDF → Text:
    - Resume Parser बोलावतो
    - PDF मधला text काढतो

4.3 Job Description घेतो:
    - Job database मधून fetch करतो
    - JD text file create करतो

4.4 NLP Engine बोलावतो:
    - process_resumes() function call करतो
    - Resume आणि JD text files पाठवतो
    - NLP extract करतो: skills, experience, education
    - Match percentage calculate करतो
    - Output: JSON file (Nlp_Engine/output/)

4.5 AI Scorer बोलावतो:
    - process_resume_batch() function call करतो
    - NLP output file पाठवतो
    - 4 scores calculate करतो:
      * Skill Match
      * Experience Match
      * Education Match
      * Preferred Skills
    - Total Score: 0-100

4.6 Status decide करतो:
    - Score >= 70 → "Selected"
    - Score < 70 → "Rejected"

4.7 Email पाठवतो (Selected असेल तर):
    - email_service.send_email() बोलावतो
    - Student ला congratulations email

↓↓↓

STEP 5: Database Storage
════════════════════════════════
application_service (परत):
- MongoDB मध्ये save करतो:
  {
    "applicationId": "abc123",
    "jobId": "job_xyz",
    "candidateName": "Mahesh Nikas",
    "email": "mahesh@example.com",
    "score": 85,
    "status": "Selected",
    "emailSent": true
  }

↓↓↓

STEP 6: Response Frontend ला
════════════════════════════════
application_routes (परत):
- JSON response create करतो:
  {
    "success": true,
    "message": "Application submitted successfully",
    "applicationId": "abc123",
    "score": 85,
    "status": "Selected"
  }

↓↓↓

STEP 7: Frontend Display
════════════════════════════════
React:
- Success message दाखवतो
- "Application submitted!" alert
- Score आणि status display
```

---

## 🇬🇧 English - Complete Journey

```
STEP 1: Student Applies
════════════════════════════════
Frontend (React):
- Student fills form (name, email, resume upload)
- Clicks "Apply" button
- Sends POST request: /api/apply

↓↓↓

STEP 2: Backend Receives Request
════════════════════════════════
application_routes.py (@application_bp.route("/apply")):
- Gets form data: jobId, fullName, email, resume file
- Validates: is resume a PDF?
- Calls services

↓↓↓

STEP 3: Application Service
════════════════════════════════
application_service.py (create_application):
- Generates UUID (unique ID)
- Calls Pipeline Service
- Saves result in database

↓↓↓

STEP 4: Pipeline Service (Main!)
════════════════════════════════
pipeline_service.py (run):

4.1 Saves Resume PDF:
    - Uses storage_service
    - Saves in uploads/ folder

4.2 Resume PDF → Text:
    - Calls Resume Parser
    - Extracts text from PDF

4.3 Gets Job Description:
    - Fetches from Job database
    - Creates JD text file

4.4 Calls NLP Engine:
    - Calls process_resumes() function
    - Sends Resume and JD text files
    - NLP extracts: skills, experience, education
    - Calculates match percentage
    - Output: JSON file (Nlp_Engine/output/)

4.5 Calls AI Scorer:
    - Calls process_resume_batch() function
    - Sends NLP output file
    - Calculates 4 scores:
      * Skill Match
      * Experience Match
      * Education Match
      * Preferred Skills
    - Total Score: 0-100

4.6 Decides Status:
    - Score >= 70 → "Selected"
    - Score < 70 → "Rejected"

4.7 Sends Email (if Selected):
    - Calls email_service.send_email()
    - Congratulations email to Student

↓↓↓

STEP 5: Database Storage
════════════════════════════════
application_service (back):
- Saves in MongoDB:
  {
    "applicationId": "abc123",
    "jobId": "job_xyz",
    "candidateName": "Mahesh Nikas",
    "email": "mahesh@example.com",
    "score": 85,
    "status": "Selected",
    "emailSent": true
  }

↓↓↓

STEP 6: Response to Frontend
════════════════════════════════
application_routes (back):
- Creates JSON response:
  {
    "success": true,
    "message": "Application submitted successfully",
    "applicationId": "abc123",
    "score": 85,
    "status": "Selected"
  }

↓↓↓

STEP 7: Frontend Display
════════════════════════════════
React:
- Shows success message
- "Application submitted!" alert
- Displays score and status
```

---

# 6. कोड एक्सप्लेनेशन | CODE EXPLANATION

## 6.1 PipelineService - मुख्य Orchestrator

### 🇮🇳 मराठी

**सर्वात महत्त्वाची Service!**

ही service 3 AI modules एकत्र करते:
1. Resume Parser
2. NLP Engine
3. AI Scorer

**पूर्ण कोड:**

```python
class PipelineService:
    def __init__(self, storage_service, email_service, project_root, score_threshold):
        """
        Initialize करतो
        - storage_service: Files save करण्यासाठी
        - email_service: Email पाठवण्यासाठी
        - project_root: Project चा root path
        - score_threshold: किती score वर selected (default: 70)
        """
        self.storage = storage_service
        self.email = email_service
        self.project_root = project_root
        self.score_threshold = score_threshold
        self.parser = ResumeParser()  # Resume Parser initialize
    
    def run(self, job, candidate, resume_file):
        """
        मुख्य function - संपूर्ण pipeline चालवतो
        
        Args:
            job: Job dictionary (jobId, title, description, etc.)
            candidate: Candidate info (name, email, phone, etc.)
            resume_file: Uploaded resume PDF file
        
        Returns:
            {
                "resumePdfPath": "path/to/pdf",
                "score": 85,
                "status": "Selected",
                "emailSent": true
            }
        """
        
        # ==== STEP 1: Resume PDF सेव्ह करतो ====
        resume_pdf_path = self.storage.save_upload(resume_file, "resumes")
        # Result: "uploads/resumes/abc123_resume.pdf"
        
        # ==== STEP 2: PDF मधून Text काढतो (Resume Parser) ====
        resume_text = self.parser.parse(resume_pdf_path)
        # Result: "MAHESH NIKAS\nEmail: mahesh@example.com\nSKILLS\nPython, Java..."
        
        # ==== STEP 3: Job Description Text घेतो ====
        jd_text = job.get("description", "")
        if not jd_text.strip():
            raise ValueError("Job description missing!")
        
        # ==== STEP 4: Text files create करतो ====
        resume_txt_path = self.storage.write_text(
            resume_text, 
            f"resume_{candidate['applicationId']}.txt"
        )
        jd_txt_path = self.storage.write_text(
            jd_text, 
            f"job_{job['jobId']}.txt"
        )
        # Results:
        # - "tmp/resume_abc123.txt"
        # - "tmp/job_xyz789.txt"
        
        # ==== STEP 5: NLP Engine बोलावतो ====
        nlp_response = process_resumes(jd_txt_path, [resume_txt_path])
        # process_resumes() function NLP Engine/Nlp_service.py मधून येतो
        
        if not nlp_response.get("success"):
            raise RuntimeError("NLP extraction failed!")
        
        # NLP output file path घेतो
        output_path = nlp_response.get("output_path")
        # Result: "Nlp_Engine/output/REQ_20260217_103022_nlp_output.json"
        
        # ==== STEP 6: NLP Output file वाचतो ====
        output_file = os.path.join(self.project_root, output_path)
        with open(output_file, "r", encoding="utf-8") as f:
            output_data = json.load(f)
        
        # output_data structure:
        # {
        #     "job_requirements": {...},
        #     "resumes": {
        #         "resume_001": {
        #             "skills": ["python", "java"],
        #             "experience_years": 2,
        #             "job_match": {"match_percentage": 75}
        #         }
        #     }
        # }
        
        # ==== STEP 7: Job Requirements extract करतो (AI Scorer साठी) ====
        job_requirements = output_data.get("job_requirements", {})
        scoring_metadata = {"job_requirements": job_requirements}
        
        # ==== STEP 8: AI Scorer बोलावतो ====
        scored_results = process_resume_batch(
            Path(output_file).name,  # Filename
            scoring_metadata         # Job requirements
        )
        # process_resume_batch() function Ai_Scoring/Ai_Scoring/scorer.py मधून येतो
        
        if scored_results and "error" in scored_results[0]:
            raise RuntimeError("AI Scoring failed!")
        
        # ==== STEP 9: Score घेतो आणि Status decide करतो ====
        result = scored_results[0] if scored_results else {}
        score = float(result.get("total_score", 0))
        
        if score >= self.score_threshold:
            status = "Selected"   # 70+ score
        else:
            status = "Rejected"   # <70 score
        
        # ==== STEP 10: Email पाठवतो (Selected असेल तर) ====
        email_sent = False
        if status == "Selected" and candidate.get("email"):
            subject = f"Shortlisted: {job.get('title')}"
            body = (
                f"Hello {candidate.get('fullName')},\n\n"
                f"Congratulations! You are shortlisted for {job.get('title')}.\n"
                f"Your score: {score}\n\n"
                "Best regards,\nHiring Team"
            )
            self.email.send_email(candidate["email"], subject, body)
            email_sent = True
        
        # ==== STEP 11: Final result return करतो ====
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

**महत्त्वाचे Points:**

1. **आधी NLP, मग AI Scorer**
   - NLP: Extract skills, experience (no scoring)
   - AI Scorer: Calculate total score (0-100)

2. **3 AI Modules integration:**
   ```python
   Resume Parser: PDF → Text
   NLP Engine: Text → Extracted Data (JSON)
   AI Scorer: JSON → Score (0-100)
   ```

3. **Text files का create करतो?**
   - AI modules ला text files लागतात
   - PDF directly process करू शकत नाहीत

4. **Email कधी पाठवतो?**
   - फक्त "Selected" candidates ला
   - Score >= 70 असेल तरच

---

### 🇬🇧 English

**Most Important Service!**

This service integrates 3 AI modules:
1. Resume Parser
2. NLP Engine
3. AI Scorer

**Complete Code:**

```python
class PipelineService:
    def __init__(self, storage_service, email_service, project_root, score_threshold):
        """
        Initializes
        - storage_service: For saving files
        - email_service: For sending emails
        - project_root: Project root path
        - score_threshold: Score for selection (default: 70)
        """
        self.storage = storage_service
        self.email = email_service
        self.project_root = project_root
        self.score_threshold = score_threshold
        self.parser = ResumeParser()  # Initialize Resume Parser
    
    def run(self, job, candidate, resume_file):
        """
        Main function - runs complete pipeline
        
        Args:
            job: Job dictionary (jobId, title, description, etc.)
            candidate: Candidate info (name, email, phone, etc.)
            resume_file: Uploaded resume PDF file
        
        Returns:
            {
                "resumePdfPath": "path/to/pdf",
                "score": 85,
                "status": "Selected",
                "emailSent": true
            }
        """
        
        # ==== STEP 1: Save Resume PDF ====
        resume_pdf_path = self.storage.save_upload(resume_file, "resumes")
        # Result: "uploads/resumes/abc123_resume.pdf"
        
        # ==== STEP 2: Extract Text from PDF (Resume Parser) ====
        resume_text = self.parser.parse(resume_pdf_path)
        # Result: "MAHESH NIKAS\nEmail: mahesh@example.com\nSKILLS\nPython, Java..."
        
        # ==== STEP 3: Get Job Description Text ====
        jd_text = job.get("description", "")
        if not jd_text.strip():
            raise ValueError("Job description missing!")
        
        # ==== STEP 4: Create Text files ====
        resume_txt_path = self.storage.write_text(
            resume_text, 
            f"resume_{candidate['applicationId']}.txt"
        )
        jd_txt_path = self.storage.write_text(
            jd_text, 
            f"job_{job['jobId']}.txt"
        )
        # Results:
        # - "tmp/resume_abc123.txt"
        # - "tmp/job_xyz789.txt"
        
        # ==== STEP 5: Call NLP Engine ====
        nlp_response = process_resumes(jd_txt_path, [resume_txt_path])
        # process_resumes() function from NLP Engine/Nlp_service.py
        
        if not nlp_response.get("success"):
            raise RuntimeError("NLP extraction failed!")
        
        # Get NLP output file path
        output_path = nlp_response.get("output_path")
        # Result: "Nlp_Engine/output/REQ_20260217_103022_nlp_output.json"
        
        # ==== STEP 6: Read NLP Output file ====
        output_file = os.path.join(self.project_root, output_path)
        with open(output_file, "r", encoding="utf-8") as f:
            output_data = json.load(f)
        
        # output_data structure:
        # {
        #     "job_requirements": {...},
        #     "resumes": {
        #         "resume_001": {
        #             "skills": ["python", "java"],
        #             "experience_years": 2,
        #             "job_match": {"match_percentage": 75}
        #         }
        #     }
        # }
        
        # ==== STEP 7: Extract Job Requirements (for AI Scorer) ====
        job_requirements = output_data.get("job_requirements", {})
        scoring_metadata = {"job_requirements": job_requirements}
        
        # ==== STEP 8: Call AI Scorer ====
        scored_results = process_resume_batch(
            Path(output_file).name,  # Filename
            scoring_metadata         # Job requirements
        )
        # process_resume_batch() function from Ai_Scoring/Ai_Scoring/scorer.py
        
        if scored_results and "error" in scored_results[0]:
            raise RuntimeError("AI Scoring failed!")
        
        # ==== STEP 9: Get Score and Decide Status ====
        result = scored_results[0] if scored_results else {}
        score = float(result.get("total_score", 0))
        
        if score >= self.score_threshold:
            status = "Selected"   # 70+ score
        else:
            status = "Rejected"   # <70 score
        
        # ==== STEP 10: Send Email (if Selected) ====
        email_sent = False
        if status == "Selected" and candidate.get("email"):
            subject = f"Shortlisted: {job.get('title')}"
            body = (
                f"Hello {candidate.get('fullName')},\n\n"
                f"Congratulations! You are shortlisted for {job.get('title')}.\n"
                f"Your score: {score}\n\n"
                "Best regards,\nHiring Team"
            )
            self.email.send_email(candidate["email"], subject, body)
            email_sent = True
        
        # ==== STEP 11: Return Final result ====
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

**Important Points:**

1. **NLP first, then AI Scorer**
   - NLP: Extract skills, experience (no scoring)
   - AI Scorer: Calculate total score (0-100)

2. **3 AI Modules integration:**
   ```python
   Resume Parser: PDF → Text
   NLP Engine: Text → Extracted Data (JSON)
   AI Scorer: JSON → Score (0-100)
   ```

3. **Why create text files?**
   - AI modules need text files
   - Cannot process PDF directly

4. **When is email sent?**
   - Only to "Selected" candidates
   - Only if Score >= 70

---

## 6.2 सगळे Routes | All Routes

### 🇮🇳 मराठी

**Backend मध्ये 4 Route Files आहेत:**

#### 1. company_routes.py - Company Account

```python
# Company नोंदणी (Registration)
POST /api/company/register
Body: {
  "companyName": "Tech Corp",
  "registrationNo": "REG12345",
  "email": "hr@techcorp.com",
  "password": "securepass"
}

# Company Login
POST /api/company/login
Body: {
  "email": "hr@techcorp.com",
  "password": "securepass"
}
```

#### 2. job_routes.py - Job Posting

```python
# सगळे jobs list
GET /api/jobs

# Company चे jobs
GET /api/company/{companyId}/jobs

# नवीन job post करा
POST /api/company/post-job
Body: {
  "companyId": "comp123",
  "title": "Python Developer",
  "descriptionPdf": <PDF file>
}

# Job delete करा
DELETE /api/company/delete-job
Body: {
  "jobId": "job_xyz"
}
```

#### 3. application_routes.py - Resume Apply (मुख्य!)

```python
# Apply for job
POST /api/apply
Form Data:
  - jobId: "job_xyz"
  - fullName: "Mahesh Nikas"
  - email: "mahesh@example.com"
  - phone: "9356736650"
  - degree: "B.E."
  - branch: "IT"
  - resume: <PDF file>

# Company चे applications
GET /api/company/{companyId}/resumes

# Single application
GET /api/resumes/{applicationId}
```

#### 4. health_routes.py - Server Status

```python
# Server चालू आहे का check करा
GET /api/health
Response: {"status": "ok", "message": "Backend is running"}
```

---

### 🇬🇧 English

**Backend has 4 Route Files:**

#### 1. company_routes.py - Company Account

```python
# Company Registration
POST /api/company/register
Body: {
  "companyName": "Tech Corp",
  "registrationNo": "REG12345",
  "email": "hr@techcorp.com",
  "password": "securepass"
}

# Company Login
POST /api/company/login
Body: {
  "email": "hr@techcorp.com",
  "password": "securepass"
}
```

#### 2. job_routes.py - Job Posting

```python
# List all jobs
GET /api/jobs

# Company's jobs
GET /api/company/{companyId}/jobs

# Post new job
POST /api/company/post-job
Body: {
  "companyId": "comp123",
  "title": "Python Developer",
  "descriptionPdf": <PDF file>
}

# Delete job
DELETE /api/company/delete-job
Body: {
  "jobId": "job_xyz"
}
```

#### 3. application_routes.py - Resume Apply (Main!)

```python
# Apply for job
POST /api/apply
Form Data:
  - jobId: "job_xyz"
  - fullName: "Mahesh Nikas"
  - email: "mahesh@example.com"
  - phone: "9356736650"
  - degree: "B.E."
  - branch: "IT"
  - resume: <PDF file>

# Company's applications
GET /api/company/{companyId}/resumes

# Single application
GET /api/resumes/{applicationId}
```

#### 4. health_routes.py - Server Status

```python
# Check if server is running
GET /api/health
Response: {"status": "ok", "message": "Backend is running"}
```

---

## 6.3 MongoDB Collections

### 🇮🇳 मराठी + 🇬🇧 English

**Database Name:** `resume_filtering`

#### Collection 1: companies

```javascript
{
  "companyId": "comp_abc123",           // Unique ID
  "companyName": "Tech Solutions Ltd",  // कंपनीचं नाव | Company name
  "registrationNo": "REG12345",         // नोंदणी क्रमांक | Registration number
  "email": "hr@techsol.com",            // Email
  "passwordHash": "$2b$10$...",         // Encrypted password
  "createdAt": "2026-02-17T10:30:22"    // तारीख | Date
}
```

#### Collection 2: jobs

```javascript
{
  "jobId": "job_xyz789",                     // Unique ID
  "title": "Senior Python Developer",       // Job title
  "description": "We need Python dev...",   // पूर्ण JD text | Full JD text
  "descriptionPdfPath": "uploads/jd_xyz.pdf",// PDF path
  "companyId": "comp_abc123",                // कोणत्या कंपनीची | Which company
  "companyName": "Tech Solutions Ltd",
  "companyRegNo": "REG12345",
  "postDate": "2026-02-17T10:30:22"
}
```

#### Collection 3: applications

```javascript
{
  "applicationId": "app_def456",             // Unique ID
  "jobId": "job_xyz789",                     // कोणत्या job साठी | For which job
  "jobTitle": "Senior Python Developer",
  "companyId": "comp_abc123",
  "candidateName": "Mahesh Nikas",           // Student चं नाव | Student name
  "email": "mahesh@example.com",
  "phone": "9356736650",
  "degree": "B.E.",
  "branch": "Information Technology",
  "resumeName": "mahesh_resume.pdf",
  "resumePdfPath": "uploads/resumes/abc_mahesh_resume.pdf",
  "resumeTextPath": "tmp/resume_app_def456.txt",
  "nlpOutputPath": "Nlp_Engine/output/REQ_20260217_103022_nlp_output.json",
  "score": 85.5,                             // AI Score (0-100)
  "rank": 2,                                 // Position (1st, 2nd, 3rd...)
  "status": "Selected",                      // "Selected" किंवा "Rejected"
  "emailSent": true,                         // Email गेला का? | Email sent?
  "createdAt": "2026-02-17T10:35:45"
}
```

---

# 7. समारोप | CONCLUSION

## 🇮🇳 मराठी

**Backend चे मुख्य Parts:**

1. **run.py** - सर्वर सुरू करतो (Entry point)
2. **app/__init__.py** - Flask app बनवतो, CORS enable करतो
3. **config.py** - सगळी settings (Database, Email, Score threshold)
4. **extensions.py** - MongoDB connection
5. **Routes** - Frontend चे requests घेतो (4 files)
6. **Services** - खरं काम करतो (7 files)
7. **PipelineService** - 3 AI modules orchestrate करतो

**Data Flow:**
```
Frontend → Routes → Services → AI Modules → Database → Response
```

**महत्त्वाचे:**
- Routes = पातळ (फक्त requests handle करतो)
- Services = जाड (सगळं business logic)
- PipelineService = मुख्य (AI integration)

---

## 🇬🇧 English

**Backend Main Parts:**

1. **run.py** - Starts server (Entry point)
2. **app/__init__.py** - Creates Flask app, enables CORS
3. **config.py** - All settings (Database, Email, Score threshold)
4. **extensions.py** - MongoDB connection
5. **Routes** - Receives Frontend requests (4 files)
6. **Services** - Does real work (7 files)
7. **PipelineService** - Orchestrates 3 AI modules

**Data Flow:**
```
Frontend → Routes → Services → AI Modules → Database → Response
```

**Important:**
- Routes = Thin (only handles requests)
- Services = Thick (all business logic)
- PipelineService = Main (AI integration)

---

**🎉 आता तुम्हाला Backend चा संपूर्ण architecture समजला! | Now you understand complete Backend architecture!**

**📚 Presentation साठी या guide मध्ये सर्व काही आहे! | This guide has everything for presentation!**

**Good luck! शुभेच्छा! 🚀**
