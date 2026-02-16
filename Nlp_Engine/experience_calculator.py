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


# Quick test
if __name__ == "__main__":
    test_text = """
    Java Full Stack Intern - RS-Softtech (2025)
    Secretary - ITSA (2024-25)
    """

    years = calculate_experience_years(test_text)
    print(f"Experience Years: {years}")