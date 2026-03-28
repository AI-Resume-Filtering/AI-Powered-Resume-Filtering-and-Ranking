# Ai_Scoring/test_scoring.py
import os
import json

try:
    from .scorer import score_resume, process_resume_batch
except ImportError:
    from scorer import score_resume, process_resume_batch