"""
NLP Engine - Microservice Mode
Can work standalone OR as microservice
"""

# Original batch processor (for standalone mode)
from .batch_Processor import NLPBatchProcessor

# Microservice API (for backend integration)
from .Nlp_service import NLPMicroservice, process_resumes

# Config
from .config import (
    INPUT_FOLDER,
    OUTPUT_FILE,
    JOB_DESCRIPTION_FILE
)

__all__ = [
    # Batch mode (original)
    'NLPBatchProcessor',

    # Microservice mode (NEW)
    'NLPMicroservice',
    'process_resumes',

    # Config
    'INPUT_FOLDER',
    'OUTPUT_FILE',
    'JOB_DESCRIPTION_FILE'
]

__version__ = '2.0.0'  # Updated for microservice support
__author__ = 'Mahesh Nikas'

print("✓ NLP Engine Loaded (Batch + Microservice Mode)")