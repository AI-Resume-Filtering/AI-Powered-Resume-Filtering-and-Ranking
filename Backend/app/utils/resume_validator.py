"""Resume content validator.

Validation checks:
1) PDF contains enough extractable text.
2) Core resume signals are present.

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

MIN_TEXT_LENGTH = 120  # characters — reject blank / near-empty PDFs
MIN_SECTION_SIGNALS = 2  # at least N of: education/experience/skills/projects
MAX_OCR_PAGES = 2  # OCR first N pages only (fast + enough for resume headers)

_EMAIL_RE = re.compile(r"\b[^\s@]+@[^\s@]+\.[^\s@]+\b")
_PHONE_RE = re.compile(r"(?:\+?\d[\d\s().-]{7,}\d)")

_REQUIRED_SIGNAL_KEYWORDS = {
    "education": [
        "education", "degree", "university", "college", "b.tech", "b.e.",
        "bachelor", "master", "m.tech", "diploma", "school",
    ],
    "experience": [
        "experience", "work history", "employment", "internship", "intern", "worked at",
    ],
    "skills": [
        "skills", "technologies", "tech stack", "tools", "languages", "frameworks",
    ],
    "projects": [
        "project", "projects", "achievement", "certification", "certificate",
        "award", "publication", "research",
    ],
}


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

    # -- Check 2: require BOTH email and phone -----------------------------
    has_email = bool(_EMAIL_RE.search(text))
    has_phone = bool(_PHONE_RE.search(text))
    if not (has_email and has_phone):
        return (
            False,
            "The uploaded document must contain BOTH an email address and a phone number. "
            "Please upload a resume with full contact details.",
        )

    # -- Check 3: require at least 3/4 core sections -----------------------
    missing_signals = []
    matched_sections = 0
    for signal_name, keywords in _REQUIRED_SIGNAL_KEYWORDS.items():
        if not any(kw in lowered for kw in keywords):
            missing_signals.append(signal_name)
        else:
            matched_sections += 1
    if matched_sections < 3:
        pretty_missing = ", ".join(missing_signals)
        return (
            False,
            f"The uploaded document does not appear to be a resume. "
            f"Missing required resume sections: {pretty_missing}. "
            "Please upload a valid resume with clear sections like education, experience, skills, or projects.",
        )

    # (Removed) Check for resume-specific keywords on first page

    # -- Optional: Require a likely name at the top ------------------------
    # Heuristic: first 5 lines, at least 2 words, mostly alphabetic
    lines = [line.strip() for line in text.splitlines() if line.strip()][:5]
    name_found = False
    for line in lines:
        if 2 <= len(line.split()) <= 5 and sum(c.isalpha() for c in line) / max(1, len(line)) > 0.7:
            name_found = True
            break
    if not name_found:
        return (
            False,
            "The uploaded document does not appear to have a candidate name at the top. "
            "Please upload a resume with your name clearly listed at the top.",
        )

    return (True, None)
