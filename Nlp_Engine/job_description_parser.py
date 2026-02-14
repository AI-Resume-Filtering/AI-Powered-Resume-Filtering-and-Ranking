"""
Job Description Parser
Extracts requirements from job descriptions

Input: Job description text
Output: {
    "required_skills": [...],
    "preferred_skills": [...],
    "minimum_experience": 2,
    "required_education": "bachelors",
    "job_title": "Full Stack Developer"
}
"""

import re

from .text_normalizer import normalize_text
from .section_detector import detect_sections, get_section_text
from .skill_extractor import extract_skills
from .education_detector import DEGREE_LEVELS


def parse_job_description(jd_text: str) -> dict:
    """
    Parse job description and extract requirements

    Args:
        jd_text: Raw job description text

    Returns:
        {
            "job_title": "Full Stack Developer",
            "required_skills": ["python", "java", "react"],
            "preferred_skills": ["docker", "aws"],
            "minimum_experience": 2,
            "required_education": "bachelors",
            "responsibilities": [...],
            "raw_text": "..."
        }
    """
    # Normalize text
    normalized = normalize_text(jd_text)

    # Detect sections
    sections = detect_sections(normalized)

    # Extract job title
    job_title = _extract_job_title(normalized, sections)

    # Extract skills
    skills_data = _extract_jd_skills(normalized, sections)

    # Extract experience requirement
    min_experience = _extract_experience_requirement(normalized)

    # Extract education requirement
    required_education = _extract_education_requirement(normalized)

    # Extract responsibilities
    responsibilities = _extract_responsibilities(normalized, sections)

    return {
        "job_title": job_title,
        "required_skills": skills_data["required"],
        "preferred_skills": skills_data["preferred"],
        "minimum_experience": min_experience,
        "required_education": required_education,
        "responsibilities": responsibilities,
        "total_requirements": len(skills_data["required"]) + len(skills_data["preferred"])
    }


def _extract_job_title(text: str, sections: dict) -> str:
    """
    Extract job title from JD

    Usually in first few lines or has keywords like:
    - "Position:", "Role:", "Job Title:"
    - "Hiring for", "Looking for"
    """
    lines = text.split('\n')[:5]  # Check first 5 lines

    for line in lines:
        line_lower = line.lower()

        # Check for title patterns
        if any(keyword in line_lower for keyword in ['position', 'role', 'job title', 'hiring for', 'looking for']):
            # Extract title after colon
            if ':' in line:
                title = line.split(':', 1)[1].strip()
                return title

        # If line is short and capitalized, might be title
        if len(line.split()) <= 5 and any(c.isupper() for c in line):
            return line.strip()

    return "Not Specified"


def _extract_jd_skills(text: str, sections: dict) -> dict:
    """
    Extract required and preferred skills

    Looks for keywords:
    - "Required:", "Must have:", "Essential:"
    - "Preferred:", "Nice to have:", "Good to have:"
    """
    # Get skills/requirements section
    skills_text = get_section_text(sections, "skills")
    if not skills_text:
        # Try requirements section
        for key in sections.keys():
            if 'requirement' in key or 'qualification' in key:
                skills_text = get_section_text(sections, key)
                break

    # If still no skills section, use full text
    if not skills_text:
        skills_text = text

    # Extract all skills from text
    all_skills_data = extract_skills(skills_text)
    all_skills = all_skills_data["skills_list"]

    # Separate into required vs preferred
    required_skills = []
    preferred_skills = []

    # Split text into required and preferred sections
    text_lower = skills_text.lower()

    # Find required section
    required_patterns = [
        r'required:?(.+?)(?:preferred|nice to have|good to have|$)',
        r'must have:?(.+?)(?:preferred|nice to have|good to have|$)',
        r'essential:?(.+?)(?:preferred|nice to have|good to have|$)',
        r'mandatory:?(.+?)(?:preferred|nice to have|good to have|$)'
    ]

    required_text = ""
    for pattern in required_patterns:
        match = re.search(pattern, text_lower, re.DOTALL)
        if match:
            required_text = match.group(1)
            break

    # Find preferred section
    preferred_patterns = [
        r'(?:preferred|nice to have|good to have|desirable):?(.+?)$'
    ]

    preferred_text = ""
    for pattern in preferred_patterns:
        match = re.search(pattern, text_lower, re.DOTALL)
        if match:
            preferred_text = match.group(1)
            break

    # Classify skills
    if required_text or preferred_text:
        required_skills_data = extract_skills(required_text)
        preferred_skills_data = extract_skills(preferred_text)

        required_skills = required_skills_data["skills_list"]
        preferred_skills = preferred_skills_data["skills_list"]
    else:
        # No clear separation - treat first 70% as required, rest as preferred
        split_point = int(len(all_skills) * 0.7)
        required_skills = all_skills[:split_point]
        preferred_skills = all_skills[split_point:]

    return {
        "required": required_skills,
        "preferred": preferred_skills
    }


