from text_normalizer import normalize_text
from section_detector import detect_sections
from zone_classifier import classify_zones
from skill_extractor import extract_explicit_skills
from skill_inference import infer_skills
from project_parser import parse_projects
from experience_parser import parse_experience

def process_resume_nlp(text: str) -> dict:
    text = normalize_text(text)
    sections = detect_sections(text)
    zones = classify_zones(sections)

    explicit_skills = extract_explicit_skills(zones["tech_zones"])
    inferred_skills = infer_skills(zones["context_zones"], explicit_skills)

    return {
        "explicit_skills": explicit_skills,
        "inferred_skills": inferred_skills,
        "projects": parse_projects(sections.get("projects", [])),
        "experience_years": parse_experience(text)
    }
