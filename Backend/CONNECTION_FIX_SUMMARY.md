# Frontend-Backend Integration: Complete Connection Guide

## 🔴 Problems Found & Fixed

### 1. **CORS Not Configured** ❌ → ✅ FIXED
**Problem:** Frontend (port 5173) couldn't connect to Backend (port 5000)
**Solution:** Added Flask-CORS configuration to allow cross-origin requests

### 2. **Delete Component Not Connected** ❌ → ✅ FIXED
**Problem:** Delete job form was just showing alerts, NOT calling backend API
**Original Code:**
```javascript
alert("Job delete request sent (backend connect करा)"); // Just alert, no API call!
```
**Fixed Code:** 
```javascript
const data = await API.deleteJob(selectedJobId); // Now calls backend!
```

### 3. **Missing Backend Route** ❌ → ✅ FIXED
**Problem:** Frontend requesting `/api/company/{companyId}/jobs` but backend didn't have it
**Solution:** Added new route in job_routes.py

### 4. **Wrong Delete Logic** ❌ → ✅ FIXED
**Problem:** Component asked for job title or PDF, but backend expects jobId
**Solution:** Changed to fetch jobs list first, let user select, then delete by jobId

---

## ✅ Complete Connection Flow (Now Working)

### Step 1: Company Registration
```
Frontend (React)
    ↓
API.registerCompany()
    ↓
POST /api/company/register
    ↓
Backend (Flask)
    ↓
CompanyService.register_company()
    ↓
MongoDB: Insert company doc
    ↓
Response: {"success": true, "company": {...}}
    ↓
Frontend: Show success, redirect to login
```

### Step 2: Company Login
```
Frontend (React)
    ↓
API.loginCompany()
    ↓
POST /api/company/login
    ↓
Backend (Flask)
    ↓
CompanyService.login_company()
    ↓
Password verification
    ↓
Response: {"success": true, "company": {...}}
    ↓
Frontend: Save company to localStorage + redirect to dashboard
```

### Step 3: View Company Jobs (Home Page)
```
Frontend (CompanyDashboard → Home)
    ↓
API.getCompanyJobs(companyId)
    ↓
GET /api/company/{companyId}/jobs
    ↓
Backend (Flask)
    ↓
JobService.list_company_jobs()
    ↓
MongoDB: Query jobs where companyId matches
    ↓
Response: [{jobId, title, description, totalApplications, ...}, ...]
    ↓
Frontend: Display list in table
```

### Step 4: Post a Job
```
Frontend (CompanyDashboard → PostJob)
    ↓
API.postJob(formData: jobTitle, PDF)
    ↓
POST /api/company/post-job
    ↓
Backend (Flask)
    ↓
JobService.create_job()
    ↓
ResumeParser.parse() [extracts text from PDF]
    ↓
MongoDB: Insert job document
    ↓
Response: {"success": true, "jobId": "xxx"}
    ↓
Frontend: Show success, clear form
```

### Step 5: Delete a Job ✅ FIXED
```
Frontend (CompanyDashboard → Delete)
    ↓
Fetch: API.getCompanyJobs(companyId)
    ↓
Display dropdown of company's jobs
    ↓
User selects job → shows details
    ↓
API.deleteJob(jobId)
    ↓
DELETE /api/company/delete-job
    ↓
Backend (Flask)
    ↓
JobService.delete_job(jobId)
    ↓
MongoDB: Delete document where jobId matches
    ↓
Response: {"success": true}
    ↓
Frontend: Remove from list, show success
```

### Step 6: View Resumes (From Applicants)
```
Frontend (CompanyDashboard → Resumes)
    ↓
API.getCompanyResumes(companyId)
    ↓
GET /api/company/{companyId}/resumes
    ↓
Backend (Flask)
    ↓
ApplicationService.list_company_resumes()
    ↓
MongoDB: Query applications where companyId matches
    ↓
Response: [{candidateName, email, status, score, ...}, ...]
    ↓
Frontend: Display in table with download links
```

### Step 7: View Application History
```
Frontend (CompanyDashboard → History)
    ↓
API.getCompanyHistory(companyId)
    ↓
GET /api/company/{companyId}/history
    ↓
Backend (Flask)
    ↓
ApplicationService.list_company_history()
    ↓
MongoDB: Query applications timeline
    ↓
Response: [{candidateName, jobTitle, status, score, date, ...}, ...]
    ↓
Frontend: Display timeline/history
```

### Step 8: Apply for Job (Candidate)
```
Frontend (JobList → ApplyJob)
    ↓
API.applyForJob(formData: jobId, resume PDF, candidate info)
    ↓
POST /api/apply
    ↓
Backend (Flask)
    ↓
PipelineService.process_application()
    ↓
Resume Parser ➜ NLP Engine ➜ AI Scoring
    ↓
MongoDB: Insert application + score
    ↓
EmailService: Send notification (if configured)
    ↓
Response: {"success": true, "score": 85, "status": "processed"}
    ↓
Frontend: Show score, success message
```

---

## 📋 All Connected Routes

### Company Routes
- ✅ `POST /api/company/register` - Register company
- ✅ `POST /api/company/login` - Login company

