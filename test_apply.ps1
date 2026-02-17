# Test Apply Endpoint
$resumePath = "D:\AI_POWER_RESUME_FILERTRING\AI-Powered-Resume-Filtering-and-Ranking\Samples\Resumes\Mahesh_Nikas_IT_2026.pdf"

# Get first job
$jobs = Invoke-RestMethod -Uri "http://localhost:5000/api/jobs" -Method GET
$jobId = $jobs[0].id
Write-Host "Using Job ID: $jobId"
Write-Host "Job Title: $($jobs[0].title)"

# Create multipart form data
$boundary = [System.Guid]::NewGuid().ToString()
$LF = "`r`n"

$bodyLines = (
    "--$boundary",
    "Content-Disposition: form-data; name=`"jobId`"$LF",
    $jobId,
    "--$boundary",
    "Content-Disposition: form-data; name=`"fullName`"$LF",
    "Test Candidate",
    "--$boundary",
    "Content-Disposition: form-data; name=`"email`"$LF",
    "test@example.com",
    "--$boundary",
    "Content-Disposition: form-data; name=`"phone`"$LF",
    "1234567890",
    "--$boundary",
    "Content-Disposition: form-data; name=`"degree`"$LF",
    "BE",
    "--$boundary",
    "Content-Disposition: form-data; name=`"branch`"$LF",
    "Computer Science",
    "--$boundary",
    "Content-Disposition: form-data; name=`"resume`"; filename=`"Mahesh_Nikas_IT_2026.pdf`"",
    "Content-Type: application/pdf$LF",
    [System.IO.File]::ReadAllBytes($resumePath),
    "--$boundary--$LF"
) -join $LF

try {
    $response = Invoke-RestMethod -Uri "http://localhost:5000/api/apply" `
        -Method POST `
        -ContentType "multipart/form-data; boundary=$boundary" `
        -Body $bodyLines
    
    Write-Host "`nSuccess!" -ForegroundColor Green
    $response | ConvertTo-Json -Depth 5
} catch {
    Write-Host "`nError occurred:" -ForegroundColor Red
    Write-Host $_.Exception.Message
    Write-Host $_.ErrorDetails.Message
}
