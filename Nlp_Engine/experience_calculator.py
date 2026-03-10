"""
Experience Calculator
Calculates total years of work experience
"""

import re
from datetime import datetime


def calculate_experience_years(text: str) -> int:
    """
    Calculate total years of experience

    Methods:
    1. Look for explicit mentions: "2 years of experience"
    2. Calculate from date ranges: "2023-2025"
    3. Count from earliest year to present

    Args:
        text: Experience section text

    Returns:
        Total years (integer)
    """
    # Method 1: Explicit mentions
    year_pattern = r'(\d+)\s*(?:year|yr)s?'
    matches = re.findall(year_pattern, text.lower())

    if matches:
        return max(map(int, matches))

    # Method 2: Calculate from year ranges
    current_year = datetime.now().year
    year_mentions = re.findall(r'\b(20\d{2})\b', text)

    if year_mentions:
        years = [int(y) for y in year_mentions]
        earliest = min(years)

        # Sanity check: Not more than 50 years ago
        if current_year - earliest < 50:
            return current_year - earliest

    # Method 3: Count positions (fallback)
    # Assume each position = 1 year
    position_keywords = [
        'intern', 'developer', 'engineer', 'analyst',
        'manager', 'consultant', 'specialist'
    ]

    count = 0
    for keyword in position_keywords:
        count += len(re.findall(keyword, text.lower()))

    return min(count, 10)  # Cap at 10 years


def calculate_skill_experience(text: str, skills_list: list) -> dict:
    """
    Calculate experience per skill

    Returns:
        {"python": 2.0, "java": 1.5, "react": 0.5}  # in years
    """
    skill_experience = {}
    text_lower = text.lower()

    for skill in skills_list:
        skill_lower = skill.lower()
        years = 0.0

        # Method 1: Explicit mention - "Python (2 years)" or "Python - 3 years"
        patterns = [
            rf'{skill_lower}\s*[\(\-:]\s*(\d+\.?\d*)\s*(?:year|yr)s?',
            rf'(\d+\.?\d*)\s*(?:year|yr)s?\s+(?:of\s+)?{skill_lower}',
            rf'{skill_lower}.*?(\d+\.?\d*)\s*(?:year|yr)s?',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text_lower)
            if matches:
                years = max(float(m) for m in matches)
                break

        # Method 2: Month patterns - "Python (6 months)"
        if years == 0:
            month_patterns = [
                rf'{skill_lower}\s*[\(\-:]\s*(\d+)\s*months?',
                rf'(\d+)\s*months?\s+(?:of\s+)?{skill_lower}',
            ]

            for pattern in month_patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    years = max(int(m) / 12.0 for m in matches)
                    break

        # Method 3: Estimate from job dates (if skill mentioned in experience)
        if years == 0 and skill_lower in text_lower:
            # Find all year ranges in text
            date_ranges = re.findall(r'(\d{4})\s*[-–]\s*(\d{4}|present|current)', text_lower)

            if date_ranges:
                # Check if skill is near any date range (within 200 chars)
                skill_positions = [m.start() for m in re.finditer(skill_lower, text_lower)]

                for start_year, end_year in date_ranges:
                    # Calculate years
                    start = int(start_year)
                    end = datetime.now().year if end_year in ['present', 'current'] else int(end_year)
                    duration = end - start

                    # Use this duration if skill is mentioned
                    if duration > 0:
                        years = max(years, duration)

        if years > 0:
            skill_experience[skill] = round(years, 1)

    return skill_experience

# Quick test
if __name__ == "__main__":
    test_text = """
    Java Full Stack Intern - RS-Softtech (2025)
    Secretary - ITSA (2024-25)
    """

    years = calculate_experience_years(test_text)
    print(f"Experience Years: {years}")