"""Resume content validator.

Validation checks:
1) PDF contains enough extractable text.

This module now uses layered extraction:
- pdfplumber text extraction
- PyMuPDF text extraction fallback
- Optional OCR fallback (pytesseract) for image-heavy resumes
"""
import logging
import re

import pdfplumber

try:
    import fitz  # PyMuPDF
except Exception:
    fitz = None

try:
    import pytesseract
except Exception:
    pytesseract = None

logger = logging.getLogger(__name__)

# -- Tuneable thresholds -----------------------------------------------------

MIN_TEXT_LENGTH = 40  # keep permissive: accept low-content docs, reject only near-empty PDFs
MAX_OCR_PAGES = 2  # OCR first N pages only (fast + enough for resume headers)

def _extract_text(pdf_path: str) -> str:
    """Extract raw text from PDF without running OCR (fast path)."""
    try:
        text_parts = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text_parts.append(page_text)
        return "\n".join(text_parts)
    except Exception as exc:
        logger.warning("resume_validator: could not read PDF %s — %s", pdf_path, exc)
        return ""


def _extract_text_pymupdf(pdf_path: str) -> str:
    """Fallback extractor: PyMuPDF often extracts text where pdfplumber returns little."""
    if fitz is None:
        return ""
    try:
        parts = []
        with fitz.open(pdf_path) as doc:
            for page in doc:
                parts.append(page.get_text("text") or "")
        return "\n".join(parts)
    except Exception as exc:
        logger.warning("resume_validator: pymupdf extraction failed for %s — %s", pdf_path, exc)
        return ""


def _extract_text_ocr(pdf_path: str, max_pages: int = MAX_OCR_PAGES) -> str:
    """Optional OCR fallback for scanned/image-heavy resumes.

    Returns empty string when OCR is unavailable (e.g., Tesseract binary missing).
    """
    if fitz is None or pytesseract is None:
        return ""

    try:
        parts = []
        with fitz.open(pdf_path) as doc:
            page_count = min(len(doc), max_pages)
            for idx in range(page_count):
                page = doc[idx]
                pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
                ocr_text = pytesseract.image_to_string(
                    pix.pil_image(),
                    config="--oem 3 --psm 6",
                )
                parts.append(ocr_text or "")
        return "\n".join(parts)
    except Exception as exc:
        logger.warning("resume_validator: OCR fallback failed for %s — %s", pdf_path, exc)
        return ""


def _merge_text(*chunks: str) -> str:
    """Merge extraction outputs, keeping useful content while avoiding pure duplicates."""
    cleaned = []
    seen = set()
    for chunk in chunks:
        text = (chunk or "").strip()
        if not text:
            continue
        key = re.sub(r"\s+", " ", text.lower())[:5000]
        if key in seen:
            continue
        seen.add(key)
        cleaned.append(text)
    return "\n".join(cleaned)


def validate_resume_content(pdf_path: str) -> tuple:
    """
    Returns (True, None) if the document looks like a resume.
    Returns (False, reason_string) if it does not.
    """
    text_pdfplumber = _extract_text(pdf_path)
    text_pymupdf = _extract_text_pymupdf(pdf_path)
    text = _merge_text(text_pdfplumber, text_pymupdf)

    # OCR fallback only when direct extraction is still too short.
    if len(text.strip()) < MIN_TEXT_LENGTH:
        text_ocr = _extract_text_ocr(pdf_path)
        text = _merge_text(text, text_ocr)

    lowered = text.lower()

    # ── Check 1: minimum length ────────────────────────────────────────────
    if len(text.strip()) < MIN_TEXT_LENGTH:
        return (
            False,
            "The uploaded document contains too little text. "
            "Please upload a proper resume PDF.",
        )

    # Keep validation permissive by design: content quality is handled in scoring.
    # This allows placeholder text (including lorem ipsum) to be accepted but scored very low.

    return (True, None)
