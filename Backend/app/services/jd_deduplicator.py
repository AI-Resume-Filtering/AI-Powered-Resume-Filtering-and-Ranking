import logging
from sentence_transformers import SentenceTransformer, util
import numpy as np

logger = logging.getLogger(__name__)

class JobDescriptionDeduplicator:
    def __init__(self, collection, model_name="all-MiniLM-L6-v2", similarity_threshold=0.9):
        self.collection = collection
        self.model = SentenceTransformer(model_name)
        self.similarity_threshold = similarity_threshold

    def compute_embedding(self, text):
        return self.model.encode(text, convert_to_numpy=True)

    def find_similar(self, new_text, company_id=None):
        """
        Find semantically similar job descriptions.
        If company_id is provided, only search within that company's jobs (scoped deduplication).
        Otherwise, search globally (for backward compatibility).
        """
        new_emb = self.compute_embedding(new_text)
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
        self.collection.update_one({"jobId": job_id}, {"$set": {"embedding": embedding.tolist()}})
