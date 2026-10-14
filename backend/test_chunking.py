"""
Phase 3 test: chunking.

Run from the backend folder:
    python test_chunking.py

Optional: test with your own PDF
    python test_chunking.py mypdf.pdf
"""
import sys
from pathlib import Path

from app.config import settings
from app.services.chunk_service import chunk_pages, chunk_text
from app.services.pdf_service import extract_pages

BACKEND_DIR = Path(__file__).parent


def check(name: str, passed: bool, detail: str = "") -> bool:
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name} {detail}")
    return passed


def run_own_pdf(path: Path) -> None:
    pages = extract_pages(path.read_bytes(), path.name)
    chunks = chunk_pages(pages)
    lengths = [len(c["text"]) for c in chunks]

    print(f"{path.name}: {len(pages)} pages with text -> {len(chunks)} chunks")
    print(f"Chunk length: min {min(lengths)}, max {max(lengths)}, "
          f"average {sum(lengths) // len(lengths)}\n")
    for c in chunks[:3]:
        print(f"--- chunk {c['chunk_id']} (page {c['page']}, {len(c['text'])} chars)")
        print(c["text"], "\n")


def main() -> None:
    if len(sys.argv) > 1:
        run_own_pdf(Path(sys.argv[1]))
        return

    results = []
    size, overlap = settings.CHUNK_SIZE, settings.CHUNK_OVERLAP
    print(f"Settings: chunk_size={size}, overlap={overlap}\n")

    # ---- Test 1: the sample PDF from Phase 2 ----
    sample = BACKEND_DIR / "sample.pdf"
    pages = extract_pages(sample.read_bytes(), sample.name)
    chunks = chunk_pages(pages)
    print("Chunks from sample.pdf:")
    for c in chunks:
        print(f"  chunk {c['chunk_id']} | page {c['page']} | {len(c['text'])} chars")
    print()

    results.append(check("Sample PDF gives chunks", len(chunks) >= 3, f"(got {len(chunks)})"))
    results.append(check("All chunks <= chunk_size", all(len(c["text"]) <= size for c in chunks)))
    results.append(check("Pages 1, 2, 3 are all kept", {c["page"] for c in chunks} == {1, 2, 3}))
    results.append(check("Document name is kept", all(c["document"] == "sample.pdf" for c in chunks)))
    results.append(check("chunk_id is 0, 1, 2, ...", [c["chunk_id"] for c in chunks] == list(range(len(chunks)))))

    # ---- Test 2: a long page with many sentences ----
    long_text = " ".join(
        f"Sentence number {i} talks about retrieval and chunking in RAG."
        for i in range(1, 31)
    )
    long_chunks = chunk_pages([{"text": long_text, "page": 5, "document": "long.pdf"}])
    print(f"\nLong text: {len(long_text)} characters -> {len(long_chunks)} chunks")
    for c in long_chunks:
        print(f"  chunk {c['chunk_id']} | page {c['page']} | {len(c['text'])} chars")
    print()

    results.append(check("Long text is split into several chunks", len(long_chunks) >= 4))
    results.append(check("All long chunks <= chunk_size", all(len(c["text"]) <= size for c in long_chunks)))
    results.append(check("Page number kept on every long chunk", all(c["page"] == 5 for c in long_chunks)))

    overlap_ok = all(
        long_chunks[i + 1]["text"][:15] in long_chunks[i]["text"]
        for i in range(len(long_chunks) - 1)
    )
    results.append(check("Neighbouring chunks overlap", overlap_ok))

    # ---- Test 3: text with no punctuation at all ----
    plain = chunk_text("word " * 400, size, overlap)
    results.append(check("Text without sentences is still split", len(plain) > 1 and all(len(c) <= size for c in plain)))

    # ---- Test 4: one huge word (like a long URL) ----
    huge = chunk_text("x" * 1200, size, overlap)
    results.append(check("One huge word is split safely", all(len(c) <= size for c in huge), f"({len(huge)} pieces)"))

    # ---- Test 5: edge cases ----
    results.append(check("No pages -> no chunks", chunk_pages([]) == []))
    try:
        chunk_text("hello", 100, 100)
        results.append(check("Overlap >= size is rejected", False))
    except ValueError:
        results.append(check("Overlap >= size is rejected", True))

    print()
    print(f"{sum(results)} of {len(results)} checks passed")


if __name__ == "__main__":
    main()
