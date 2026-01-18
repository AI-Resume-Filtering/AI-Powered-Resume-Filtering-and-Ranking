# experience_extractor.py

import re

def extract_experience(text: str) -> int:
    matches = re.findall(r'(\d+)\s*\+?\s*years?', text)
    years = [int(m) for m in matches]

    return max(years) if years else 0
