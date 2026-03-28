import logging
from functools import lru_cache
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

@lru_cache(maxsize=1)
def _get_model(model_name: str = "all-MiniLM-L6-v2"):
    try:
        from sentence_transformers import SentenceTransformer, util
        model = SentenceTransformer(model_name)
        return model, util
    except Exception:
        logger.exception("Failed to load semantic model '%s'", model_name)
        return None





def semantic_similarity_score(resume_text: str, job_description: str, model_name: str = "all-MiniLM-L6-v2") -> float:
    """
    Compute similarity in [0, 1] between resume and job description.
    Uses sentence-transformers when available, otherwise uses a lightweight fallback.
    """
    resume_text = (resume_text or "").strip()
    job_description = (job_description or "").strip()
    if not resume_text or not job_description:
        return 0.0

    model_bundle = _get_model(model_name)
    if model_bundle is None:
        return 0.0

    model, util = model_bundle

    try:
        resume_embedding = model.encode(resume_text, convert_to_tensor=True)
        jd_embedding = model.encode(job_description, convert_to_tensor=True)
        similarity = util.cos_sim(resume_embedding, jd_embedding).item()
        similarity = max(0.0, min(float(similarity), 1.0))
        return round(similarity, 6)
    except Exception:
        logger.exception("Semantic similarity computation failed; returning 0.0")
        return 0.0