### Job Routes
- ✅ `GET /api/jobs` - All jobs (for candidates)
- ✅ `GET /api/jobs/{job_id}` - Job details
- ✅ `POST /api/company/post-job` - Post new job (form data)
- ✅ `DELETE /api/company/delete-job` - Delete job (JSON)
- ✅ `GET /api/company/{company_id}/jobs` - Company's posted jobs ✅ NEW

### Application Routes
- ✅ `POST /api/apply` - Submit application (form data)
- ✅ `GET /api/company/{company_id}/resumes` - Company's received resumes
- ✅ `GET /api/company/{company_id}/history` - Company's application history
- ✅ `GET /api/resumes/{application_id}` - Download resume

### Health Routes
- ✅ `GET /` - Root endpoint (shows service info)
- ✅ `GET /api/health` - Health check

---

## 🧪 Test Complete Flow

### Test 1: Company Registration & Login
```powershell
# Step 1: Register
$body = @{
    companyName = "TechCorp"
    registrationNo = "REG2026"
    email = "tech@corp.com"
    password = "Test@12345"
} | ConvertTo-Json

$result = Invoke-WebRequest -Uri "http://localhost:5000/api/company/register" `
    -Method POST -ContentType "application/json" -Body $body -UseBasicParsing
$result.Content | ConvertFrom-Json

# Step 2: Login
$loginBody = @{
    email = "tech@corp.com"
    password = "Test@12345"
} | ConvertTo-Json

$login = Invoke-WebRequest -Uri "http://localhost:5000/api/company/login" `
    -Method POST -ContentType "application/json" -Body $loginBody -UseBasicParsing
$companyData = $login.Content | ConvertFrom-Json
$companyId = $companyData.company.companyId
```

### Test 2: Post Job & View Jobs
```powershell
# Step 3: View company's jobs
$jobs = Invoke-WebRequest -Uri "http://localhost:5000/api/company/$companyId/jobs" `
    -UseBasicParsing | Select-Object -ExpandProperty Content | ConvertFrom-Json
$jobs | Format-Table -Property title, totalApplications
```

### Test 3: Delete Job
```powershell
# Get a job to delete
$firstJobId = $jobs[0].jobId

# Delete it
$deleteBody = @{ jobId = $firstJobId } | ConvertTo-Json

$delete = Invoke-WebRequest -Uri "http://localhost:5000/api/company/delete-job" `
    -Method DELETE -ContentType "application/json" -Body $deleteBody -UseBasicParsing
$delete.Content | ConvertFrom-Json
```

---

## 🎯 Frontend Test Checklist

### In Browser (http://localhost:5173)

1. **Company Registration** ✅
   - [ ] Click "Company Register"
   - [ ] Enter: Company Name, Reg No, Email, Password
   - [ ] Password: Min 8 chars, uppercase, lowercase, number, special char
   - [ ] Click "Register"
   - [ ] Should redirect to login

2. **Company Login** ✅
   - [ ] Click "Company Login"
   - [ ] Enter credentials from registration
   - [ ] Click "Login"
   - [ ] Should redirect to dashboard

3. **Company Dashboard - Home** ✅
   - [ ] View "Total Jobs Posted" card
   - [ ] View "Job Posted List" table
   - [ ] Should show all posted jobs

4. **Company Dashboard - Post Job** ✅
   - [ ] Click "Post Job" button
   - [ ] Enter job title
   - [ ] Upload PDF (job description)
   - [ ] Click "Post Job"
   - [ ] Success message shown

5. **Company Dashboard - Delete Job** ✅ FIXED
   - [ ] Click "Delete Job Post" button
   - [ ] Dropdown appears with company's jobs
   - [ ] Select a job
   - [ ] Shows job details
   - [ ] Click "Delete Job Post"
   - [ ] Confirmation dialog
   - [ ] Job deleted from list

6. **View Resumes** ✅
   - [ ] Click "View Resumes" button
   - [ ] See list of submitted resumes from candidates

7. **View History** ✅
   - [ ] Click "History" button
   - [ ] See timeline of all applications

---

## 🔧 Connection Verification Commands

```powershell
# Check backend routes are loading
Invoke-WebRequest -Uri "http://localhost:5000/" -UseBasicParsing | Select-Object -ExpandProperty Content

# Test health
Invoke-WebRequest -Uri "http://localhost:5000/api/health" -UseBasicParsing | Select-Object -ExpandProperty Content

# Test CORS preflight
Invoke-WebRequest -Uri "http://localhost:5000/api/company/register" `
    -Method OPTIONS -UseBasicParsing | Select-Object -ExpandProperty Headers
```

---

## 📊 System Status

| Component | Status | Port | Details |
|-----------|--------|------|---------|
| Backend API | ✅ Running | 5000 | Flask with CORS |
| Frontend | ✅ Running | 5173 | React Vite |
| MongoDB | ✅ Connected | 27017 | resume_filtering |
| CORS | ✅ Enabled | N/A | Allows 5173 & 3000 |

---

## 🚀 Everything is Now Connected!

1. ✅ **CORS Enabled** - Frontend can talk to Backend
2. ✅ **Routes Added** - All endpoints working
3. ✅ **Delete Fixed** - Actually calls backend API now
4. ✅ **Data Flow** - Proper MongoDB integration
5. ✅ **Error Handling** - Better logging and messages

**Test the complete flow now in your browser!** 🎯

