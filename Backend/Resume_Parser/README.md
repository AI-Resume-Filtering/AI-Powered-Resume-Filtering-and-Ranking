# Resume Parser Module

Resume Parser is the ingestion layer that converts PDF documents into clean plain text.

It supports both text-based PDFs and scanned/image-heavy PDFs through OCR fallback.

## 1. Why this module exists

Downstream NLP and AI scoring depend on text quality.
Real-world resumes often contain:
1. Mixed layouts.
2. Tables and columns.
3. Scanned pages with no selectable text.
4. Embedded images and formatting artifacts.

This module normalizes those inputs into readable text for reliable feature extraction.

## 2. What this module handles

1. Read resume and JD PDFs from supported folders.
2. Extract text with pdfplumber for normal PDFs.
3. Fallback to OCR for scanned content.
4. Clean text before NLP stage.
5. Batch process many files.
6. Save consistent `.txt` outputs.

## 3. File-by-file guide

1. `resume_parser.py`
Purpose: main parser interface and extraction orchestration.

2. `ocr_parser.py`
Purpose: OCR pipeline for image/scanned pages.
Uses: PyMuPDF rendering + OpenCV/Pillow preprocessing + Tesseract recognition.

3. `text_cleaner.py`
Purpose: remove noise, normalize whitespace, improve downstream NLP quality.

4. `batch_parser.py`
Purpose: process multiple resumes/JDs in one run and return summary counts.

5. `requirements.txt`
Purpose: module-specific dependency pointer for parser stack.

6. `__init__.py`
Purpose: package exports for simple imports.

## 4. Supported input folder layouts

Layout option A:
1. `Samples/Resumes/`
2. `Samples/Job_Descriptions/`

Layout option B:
1. `data/resumes/`
2. `data/job_descriptions/`

## 5. Parsing flow in detail

1. Discover PDF files from supported input layout.
2. For each file, attempt direct text extraction.
3. If extracted text is weak/empty, trigger OCR fallback.
4. Merge useful text blocks.
5. Clean and normalize extracted text.
6. Save output `.txt` files to parser output folders.
7. Return summary metadata for success/failure counts.

## 6. Output contract

Outputs are plain UTF-8 text files consumed by NLP Engine.

Typical outputs:
1. Resume text files in parsed resume output directory.
2. JD text files in parsed JD output directory.
3. Batch summary dict containing parsed and failed counts.

## 7. Integration with NLP and scoring

1. Resume Parser produces cleaned text files.
2. NLP Engine reads those files and extracts structured features.
3. AI Scoring ranks candidates using extracted features.

Any parser extraction issue propagates to NLP/scoring quality, so this module is quality-critical.

## 8. Troubleshooting guide

If parser finds no PDFs:
1. Verify folder layout and file extension `.pdf`.
2. Check file permissions.

If OCR fails:
1. Verify Tesseract is installed.
2. Verify Tesseract binary is available in PATH.
3. Verify OCR dependencies are installed from requirements.

If output text quality is poor:
1. Inspect scanned image quality.
2. Adjust cleaning rules in `text_cleaner.py`.
3. Add preprocessing in `ocr_parser.py` for noisy scans.

If parser is slow:
1. Batch large files in smaller groups.
2. Avoid repeated OCR on same files.
3. Consider caching parse outputs for unchanged documents.

## 9. Performance and reliability notes

1. OCR is expensive; direct extraction is preferred when available.
2. Resume table parsing is important because skills often live inside tables.
3. Cleaning stage should preserve semantics while removing artifacts.

## 10. Recommended best practices

1. Keep sample and production input folders separate.
2. Track parse failures and review failed files regularly.
3. Validate parser outputs before NLP upgrades.

## 11. Interview questions and answers

1. Why combine direct extraction and OCR?
Answer: direct extraction is faster and cleaner for digital PDFs, OCR handles scanned/image-only documents.

2. Why is text cleaning required before NLP?
Answer: normalization reduces noise and improves section/skill extraction reliability.

3. What is the biggest risk in resume parsing?
Answer: poor extraction causes downstream false negatives in matching and ranking.

4. How do you make parser robust in production?
Answer: use fallback extraction paths, batch-level summaries, and per-file failure diagnostics.
