# Ai_Scoring/config.py

SCORING_PROFILES = {
    "FRESHER": {
        "skill_match": 70,
        "experience": 5,
        "education": 20,
        "preferred_skills": 5
    },
    "MID_LEVEL": {
        "skill_match": 60,
        "experience": 25,
        "education": 10,
        "preferred_skills": 5
    },
    "SENIOR": {
        "skill_match": 40,
        "experience": 45,
        "education": 5,
        "preferred_skills": 10
    }
}

EDUCATION_RANKING = {
    "high school": 1,
    "diploma": 2,
    "bachelors": 3,
    "masters": 4,
    "phd": 5
}

EXP_THRESHOLDS = {
    "mid_level": 3,
    "senior_level": 5
}