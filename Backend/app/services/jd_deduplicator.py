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

    def find_similar(self, new_text):
        new_emb = self.compute_embedding(new_text)
        # Ensure new_emb is float32
        new_emb = np.asarray(new_emb, dtype=np.float32)
        # Fetch all existing embeddings from DB
        jobs = list(self.collection.find({}, {"jobId": 1, "description": 1, "embedding": 1}))
        for job in jobs:
            if "embedding" in job:
                existing_emb = np.array(job["embedding"], dtype=np.float32)
                sim = util.cos_sim(new_emb, existing_emb).item()
                if sim >= self.similarity_threshold:
                    return job["jobId"], sim
        return None, None

    def store_embedding(self, job_id, embedding):
        self.collection.update_one({"jobId": job_id}, {"$set": {"embedding": embedding.tolist()}})
