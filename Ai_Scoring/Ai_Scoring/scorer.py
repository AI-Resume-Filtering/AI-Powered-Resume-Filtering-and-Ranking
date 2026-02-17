# Ai_Scoring/scorer.py
import os
import json

# --- IMPORTS (Handles Local & Package modes) ---
try:
    from .config import SCORING_PROFILES, EDUCATION_RANKING, EXP_THRESHOLDS
    from .utils import parse_education_level, standardize_resume_data
except ImportError:
    from config import SCORING_PROFILES, EDUCATION_RANKING, EXP_THRESHOLDS
    from utils import parse_education_level, standardize_resume_data


# -----------------------------------------------

def get_adaptive_weights(job_reqs: dict) -> dict:
    """
    Returns the scoring profile (Fresher vs Senior) based on
    the job's minimum experience requirement.
    """
    req_exp = job_reqs.get("minimum_experience", 0)

    if req_exp == 0:
        return SCORING_PROFILES["FRESHER"]
    elif req_exp >= EXP_THRESHOLDS["senior_level"]:
        return SCORING_PROFILES["SENIOR"]
    else:
        return SCORING_PROFILES["MID_LEVEL"]


def score_resume(resume_raw: dict, metadata: dict) -> float:
    """
    Calculates the score for a single resume.
    """
    # 1. STANDARDIZE INPUT (Fixes messy data instantly)
    resume = standardize_resume_data(resume_raw)

    # 2. EXTRACT JOB REQUIREMENTS
    # Handles if metadata is the full object OR just the requirements dict
    job_reqs = metadata.get("job_requirements", metadata)

    # 3. GET DYNAMIC WEIGHTS
    weights = get_adaptive_weights(job_reqs)

    # --- METRIC 1: Skill Match ---
    match_pct = resume.get("job_match", {}).get("match_percentage", 0)
    skill_score = (match_pct / 100) * weights["skill_match"]

    # --- METRIC 2: Experience ---
    years = resume.get("experience_years", 0)
    req_exp = job_reqs.get("minimum_experience", 0)

    if req_exp == 0:
        # If no experience needed, everyone gets full points relative to the weight
        exp_ratio = 1.0
    else:
        # Cap the multiplier at 1.5x to prevent skewing
        exp_ratio = min(years / req_exp, 1.5)

    exp_score = min(exp_ratio * weights["experience"], weights["experience"])

    # --- METRIC 3: Education ---
    req_edu = job_reqs.get("required_education", "bachelors")
    cand_edu = resume.get("education_level", "")

    req_rank = EDUCATION_RANKING.get(parse_education_level(req_edu), 3)
    cand_rank = EDUCATION_RANKING.get(parse_education_level(cand_edu), 0)

    # Full points if degree is equal or higher
    if cand_rank >= req_rank:
        edu_score = weights["education"]
    else:
        edu_score = 0

    # --- METRIC 4: Preferred Skills (Bonus) ---
    pref_list = job_reqs.get("preferred_skills", [])
    cand_skills = resume.get("skills", [])

    # Find common skills
    matched_pref = set(pref_list) & set(cand_skills)

    # 2 points per preferred skill, capped at the max weight
    pref_score = min(len(matched_pref) * 2, weights["preferred_skills"])

    # --- FINAL CALCULATION ---
    final_score = skill_score + exp_score + edu_score + pref_score
    return round(final_score, 2)


# ==========================================================
# MICROSERVICE INTERFACE (For the Backend Team)
# ==========================================================
def process_resume_batch(filename: str, backend_metadata: dict) -> list:
    """
    This function is the API endpoint logic.
    1. Finds the NLP file in 'Nlp_Engine/output'
    2. Scores every resume using the provided metadata
    3. Returns a sorted list of results
    """

    # 1. Locate the file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(current_dir))

    candidate_paths = []
    # Absolute path provided by caller
    if os.path.isabs(filename):
        candidate_paths.append(filename)

    # Filename (or relative path) under repo-root Nlp_Engine/output
    candidate_paths.append(os.path.join(repo_root, "Nlp_Engine", "output", filename))

    # If filename already includes a relative path like Nlp_Engine/output/...
    candidate_paths.append(os.path.join(repo_root, filename))

    nlp_path = next((path for path in candidate_paths if os.path.exists(path)), None)
    if not nlp_path:
        return [{"error": f"File not found: {filename}"}]

    try:
        with open(nlp_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return [{"error": f"Invalid JSON file: {str(e)}"}]

    resumes = data.get("resumes", {})
    results = []

    # 2. Score Loop
    for res_id, res_data in resumes.items():
        if res_data.get("scoring_ready", False):
            # Use our standardized scoring function
            final_score = score_resume(res_data, backend_metadata)

            # Prepare clean output for Frontend
            results.append({
                "resume_id": res_id,
                "filename": res_data.get("resume_filename", "Unknown"),
                "email": res_data.get("contact_info", {}).get("email", ""),
                "total_score": final_score,
                "details": {
                    "experience_years": res_data.get("experience_years", 0),
                    "skills_match": res_data.get("job_match", {}).get("match_percentage", 0)
                }
            })

    # 3. Sort (High to Low)
    results.sort(key=lambda x: x["total_score"], reverse=True)

    # 4. Assign Ranks
    for i, res in enumerate(results, 1):
        res["rank"] = i

    return results