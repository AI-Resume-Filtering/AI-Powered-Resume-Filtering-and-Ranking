"""
Text Normalizer
Cleans and standardizes resume text for accurate parsing
"""

import re


def normalize_text(text: str) -> str:
    """
    Normalize resume text

    Steps:
    1. Replace bullets with newlines
    2. Fix encoding issues
    3. Normalize whitespace
    4. Remove extra line breaks

    Args:
        text: Raw resume text

    Returns:
        Cleaned, normalized text
    """
    if not text:
        return ""

    # Step 1: Replace all bullet types with newlines
    bullet_chars = ["•", "➢", "○", "●", "■", "□", "▪", "▫", "→", "➤", "⦿", "⦾"]
    for bullet in bullet_chars:
        text = text.replace(bullet, "\n")

    # Step 2: Fix line endings
    text = re.sub(r'\r\n', '\n', text)  # Windows → Unix
    text = re.sub(r'\r', '\n', text)     # Old Mac → Unix
    text = re.sub(r'\n+', '\n', text)    # Multiple → Single

    # Step 3: Fix encoding issues (PDF artifacts)
    encoding_fixes = {
        'â€"': '-',   # Em dash
        'â€"': '-',   # En dash
        'â€™': "'",   # Apostrophe
        'â€œ': '"',   # Opening quote
        'â€�': '"',   # Closing quote
        'â€¢': '-',   # Bullet
        'Ã¢â‚¬"': '-',
        'Ã¢â‚¬â„¢': "'",
    }
    for old, new in encoding_fixes.items():
        text = text.replace(old, new)

    # Step 4: Normalize whitespace
    text = re.sub(r'\t', ' ', text)     # Tabs → Spaces
    text = re.sub(r' +', ' ', text)     # Multiple spaces → Single

    # Step 5: Clean up lines
    lines = text.split('\n')
    cleaned_lines = [line.strip() for line in lines if line.strip()]

    return '\n'.join(cleaned_lines)


# Quick test
if __name__ == "__main__":
    messy_text = """
    SKILLS
    •Python  •Java    •Machine Learning
    
    Experience â€" 2 years
    """

    clean = normalize_text(messy_text)
    print("CLEANED TEXT:")
    print(clean)