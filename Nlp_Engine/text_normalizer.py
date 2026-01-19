import re

def normalize_text(text: str) -> str:
    """
    Normalizes resume text while preserving structure.
    """
    text = text.replace("•", "\n")
    text = text.replace("➢", "\n")
    text = re.sub(r'\r', '\n', text)
    text = re.sub(r'\n+', '\n', text)
    return text.strip()
