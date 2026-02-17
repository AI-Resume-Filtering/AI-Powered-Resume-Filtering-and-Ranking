# Integration Testing Guide

## System Status
- **Backend**: Running on http://localhost:5000
- **Frontend**: Running on http://localhost:5173
- **Database**: MongoDB (resume_filtering)
- **CORS**: Enabled ✅

## Test Checklist

### 1️⃣ Health Check ✅ (Should work immediately)
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/health" -UseBasicParsing | Select-Object -ExpandProperty Content
```
**Expected Response:**
```json
{"status": "ok"}
```

### 2️⃣ Company Registration (Frontend or API Test)
**Frontend Action:** Navigate to http://localhost:5173 → Click "Company Register"

**Manual API Test:**
```powershell
$body = @{
    companyName = "Tech Corp"
    registrationNo = "REG123456"
    email = "company@techcorp.com"
    password = "SecurePass123!" 
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/api/company/register" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body `
    -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Expected Response (Success):**
```json
{
  "success": true,
  "company": {
    "companyId": "xxx",
    "name": "Tech Corp",
    "registrationNo": "REG123456",
    "email": "company@techcorp.com"
  }
}
```

**Expected Response (Duplicate):**
```json
{
  "success": false,
  "message": "Company already exists"
}
```

### 3️⃣ Company Login (Frontend or API Test)
**Frontend Action:** Navigate to http://localhost:5173 → Click "Company Login"

**Manual API Test:**
```powershell
$body = @{
    email = "company@techcorp.com"
    password = "SecurePass123!"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:5000/api/company/login" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body `
    -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Expected Response (Success):**
```json
{
  "success": true,
  "company": {
    "companyId": "xxx",
    "name": "Tech Corp",
    "registrationNo": "REG123456",
    "email": "company@techcorp.com"
  }
}
```

### 4️⃣ Post Job (Company Dashboard)
**Frontend Action:** 
1. Login as company
2. Go to Company Dashboard
3. Click "Post Job"
4. Enter job title
5. Upload job description PDF
6. Submit

**Expected Result:** Job posted successfully, ID returned

### 5️⃣ View Available Jobs (Candidate Side)
**Frontend Action:** Navigate to "Job List" page

**Manual API Test:**
```powershell
Invoke-WebRequest -Uri "http://localhost:5000/api/jobs" `
    -UseBasicParsing | Select-Object -ExpandProperty Content
```

**Expected Response:**
```json
[
  {
    "id": "job123",
    "title": "Senior Developer",
    "companyName": "Tech Corp",
    "companyRegNo": "REG123456",
    "location": "NYC",
    "experience": "5+ years"
  }
]
```

### 6️⃣ Apply for Job (Candidate Submission)
**Frontend Action:**
1. Go to Job List
2. Click on a job
3. Fill in candidate details
4. Upload resume PDF
5. Click "Apply"

**Expected Result:** 
- Resume uploaded ✅
- AI scoring system runs ✅
- Score displayed ✅
- Success message shown ✅

### 7️⃣ View Company Resumes (Company Dashboard)
**Frontend Action:** Go to Company Dashboard → "Resumes" tab

**Expected Result:** List of submitted resumes with scores

### 8️⃣ View Application History (Company Dashboard)
**Frontend Action:** Go to Company Dashboard → "History" tab

**Expected Result:** Timeline of all applications

---

## Troubleshooting

### Frontend Shows Error but Backend is Running
**Solution:** Clear browser cache (Ctrl+Shift+Delete) and reload

### "Connection Refused" Error
**Check:**
1. Backend running: `Invoke-WebRequest http://localhost:5000/api/health`
2. Port 5000 in use: `netstat -ano | findstr :5000`
3. Restart backend if needed

### "MongoDB Connection Error"
**Check:**
1. MongoDB installed and running
2. MONGO_URI in .env is correct
3. Port 27017 is accessible

### "CORS Error" in Browser Console
**Already Fixed!** CORS is now configured to allow:
- Frontend: http://localhost:5173
- Also supports: http://localhost:3000

### "Missing Required Fields" Error
**Check Frontend Form:**
- companyName (not company_name)
- registrationNo (not registration_no)
- email
- password (minimum 8 chars, with uppercase, lowercase, number, special char)

---

## Terminal Commands to Monitor Logs

### Backend Logs (when terminal is running)
- Should show successful requests like: `"POST /company/register HTTP/1.1" 200`
- Errors will show full stack trace for debugging

### Test Connection
```powershell
# Quick test all endpoints are responding
@('/', '/api/health', '/api/jobs') | ForEach-Object {
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:5000$_" -UseBasicParsing
        Write-Host "✓ $_ - Status: $($response.StatusCode)"
    } catch {
        Write-Host "✗ $_ - Error: $($_.Exception.Message)"
    }
}
```

---

## Success Criteria

- [x] Backend running with CORS enabled
- [x] Frontend can communicate with backend
- [x] Health check responds
- [x] Company registration works
- [x] Company login works
- [x] Job posting works
- [x] Resume upload works
- [x] AI scoring processes applications
- [x] Email notifications send (if SMTP configured)

---

## Next Steps After Testing

1. **If registration works:** Test company dashboard and job posting
2. **If job posting works:** Test candidate job application
3. **If application works:** Verify AI scoring pipeline runs
4. **If scoring works:** Check MongoDB for stored results
5. **Integration complete:** The system is ready for production use

---

## Key Files to Reference

- Backend config: `Backend/app/config.py`
- Frontend API calls: `Frontend/react-project/src/api/index.js`
- Backend routes: `Backend/app/routes/`
- Services: `Backend/app/services/`
- Env variables: `Backend/.env`

