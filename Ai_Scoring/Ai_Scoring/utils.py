# Ai_Scoring/utils.py

def normalize_score(value: float, max_value: float) -> float:
    """Safely normalizes a value between 0 and 1."""
    if max_value <= 0:
        return 0.0
    return min(value / max_value, 1.0)


def parse_education_level(edu_string: str) -> str:
    """
    Standardizes education strings to match config keys.
    """
    if not edu_string:
        return "diploma"  # Default fallback

    clean_edu = str(edu_string).lower().strip()

    if "phd" in clean_edu or "doctorate" in clean_edu:
        return "phd"
    elif "master" in clean_edu or "m.tech" in clean_edu or "mba" in clean_edu:
        return "masters"
    elif "bachelor" in clean_edu or "b.tech" in clean_edu or "b.e" in clean_edu or "bsc" in clean_edu:
        return "bachelors"
    elif "diploma" in clean_edu:
        return "diploma"

    return "bachelors"


def standardize_resume_data(resume_data: dict) -> dict:
    """
    Universal Normalizer: Converts different input formats into
    the standard format expected by the Scorer.
    """
    # Create a copy so we don't modify the original data unexpectedly
    standard = resume_data.copy()

    # 1. Handle Experience Variations (e.g., "total_exp", "years_of_experience")
    if "experience_years" not in standard:
        # Tries to find ANY valid key for experience
        exp_val = (
                standard.get("exp") or
                standard.get("total_exp") or
                standard.get("total_experience") or
                standard.get("years_of_experience") or
                0
        )
        # Ensure it's a number (handle string "5 years")
        try:
            standard["experience_years"] = float(str(exp_val).split()[0])
        except (ValueError, AttributeError):
            standard["experience_years"] = 0

    # 2. Handle Skill Variations (String vs List)
    # Convert "python, java, sql" -> ["python", "java", "sql"]
    raw_skills = standard.get("skills", [])
    if isinstance(raw_skills, str):
        standard["skills"] = [s.strip() for s in raw_skills.split(",")]

    # 3. Handle Education Variations
    if "education_level" not in standard:
        standard["education_level"] = (
                standard.get("degree") or
                standard.get("qualification") or
                standard.get("highest_education") or
                "diploma"
        )

    # 4. Handle Job Match Variations
    if "job_match" not in standard:
        # Create a default structure if missing
        standard["job_match"] = {"match_percentage": 0.0}

    return standard