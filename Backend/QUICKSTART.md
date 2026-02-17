# 📋 Quick Start Card (30 seconds)

## Current Status
✅ **Backend RUNNING**: http://localhost:5000/api/health  
✅ **All services loaded**  
✅ **Ready to test**  

---

## What's Running?

```
PIPELINE: PDF Resume → Parse → NLP Extract → AI Score → Save DB → Send Email
```

---

## Start Using

### Option 1: React Frontend (Recommended)
```bash
# Terminal 1: Backend (Already running)
# Terminal 2: Start Frontend
cd Frontend/react-project
npm start

# Navigate to http://localhost:3000
# Use UI to register company → post job → apply
```

### Option 2: Test via API

#### 1. Register Company
```powershell
$body = @{
    companyName="TechCorp"
    registrationNo="COM123"
    email="tech@example.com"
    password="Secure123!"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://localhost:5000/api/company/register" `
    -Method POST -ContentType "application/json" -Body $body

$companyId = $response.company.companyId
Write-Output "Company ID: $companyId"
```

#### 2. Post Job (with PDF)
```powershell
# Place: Samples/Job_Descriptions/test_jd.pdf

$form = @{
    companyId = $companyId
    jobTitle = "Software Engineer"
    descriptionPdf = Get-Item "Samples/Job_Descriptions/test_jd.pdf"
}

$jobResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/company/post-job" `
    -Method POST -Form $form

$jobId = $jobResponse.jobId
Write-Output "Job ID: $jobId"
```

#### 3. Apply for Job (Triggers Pipeline) ⭐
```powershell
# Place: Samples/Resumes/test_resume.pdf

$form = @{
    jobId = $jobId
    fullName = "John Doe"
    email = "john@example.com"
    phone = "9876543210"
    degree = "BS Computer Science"
    branch = "Engineering"
    resume = Get-Item "Samples/Resumes/test_resume.pdf"
}

$applyResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/apply" `
    -Method POST -Form $form

Write-Output "Status: $($applyResponse.status)"
Write-Output "Score: $($applyResponse.score)"
```

#### 4. View Results
```powershell
$resumes = Invoke-RestMethod -Uri "http://localhost:5000/api/company/$companyId/resumes" `
    -Method GET

$resumes | Format-Table -AutoSize
```

---

## Documentation

| Need | File |
|------|------|
| **All details** | [SUMMARY.md](SUMMARY.md) |
| **Architecture** | [ARCHITECTURE.md](ARCHITECTURE.md) |
| **Step-by-step tests** | [TESTING_GUIDE.md](TESTING_GUIDE.md) |
| **Visual diagrams** | [VISUAL_REFERENCE.md](VISUAL_REFERENCE.md) |
| **Config/setup** | [README.md](README.md) |

---

## Key Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /api/health` | Check if running |
| `POST /api/company/register` | Register company |
| `POST /api/company/post-job` | Post job (with JD PDF) |
| `POST /api/apply` | ⭐ Apply (triggers pipeline) |
| `GET /api/company/{id}/resumes` | View received resumes |
| `GET /api/company/{id}/history` | View history |

---

## Files Created

```
Backend/
├── app/
│   ├── services/pipeline_service.py     ⭐ CORE
│   ├── routes/application_routes.py     ⭐ Apply endpoint
│   └── [other services & routes]
├── run.py                              ← Start here
├── README.md                           ← Full guide
└── [Documentation files]
```

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Backend not running | `python Backend/run.py` from project root |
| MongoDB error | Start mongod: `mongod` |
| Module import error | Ensure running from project root |
| Email not sending | Check SMTP settings in `.env` |
| Port 5000 in use | `netstat -ano \| findstr :5000` then `taskkill /PID {PID} /F` |

---

## Next: Advanced

- **Add validation schemas** → Use marshmallow/pydantic
- **Add async jobs** → Use Celery + Redis
- **Add caching** → Use Redis
- **Deploy to cloud** → AWS/Azure/Heroku
- **Add authentication** → JWT tokens
- **Add rate limiting** → Flask-Limiter

---

**Status:** ✅ Ready  
**Date:** Feb 16, 2026  
**Backend:** Running on http://localhost:5000
