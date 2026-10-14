"""
Phase 4 test: embeddings.

Run from the backend folder:
    python test_embeddings.py

The first run downloads the model (about 90 MB), so it can take a few minutes.
"""
import time
from pathlib import Path

import numpy as np

from app.config import settings
from app.services.chunk_service import chunk_pages
from app.services.embedding_service import embed_query, embed_texts, get_model
from app.services.pdf_service import extract_pages

BACKEND_DIR = Path(__file__).parent


def check(name: str, passed: bool, detail: str = "") -> bool:
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name} {detail}")
    return passed


def main() -> None:
    results = []
    dim = settings.EMBEDDING_DIM

    # ---- Test 1: load the model only once ----
    start = time.time()
    model = get_model()
    print(f"Model loaded in {time.time() - start:.1f} seconds\n")

    start = time.time()
    same_model = get_model() is model
    results.append(
        check("Model is loaded once and reused", same_model, f"(second call took {time.time() - start:.4f}s)")
    )

    # ---- Test 2: shape and type ----
    sent_a = "FAISS is a library for fast similarity search."
    sent_b = "FAISS finds vectors that are close to a query vector very quickly."
    sent_c = "I cooked pasta with tomato sauce for dinner yesterday."

    vectors = embed_texts([sent_a, sent_b, sent_c])
    print(f"Embedding shape: {vectors.shape}, type: {vectors.dtype}")
    print(f"First 5 numbers of sentence A: {np.round(vectors[0][:5], 4)}\n")

    results.append(check("Shape is (3, 384)", vectors.shape == (3, dim), f"(got {vectors.shape})"))
    results.append(check("Type is float32", vectors.dtype == np.float32))

    # ---- Test 3: vectors are normalized ----
    lengths = np.linalg.norm(vectors, axis=1)
    results.append(check("Every vector has length 1", bool(np.allclose(lengths, 1.0, atol=1e-4))))

    # ---- Test 4: similar meaning -> higher score ----
    sim_ab = float(vectors[0] @ vectors[1])
    sim_ac = float(vectors[0] @ vectors[2])
    print(f"Similarity A-B (same topic):      {sim_ab:.3f}")
    print(f"Similarity A-C (different topic): {sim_ac:.3f}\n")
    results.append(
        check("Same-topic sentences score higher", sim_ab > sim_ac + 0.2)
    )

    # ---- Test 5: empty input ----
    empty = embed_texts([])
    results.append(check("Empty list gives shape (0, 384)", empty.shape == (0, dim)))

    # ---- Test 6: one question ----
    results.append(check("embed_query gives shape (1, 384)", embed_query("test").shape == (1, dim)))

    # ---- Test 7: a preview of retrieval using sample.pdf ----
    sample = BACKEND_DIR / "sample.pdf"
    pages = extract_pages(sample.read_bytes(), sample.name)
    chunks = chunk_pages(pages)
    chunk_vectors = embed_texts([c["text"] for c in chunks])

    questions = [
        ("What is FAISS used for?", 2),
        ("Why does each chunk keep its page number?", 3),
        ("How does retrieval augmented generation work?", 1),
    ]
    print("Which page matches each question best?")
    for question, expected_page in questions:
        scores = chunk_vectors @ embed_query(question)[0]
        best = int(np.argmax(scores))
        found_page = chunks[best]["page"]
        print(f"  '{question}'")
        print(f"     scores by page: {[round(float(s), 3) for s in scores]} -> best page {found_page}")
        results.append(
            check(f"Best page for '{question}' is {expected_page}", found_page == expected_page)
        )

    print()
    print(f"{sum(results)} of {len(results)} checks passed")


if __name__ == "__main__":
    main()