def _extract_experience_requirement(text: str) -> int:
    """
    Extract minimum experience requirement

    Looks for patterns like:
    - "2+ years", "2-5 years", "minimum 2 years"
    - "Experience: 2 years"
    """
    text_lower = text.lower()

    # Pattern 1: "2+ years", "2-5 years"
    pattern1 = r'(\d+)\+?\s*(?:to|-)\s*\d*\s*years?'
    matches = re.findall(pattern1, text_lower)

    if matches:
        return int(matches[0])

    # Pattern 2: "minimum 2 years", "at least 2 years"
    pattern2 = r'(?:minimum|at least|minimum of)\s+(\d+)\s*years?'
    matches = re.findall(pattern2, text_lower)

    if matches:
        return int(matches[0])

    # Pattern 3: "experience: 2 years"
    pattern3 = r'experience:?\s*(\d+)\s*years?'
    matches = re.findall(pattern3, text_lower)

    if matches:
        return int(matches[0])

    return 0  # No experience requirement found


def _extract_education_requirement(text: str) -> str:
    """
    Extract education requirement

    Returns: "phd", "masters", "bachelors", "diploma", "high_school"
    """
    text_lower = text.lower()

    # Check each degree level (highest first)
    for degree_name, degree_info in sorted(
        DEGREE_LEVELS.items(),
        key=lambda x: x[1]["level"],
        reverse=True
    ):
        for pattern in degree_info["patterns"]:
            if re.search(r'\b' + pattern + r'\b', text_lower):
                return degree_name

    return "bachelors"  # Default requirement


def _extract_responsibilities(text: str, sections: dict) -> list:
    """Extract job responsibilities"""
    responsibilities = []

    # Look for responsibilities section
    for key in sections.keys():
        if any(word in key for word in ['responsibilit', 'duties', 'role']):
            resp_lines = sections[key]
            # Take first 5 responsibilities
            responsibilities = resp_lines[:5]
            break

    return responsibilities


# Quick test
if __name__ == "__main__":
    sample_jd = """
    Job Title: Full Stack Developer
    
    Required Skills:
    - Java, Spring Boot
    - React, JavaScript
    - MySQL, MongoDB
    - 3+ years experience
    
    Preferred Skills:
    - Docker, Kubernetes
    - AWS
    
    Education: B.E./B.Tech in Computer Science
    
    Responsibilities:
    - Develop REST APIs
    - Build React frontend
    - Database optimization
    """

    result = parse_job_description(sample_jd)
    print("JOB REQUIREMENTS:")
    print(f"Title: {result['job_title']}")
    print(f"Required Skills: {result['required_skills']}")
    print(f"Preferred Skills: {result['preferred_skills']}")
    print(f"Min Experience: {result['minimum_experience']} years")
    print(f"Education: {result['required_education']}")