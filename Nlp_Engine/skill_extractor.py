# skill_extractor.py

from constants import STOPWORDS

def extract_skills(words: list[str]) -> dict:
    skill_count = {}

    for word in words:
        if word.isalpha() and word not in STOPWORDS:
            skill_count[word] = skill_count.get(word, 0) + 1

    return skill_count
