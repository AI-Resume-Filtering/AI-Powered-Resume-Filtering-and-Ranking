"""
Text Normalizer
Cleans and standardizes resume text for accurate parsing
"""

import re


def normalize_text(text: str) -> str:
    """
    Clean and standardize text for parsing
    """
    if not text:
        return ""

    # Replace bullets and format characters
    bullet_chars = ["•", "➢", "○", "●", "■", "□", "▪", "▫", "→", "➤", "⦿", "⦾"]
    for bullet in bullet_chars:
        text = text.replace(bullet, "\n")

    # Normalize line endings
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\r', '\n', text)
    text = re.sub(r'\n+', '\n', text)

    # Fix common PDF encoding issues
    encoding_fixes = {
        'â€"': '-', 'â€"': '-', 'â€™': "'", 'â€œ': '"',
        'â€�': '"', 'â€¢': '-', 'Ã¢â‚¬"': '-', 'Ã¢â‚¬â„¢': "'",
    }
    for old, new in encoding_fixes.items():
        text = text.replace(old, new)

    # Normalize spacing and clean lines
    text = re.sub(r'\t', ' ', text)
    text = re.sub(r' +', ' ', text)
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