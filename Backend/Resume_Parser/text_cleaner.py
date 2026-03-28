import re

def clean_text(text: str) -> str:
    if not text:
        return ""

    # Remove (cid:xxx) artifacts
    text = re.sub(r'\(cid:\d+\)', '', text)

    # Fix common PDF bullet replacements
    text = re.sub(r'(?m)^[nlo]\s+', '', text)     # bullets at line start
    text = re.sub(r'\s[nlo]\s', ' ', text)        # bullets in middle

    # Remove standalone percent symbols caused by ☎
    text = re.sub(r'\s%\s?', ' ', text)

    # Allow ONLY text, numbers, spaces, and basic resume symbols
    text = re.sub(
        r'[^A-Za-z0-9\s\.\,\:\;\@\+\-\_\/\(\)\[\]\n]','',text)

    # Normalize line breaks (keep structure)
    text = re.sub(r'\r\n', '\n', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Normalize spaces
    text = re.sub(r'[ \t]+', ' ', text)

    return text.strip()
