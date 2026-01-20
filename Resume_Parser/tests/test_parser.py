# with txt file

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from parsers.resume_parser import ResumeParser
from utils.text_cleaner import clean_text


parser = ResumeParser()

RESUME_FOLDER = "resumes"
OUTPUT_FILE = "requirements.txt"

open(OUTPUT_FILE, "w").close()

for file_name in os.listdir(RESUME_FOLDER):
    file_path = os.path.join(RESUME_FOLDER, file_name)

    if file_name.lower().endswith((".pdf")):
        try:
            text = parser.parse(file_path)
            cleaned_text = clean_text(text)

            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                f.write(f"===== {file_name} =====\n")
                f.write(cleaned_text + "\n\n")

        except Exception as e:
            print(f"Failed to parse {file_name}: {e}")

print("\nAll extracted resume text saved in txt file")
