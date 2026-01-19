INFERENCE_RULES = {
    "nlp": ["machine learning"],
    "artificial intelligence": ["machine learning"],
    "ai-powered": ["artificial intelligence"],
    "face recognition": ["computer vision"],
    "backend": ["backend development"]
}

def infer_skills(context_zones: dict, explicit_skills: dict) -> dict:
    inferred = {}
    text = " ".join(
        " ".join(lines) for lines in context_zones.values()
    ).lower()

    for trigger, inferred_list in INFERENCE_RULES.items():
        if trigger in text:
            for skill in inferred_list:
                if skill not in explicit_skills:
                    inferred[skill] = "medium"

    return inferred
