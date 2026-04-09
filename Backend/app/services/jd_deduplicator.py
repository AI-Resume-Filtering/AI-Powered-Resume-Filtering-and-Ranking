import logging
from threading import Lock

import numpy as np
from sentence_transformers import SentenceTransformer, util

logger = logging.getLogger(__name__)

class JobDescriptionDeduplicator:
    _model_cache = {}
    _model_cache_lock = Lock()

    def __init__(self, collection, model_name="all-MiniLM-L6-v2", similarity_threshold=0.9):
        self.collection = collection
        self.model_name = model_name
        self.model = self._get_or_load_model(model_name)
        self.similarity_threshold = similarity_threshold

    @classmethod
    def _get_or_load_model(cls, model_name: str):
        """Load SentenceTransformer once per process and fail open on load errors."""
        with cls._model_cache_lock:
            if model_name in cls._model_cache:
                return cls._model_cache[model_name]
            try:
                model = SentenceTransformer(model_name)
                cls._model_cache[model_name] = model
                return model
            except Exception as exc:
                logger.exception(
                    "JD dedup model load failed for '%s'. Falling back to hash-only dedup. Error: %s",
                    model_name,
                    exc,
                )
                cls._model_cache[model_name] = None
                return None

    def compute_embedding(self, text):
        if not self.model:
            return None
        try:
            return self.model.encode(text, convert_to_numpy=True)
        except Exception as exc:
            logger.warning("JD embedding failed; semantic dedup skipped: %s", exc)
            return None

    def find_similar(self, new_text, company_id=None):
        """
        Find semantically similar job descriptions.
        If company_id is provided, only search within that company's jobs (scoped deduplication).
        Otherwise, search globally (for backward compatibility).
        """
        new_emb = self.compute_embedding(new_text)
        if new_emb is None:
            return None, None
        # Ensure new_emb is float32
        new_emb = np.asarray(new_emb, dtype=np.float32)
        
        # Build filter: scope by company if provided
        filter_query = {}
        if company_id:
            filter_query["companyId"] = company_id
        
        # Fetch existing embeddings from DB with optional company filtering
        jobs = list(self.collection.find(filter_query, {"jobId": 1, "description": 1, "companyId": 1, "embedding": 1}))
        for job in jobs:
            if "embedding" in job:
                existing_emb = np.array(job["embedding"], dtype=np.float32)
                sim = util.cos_sim(new_emb, existing_emb).item()
                if sim >= self.similarity_threshold:
                    return job["jobId"], sim
        return None, None

    def store_embedding(self, job_id, embedding):
        if embedding is None:
            return
        self.collection.update_one({"jobId": job_id}, {"$set": {"embedding": embedding.tolist()}})
