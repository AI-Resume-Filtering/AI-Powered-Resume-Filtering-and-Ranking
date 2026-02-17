"""
Output Formatter
Formats extracted data for AI scoring
"""

from typing import Dict


def format_resume_data(
    resume_id: str,
    filename: str,
    contact_info: dict,
    skills_data: dict,
    experience_years: int,
    education_level: str,
    job_requirements: dict
) -> dict:
    """
    Format extracted data into scoring-ready structure
    """

    # Calculate job match
    job_match = calculate_job_match(
        skills_data,
        experience_years,
        education_level,
        job_requirements
    )

    return {
        "resume_filename": filename,
        "sequential_id": resume_id.split('_')[-1],

        "contact_info": contact_info,

        "skills": skills_data["skills_list"],

        "skill_categories": skills_data["skills_by_category"],

        "experience_years": experience_years,

        "education_level": education_level,

        "job_match": job_match,

        "scoring_ready": True
    }


def calculate_job_match(
    skills_data: dict,
    experience_years: int,
    education_level: str,
    job_requirements: dict
) -> dict:
    """
    Calculate match with job requirements

    Returns:
        {
            "meets_requirements": True/False,
            "matched_required_skills": ["python", "java"],
            "matched_preferred_skills": ["docker"],
            "missing_required_skills": [],
            "match_percentage": 100.0,
            "experience_match": True,
            "education_match": True
        }
    """
    candidate_skills = set([s.lower() for s in skills_data["skills_list"]])
    required_skills = set([s.lower() for s in job_requirements.get("required_skills", [])])
    preferred_skills = set([s.lower() for s in job_requirements.get("preferred_skills", [])])

    # Match required skills
    matched_required = candidate_skills.intersection(required_skills)
    missing_required = required_skills - candidate_skills

    # Match preferred skills
    matched_preferred = candidate_skills.intersection(preferred_skills)

    # Calculate match percentage (based on required skills only)
    if required_skills:
        match_percentage = (len(matched_required) / len(required_skills)) * 100
    else:
        match_percentage = 100.0

    # Check experience match
    min_experience = job_requirements.get("minimum_experience", 0)
    experience_match = experience_years >= min_experience

    # Check education match
    required_education = job_requirements.get("required_education", "high_school")
    education_levels = {
        "phd": 5, "masters": 4, "bachelors": 3,
        "diploma": 2, "high_school": 1, "unknown": 0
    }
    candidate_edu_level = education_levels.get(education_level, 0)
    required_edu_level = education_levels.get(required_education, 0)
    education_match = candidate_edu_level >= required_edu_level

    # Overall qualification
    meets_requirements = (
        len(missing_required) == 0 and  # All required skills present
        experience_match and
        education_match
    )

    return {
        "meets_requirements": meets_requirements,
        "matched_required_skills": list(matched_required),
        "matched_preferred_skills": list(matched_preferred),
        "missing_required_skills": list(missing_required),
        "match_percentage": round(match_percentage, 2),
        "experience_match": experience_match,
        "education_match": education_match
    }


def format_error_resume(resume_id: str, filename: str, error_message: str) -> dict:
    """Format failed resume with error"""
    return {
        "resume_filename": filename,
        "sequential_id": resume_id.split('_')[-1],
        "error": error_message,
        "skills": [],
        "skill_categories": {},
        "experience_years": 0,
        "education_level": "unknown",
        "job_match": {
            "meets_requirements": False,
            "matched_required_skills": [],
            "matched_preferred_skills": [],
            "missing_required_skills": [],
            "match_percentage": 0.0,
            "experience_match": False,
            "education_match": False
        },
        "scoring_ready": False
    }