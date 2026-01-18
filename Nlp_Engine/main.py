# main.py

from text_preprocessor import preprocess_text
from section_detector import detect_sections
from skill_extractor import extract_skills
from experience_extractor import extract_experience
from nlp_pipeline import process_resume_nlp

def process_resume(text: str) -> dict:
    words = preprocess_text(text)
    sections = detect_sections(words)

    skills = extract_skills(sections.get("technical_skills", []))
    experience = extract_experience(text)

    return {
        "technical_skills": skills,
        "experience_years": experience
    }


if __name__ == "__main__":
    sample_resume = """
    CAREER OBJECTIVE
    I am best in technical skills and problem solving.

    TECHNICAL SKILLS
    Java Spring Docker LangChain

    EXPERIENCE
    Worked as Backend Engineer for 3 years

    PROJECTS
     AI Resume System
     # Accuracy: 80%
     E-Commerce Backend
     Business Impact: 50%

    CERTIFICATIONS
    AWS Certified Developer
    Udemy Machine Learning Course

    PUBLICATIONS
    Resume Ranking using NLP
    """

    result = process_resume_nlp(sample_resume)
    print(result)
