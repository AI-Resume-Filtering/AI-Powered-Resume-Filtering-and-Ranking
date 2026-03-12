import os
import json

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
    resume = standardize_resume_data(resume_raw)
    job_reqs = metadata.get("job_requirements", metadata)
    weights = get_adaptive_weights(job_reqs)

    match_pct = resume.get("job_match", {}).get("match_percentage", 0)
    skill_score = (match_pct / 100) * weights["skill_match"]

    years = resume.get("experience_years", 0)
    req_exp = job_reqs.get("minimum_experience", 0)
    exp_ratio = 1.0 if req_exp == 0 else min(years / req_exp, 1.5)
    exp_score = min(exp_ratio * weights["experience"], weights["experience"])

    req_edu = job_reqs.get("required_education", "bachelors")
    cand_edu = resume.get("education_level", "")
    req_rank = EDUCATION_RANKING.get(parse_education_level(req_edu), 3)
    cand_rank = EDUCATION_RANKING.get(parse_education_level(cand_edu), 0)
    edu_score = weights["education"] if cand_rank >= req_rank else 0

    pref_list = job_reqs.get("preferred_skills", [])
    cand_skills = resume.get("skills", [])
    matched_pref = set(pref_list) & set(cand_skills)
    pref_score = min(len(matched_pref) * 2, weights["preferred_skills"])

    skill_count_bonus = len(cand_skills) * 0.001
    project_bonus = resume.get("projects_count", 0) * 0.005
    exp_micro_bonus = years * 0.0001

    micro_bonus = skill_count_bonus + project_bonus + exp_micro_bonus
    final_score = skill_score + exp_score + edu_score + pref_score + micro_bonus
    return round(final_score, 4)