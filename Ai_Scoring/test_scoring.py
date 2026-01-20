# scoring_engine/test_scoring.py

from scorer import score_resume
from ranker import rank_resumes

# -------------------------
# TEST INPUT 1: FRESHER
# -------------------------
fresher_nlp_output = {
    "explicit_skills": {
        "python": 1,
        "java": 1,
        "flask": 1,
        "docker": 1,
        "nlp": 1
    },
    "inferred_skills": {
        "machine learning": "medium"
    },
    "projects": {"count": 3},
    "experience_years": 0
}

# -------------------------
# TEST INPUT 2: EXPERIENCED
# -------------------------
experienced_nlp_output = {
    "explicit_skills": {
        "java": 1,
        "spring": 1,
        "microservices": 1,
        "docker": 1
    },
    "inferred_skills": {},
    "projects": {"count": 2},
    "experience_years": 5
}

# -------------------------
# SCORE BOTH
# -------------------------
fresher_score = score_resume(fresher_nlp_output)
experienced_score = score_resume(experienced_nlp_output)

# -------------------------
# DISPLAY RESULTS
# -------------------------
print("FRESHER SCORE:")
print(fresher_score)

print("\nEXPERIENCED SCORE:")
print(experienced_score)

# -------------------------
# RANKING TEST
# -------------------------
ranked = rank_resumes([
    {"name": "Fresher", **fresher_score},
    {"name": "Experienced", **experienced_score}
])

print("\nFINAL RANKING:")
for r in ranked:
    print(r)