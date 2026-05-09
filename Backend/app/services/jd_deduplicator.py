import logging
import os
import sys

import numpy as np

logger = logging.getLogger(__name__)

# Ensure Backend root is on sys.path so Ai_Scoring can be imported.
_backend_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if _backend_root not in sys.path:
    sys.path.insert(0, _backend_root)


def _get_embedding(text: str):
    """Lazy import of get_embedding to avoid importing heavy ML libs at module load time."""
    try:
        from Ai_Scoring.Ai_Scoring.semantic_matcher import get_embedding  # noqa: PLC0415
        return get_embedding(text)
    except Exception:
        logger.exception("Could not compute embedding for text")
        return None


class JobDescriptionDeduplicator:
    def __init__(self, collection, similarity_threshold=0.9):
        self.collection = collection
        self.similarity_threshold = similarity_threshold

    def compute_embedding(self, text) -> "np.ndarray | None":
        embedding = _get_embedding(text)
        if embedding is None:
            return None
        return np.asarray(embedding, dtype=np.float32)

    def find_similar(self, new_text, company_id=None):
        """Find semantically similar job descriptions.

        If company_id is provided, only search within that company's jobs (scoped deduplication).
        Otherwise, search globally (for backward compatibility).

        Returns (job_id, similarity) or (None, None) if no match found.
        If embeddings are unavailable, deduplication is skipped and (None, None) is returned.
        """
        new_emb = self.compute_embedding(new_text)
        if new_emb is None:
            logger.warning("No embedding provider available — JD deduplication skipped")
            return None, None

        new_emb = np.asarray(new_emb, dtype=np.float32)

        filter_query = {}
        if company_id:
            filter_query["companyId"] = company_id

        jobs = list(self.collection.find(
            filter_query,
            {"jobId": 1, "description": 1, "companyId": 1, "embedding": 1},
        ))
        for job in jobs:
            if "embedding" not in job:
                continue
            existing_emb = np.array(job["embedding"], dtype=np.float32)
            if existing_emb.shape != new_emb.shape:
                # Skip embeddings stored by a different provider (different dimensions).
                continue
            denom = float(np.linalg.norm(new_emb)) * float(np.linalg.norm(existing_emb))
            if denom == 0:
                continue
            sim = float(np.dot(new_emb, existing_emb) / denom)
            if sim >= self.similarity_threshold:
                return job["jobId"], sim
        return None, None

    def store_embedding(self, job_id, embedding) -> None:
        if embedding is None:
            return
        emb_list = embedding.tolist() if hasattr(embedding, "tolist") else list(embedding)
        self.collection.update_one(
            {"jobId": job_id},
            {"$set": {"embedding": emb_list}},
        )
