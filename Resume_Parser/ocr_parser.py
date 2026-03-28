import os
import platform
import shutil

import pytesseract


def _find_tesseract() -> str:
    system = platform.system()
    candidates = []
    if system == "Windows":
        candidates = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
    elif system == "Darwin":
        candidates = [
            "/usr/local/bin/tesseract",
            "/opt/homebrew/bin/tesseract",
        ]
    else:
        candidates = ["/usr/bin/tesseract"]

    for path in candidates:
        if os.path.exists(path):
            return path
    return shutil.which("tesseract") or ""


if _TESSERACT_CMD := _find_tesseract():
    pytesseract.pytesseract.tesseract_cmd = _TESSERACT_CMD


def _load_image_ocr_dependencies():
    missing = []

    try:
        import cv2  # type: ignore
    except ImportError:
        cv2 = None
        missing.append("opencv-python")

    try:
        import numpy as np  # type: ignore
    except ImportError:
        np = None
        missing.append("numpy")

    if missing:
        raise RuntimeError(
            "OCR dependencies are missing. Install: " + ", ".join(missing)
        )

    return cv2, np


def _load_pdf_ocr_dependencies():
    cv2, np = _load_image_ocr_dependencies()

    try:
        import fitz  # type: ignore
    except ImportError as exc:
        raise RuntimeError("OCR dependency is missing. Install: PyMuPDF") from exc

    return cv2, np, fitz


def _ensure_image_ocr_ready() -> None:
    _load_image_ocr_dependencies()
    tesseract_cmd = pytesseract.pytesseract.tesseract_cmd or "tesseract"
    if os.path.isabs(tesseract_cmd):
        tesseract_available = os.path.exists(tesseract_cmd)
    else:
        tesseract_available = bool(shutil.which(tesseract_cmd))

    if not tesseract_available:
        raise RuntimeError(
            "Tesseract OCR is not installed or not available on PATH. "
            "Install Tesseract and configure pytesseract.pytesseract.tesseract_cmd if needed."
        )


def _ensure_pdf_ocr_ready() -> None:
    _ensure_image_ocr_ready()
    _load_pdf_ocr_dependencies()


def _prepare_image(image) -> "np.ndarray":
    _ensure_image_ocr_ready()
    cv2, np = _load_image_ocr_dependencies()

    if hasattr(image, "convert"):
        image = np.array(image.convert("RGB"))

    if image.ndim == 2:
        gray = image
    elif image.shape[2] == 4:
        gray = cv2.cvtColor(image, cv2.COLOR_RGBA2GRAY)
    else:
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


def _text_density(text: str) -> int:
    return sum(char.isalnum() for char in text)


def image_to_text(image, psm: int = 6) -> str:
    processed = _prepare_image(image)

    variants = [
        pytesseract.image_to_string(
            processed,
            lang="eng",
            config=f"--oem 3 --psm {psm}",
        ).strip()
    ]

    height, width = processed.shape[:2]
    if width >= 600 and height >= 300:
        cropped = processed[:, int(width * 0.12):]
        variants.append(
            pytesseract.image_to_string(
                cropped,
                lang="eng",
                config="--oem 3 --psm 4",
            ).strip()
        )

    return max(variants, key=_text_density, default="")


def extract_text_ocr(pdf_path: str) -> str:
    _ensure_pdf_ocr_ready()
    _, np, fitz = _load_pdf_ocr_dependencies()

    text_parts = []
    document = fitz.open(pdf_path)
    try:
        for page in document:
            pixmap = page.get_pixmap(dpi=400, alpha=False)
            image = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(
                pixmap.height, pixmap.width, pixmap.n
            )
            if page_text := image_to_text(image, psm=4):
                text_parts.append(page_text)
    finally:
        document.close()

    return "\n".join(text_parts)


def extract_page_ocr(pdf_path: str, page_num: int) -> str:
    _ensure_pdf_ocr_ready()
    _, np, fitz = _load_pdf_ocr_dependencies()

    document = fitz.open(pdf_path)
    try:
        page = document.load_page(page_num - 1)
        pixmap = page.get_pixmap(dpi=400, alpha=False)
        image = np.frombuffer(pixmap.samples, dtype=np.uint8).reshape(
            pixmap.height, pixmap.width, pixmap.n
        )
        return image_to_text(image, psm=4)
    finally:
        document.close()