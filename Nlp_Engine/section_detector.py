# section_detector.py

from constants import SECTION_KEYWORDS

def is_heading(line: str):
    clean = line.strip().lower()

    if len(clean) > 40:
        return None
    if "." in clean:
        return None

    for section, keywords in SECTION_KEYWORDS.items():
        for kw in keywords:
            if clean == kw:
                return section
    return None


def detect_sections(text: str) -> dict:
    sections = {key: [] for key in SECTION_KEYWORDS}
    current_section = None

    lines = text.split("\n")

    for line in lines:
        heading = is_heading(line)

        if heading:
            current_section = heading
            continue

        if current_section and line.strip():
            sections[current_section].append(line.strip())

    return sections
