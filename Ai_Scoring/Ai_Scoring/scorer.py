import os

try:
    from .config import SCORING_PROFILES, EDUCATION_RANKING, EXP_THRESHOLDS
    from .utils import parse_education_level, standardize_resume_data
except ImportError:
    from config import SCORING_PROFILES, EDUCATION_RANKING, EXP_THRESHOLDS
    from utils import parse_education_level, standardize_resume_data


def get_adaptive_weights(job_reqs: dict) -> dict:
    req_exp = job_reqs.get("minimum_experience", 0)
    if req_exp == 0:
        return SCORING_PROFILES["FRESHER"]
    elif req_exp >= EXP_THRESHOLDS["senior_level"]:
        return SCORING_PROFILES["SENIOR"]
    else:
        return SCORING_PROFILES["MID_LEVEL"]


def score_resume(resume_raw: dict, metadata: dict) -> float:
    """
    Calculate weighted score for a single resume.

    Metrics:
      1. Skill Match      — required skills present vs total required
      2. Total Experience — candidate years vs minimum required
      3. Education        — candidate level vs required level
      4. Preferred Skills — bonus for nice-to-have skills
      5. Skill Experience — years of documented experience IN required skills
                            (produces real score gaps between candidates who merely
                             list a skill vs those who have worked with it)
    """
    resume = standardize_resume_data(resume_raw)
    job_reqs = metadata.get("job_requirements", metadata)
    weights = get_adaptive_weights(job_reqs)

    # --- METRIC 1: Skill Match ---
    match_pct = resume.get("job_match", {}).get("match_percentage", 0)
    skill_score = (match_pct / 100) * weights["skill_match"]

    # --- METRIC 2: Total Experience ---
    years = resume.get("experience_years", 0)
    req_exp = job_reqs.get("minimum_experience", 0)
    exp_ratio = 1.0 if req_exp == 0 else min(years / req_exp, 1.5)
    exp_score = min(exp_ratio * weights["experience"], weights["experience"])

    # --- METRIC 3: Education ---
    req_edu = job_reqs.get("required_education", "bachelors")
    cand_edu = resume.get("education_level", "")
    req_rank = EDUCATION_RANKING.get(parse_education_level(req_edu), 3)
    cand_rank = EDUCATION_RANKING.get(parse_education_level(cand_edu), 0)
    edu_score = weights["education"] if cand_rank >= req_rank else 0

    # --- METRIC 4: Preferred Skills ---
    pref_list = [s.lower() for s in job_reqs.get("preferred_skills", [])]
    cand_skills = [s.lower() for s in resume.get("skills", [])]
    matched_pref = set(pref_list) & set(cand_skills)
    pref_score = min(len(matched_pref) * 2, weights["preferred_skills"])

    # --- METRIC 5: Skill-wise Experience Bonus ---
    # Rewards candidates with documented years of experience in required skills.
    # Max 5 points — creates meaningful separation beyond simple skill presence.
    skill_experience = resume.get("skill_experience", {})
    required_skills = [s.lower() for s in job_reqs.get("required_skills", [])]
    skill_exp_bonus = 0.0

    if skill_experience and required_skills:
        matched_exp_years = sum(
            v for k, v in skill_experience.items()
            if k.lower() in required_skills
        )
        # Normalize against expected total skill-years
        expected = max(req_exp, 1) * max(len(required_skills), 1)
        skill_exp_bonus = min(matched_exp_years / expected, 1.0) * 5.0

    final_score = skill_score + exp_score + edu_score + pref_score + skill_exp_bonus
    # L12: The skill_exp_bonus is an extra up-to-5-point reward on top of the
    # 100-point base. Cap the total at 100 so the score remains on a consistent
    # 0-100 scale and SCORE_THRESHOLD comparisons stay meaningful.
    return round(min(final_score, 100.0), 4)


def process_resume_batch(filename: str, backend_metadata: dict) -> list:
    """
    Backend integration entry point.
    Reads a single NLP output JSON file, scores every resume inside it,
    and returns a ranked list ready for the API response.
    """
    import json

    current_dir = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(current_dir))

    candidate_paths = []
    if os.path.isabs(filename):
        candidate_paths.append(filename)
    candidate_paths.append(os.path.join(repo_root, "Nlp_Engine", "output", filename))
    candidate_paths.append(os.path.join(repo_root, filename))

    nlp_path = next((p for p in candidate_paths if os.path.exists(p)), None)
    if not nlp_path:
        return [{"error": f"File not found: {filename}"}]

    try:
        with open(nlp_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return [{"error": f"Invalid JSON file: {str(e)}"}]

    resumes = data.get("resumes", {})
    results = []

    for res_id, res_data in resumes.items():
        if not res_data.get("scoring_ready", False):
            continue

        final_score = score_resume(res_data, backend_metadata)
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

    results.sort(key=lambda x: (
        -x["total_score"],
        -x["details"]["experience_years"],
    ))
    for i, res in enumerate(results, 1):
        res["rank"] = i

    return results