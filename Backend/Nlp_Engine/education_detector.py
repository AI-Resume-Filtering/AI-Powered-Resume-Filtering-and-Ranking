"""
Education Detector
Detects highest education level
"""

import re


# Degree hierarchy
DEGREE_LEVELS = {
    "phd": {
        "patterns": ["phd", "ph.d", "doctorate", "doctoral"],
        "level": 5
    },
    "masters": {
        "patterns": ["master", "msc", "m.sc", "mtech", "m.tech", "mba", "m.b.a", "me", "m.e"],
        "level": 4
    },
    "bachelors": {
        "patterns": ["bachelor", "bsc", "b.sc", "btech", "b.tech", "be", "b.e", "ba", "b.a"],
        "level": 3
    },
    "diploma": {
        "patterns": ["diploma"],
        "level": 2
    },
    "high_school": {
        "patterns": ["hsc", "12th", "ssc", "10th"],
        "level": 1
    }
}


def detect_education_level(text: str) -> str:
    """
    Detect highest education level

    Args:
        text: Education section text

    Returns:
        "phd" | "masters" | "bachelors" | "diploma" | "high_school" | "unknown"
    """
    text_lower = text.lower()
    highest_degree = None
    highest_level = 0

    for degree_name, degree_info in DEGREE_LEVELS.items():
        for pattern in degree_info["patterns"]:
            if pattern in text_lower:
                if degree_info["level"] > highest_level:
                    highest_level = degree_info["level"]
                    highest_degree = degree_name
                break

    return highest_degree if highest_degree else "unknown"


# Quick test
if __name__ == "__main__":
    test_text = """
    B.E. Information Technology - 69.10%
    Mauli College of Engineering (2026)
    """

    level = detect_education_level(test_text)
    print(f"Education Level: {level}")