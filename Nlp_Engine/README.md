# NLP Engine Module

**Update:**
- Skill extraction now supports all major fields/branches (Engineering, Commerce, Law, Medicine, Arts, etc.).
- Semantic matching (SBERT) is integrated for meaning-based candidate-job alignment.

NLP Engine converts cleaned text into structured, scoring-ready candidate features.

It receives plain text from Resume Parser and produces one normalized JSON file that AI Scoring can consume directly.

## 1. Why this module exists

Raw resume text is noisy and inconsistent:
1. Different formats and writing styles.
2. Missing section headings.
3. Skill names written in many variants.
4. Education and experience described in free text.

If scoring reads raw text directly, ranking quality becomes unstable.
So this module isolates feature engineering and gives a standard output schema.

## 2. Responsibilities and boundaries

This module does:
1. Text normalization.
2. JD requirement extraction.
3. Resume section detection.
4. Skill, experience, education, and contact extraction.
5. JD-vs-resume match field preparation.
6. Output formatting with per-resume success/error blocks.

This module does not:
1. Assign final candidate rank.
2. Make selection/rejection decisions.
3. Send emails.

Those tasks are handled by AI Scoring and Backend.

## 3. Input and output contract

### Input
1. One JD text file path.
2. One or more resume text file paths.

### Output
1. JSON file in `Nlp_Engine/output/`.
2. `job_requirements` block used by scorer.
3. Per-resume extracted features.
4. `scoring_ready` flag.
5. Error metadata for failed resumes (without failing whole batch).

## 4. Detailed file-by-file guide

Core orchestration:
1. `Nlp_service.py`
Purpose: public entrypoint and end-to-end flow controller.
Contains: loading text files, calling extractors, writing final JSON.

JD parsing:
1. `job_description_parser.py`
Purpose: parse required skills, preferred skills, min experience, and education from JD text.
Contains: pattern/section logic and default fallback behavior.

Resume feature extraction:
1. `section_detector.py`
Purpose: split resume into logical segments such as skills, education, and experience.
2. `skill_extractor.py`
Purpose: detect skills using keyword rules and skill database lookup.
3. `experience_calculator.py`
Purpose: estimate total experience and optionally skill-wise experience signals.
4. `education_detector.py`
Purpose: map free-text education mentions to normalized levels.
5. `contact_extractor.py`
Purpose: extract phone, email, and contact identifiers from text.

Preprocessing and standardization:
1. `text_normalizer.py`
Purpose: normalize spacing/case/noise before extraction.
2. `output_formatter.py`
Purpose: enforce stable output JSON schema for downstream modules.

Shared data and configuration:
1. `skill_database.py`
Purpose: central skill vocabulary and aliases.
2. `config.py`
Purpose: NLP thresholds/defaults and behavior switches.
3. `batch_Processor.py`
Purpose: convenience handling for multi-file processing workflows.
4. `__init__.py`
Purpose: package exports.

Artifacts:
1. `output/*.json`
Purpose: generated NLP outputs for scoring/debugging.

## 5. Internal processing pipeline

1. Load and normalize JD text.
2. Parse job requirements.
3. For each resume:
4. Normalize resume text.
5. Detect sections.
6. Extract contact data.
7. Extract skills.
8. Estimate experience.
9. Detect education level.
10. Compute JD-alignment feature fields.
11. Build standardized resume output object.
12. Add success/error metadata.
13. Write single consolidated output JSON.

## 6. Output fields important for AI Scoring

Expected scorer-critical fields include:
1. Parsed skills list.
2. Experience estimate.
3. Education level signal.
4. Job requirements snapshot.
5. `scoring_ready`.

Any change to these fields must be coordinated with AI Scoring module.

## 7. Failure handling strategy

Design principle: partial success over full failure.

1. One bad resume should not block all resumes.
2. Resume-level error info is stored in output.
3. Batch metadata tracks total, success, and failed counts.

This makes operations safer in real hiring data where file quality varies.

## 8. How to run this module directly

Typical Python usage pattern:
1. Import process function from `Nlp_service.py`.
2. Pass JD text path and resume text path list.
3. Read output JSON path from response.

From the full project flow, Backend calls this module through PipelineService.

## 9. Troubleshooting checklist

If output file is not generated:
1. Check JD path exists and is readable.
2. Check resume text files exist.
3. Check write permission on `Nlp_Engine/output/`.

If skill extraction seems low:
1. Inspect section detection quality.
2. Extend `skill_database.py` with missing aliases.
3. Verify text normalization is not removing key tokens.

If experience looks wrong:
1. Validate date parsing assumptions.
2. Verify resume has parseable date ranges.
3. Add additional regex patterns in `experience_calculator.py`.

## 10. Extension points

1. Add domain-specific skills to `skill_database.py`.
2. Add new section labels in `section_detector.py`.
3. Add extra match fields in `output_formatter.py`.
4. Add language support by expanding normalization and extraction rules.

## 11. Interview questions and model answers

1. Why split NLP extraction from scoring?
Answer: it keeps feature engineering independent, testable, and reusable across scoring strategies.

2. How do you handle non-standard resume layouts?
Answer: section detection uses flexible fallbacks and extraction does not depend on a single strict template.

3. How do you prevent one bad file from failing a batch?
Answer: per-resume error handling with batch-level summary metadata.

4. Why keep a normalized output schema?
Answer: stable contracts reduce coupling and make model evolution safer.
