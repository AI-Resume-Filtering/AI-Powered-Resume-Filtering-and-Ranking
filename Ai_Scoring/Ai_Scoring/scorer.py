import os
from datetime import datetime
from functools import lru_cache

try:
    import joblib
except ImportError:
    joblib = None

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


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _calculate_experience_score(resume: dict, job_reqs: dict) -> float:
    years = float(resume.get("experience_years", 0) or 0)
    req_exp = float(job_reqs.get("minimum_experience", 0) or 0)
    if req_exp <= 0:
        return 100.0 if years > 0 else 80.0
    return _clamp((years / req_exp) * 100.0, 0.0, 100.0)


def _calculate_education_score(resume: dict, job_reqs: dict) -> float:
    req_edu = job_reqs.get("required_education", "bachelors")
    cand_edu = resume.get("education_level", "")
    req_rank = EDUCATION_RANKING.get(parse_education_level(req_edu), 3)
    cand_rank = EDUCATION_RANKING.get(parse_education_level(cand_edu), 0)
    if cand_rank >= req_rank:
        return 100.0
    if req_rank <= 0:
        return 0.0
    return _clamp((cand_rank / req_rank) * 100.0, 0.0, 100.0)


@lru_cache(maxsize=1)
def _load_model_bundle(model_path: str):
    if not joblib or not os.path.exists(model_path):
        return None
    try:
        bundle = joblib.load(model_path)
        if isinstance(bundle, dict) and bundle.get("model") is not None:
            return bundle
    except Exception:
        return None
    return None


def clear_model_cache() -> None:
    _load_model_bundle.cache_clear()


def score_resume(resume_raw: dict, metadata: dict, return_details: bool = False):
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
    model_path = metadata.get("model_path") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "model.pkl"
    )


    semantic_score = float(metadata.get("semantic_score", 0.0) or 0.0)
    semantic_score = _clamp(semantic_score, 0.0, 1.0)
    experience_score = _calculate_experience_score(resume, job_reqs)
    education_score = _calculate_education_score(resume, job_reqs)

    # --- Required Skills Strict Matching ---
    required_skills = set([s.lower() for s in job_reqs.get("required_skills", [])])
    resume_skills = set([s.lower() for s in resume.get("skills", [])])
    matched_skills = required_skills.intersection(resume_skills)
    required_skills_match_pct = (len(matched_skills) / len(required_skills)) * 100 if required_skills else 0

    # Penalize if any required skill is missing
    missing_required = len(matched_skills) < len(required_skills)
    penalty = 0.0
    if missing_required:
        penalty = 30.0  # Cap or subtract from score if required skills missing

    # Adjusted weights: semantic 40%, experience 20%, education 20%, required skills 20%
    blended_score = (
        0.4 * (semantic_score * 100.0) +
        0.2 * experience_score +
        0.2 * education_score +
        0.2 * required_skills_match_pct
    )
    final_score = _clamp(blended_score - penalty, 0.0, 100.0)
    score_source = "blended-strict"

    model_bundle = _load_model_bundle(model_path)
    if model_bundle is not None:
        model = model_bundle.get("model")
        try:
            proba = model.predict_proba([[semantic_score, experience_score, education_score]])
            if len(proba[0]) > 1:
                final_score = _clamp(float(proba[0][1]) * 100.0, 0.0, 100.0)
                score_source = "ml"
        except Exception:
            score_source = "blended"

    details = {
        "semantic_score": round(semantic_score, 6),
        "experience_score": round(experience_score, 4),
        "education_score": round(education_score, 4),
        "blended_score": round(blended_score, 4),
        "score_source": score_source,
        "scored_at": datetime.utcnow().isoformat(),
    }

    if return_details:
        return round(final_score, 4), details
    return round(final_score, 4)


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

        final_score, score_details = score_resume(res_data, backend_metadata, return_details=True)
        results.append({
            "resume_id": res_id,
            "filename": res_data.get("resume_filename", "Unknown"),
            "email": res_data.get("contact_info", {}).get("email", ""),
            "total_score": final_score,
            "details": {
                "experience_years": res_data.get("experience_years", 0),
                "skills_match": res_data.get("job_match", {}).get("match_percentage", 0),
                "semantic_score": score_details.get("semantic_score", 0.0),
                "experience_score": score_details.get("experience_score", 0.0),
                "education_score": score_details.get("education_score", 0.0),
                "blended_score": score_details.get("blended_score", 0.0),
                "score_source": score_details.get("score_source", "blended"),
            }
        })

    results.sort(key=lambda x: (
        -x["total_score"],
        -x["details"]["experience_years"],
    ))
    for i, res in enumerate(results, 1):
        res["rank"] = i

    return results