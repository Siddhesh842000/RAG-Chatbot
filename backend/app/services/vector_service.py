import threading
from collections import OrderedDict

import faiss
import numpy as np

from app.config import settings

# Used when the caller does not give a session id
DEFAULT_SESSION = "default"


class VectorStoreNotFoundError(Exception):
    """No document has been indexed for this session."""


class VectorStore:
    """
    One FAISS index plus the chunk information (text, page, document).

    FAISS only stores numbers, so we keep the chunk details in a list.
    Position 0 in the index matches position 0 in the list, and so on.
    """

    def __init__(self, dim: int):
        self.dim = dim
        # IndexFlatIP = exact search using the inner (dot) product.
        # Our vectors have length 1, so the dot product is the cosine similarity.
        self.index = faiss.IndexFlatIP(dim)
        self.chunks: list[dict] = []

    def add(self, chunks: list[dict], vectors: np.ndarray) -> None:
        if not chunks:
            raise ValueError("There are no chunks to index.")

        vectors = np.ascontiguousarray(vectors, dtype="float32")
        if vectors.ndim != 2 or vectors.shape[1] != self.dim:
            raise ValueError(
                f"Vectors must have shape (n, {self.dim}), got {vectors.shape}."
            )
        if len(chunks) != vectors.shape[0]:
            raise ValueError("The number of chunks and vectors must be the same.")

        self.index.add(vectors)
        self.chunks.extend(chunks)

    def search(self, query_vector: np.ndarray, top_k: int) -> list[dict]:
        """Return the top_k most similar chunks, best first, each with a score."""
        query_vector = np.ascontiguousarray(query_vector, dtype="float32")
        k = min(top_k, self.index.ntotal)  # cannot return more than we have

        scores, ids = self.index.search(query_vector, k)

        results = []
        for score, idx in zip(scores[0], ids[0]):
            if idx == -1:  # FAISS uses -1 for "no result"
                continue
            results.append({**self.chunks[idx], "score": float(score)})
        return results


# ---------------------------------------------------------------
# Stores live in memory, one per session (one per visitor).
# Only the newest MAX_SESSIONS are kept, so memory stays small.
# ---------------------------------------------------------------
_stores: "OrderedDict[str, VectorStore]" = OrderedDict()
_lock = threading.Lock()


def build_index(
    chunks: list[dict],
    vectors: np.ndarray,
    session_id: str = DEFAULT_SESSION,
) -> int:
    """Create a new index for this session (replacing any old one). Returns chunk count."""
    store = VectorStore(settings.EMBEDDING_DIM)
    store.add(chunks, vectors)

    with _lock:
        _stores.pop(session_id, None)
        _stores[session_id] = store
        while len(_stores) > settings.MAX_SESSIONS:
            _stores.popitem(last=False)  # remove the oldest session

    return store.index.ntotal


def search(
    query_vector: np.ndarray,
    top_k: int = settings.TOP_K,
    session_id: str = DEFAULT_SESSION,
) -> list[dict]:
    """Find the top_k chunks most similar to the question vector."""
    with _lock:
        store = _stores.get(session_id)
        if store is not None:
            _stores.move_to_end(session_id)  # mark as recently used

    if store is None:
        raise VectorStoreNotFoundError(
            "No document has been uploaded yet. Please upload a PDF first."
        )
    return store.search(query_vector, top_k)


def has_index(session_id: str = DEFAULT_SESSION) -> bool:
    with _lock:
        return session_id in _stores


def clear_index(session_id: str = DEFAULT_SESSION) -> bool:
    """Delete the index for this session. Returns True if one existed."""
    with _lock:
        return _stores.pop(session_id, None) is not None
