# AI Scoring Module

**Update:**
- Semantic similarity (SBERT) is now used for meaning-based scoring.
- Scoring logic and skill matching are field-agnostic and support all branches.

AI Scoring converts extracted NLP features into an explainable final score and rank.

It supports both deterministic blended scoring and model-based scoring (when feedback data is sufficient).

## 1. Why this module exists

Ranking candidates with only keyword checks is weak.
This module improves ranking quality using:
1. Semantic similarity between resume and JD.
2. Structured feature alignment (experience and education).
3. Optional supervised model trained from recruiter feedback.

## 2. Scope and non-scope

This module does:
1. Compute semantic score.
2. Compute rule-based feature scores.
3. Build final score output with explanation fields.
4. Retrain model from feedback.

This module does not:
1. Parse PDFs.
2. Perform low-level NLP extraction from raw text files.
3. Handle HTTP routing.

## 3. Folder and file guide

Module root:
1. `README.md`
Purpose: module documentation.

Main implementation package:
1. `Ai_Scoring/scorer.py`
Purpose: orchestrates score calculation, fallback logic, and score packaging.
2. `Ai_Scoring/semantic_matcher.py`
Purpose: embedding-based semantic similarity computation.
3. `Ai_Scoring/model_trainer.py`
Purpose: build training dataset from feedback and train/update model.
4. `Ai_Scoring/ranker.py`
Purpose: helper ranking utilities for candidate ordering workflows.
5. `Ai_Scoring/config.py`
Purpose: score weights and related defaults.
6. `Ai_Scoring/utils.py`
Purpose: shared helper functions.
7. `Ai_Scoring/__init__.py`
Purpose: package exports.

Artifacts and sample outputs:
1. `Ai_Scoring/parser_output.json`
Purpose: sample/working input data representation.
2. `Ai_Scoring/ranked_candidates.json`
Purpose: sample/working ranking result artifact.
3. `Ai_Scoring/test_scoring.py`
Purpose: module-level scoring behavior checks.

## 4. Scoring pipeline in detail

1. Read structured NLP output.
2. Compute semantic match between resume and JD text.
3. Compute experience score from extracted experience vs requirement.
4. Compute education score from normalized education mapping.
5. Compute blended score with weighted formula.
6. If trained model exists and is valid, compute ML probability score.
7. Choose final score source (`ml` or `blended`).
8. Return score object including explainability fields.

Blended formula currently uses weighted contributions:
1. Semantic contribution.
2. Experience contribution.
3. Education contribution.

## 5. Explainability contract

Scoring response exposes component signals:
1. `semantic_score`
2. `experience_score`
3. `education_score`
4. `blended_score`
5. `score_source`
6. `total_score`

This helps recruiters understand why a candidate ranked higher/lower.

## 6. Model retraining lifecycle

1. Recruiter submits selected/rejected decisions.
2. Backend stores labeled feedback with feature values.
3. When threshold conditions are met, trainer builds dataset.
4. Model is fitted (RandomForest baseline).
5. Saved model becomes available for future scoring runs.

Training safeguards include:
1. Minimum sample count check.
2. Positive/negative class availability check.
3. Fallback to blended scoring if model is unavailable.

## 7. Cold-start and fallback strategy

Why fallback exists:
1. Early project phase has little feedback.
2. Training might be skipped due to insufficient class distribution.

Fallback behavior:
1. Always compute blended score.
2. Use blended score as primary until valid model exists.

This ensures the system stays functional at all times.

## 8. Performance and quality notes

1. Semantic model can be expensive; cache/model reuse is important.
2. Deterministic components keep output stable across runs.
3. Retraining frequency should balance freshness vs noise.

## 9. Troubleshooting checklist

If all candidates get similar scores:
1. Inspect semantic matcher output for collapse.
2. Verify JD/resume texts are correctly populated.
3. Check extracted NLP features are not empty.

If ML score never appears:
1. Verify feedback collection count.
2. Verify both selected and rejected labels exist.
3. Check model training logs/errors.

If ranking appears unfair:
1. Inspect per-feature breakdown fields.
2. Revisit scoring weights in `config.py`.
3. Audit feedback quality for bias and noise.

## 10. Extension ideas

1. Add skills gap penalty/bonus components.
2. Add profile completeness confidence scoring.
3. Add per-job adaptive weighting.
4. Add model registry with version tracking.

## 11. Interview questions and answers

1. Why combine semantic and rule-based scoring?
Answer: semantic captures meaning while rule-based metrics retain explicit requirement alignment.

2. Why keep blended score when ML is present?
Answer: deterministic fallback protects reliability and supports cold start.

3. Why RandomForest as baseline?
Answer: robust with tabular features, low preprocessing overhead, and good interpretability.

4. How do you keep scoring transparent?
Answer: always return component-level scores and final score source.
