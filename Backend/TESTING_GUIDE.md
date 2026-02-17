# Quick Start & Testing Guide

## System Status

✅ **Backend Running:** `http://localhost:5000`  
✅ **API Base:** `http://localhost:5000/api`  
✅ **Database:** MongoDB (configure in `.env`)  
✅ **Frontend:** React on port 3000 (if running)

---

## Testing the Pipeline (Step-by-Step)

### Step 1: Health Check

```powershell
$ProgressPreference = 'SilentlyContinue'
Invoke-WebRequest -Uri "http://localhost:5000/api/health" -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Expected:** `{"status": "ok"}`

---

### Step 2: Register Company

```powershell
$body = @{
    companyName = "TechCorp"
    registrationNo = "COM123"
    email = "techcorp@example.com"
    password = "SecurePass123!"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/api/company/register" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body `
    -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Response:**
```json
{
  "success": true,
  "company": {
    "companyId": "abc123...",
    "name": "TechCorp",
    "registrationNo": "COM123",
    "email": "techcorp@example.com"
  }
}
```

**Save `companyId` for next steps!**

---

### Step 3: Create Job with JD (PDF)

**Prepare:**
1. Place a PDF file at: `Samples/Job_Descriptions/test_jd.pdf`
2. The PDF should contain job description text (skills, experience, education)

```powershell
$companyId = "YOUR_COMPANY_ID_FROM_STEP_2"
$jdPdfPath = "Samples/Job_Descriptions/test_jd.pdf"

$form = @{
    companyId = $companyId
    jobTitle = "Senior Software Engineer"
    descriptionPdf = Get-Item $jdPdfPath
}

$response = Invoke-RestMethod `
    -Uri "http://localhost:5000/api/company/post-job" `
    -Method POST `
    -Form $form `
    -UseBasicParsing

$response | ConvertTo-Json
```

**Response:**
```json
{
  "success": true,
  "jobId": "job123..."
}
```

**Save `jobId` for next steps!**

---

### Step 4: Apply for Job (Triggers Full Pipeline)

**Prepare:**
1. Place a resume PDF at: `Samples/Resumes/test_candidate.pdf`
2. The resume should contain skills, experience, education sections

```powershell
$jobId = "YOUR_JOB_ID_FROM_STEP_3"
$resumePath = "Samples/Resumes/test_candidate.pdf"

$form = @{
    jobId = $jobId
    fullName = "John Doe"
    email = "john@example.com"
    phone = "9876543210"
    degree = "Bachelor's in CS"
    branch = "Computer Science"
    resume = Get-Item $resumePath
}

$response = Invoke-RestMethod `
    -Uri "http://localhost:5000/api/apply" `
    -Method POST `
    -Form $form `
    -UseBasicParsing

$response | ConvertTo-Json
```

**Response:** (If successful)
```json
{
  "success": true,
  "message": "Resume submitted successfully! AI is processing your application...",
  "applicationId": "app123...",
  "status": "Selected",
  "score": 85.5
}
```

**What happened behind the scenes:**
1. ✅ Resume PDF saved to `Backend/instance/storage/uploads/resumes/`
2. ✅ Resume Parser extracted text
3. ✅ Text files created for NLP Engine
4. ✅ NLP Engine processed resume + job
5. ✅ AI Scoring calculated match score (85.5)
6. ✅ Score ≥ 70 → Status = "Selected"
7. ✅ Email sent (if SMTP configured)
8. ✅ Application saved to MongoDB with all metadata

---

### Step 5: View Company Resumes

```powershell
$companyId = "YOUR_COMPANY_ID_FROM_STEP_2"

Invoke-RestMethod `
    -Uri "http://localhost:5000/api/company/$companyId/resumes" `
    -Method GET `
    -UseBasicParsing | ConvertTo-Json
```

**Response:**
```json
[
  {
    "candidateName": "John Doe",
    "resumeName": "test_candidate.pdf",
    "email": "john@example.com",
    "jobTitle": "Senior Software Engineer",
    "status": "Selected"
  }
]
```

---

### Step 6: View Company History

```powershell
$companyId = "YOUR_COMPANY_ID_FROM_STEP_2"

Invoke-RestMethod `
    -Uri "http://localhost:5000/api/company/$companyId/history" `
    -Method GET `
    -UseBasicParsing | ConvertTo-Json
```

**Response:**
```json
[
  {
    "candidateName": "John Doe",
    "jobTitle": "Senior Software Engineer",
    "status": "Selected",
    "date": "2026-02-16T12:34:56.789000"
  }
]
```

---

## Testing Different Scenarios

### Scenario 1: Low Score (Below Threshold)

If resume doesn't match job well:
- Score < 70 → Status = "Rejected"
- Email still sent with rejection message
- Application stored in DB

### Scenario 2: Email Not Configured

If SMTP settings missing in `.env`:
- Pipeline completes normally
- Application saved with `emailSent: false`
- Check logs: "SMTP settings missing, skipping email"

### Scenario 3: Resume Parser Error

If PDF is invalid/corrupted:
- Returns 500 with error message
- Check `/Backend/app/logs` for details
- Example: "Unable to extract text from PDF"

---

## Database Inspection

### View Applications in MongoDB

```bash
# Connect to MongoDB CLI
mongosh

# Use database
use resume_filtering

# View applications
db.applications.find({}).pretty()

# View specific company applications
db.applications.find({companyId: "abc123..."}).pretty()

# Check scores distribution
db.applications.aggregate([
  {$group: {_id: "$status", count: {$sum: 1}, avgScore: {$avg: "$score"}}}
])
```

---

## Troubleshooting

### Backend not starting?

```bash
# Check Python version
python --version  # Should be 3.8+

# Check if port 5000 is in use
netstat -ano | findstr :5000

# Kill process on 5000 (Windows)
taskkill /PID <PID> /F

# Run with debug output
set FLASK_DEBUG=1
python Backend/run.py
```

### Module imports failing?

```
ModuleNotFoundError: No module named 'Resume_Parser'
→ Run from project root: cd AI-Powered-Resume-Filtering-and-Ranking
→ Check sys.path in run.py includes project root

ModuleNotFoundError: No module named 'Ai_Scoring.Ai_Scoring.scorer'
→ Verify folder structure: Ai_Scoring/Ai_Scoring/scorer.py
→ Check import paths in pipeline_service.py
```

### MongoDB connection error?

```
pymongo.errors.ServerSelectionTimeoutError
→ MongoDB not running
→ Start: mongod
→ Or update MONGO_URI in .env to correct host
```

### Email not sending?

```
Check .env:
- SMTP_HOST (e.g., smtp.gmail.com)
- SMTP_PORT (587 for TLS)
- SMTP_USER (your email)
- SMTP_PASSWORD (app-specific password, not Gmail password)
- SMTP_FROM (should match SMTP_USER)

Gmail: Use App Passwords, not regular password
Outlook: Use app-specific password
```

---

## Frontend Integration

### If Frontend is Running (Port 3000)

The React frontend already has the correct API calls configured in:
- [Frontend/react-project/src/api/index.js](Frontend/react-project/src/api/index.js)

**No changes needed!** Just start both:

```bash
# Terminal 1: Backend
cd AI-Powered-Resume-Filtering-and-Ranking
python Backend/run.py

# Terminal 2: Frontend
cd AI-Powered-Resume-Filtering-and-Ranking/Frontend/react-project
npm start
```

---

## Performance Metrics

### Expected Response Times

| Endpoint | Time | Notes |
|----------|------|-------|
| `/api/health` | <10ms | No processing |
| `/api/company/register` | <50ms | Hash password |
| `/api/jobs` | <100ms | DB query |
| `/api/apply` | 15-30sec | Full pipeline (Parser + NLP + Scoring) |
| `/api/company/{id}/resumes` | <100ms | DB query |

### At Scale

- **1000 jobs:** <500ms query time
- **10000 applications:** <1s to filter by company
- **Add indexes** for companyId, jobId in MongoDB

---

## Monitoring Commands

### Check Backend Logs (Real-time)

```bash
# If running in terminal 1, tail logs
tail -f Backend/logs/app.log
```

### Database Stats

```bash
# MongoDB connection stats
db.serverStatus().connections

# Collection sizes
db.applications.stats()
db.companies.stats()
db.jobs.stats()
```

### API Rate Limiting (Future)

Currently: None implemented
To add: Use Flask-Limiter extension

---

## Security Checklist

- ✅ Passwords hashed (werkzeug)
- ✅ Secrets in .env (not in code)
- ✅ File upload validation (PDF only)
- ✅ Error messages don't leak internals (500 response)
- ⚠️ Add CORS headers (if calling from different domain)
- ⚠️ Add rate limiting (if public API)
- ⚠️ Add authentication tokens (if mobile/SPA)

---

## Next: Production Deployment

Ready to deploy? Checklist:

1. Update `.env` with production secrets
2. Change `SECRET_KEY`
3. Use production MongoDB URI
4. Configure SMTP with production email
5. Set `debug=False` in run.py
6. Add CORS handling
7. Use WSGI server (Gunicorn):
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 Backend.run:app
   ```
8. Deploy to cloud (AWS, Azure, Heroku, etc.)

---

**Last Updated:** Feb 16, 2026  
**Status:** ✅ Ready for Testing
