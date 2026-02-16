"""
Skill Extractor
Extracts skills using fuzzy matching and synonyms
"""

import re
from difflib import SequenceMatcher
from .skill_database import SKILL_DATABASE
from .config import MIN_CONFIDENCE, USE_FUZZY_MATCHING, FUZZY_THRESHOLD


def extract_skills(text: str) -> dict:
    """
    Extract all skills from text

    Args:
        text: Resume text (skills section + projects)

    Returns:
        {
            "skills_list": ["python", "java", "machine learning"],
            "skills_by_category": {
                "programming_language": 2,
                "ai_ml": 1
            },
            "skill_details": {
                "python": {"confidence": 0.95, "category": "programming_language"}
            }
        }
    """
    text_lower = text.lower()
    found_skills = {}

    # Check each skill in database
    for skill_name, skill_data in SKILL_DATABASE.items():
        matched, confidence = _match_skill(
            text_lower,
            skill_name,
            skill_data["synonyms"]
        )

        if matched and confidence >= MIN_CONFIDENCE:
            found_skills[skill_name] = {
                "confidence": confidence,
                "category": skill_data["category"]
            }

    # Categorize skills
    skills_by_category = {}
    for skill_name, skill_info in found_skills.items():
        category = skill_info["category"]
        skills_by_category[category] = skills_by_category.get(category, 0) + 1

    return {
        "skills_list": list(found_skills.keys()),
        "skills_by_category": skills_by_category,
        "skill_details": found_skills
    }


def _match_skill(text: str, skill: str, synonyms: list) -> tuple:
    """
    Match skill using multiple methods

    Returns:
        (matched: bool, confidence: float)
    """
    # Method 1: Exact match
    if skill.lower() in text:
        return True, 1.0

    # Method 2: Synonym match
    for synonym in synonyms:
        if synonym.lower() in text:
            return True, 0.95

    # Method 3: Fuzzy match (if enabled)
    if USE_FUZZY_MATCHING:
        words = re.findall(r'\b\w+\b', text)
        for word in words:
            similarity = SequenceMatcher(None, skill.lower(), word).ratio()
            if similarity >= FUZZY_THRESHOLD:
                return True, round(similarity, 2)

    return False, 0.0


# Quick test
if __name__ == "__main__":
    test_text = """
    Programming Languages: Java, Python, C++
    AI/ML: Machine Learning, NLP, OpenCV
    Databases: MySQL, MongoDB
    """

    result = extract_skills(test_text)
    print(f"Skills Found: {result['skills_list']}")
    print(f"\nBy Category: {result['skills_by_category']}")