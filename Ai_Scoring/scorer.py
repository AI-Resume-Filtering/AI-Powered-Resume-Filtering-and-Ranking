
# scoring_engine/scorer.py

from normalizer import normalize

SKILL_CAP = 20
INFERRED_SKILL_CAP = 5
PROJECT_CAP = 5
EXPERIENCE_CAP = 5

WEIGHTS = {
    "explicit_skills": 0.40,
    "inferred_skills": 0.15,
    "projects": 0.25,
    "experience": 0.20
}

def score_resume(nlp_output: dict) -> dict:
    explicit_skill_count = len(nlp_output.get("explicit_skills", {}))
    inferred_skill_count = len(nlp_output.get("inferred_skills", {}))
    project_count = nlp_output.get("projects", {}).get("count", 0)
    experience_years = nlp_output.get("experience_years", 0)

    explicit_score = normalize(explicit_skill_count, SKILL_CAP)
    inferred_score = normalize(inferred_skill_count, INFERRED_SKILL_CAP)
    project_score = normalize(project_count, PROJECT_CAP)
    experience_score = normalize(experience_years, EXPERIENCE_CAP)

    final_score = (
        explicit_score * WEIGHTS["explicit_skills"] +
        inferred_score * WEIGHTS["inferred_skills"] +
        project_score * WEIGHTS["projects"] +
        experience_score * WEIGHTS["experience"]
    )

    return {
        "final_score": round(final_score * 100, 3),
        "breakdown": {
            "explicit_skill_score": round(explicit_score * 100, 3),
            "inferred_skill_score": round(inferred_score * 100, 3),
            "project_score": round(project_score * 100, 3),
            "experience_score": round(experience_score, 3)
        }
    }
