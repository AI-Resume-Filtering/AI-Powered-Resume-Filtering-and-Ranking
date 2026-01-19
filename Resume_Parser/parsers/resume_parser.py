import os
import pdfplumber
from resume_parser.utils.text_cleaner import clean_text


class ResumeParser:
    def parse(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError("Resume file not found")

        extension = os.path.splitext(file_path)[1].lower()

        if extension == ".pdf":
            raw_text = self._parse_pdf(file_path)
        elif extension == ".txt":
            raw_text = self._parse_txt(file_path)
        else:
            raise ValueError("Unsupported file format")

        return clean_text(raw_text)

    def _parse_pdf(self, file_path: str) -> str:
        text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text

    def _parse_txt(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
            return file.read()
