import re

def parse_experience(text: str) -> int:
    matches = re.findall(r'(\d+)\s*years?', text.lower())
    return max(map(int, matches)) if matches else 0
