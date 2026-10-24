import threading

import numpy as np
from sentence_transformers import SentenceTransformer

from app.config import settings

# The model is loaded ONE time and then reused for every request.
_model: SentenceTransformer | None = None
_lock = threading.Lock()


def get_model() -> SentenceTransformer:
    """Return the embedding model. It is loaded the first time this is called."""
    global _model
    if _model is None:
        with _lock:  # stops two requests from loading it at the same time
            if _model is None:
                _model = SentenceTransformer(
                    settings.EMBEDDING_MODEL, cache_folder=settings.MODEL_CACHE_DIR
                )
    return _model


def embed_texts(texts: list[str]) -> np.ndarray:
    """
    Turn a list of texts into vectors.

    Returns an array of shape (number_of_texts, 384), type float32.
    Vectors are normalized (length 1), so a simple dot product between two
    vectors equals their cosine similarity.
    """
    if not texts:
        return np.empty((0, settings.EMBEDDING_DIM), dtype="float32")

    vectors = get_model().encode(
        texts,
        batch_size=settings.EMBEDDING_BATCH_SIZE,
        convert_to_numpy=True,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    return vectors.astype("float32")


def embed_query(question: str) -> np.ndarray:
    """Embed one question. Returns shape (1, 384), which is what FAISS expects."""
    return embed_texts([question])
