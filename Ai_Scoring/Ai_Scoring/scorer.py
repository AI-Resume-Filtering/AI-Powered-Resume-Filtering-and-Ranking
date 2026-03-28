import os
import re
from datetime import datetime
from difflib import SequenceMatcher

try:
    from .config import SCORING_PROFILES, EDUCATION_RANKING, EXP_THRESHOLDS
    from .utils import parse_education_level, standardize_resume_data
except ImportError:
    from config import SCORING_PROFILES, EDUCATION_RANKING, EXP_THRESHOLDS
    from utils import parse_education_level, standardize_resume_data

try:
    from Nlp_Engine.skill_database import SKILL_DATABASE
except Exception:
    SKILL_DATABASE = {}


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


def _normalize_skill_token(skill: str) -> str:
    token = (skill or "").strip().lower()
    token = token.replace("+", " plus ")
    token = token.replace("#", " sharp ")
    token = re.sub(r"[^a-z0-9]+", " ", token)
    token = re.sub(r"\s+", " ", token).strip()
    return token


def _build_skill_alias_map() -> dict:
    alias_map = {}
    for canonical, meta in SKILL_DATABASE.items():
        canonical_norm = _normalize_skill_token(canonical)
        if canonical_norm:
            alias_map[canonical_norm] = canonical_norm
        for syn in meta.get("synonyms", []):
            syn_norm = _normalize_skill_token(syn)
            if syn_norm:
                alias_map[syn_norm] = canonical_norm
    return alias_map


_SKILL_ALIAS_MAP = _build_skill_alias_map()


def _canonical_skill(skill: str) -> str:
    norm = _normalize_skill_token(skill)
    if not norm:
        return ""
    return _SKILL_ALIAS_MAP.get(norm, norm)


def _skill_similarity(required_skill: str, resume_skill: str) -> float:
    req = _canonical_skill(required_skill)
    res = _canonical_skill(resume_skill)
    if not req or not res:
        return 0.0
    if req == res:
        return 1.0
    # Fuzzy tolerance for near-equivalent surface forms not covered in synonyms
    ratio = SequenceMatcher(None, req, res).ratio()
    if ratio >= 0.90:
        return 0.90
    if ratio >= 0.84:
        return 0.75
    return 0.0


def _required_skill_match_stats(required_skills: list, resume_skills: list) -> tuple[float, int, int]:
    """
    Returns:
      required_match_pct (0-100), matched_required_count, missing_required_count
    """
    req = [s for s in required_skills if (s or "").strip()]
    cand = [s for s in resume_skills if (s or "").strip()]
    if not req:
        return 100.0, 0, 0

    total_similarity = 0.0
    matched = 0
    missing = 0

    for required in req:
        best = 0.0
        for candidate in cand:
            score = _skill_similarity(required, candidate)
            if score > best:
                best = score
            if best >= 1.0:
                break
        total_similarity += best
        if best >= 0.75:
            matched += 1
        if best < 0.50:
            missing += 1

    required_match_pct = (total_similarity / len(req)) * 100.0
    return _clamp(required_match_pct, 0.0, 100.0), matched, missing


def _apply_low_signal_guard(
    final_score: float,
    *,
    semantic_score: float,
    required_match_pct: float,
    matched_required_count: int,
    resume_skill_count: int,
) -> tuple[float, str]:
    """
    Prevent placeholder or meaningless resumes from receiving high scores.
    Returns (guarded_score, guard_reason).
    """
    guard_reason = ""
    guarded = final_score

    if semantic_score < 0.25 and matched_required_count == 0:
        guarded = 0.0
        guard_reason = "force-zero-very-low-semantic-no-required-match"
    elif semantic_score < 0.35 and required_match_pct <= 20.0 and resume_skill_count <= 2:
        guarded = 0.0
        guard_reason = "force-zero-low-signal-profile"
    elif semantic_score < 0.30 and required_match_pct < 20.0:
        guarded = min(guarded, 20.0)
        guard_reason = "low-semantic-and-low-skill-match"
    elif resume_skill_count <= 2 and required_match_pct < 15.0:
        guarded = min(guarded, 25.0)
        guard_reason = "insufficient-skill-signal"

    return guarded, guard_reason


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


