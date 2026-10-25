import threading

import numpy as np
from fastembed import TextEmbedding

from app.config import settings

# The model is loaded ONE time and then reused for every request.
# We use fastembed: it runs the same all-MiniLM-L6-v2 model with ONNX Runtime,
# which needs far less memory than PyTorch (important on small free servers).
_model: TextEmbedding | None = None
_lock = threading.Lock()


def get_model() -> TextEmbedding:
    """Return the embedding model. It is loaded the first time this is called."""
    global _model
    if _model is None:
        with _lock:  # stops two requests from loading it at the same time
            if _model is None:
                _model = TextEmbedding(
                    model_name=settings.EMBEDDING_MODEL,
                    cache_dir=settings.MODEL_CACHE_DIR,
                    threads=settings.EMBEDDING_THREADS,
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

    vectors = np.array(
        list(get_model().embed(texts, batch_size=settings.EMBEDDING_BATCH_SIZE)),
        dtype="float32",
    )

    # Make every vector exactly length 1
    lengths = np.linalg.norm(vectors, axis=1, keepdims=True)
    lengths[lengths == 0] = 1.0
    return (vectors / lengths).astype("float32")


def embed_query(question: str) -> np.ndarray:
    """Embed one question. Returns shape (1, 384), which is what FAISS expects."""
    return embed_texts([question])
