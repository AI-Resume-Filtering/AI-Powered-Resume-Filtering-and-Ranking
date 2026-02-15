"""
Resume Parser Package
Parses PDF/DOCX resumes and job descriptions to text

Author: Mahesh Nikas
Version: 1.0.0
"""

from .resume_parser import ResumeParser
from .batch_parser import BatchParser

__all__ = [
    'ResumeParser',
    'BatchParser'
]

__version__ = '1.0.0'
__author__ = 'V. T'

print("✓ Resume Parser Package Loaded")
