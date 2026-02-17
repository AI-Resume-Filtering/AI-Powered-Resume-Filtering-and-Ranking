import requests
import sys

# Test the apply endpoint
resume_path = r"D:\AI_POWER_RESUME_FILERTRING\AI-Powered-Resume-Filtering-and-Ranking\Samples\Resumes\Mahesh_Nikas_IT_2026.pdf"

# Get first job
print("Getting jobs...")
jobs_response = requests.get("http://localhost:5000/api/jobs")
jobs = jobs_response.json()

if not jobs:
    print("No jobs available!")
    sys.exit(1)

job_id = jobs[0]["id"]
print(f"Job ID: {job_id}")
print(f"Job Title: {jobs[0]['title']}")

# Prepare form data
files = {
    'resume': ('Mahesh_Nikas_IT_2026.pdf', open(resume_path, 'rb'), 'application/pdf')
}

data = {
    'jobId': job_id,
    'fullName': 'Mahesh Nikas',
    'email': 'mahesh@example.com',
    'phone': '1234567890',
    'degree': 'BE',
    'branch': 'Computer Science'
}

print("\nSubmitting application...")
try:
    response = requests.post("http://localhost:5000/api/apply", files=files, data=data)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        print("\n✓ Application submitted successfully!")
    else:
        print("\n✗ Application failed!")
        print(response.text)
except Exception as e:
    print(f"\n✗ Error: {e}")
