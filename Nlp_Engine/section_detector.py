SECTION_HEADERS = {
    "summary": ["professional summary", "summary"],
    "technical_skills": ["technical skills"],
    "projects": ["projects"],
    "experience": ["experience", "internship"],
    "education": ["education"],
    "certifications": ["certifications"],
    "achievements": ["achievements"],
    "behavioural": ["behavioural skills"]
}

def detect_sections(text: str) -> dict:
    sections = {}
    current_section = "unknown"
    sections[current_section] = []

    for line in text.split("\n"):
        clean = line.strip().lower()

        matched = False
        for section, keywords in SECTION_HEADERS.items():
            if clean in keywords:
                current_section = section
                sections[current_section] = []
                matched = True
                break

        if not matched and line.strip():
            sections[current_section].append(line.strip())

    return sections
