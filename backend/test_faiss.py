"""
Phase 5 test: FAISS vector store and similarity search.

Run from the backend folder:
    python test_faiss.py
"""
from pathlib import Path

import numpy as np

from app.config import settings
from app.services import vector_service
from app.services.chunk_service import chunk_pages
from app.services.embedding_service import embed_query, embed_texts
from app.services.pdf_service import extract_pages
from app.services.vector_service import VectorStoreNotFoundError

BACKEND_DIR = Path(__file__).parent

TOPIC_PAGES = [
    "The Solar System has eight planets. Jupiter is the largest planet, and Mercury is the closest planet to the Sun.",
    "To make pasta, boil water, add salt, and cook the noodles for ten minutes. Serve with tomato sauce and cheese.",
    "A football match has two teams of eleven players. A game lasts ninety minutes, split into two halves.",
    "Python is a programming language. A list stores many values, and a function lets you reuse code.",
    "The ocean covers most of the Earth. Whales are huge mammals, and coral reefs are home to many fish.",
    "In the Middle Ages, knights wore armor and lived in castles. Kings ruled kingdoms and peasants farmed the land.",
]

TOPIC_QUESTIONS = [
    ("Which planet is the biggest?", 1),
    ("How long should I cook noodles?", 2),
    ("How many players are in a football team?", 3),
    ("What does a function do in Python?", 4),
    ("What animals live in coral reefs?", 5),
    ("Where did knights live?", 6),
]


def check(name: str, passed: bool, detail: str = "") -> bool:
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name} {detail}")
    return passed


def main() -> None:
    results = []

    # ---- Prepare the sample.pdf chunks ----
    sample = BACKEND_DIR / "sample.pdf"
    sample_chunks = chunk_pages(extract_pages(sample.read_bytes(), sample.name))
    sample_vectors = embed_texts([c["text"] for c in sample_chunks])

    # ---- Test 1: build an index ----
    count = vector_service.build_index(sample_chunks, sample_vectors, "demo")
    results.append(check("Index is built with 3 chunks", count == 3, f"(got {count})"))
    results.append(check("has_index is True", vector_service.has_index("demo")))

    # ---- Test 2: search sample.pdf ----
    print("\nSearching sample.pdf:")
    for question, expected_page in [
        ("What is FAISS used for?", 2),
        ("Why does each chunk keep its page number?", 3),
        ("How does retrieval augmented generation work?", 1),
    ]:
        found = vector_service.search(embed_query(question), top_k=3, session_id="demo")
        print(f"  '{question}'")
        for r in found:
            print(f"     page {r['page']} | score {r['score']:.3f} | {r['text'][:50]}...")
        results.append(
            check(f"Top result for '{question}' is page {expected_page}", found[0]["page"] == expected_page)
        )

    # ---- Test 3: result format and order ----
    found = vector_service.search(embed_query("What is FAISS?"), top_k=3, session_id="demo")
    keys_ok = all({"text", "page", "document", "score", "chunk_id"} <= set(r) for r in found)
    scores = [r["score"] for r in found]
    print()
    results.append(check("Each result has text, page, document, score", keys_ok))
    results.append(check("Results are sorted best first", scores == sorted(scores, reverse=True)))

    # ---- Test 4: a bigger document with six different topics ----
    topic_pages = [
        {"text": t, "page": i + 1, "document": "topics.pdf"} for i, t in enumerate(TOPIC_PAGES)
    ]
    topic_chunks = chunk_pages(topic_pages)
    topic_vectors = embed_texts([c["text"] for c in topic_chunks])
    vector_service.build_index(topic_chunks, topic_vectors, "topics")

    print("\nSearching topics.pdf (6 different subjects):")
    for question, expected_page in TOPIC_QUESTIONS:
        found = vector_service.search(embed_query(question), top_k=3, session_id="topics")
        pages = [r["page"] for r in found]
        print(f"  '{question}' -> pages {pages}")
        results.append(
            check(f"Top result for '{question}' is page {expected_page}", found[0]["page"] == expected_page)
        )

    # ---- Test 5: top_k ----
    found = vector_service.search(embed_query("planets"), top_k=3, session_id="topics")
    results.append(check("top_k=3 returns 3 results", len(found) == 3))
    found = vector_service.search(embed_query("planets"), top_k=50, session_id="topics")
    results.append(check("top_k bigger than chunk count returns all 6", len(found) == 6))

    # ---- Test 6: searching a chunk's own text gives a score near 1 ----
    found = vector_service.search(embed_query(topic_chunks[1]["text"]), top_k=1, session_id="topics")
    results.append(
        check("A chunk's own text scores about 1.0", found[0]["page"] == 2 and found[0]["score"] > 0.99,
              f"(score {found[0]['score']:.3f})")
    )

    # ---- Test 7: sessions are separate ----
    found = vector_service.search(embed_query("What is FAISS used for?"), top_k=1, session_id="demo")
    results.append(check("Session 'demo' still has its own document", found[0]["document"] == "sample.pdf"))
    found = vector_service.search(embed_query("Which planet is the biggest?"), top_k=1, session_id="topics")
    results.append(check("Session 'topics' has its own document", found[0]["document"] == "topics.pdf"))

    # ---- Test 8: missing vector store ----
    try:
        vector_service.search(embed_query("hello"), session_id="never-uploaded")
        results.append(check("Missing store raises an error", False))
    except VectorStoreNotFoundError as exc:
        results.append(check("Missing store raises an error", True, f"-> {exc}"))

    # ---- Test 9: clear ----
    results.append(check("clear_index removes the index", vector_service.clear_index("demo") is True))
    results.append(check("has_index is False after clear", not vector_service.has_index("demo")))
    results.append(check("clear_index on a missing session returns False", vector_service.clear_index("demo") is False))

    # ---- Test 10: wrong input is rejected ----
    try:
        vector_service.build_index(sample_chunks, sample_vectors[:, :10], "bad")
        results.append(check("Wrong vector size is rejected", False))
    except ValueError:
        results.append(check("Wrong vector size is rejected", True))
    try:
        vector_service.build_index(sample_chunks[:2], sample_vectors, "bad")
        results.append(check("Chunk/vector count mismatch is rejected", False))
    except ValueError:
        results.append(check("Chunk/vector count mismatch is rejected", True))

    # ---- Test 11: old sessions are removed ----
    for i in range(settings.MAX_SESSIONS + 1):
        vector_service.build_index(sample_chunks, sample_vectors, f"user{i}")
    results.append(
        check(
            f"Only the newest {settings.MAX_SESSIONS} sessions are kept",
            not vector_service.has_index("user0")
            and vector_service.has_index(f"user{settings.MAX_SESSIONS}"),
        )
    )

    print()
    print(f"{sum(results)} of {len(results)} checks passed")


if __name__ == "__main__":
    main()
