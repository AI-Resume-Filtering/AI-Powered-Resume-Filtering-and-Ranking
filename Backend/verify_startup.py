#!/usr/bin/env python
"""Quick startup verification script."""

import sys
sys.path.insert(0, '.')

print("Testing module imports...")
print()

try:
    from app import create_app
    print("✅ Flask app loads")
except Exception as e:
    print(f"❌ Flask app: {e}")
    sys.exit(1)

try:
    from Ai_Scoring.Ai_Scoring.scorer import score_resume
    print("✅ AI Scoring loads")
except Exception as e:
    print(f"❌ AI Scoring: {e}")
    sys.exit(1)

try:
    from Nlp_Engine.skill_database import SKILL_DATABASE
    print("✅ NLP Engine loads")
except Exception as e:
    print(f"❌ NLP Engine: {e}")
    sys.exit(1)

try:
    from Resume_Parser.resume_parser import ResumeParser
    print("✅ Resume Parser loads")
except Exception as e:
    print(f"❌ Resume Parser: {e}")
    sys.exit(1)

print()
print("✅ ALL MODULES VERIFIED - READY FOR DEPLOYMENT")
