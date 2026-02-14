"""
Section Detector
Finds resume sections using pattern matching
"""

import re


# Section header patterns
SECTION_PATTERNS = {
    "skills": [
        r"technical\s+skills",
        r"skills",
        r"core\s+competencies",
        r"technologies",
        r"technical\s+competencies"
    ],
    "experience": [
        r"experience",
        r"work\s+experience",
        r"professional\s+experience",
        r"employment",
        r"internship",
        r"internship\s+and\s+achievements"
    ],
    "education": [
        r"education",
        r"academic\s+background",
        r"qualifications",
        r"educational\s+qualification"
    ],
    "projects": [
        r"projects",
        r"key\s+projects",
        r"academic\s+projects"
    ],
    "summary": [
        r"professional\s+summary",
        r"summary",
        r"profile",
        r"objective"
    ]
}


def detect_sections(text: str) -> dict:
    """
    Detect and extract sections from resume

    Args:
        text: Normalized resume text

    Returns:
        {
            "skills": ["Python, Java, Machine Learning"],
            "experience": ["Software Intern - 2 years"],
            "education": ["B.E. Information Technology"],
            "projects": ["Smart Attendance Tracker"],
            "unknown": ["Header content"]
        }
    """
    sections = {}
    current_section = "unknown"
    sections[current_section] = []

    lines = text.split('\n')

    for line in lines:
        clean_line = line.strip()
        if not clean_line:
            continue

        clean_lower = clean_line.lower()
        matched = False

        # Try to match section headers
        for section_name, patterns in SECTION_PATTERNS.items():
            for pattern in patterns:
                # Flexible regex matching
                if re.search(f'^{pattern}:?$', clean_lower):
                    current_section = section_name
                    if current_section not in sections:
                        sections[current_section] = []
                    matched = True
                    break
            if matched:
                break

        # Add line to current section
        if not matched:
            sections[current_section].append(clean_line)

    return sections


def get_section_text(sections: dict, section_name: str) -> str:
    """Get combined text from a section"""
    return '\n'.join(sections.get(section_name, []))


# Quick test
if __name__ == "__main__":
    test_text = """
    MAHESH NIKAS
    
    TECHNICAL SKILLS
    Python, Java, Machine Learning
    
    EXPERIENCE
    Software Intern - 2025
    """

    sections = detect_sections(test_text)
    for section, content in sections.items():
        print(f"\n[{section.upper()}]")
        for line in content:
            print(f"  {line}")