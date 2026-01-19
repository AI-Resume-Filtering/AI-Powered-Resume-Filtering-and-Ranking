TECH_ZONES = {"technical_skills", "projects"}
CONTEXT_ZONES = {"summary", "experience"}

def classify_zones(sections: dict) -> dict:
    return {
        "tech_zones": {k: v for k, v in sections.items() if k in TECH_ZONES},
        "context_zones": {k: v for k, v in sections.items() if k in CONTEXT_ZONES}
    }
