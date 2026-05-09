import os

import pdfplumber

from .ocr_parser import extract_page_ocr, image_to_text
from .text_cleaner import clean_text

# Minimum image dimensions (pts) to attempt OCR — skips tiny icons/logos
_MIN_IMAGE_WIDTH = 50
_MIN_IMAGE_HEIGHT = 50

class ResumeParser:
    def parse(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError("Resume file not found")

        extension = os.path.splitext(file_path)[1].lower()

        if extension == ".pdf":
            raw_text = self._parse_pdf(file_path)
        else:
            raise ValueError("Unsupported file format")

        return clean_text(raw_text)

    def _parse_pdf(self, file_path: str) -> str:
        """
        Extract all content from a PDF:
          1. Selectable text layer (pdfplumber)
          2. Tables (pdfplumber)
          3. Embedded images / charts / graphs → OCR (pytesseract)
          4. Scanned / image-only pages → full-page OCR (PyMuPDF + OpenCV + pytesseract)
        """
        text = ""

        with pdfplumber.open(file_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):

                # ── 1. Selectable text ──────────────────────────────────────
                page_text = page.extract_text() or ""

                # ── 2. Tables ───────────────────────────────────────────────
                for table in page.extract_tables():
                    for row in table:
                        row_text = " ".join(cell or "" for cell in row)
                        page_text += "\n" + row_text

                if page_text.strip():
                    text += page_text + "\n"
                else:
                    # ── 4. Scanned page fallback: full-page OCR ─────────────
                    print(f"[OCR] Page {page_num} has no text layer — running full-page OCR...")
                    ocr_text = self._ocr_full_page(file_path, page_num)
                    if ocr_text:
                        text += ocr_text + "\n"

                # ── 3. Embedded images / charts / graphs ────────────────────
                image_text = self._ocr_embedded_images(page, page_num)
                if image_text:
                    text += image_text + "\n"

        return text

    # ──────────────────────────────────────────────────────────────────────────
    # Image / graph extraction
    # ──────────────────────────────────────────────────────────────────────────

    def _ocr_embedded_images(self, page, page_num: int) -> str:
        """
        Crop every embedded image/chart/graph from the page and run OCR on it.
        Results are tagged so downstream NLP knows the text came from a visual.
        Tiny decorative images (< _MIN_IMAGE_WIDTH x _MIN_IMAGE_HEIGHT pts) are skipped.
        """
        results = []

        for idx, img in enumerate(page.images, start=1):
            try:
                x0, y0 = img["x0"], img["top"]
                x1, y1 = img["x1"], img["bottom"]

                # Skip decorative / icon-sized images
                if (x1 - x0) < _MIN_IMAGE_WIDTH or (y1 - y0) < _MIN_IMAGE_HEIGHT:
                    continue

                # Crop region → PIL Image → OCR.
                # 150 DPI is sufficient for embedded images / charts and uses
                # ~44% less memory than the previous 200 DPI setting.
                pil_image = (
                    page.crop((x0, y0, x1, y1))
                        .to_image(resolution=150)
                        .original
                )
                try:
                    ocr_text = image_to_text(pil_image)
                finally:
                    del pil_image

                if ocr_text:
                    results.append(
                        f"[IMAGE/GRAPH - Page {page_num}, Item {idx}]\n{ocr_text}"
                    )

            except Exception as e:
                print(f"[IMAGE OCR] Warning: page {page_num}, image {idx} — {e}")

        return "\n".join(results)

    # ──────────────────────────────────────────────────────────────────────────
    # Full-page OCR (scanned / image-only pages)
    # ──────────────────────────────────────────────────────────────────────────

    def _ocr_full_page(self, file_path: str, page_num: int) -> str:
        """
        Render a single PDF page at 300 DPI and run OCR on the whole page.
        page_num is 1-based.
        """
        try:
            return extract_page_ocr(file_path, page_num).strip()
        except Exception as e:
            print(f"[OCR] Warning: full-page OCR failed on page {page_num} — {e}")
            return ""

