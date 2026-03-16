"""
Experience Calculator
Calculates total years of work experience
"""

import re
from datetime import datetime


def calculate_experience_years(text: str) -> int:
    """
    Calculate total years of work experience.

    Methods (in priority order):
    1. Sum explicit date ranges: "2020-2023", "Jan 2022 - Present"
    2. Sum explicit year mentions per position: "2 years at X", "3 years at Y"  -> 5
    3. Count recognised job-title keywords as a last-resort fallback (1 yr each)

    L9 fix: SUM ranges/mentions instead of taking max.
    L10 fix: Use actual (end - start) arithmetic per range, not (now - earliest).
    """
    current_year = datetime.now().year
    text_lower = text.lower()

    # Method 1: Detect and SUM all date ranges in the experience section
    # Handles: "2020-2023", "2020 - present", "2020–2023"
    range_pattern = r'\b(20\d{2})\s*[-\u2013to]+\s*(20\d{2}|present|current|now)\b'
    ranges = re.findall(range_pattern, text_lower)
    if ranges:
        total = 0
        for start_str, end_str in ranges:
            start = int(start_str)
            end = current_year if end_str in ('present', 'current', 'now') else int(end_str)
            duration = end - start
            # Sanity: only count positive durations under 20 years per job
            if 0 < duration <= 20:
                total += duration
        if total > 0:
            return min(total, 40)  # hard cap at 40 years

    # Method 2: Sum all explicit "N year(s)" mentions (likely separate positions)
    year_pattern = r'(\d+)\s*\+?\s*(?:year|yr)s?'
    matches = re.findall(year_pattern, text_lower)
    if matches:
        return min(sum(int(m) for m in matches), 40)

    # Method 3: Count recognised job-title keywords as a fallback (1 year each)
    position_keywords = [
        'intern', 'developer', 'engineer', 'analyst',
        'manager', 'consultant', 'specialist',
    ]
    count = sum(len(re.findall(kw, text_lower)) for kw in position_keywords)
    return min(count, 10)


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