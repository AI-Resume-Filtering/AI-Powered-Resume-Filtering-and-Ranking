"""
Skill Extractor
Extracts skills using fuzzy matching and synonyms
"""

import re
from difflib import SequenceMatcher
from .skill_database import SKILL_DATABASE
from .config import MIN_CONFIDENCE, USE_FUZZY_MATCHING, FUZZY_THRESHOLD

_WORD_RE = re.compile(r"[a-zA-Z]{2,}")
_LOREM_WORDS = {
    "lorem", "ipsum", "dolor", "sit", "amet", "consectetur", "adipiscing",
    "elit", "sed", "eiusmod", "tempor", "incididunt", "labore", "dolore",
    "magna", "aliqua", "enim", "minim", "veniam",
}


def _looks_placeholder_or_gibberish(text: str) -> bool:
    tokens = [t.lower() for t in _WORD_RE.findall(text)]
    if not tokens:
        return True

    lorem_hits = sum(1 for t in tokens if t in _LOREM_WORDS)
    lorem_ratio = lorem_hits / max(len(tokens), 1)
    unique_ratio = len(set(tokens)) / max(len(tokens), 1)

    if lorem_hits >= 6 and lorem_ratio >= 0.08:
        return True
    if len(tokens) >= 50 and unique_ratio < 0.20:
        return True
    return False


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

    # Hard gate: placeholder/gibberish text should not produce any skill matches.
    if _looks_placeholder_or_gibberish(text_lower):
        return {
            "skills_list": [],
            "skills_by_category": {},
            "skill_details": {}
        }

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
    # Method 1: Exact phrase with boundaries (avoids random substring hits)
    skill_pattern = r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)"
    if re.search(skill_pattern, text):
        return True, 1.0

    # Method 2: Synonym match
    for synonym in synonyms:
        synonym_pattern = r"(?<!\w)" + re.escape(synonym.lower()) + r"(?!\w)"
        if re.search(synonym_pattern, text):
            return True, 0.95

    # Method 3: Fuzzy match (if enabled)
    if USE_FUZZY_MATCHING:
        words = re.findall(r'\b[\w\+#\.\-/]+\b', text)
        for word in words:
            # Avoid fuzzy-matching tiny tokens such as "c" or "r".
            if len(skill) < 4 or len(word) < 4:
                continue
            similarity = SequenceMatcher(None, skill.lower(), word).ratio()
            if similarity >= FUZZY_THRESHOLD:
                return True, round(similarity, 2)

    return False, 0.0


