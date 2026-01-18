# nlp_pipeline.py

from text_preprocessor import preprocess_text
from section_detector import detect_sections
from project_extractor import extract_project_metrics
from certification_extractor import extract_certifications
from publication_extractor import extract_publications
from skill_extractor import extract_skills
from experience_extractor import extract_experience


def process_resume_nlp(text: str) -> dict:
    clean_text = text.lower()
    sections = detect_sections(text)

    skills = extract_skills(" ".join(sections["technical_skills"]).split())
    experience = extract_experience(text)

    projects = extract_project_metrics(sections["projects"])
    certifications = extract_certifications(sections["certifications"])
    publications = extract_publications(sections["publications"])

    return {
        "technical_skills": skills,
        "experience_years": experience,
        "projects": projects,
        "certifications": certifications,
        "publications": publications
    }
