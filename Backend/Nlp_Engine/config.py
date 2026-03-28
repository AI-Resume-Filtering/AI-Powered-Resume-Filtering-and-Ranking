"""
NLP Engine Configuration
All settings in one place for easy modification
"""

import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))  # Nlp_Engine/
ROOT_DIR = os.path.dirname(CURRENT_DIR)
print(f"  Root Directory: {ROOT_DIR}")
print(f"  Current Directory: {CURRENT_DIR}")
# ============================================
# PATH CONFIGURATIONS
# ============================================

INPUT_FOLDER = os.path.join(ROOT_DIR, "Resume_Parser", "parsed_resumes")

# Job Description file (inside Resume_Parser)
JOB_DESCRIPTION_FILE = os.path.join(ROOT_DIR, "Resume_Parser", "Parsed_JD")

# Output folder and file (INSIDE Nlp_Engine package)
OUTPUT_FOLDER = os.path.join(CURRENT_DIR, "output")
OUTPUT_FILE = os.path.join(OUTPUT_FOLDER, "nlp_extracted_data.json")

# Error log
ERROR_LOG_FILE = os.path.join(OUTPUT_FOLDER, "errors.log")
# ============================================
# PROCESSING CONFIGURATIONS
# ============================================

# Batch size for processing
BATCH_SIZE = 100  # Process 100 resumes at once

# Supported file extensions
SUPPORTED_EXTENSIONS = ['.txt']  # Only TXT for now

# ============================================
# RESUME ID CONFIGURATIONS
# ============================================

# ID Prefix
RESUME_ID_PREFIX = "resume_id_"

# ID Format: "resume_id_001" (3-digit sequential)
ID_PADDING = 3

# ============================================
# SKILL EXTRACTION CONFIGURATIONS
# ============================================

# Minimum confidence for skill extraction
MIN_CONFIDENCE = 0.75  # 75% confidence threshold

# Include synonym matching
USE_SYNONYM_MATCHING = True

# Include fuzzy matching (for typos)
USE_FUZZY_MATCHING = True
FUZZY_THRESHOLD = 0.85  # 85% similarity

# ============================================
# JOB MATCHING CONFIGURATIONS
# ============================================

# REMOVED: No more default job requirements!
# Will be parsed from job_requirements.txt.txt

# Minimum match percentage to consider as "qualified"
MINIMUM_MATCH_PERCENTAGE = 50  # 50% skills must match

# ============================================
# SKILL CATEGORIES
# ============================================

SKILL_CATEGORIES = [
    "programming_language",
    "ai_ml",
    "database",
    "backend",
    "frontend",
    "tools",
    "cloud",
    "mobile"
]

# ============================================
# ERROR HANDLING
# ============================================

# Continue processing on errors
CONTINUE_ON_ERROR = True

# Log errors to file
ERROR_LOG_FILE = os.path.join(OUTPUT_FOLDER, "errors.log")

# ============================================
# PROGRESS BAR
# ============================================

# Show progress bar
SHOW_PROGRESS = True

# Progress bar style
PROGRESS_BAR_FORMAT = "{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]"

# ============================================
# VALIDATION
# ============================================

# Ensure output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

print("✓ NLP Engine Configuration Loaded")
print(f"  Input Folder: {INPUT_FOLDER}")
print(f"  Job Description: {JOB_DESCRIPTION_FILE}")
print(f"  Output File: {OUTPUT_FILE}")