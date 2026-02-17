# Ai_Scoring/test_scoring.py
from scorer import score_resume

# ==========================================
# TEST CASE 1: THE FRESHER (Entry Level)
# ==========================================
print("\n--- TEST 1: FRESHER CANDIDATE ---")
fresher_job = {
    "job_requirements": {
        "minimum_experience": 0,  # <--- TRIGGERS FRESHER WEIGHTS
        "required_education": "bachelors",
        "preferred_skills": ["react", "node"]
    }
}

fresher_resume = {
    "experience_years": 0,
    "education_level": "bachelors",
    "skills": ["react", "html", "css"],
    "job_match": {"match_percentage": 85.0} # Good skills
}

score1 = score_resume(fresher_resume, fresher_job)
print(f"Candidate: Fresh Graduate")
print(f"Job Type: Entry Level (0 years)")
print(f"Final Score: {score1} / 100")
print("(Expected: High score because Skills > Experience here)")


# ==========================================
# TEST CASE 2: THE SENIOR (Experienced)
# ==========================================
print("\n--- TEST 2: SENIOR CANDIDATE ---")
senior_job = {
    "job_requirements": {
        "minimum_experience": 5,  # <--- TRIGGERS SENIOR WEIGHTS
        "required_education": "bachelors",
        "preferred_skills": ["aws", "docker", "kubernetes"]
    }
}

# Resume A: Has 6 years exp (Good)
senior_resume_good = {
    "experience_years": 6,
    "education_level": "bachelors",
    "skills": ["java", "spring", "aws", "docker"],
    "job_match": {"match_percentage": 70.0}
}

# Resume B: Has 1 year exp (Bad for this job)
senior_resume_bad = {
    "experience_years": 1,
    "education_level": "masters", # Good education, but...
    "skills": ["java", "spring"],
    "job_match": {"match_percentage": 90.0} # Great skills, but...
}

score_a = score_resume(senior_resume_good, senior_job)
score_b = score_resume(senior_resume_bad, senior_job)

print(f"\nCandidate A (6 Years Exp): {score_a}")
print(f"Candidate B (1 Year Exp): {score_b}")
print("(Expected: Candidate A should win, even if B has better skills/education, because Experience weight is 45%)")