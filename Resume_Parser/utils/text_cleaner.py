import re

def clean_text(text: str) -> str:
    if not text:
        return ""

    # Remove (cid:xxx) artifacts
    text = re.sub(r'\(cid:\d+\)', ' ', text)

    # Remove non-ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)

    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)

    # Normalize line breaks
    text = re.sub(r'\n+', '\n', text)

    return text.strip()
