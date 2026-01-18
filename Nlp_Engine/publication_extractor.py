# publication_extractor.py

def extract_publications(pub_lines: list[str]) -> dict:
    count = len(pub_lines)
    bonus = count * 2  # 2% per publication

    return {
        "count": count,
        "bonus_percentage": bonus
    }
