# text_preprocessor.py

import re

def preprocess_text(text: str) -> list[str]:
    """
    Cleans resume text and returns list of lines.
    """
    text = text.lower()
    text = re.sub(r'[^\w\s%]', ' ', text)  # keep numbers & %
    text = re.sub(r'\s+', ' ', text)

    lines = text.split(" ")
    return lines
