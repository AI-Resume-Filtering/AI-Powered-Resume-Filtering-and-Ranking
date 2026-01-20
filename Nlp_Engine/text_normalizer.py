import re


def normalize_text(text: str) -> str:

    if not text:
        return ""
 #  Replace bullets with newlines

    text = text.replace("•", "\n")
    text = text.replace("➢", "\n")
    text = text.replace("○", "\n")
    text = text.replace("●", "\n")
    text = text.replace("■", "\n")
    text = text.replace("□", "\n")
    text = text.replace("▪", "\n")
    text = text.replace("▫", "\n")
    text = text.replace("→", "\n")
    text = text.replace("➤", "\n")

    # Step 2: Fix line endings
    text = re.sub(r'\r', '\n', text)
    text = re.sub(r'\n+', '\n', text)

    # Step 3: Fix encoding issues (in PDF extraction)

    text = text.replace('â€"', '-')  # Em dash
    text = text.replace('â€"', '-')  # En dash
    text = text.replace('â€™', "'")  # Apostrophe
    text = text.replace('â€œ', '"')  # Opening quote
    text = text.replace('â€�', '"')  # Closing quote

    # Step 4: Normalize spaces
    text = re.sub(r'\t', ' ', text)  # Tabs → Spaces
    text = re.sub(r' +', ' ', text)  # Multiple spaces → Single

    return text.strip()