def clear_model_cache() -> None:
    """Kept for backward compatibility; scoring is now deterministic."""
    return None


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
    # Important: score ONLY from resume-vs-JD signals.
    # No historical model, no cross-candidate comparison.
    semantic_score = float(metadata.get("semantic_score", 0.0) or 0.0)
    semantic_score = _clamp(semantic_score, 0.0, 1.0)
    experience_score = _calculate_experience_score(resume, job_reqs)
    education_score = _calculate_education_score(resume, job_reqs)

    # --- Required Skills Strict Matching ---
    required_skills = list(job_reqs.get("required_skills", []))
    resume_skills = list(resume.get("skills", []))
    required_skills_match_pct, matched_required_count, missing_required_count = _required_skill_match_stats(
        required_skills,
        resume_skills,
    )

    total_required = len([s for s in required_skills if (s or "").strip()])

    # Weighted JD-vs-resume score.
    # Favor semantic + required skill match while still considering exp/education from JD.
    blended_score = (
        0.60 * (semantic_score * 100.0) +
        0.25 * required_skills_match_pct +
        0.10 * experience_score +
        0.05 * education_score
    )

    # Proportional penalty avoids over-punishing near-matches.
    # Example: missing 1/10 skills applies far less penalty than missing 7/10.
    penalty = 0.0
    if total_required > 0 and missing_required_count > 0:
        penalty = min(6.0, (missing_required_count / total_required) * 6.0)

    final_score = _clamp(blended_score - penalty, 0.0, 100.0)
    score_source = "jd-only-blended"

    final_score, low_signal_guard = _apply_low_signal_guard(
        final_score,
        semantic_score=semantic_score,
        required_match_pct=required_skills_match_pct,
        matched_required_count=matched_required_count,
        resume_skill_count=len([s for s in resume_skills if (s or "").strip()]),
    )
    if low_signal_guard:
        score_source = "jd-only-blended-guarded"
        # Ensure low-signal resumes do not report misleading partial matches.
        if low_signal_guard.startswith("force-zero"):
            required_skills_match_pct = 0.0
            matched_required_count = 0
            missing_required_count = total_required

    details = {
        "semantic_score": round(semantic_score, 6),
        "experience_score": round(experience_score, 4),
        "education_score": round(education_score, 4),
        "required_skills_match_pct": round(required_skills_match_pct, 4),
        "matched_required_skills": matched_required_count,
        "total_required_skills": total_required,
        "missing_required_skills": missing_required_count,
        "penalty": round(penalty, 4),
        "blended_score": round(blended_score, 4),
        "low_signal_guard": low_signal_guard,
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
        displayed_skill_match = res_data.get("job_match", {}).get("match_percentage", 0)
        if score_details.get("low_signal_guard", "").startswith("force-zero"):
            displayed_skill_match = 0.0
        results.append({
            "resume_id": res_id,
            "filename": res_data.get("resume_filename", "Unknown"),
            "email": res_data.get("contact_info", {}).get("email", ""),
            "total_score": final_score,
            "details": {
                "experience_years": res_data.get("experience_years", 0),
                "skills_match": displayed_skill_match,
                "semantic_score": score_details.get("semantic_score", 0.0),
                "experience_score": score_details.get("experience_score", 0.0),
                "education_score": score_details.get("education_score", 0.0),
                "required_skills_match_pct": score_details.get("required_skills_match_pct", 0.0),
                "matched_required_skills": score_details.get("matched_required_skills", 0),
                "total_required_skills": score_details.get("total_required_skills", 0),
                "missing_required_skills": score_details.get("missing_required_skills", 0),
                "penalty": score_details.get("penalty", 0.0),
                "blended_score": score_details.get("blended_score", 0.0),
                "low_signal_guard": score_details.get("low_signal_guard", ""),
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