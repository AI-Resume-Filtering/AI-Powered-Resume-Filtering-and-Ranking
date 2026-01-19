from tech_phrases import TECH_PHRASES

def extract_explicit_skills(tech_zones: dict) -> dict:
    skills = {}

    for lines in tech_zones.values():
        text = " ".join(lines).lower()

        for phrase in TECH_PHRASES:
            if phrase.lower() in text:
                skills[phrase] = skills.get(phrase, 0) + 1

    return skills
