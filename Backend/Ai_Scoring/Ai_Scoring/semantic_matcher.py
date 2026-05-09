import json
import logging
import math
import os
import re
import urllib.request
from collections import Counter
from functools import lru_cache

logger = logging.getLogger(__name__)

# all-MiniLM-L6-v2 has a max_seq_length of 256 tokens (~1 500–2 000 chars).
# Passing longer strings only wastes tokeniser time and temporary tensor
# memory without improving the similarity result.
_MAX_SBERT_CHARS = 2000

# ── External API helpers ──────────────────────────────────────────────────────

def _openai_embed_pair(text1: str, text2: str, api_key: str, model: str = "text-embedding-3-small") -> tuple:
    """Return embeddings for two texts in a single OpenAI API call (batched)."""
    payload = json.dumps({
        "input": [text1[:8191], text2[:8191]],
        "model": model,
    }).encode()
    req = urllib.request.Request(
        "https://api.openai.com/v1/embeddings",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    items = sorted(data["data"], key=lambda x: x["index"])
    return items[0]["embedding"], items[1]["embedding"]


def _cohere_embed_pair(text1: str, text2: str, api_key: str, model: str = "embed-english-light-v3.0") -> tuple:
    """Return embeddings for two texts in a single Cohere API call (batched)."""
    payload = json.dumps({
        "texts": [text1[:2048], text2[:2048]],
        "model": model,
        "input_type": "search_document",
        "embedding_types": ["float"],
    }).encode()
    req = urllib.request.Request(
        "https://api.cohere.ai/v2/embed",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    floats = data["embeddings"]["float"]
    return floats[0], floats[1]


def _cosine_from_lists(a: list, b: list) -> float:
    """Cosine similarity between two equal-length lists of floats."""
    try:
        import numpy as np
        a_arr = np.asarray(a, dtype=np.float32)
        b_arr = np.asarray(b, dtype=np.float32)
        denom = float(np.linalg.norm(a_arr)) * float(np.linalg.norm(b_arr))
        if denom == 0:
            return 0.0
        return float(np.dot(a_arr, b_arr) / denom)
    except Exception:
        dot = sum(x * y for x, y in zip(a, b))
        mag_a = math.sqrt(sum(x * x for x in a))
        mag_b = math.sqrt(sum(y * y for y in b))
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)


def _tfidf_cosine(text1: str, text2: str) -> float:
    """Keyword-frequency cosine similarity — zero-dependency fallback."""
    def _tokenize(text: str) -> Counter:
        return Counter(re.findall(r"\b[a-z]{2,}\b", text.lower()))

    c1, c2 = _tokenize(text1), _tokenize(text2)
    vocab = set(c1) | set(c2)
    if not vocab:
        return 0.0
    dot = sum(c1[w] * c2[w] for w in vocab)
    mag1 = math.sqrt(sum(v * v for v in c1.values()))
    mag2 = math.sqrt(sum(v * v for v in c2.values()))
    if mag1 == 0 or mag2 == 0:
        return 0.0
    return round(dot / (mag1 * mag2), 6)


# ── Local SBERT (optional — only when sentence-transformers is installed) ─────

@lru_cache(maxsize=1)
def _get_model(model_name: str = "all-MiniLM-L6-v2"):
    """Load a local sentence-transformers model if the package is installed.

    Returns ``(model, util)`` on success, ``None`` if the package is absent.
    On Render deployments sentence-transformers is not installed; the function
    returns None silently so the API/TF-IDF fallback path is used instead.
    """
    try:
        from sentence_transformers import SentenceTransformer, util
        model = SentenceTransformer(model_name)
        return model, util
    except Exception:
        logger.debug("sentence-transformers not available — using API/TF-IDF fallback.")
        return None


# ── Provider-agnostic embedding ───────────────────────────────────────────────

def get_embedding(text: str) -> "list | None":
    """Return a text embedding using the configured provider.

    Provider resolution order (first match wins):

    1. ``EMBEDDINGS_PROVIDER=openai``  *or* ``OPENAI_API_KEY`` is set
       → OpenAI ``text-embedding-3-small`` (1 536 dims)
    2. ``EMBEDDINGS_PROVIDER=cohere``  *or* ``COHERE_API_KEY`` is set
       → Cohere ``embed-english-light-v3.0`` (384 dims)
    3. ``sentence-transformers`` is installed
       → local ``all-MiniLM-L6-v2`` (384 dims)
    4. Returns ``None`` — caller falls back to TF-IDF cosine.

    Pin the provider explicitly with ``EMBEDDINGS_PROVIDER=openai|cohere|local``.
    """
    provider = os.getenv("EMBEDDINGS_PROVIDER", "").lower()
    openai_key = os.getenv("OPENAI_API_KEY", "")
    cohere_key = os.getenv("COHERE_API_KEY", "")

    if provider == "openai":
        if not openai_key:
            logger.warning(
                "EMBEDDINGS_PROVIDER=openai is set but OPENAI_API_KEY is empty; "
                "falling back to next available provider."
            )
        else:
            try:
                payload = json.dumps({"input": text[:8191], "model": "text-embedding-3-small"}).encode()
                req = urllib.request.Request(
                    "https://api.openai.com/v1/embeddings",
                    data=payload,
                    headers={"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"},
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return json.loads(resp.read())["data"][0]["embedding"]
            except Exception:
                logger.exception("OpenAI embedding failed; trying next provider")

    if provider == "cohere":
        if not cohere_key:
            logger.warning(
                "EMBEDDINGS_PROVIDER=cohere is set but COHERE_API_KEY is empty; "
                "falling back to next available provider."
            )
        else:
            try:
                payload = json.dumps({
                    "texts": [text[:2048]], "model": "embed-english-light-v3.0",
                    "input_type": "search_document", "embedding_types": ["float"],
                }).encode()
                req = urllib.request.Request(
                    "https://api.cohere.ai/v2/embed",
                    data=payload,
                    headers={"Authorization": f"Bearer {cohere_key}", "Content-Type": "application/json"},
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return json.loads(resp.read())["embeddings"]["float"][0]
            except Exception:
                logger.exception("Cohere embedding failed; trying next provider")

    # Auto-detect: try OpenAI then Cohere by key presence (no explicit provider pinned)
    if not provider:
        if openai_key:
            try:
                payload = json.dumps({"input": text[:8191], "model": "text-embedding-3-small"}).encode()
                req = urllib.request.Request(
                    "https://api.openai.com/v1/embeddings",
                    data=payload,
                    headers={"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"},
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return json.loads(resp.read())["data"][0]["embedding"]
            except Exception:
                logger.exception("OpenAI embedding failed; trying next provider")
        if cohere_key:
            try:
                payload = json.dumps({
                    "texts": [text[:2048]], "model": "embed-english-light-v3.0",
                    "input_type": "search_document", "embedding_types": ["float"],
                }).encode()
                req = urllib.request.Request(
                    "https://api.cohere.ai/v2/embed",
                    data=payload,
                    headers={"Authorization": f"Bearer {cohere_key}", "Content-Type": "application/json"},
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    return json.loads(resp.read())["embeddings"]["float"][0]
            except Exception:
                logger.exception("Cohere embedding failed; trying next provider")

    # Local SBERT (dev fallback)
    if provider in ("", "local"):
        bundle = _get_model()
        if bundle is not None:
            model, _ = bundle
            try:
                return model.encode(text, convert_to_numpy=True).tolist()
            except Exception:
                logger.exception("Local SBERT embedding failed")

    return None


def _get_similarity_embeddings(text1: str, text2: str) -> "tuple[list, list] | tuple[None, None]":
    """Return embeddings for two texts using a single batched API call where supported.

    Batching avoids sending two separate HTTP requests for the common case of
    computing similarity between a resume and a job description.
    Falls back to two individual ``get_embedding`` calls when batching is not
    possible (e.g. local SBERT path).
    """
    provider = os.getenv("EMBEDDINGS_PROVIDER", "").lower()
    openai_key = os.getenv("OPENAI_API_KEY", "")
    cohere_key = os.getenv("COHERE_API_KEY", "")

    if provider == "openai" or (not provider and openai_key):
        if openai_key:
            try:
                e1, e2 = _openai_embed_pair(text1, text2, openai_key)
                return e1, e2
            except Exception:
                logger.exception("Batched OpenAI embedding failed; trying next provider")

    if provider == "cohere" or (not provider and cohere_key):
        if cohere_key:
            try:
                e1, e2 = _cohere_embed_pair(text1, text2, cohere_key)
                return e1, e2
            except Exception:
                logger.exception("Batched Cohere embedding failed; trying next provider")

    # Local SBERT or no provider — fall back to individual calls
    e1 = get_embedding(text1)
    e2 = get_embedding(text2)
    if e1 is not None and e2 is not None:
        return e1, e2
    return None, None


def semantic_similarity_score(resume_text: str, job_description: str) -> float:
    """Compute semantic similarity in [0, 1] between a resume and a job description.

    Uses a single batched API call when possible (OpenAI/Cohere) to reduce
    latency and cost. Falls back to TF-IDF cosine when no provider is available.

    Provider order:

    1. OpenAI embeddings  (``OPENAI_API_KEY``)
    2. Cohere embeddings  (``COHERE_API_KEY``)
    3. Local sentence-transformers (if installed)
    4. TF-IDF keyword cosine  (always available — zero extra dependencies)
    """
    resume_text = (resume_text or "").strip()[:_MAX_SBERT_CHARS]
    job_description = (job_description or "").strip()[:_MAX_SBERT_CHARS]
    if not resume_text or not job_description:
        return 0.0

    try:
        r_emb, j_emb = _get_similarity_embeddings(resume_text, job_description)
        if r_emb is not None and j_emb is not None:
            sim = _cosine_from_lists(r_emb, j_emb)
            return round(max(0.0, min(float(sim), 1.0)), 6)
    except Exception:
        logger.exception("Embedding-based similarity failed; falling back to TF-IDF")

    return _tfidf_cosine(resume_text, job_description)
