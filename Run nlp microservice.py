"""
Run NLP Engine in Microservice Mode
Simple script to test microservice functionality
"""

import os
from Nlp_Engine import process_resumes
# ============================================
# CONFIGURATION
# ============================================

# Set your paths here
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# JD path (change this to your JD location)
JD_PATH = os.path.join(ROOT_DIR, "Resume_Parser", "Parsed_JD", "Full stack.txt")

# Resume folder (change this to where your parsed resumes are)
RESUME_FOLDER = os.path.join(ROOT_DIR, "Resume_Parser", "parsed_resumes")

# Output directory (where to save results)
OUTPUT_DIR = os.path.join(ROOT_DIR, "output")

# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║         NLP ENGINE - MICROSERVICE MODE                       ║
    ║         Flexible Input Processing                            ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

    # Get all resume files from folder
    resume_files = []
    if os.path.exists(RESUME_FOLDER):
        for file in os.listdir(RESUME_FOLDER):
            if file.endswith('.txt'):
                resume_files.append(os.path.join(RESUME_FOLDER, file))

    if not resume_files:
        print(f"❌ No resume files found in: {RESUME_FOLDER}")
        exit(1)

    print(f"📋 Found {len(resume_files)} resumes to process")


    # Process using microservice
    result = process_resumes(
        jd_path=JD_PATH,
        resume_paths=resume_files,
    )

