"""
Phase 2 test: PDF extraction.

Run from the backend folder:
    python test_pdf.py

If sample.pdf does not exist, this script creates a 3-page one for you.
"""
from pathlib import Path

import pymupdf

from app.services.pdf_service import (
    EmptyPDFError,
    InvalidPDFError,
    NoTextError,
    PDFError,
    extract_pages,
)

SAMPLE_PATH = Path(__file__).parent / "sample.pdf"

SAMPLE_PAGES = [
    "Page one: Introduction to RAG.\n\n"
    "Retrieval Augmented Generation (RAG) combines a search step with a language model. "
    "First the system finds the most relevant parts of a document. "
    "Then the language model writes an answer using only those parts.",
    "Page two: About FAISS.\n\n"
    "FAISS is a library made by Meta for fast similarity search. "
    "It stores embedding vectors and quickly finds the vectors closest to a question vector.",
    "Page three: About chunking.\n\n"
    "Chunking means splitting a long document into small pieces. "
    "Each chunk keeps its page number so the answer can show its source.",
]


def create_sample_pdf(path: Path) -> None:
    doc = pymupdf.open()
    for text in SAMPLE_PAGES:
        page = doc.new_page()
        page.insert_textbox(pymupdf.Rect(72, 72, 523, 770), text, fontsize=12)
    doc.save(str(path))
    doc.close()


def check(name: str, passed: bool, detail: str = "") -> bool:
    status = "PASS" if passed else "FAIL"
    print(f"[{status}] {name} {detail}")
    return passed


def expect_error(name: str, data: bytes, error_type: type) -> bool:
    try:
        extract_pages(data, "test.pdf")
    except error_type as exc:
        return check(name, True, f"-> {type(exc).__name__}: {exc}")
    except Exception as exc:
        return check(name, False, f"-> wrong error {type(exc).__name__}: {exc}")
    return check(name, False, "-> no error was raised")


def main() -> None:
    results = []

    # ---- Test 1: normal PDF ----
    if not SAMPLE_PATH.exists():
        create_sample_pdf(SAMPLE_PATH)
        print(f"Created {SAMPLE_PATH.name}\n")

    pages = extract_pages(SAMPLE_PATH.read_bytes(), SAMPLE_PATH.name)
    print("Extracted pages:")
    for item in pages:
        preview = item["text"][:70].replace("\n", " ")
        print(f"  page {item['page']} | {item['document']} | {preview}...")
    print()

    results.append(check("Sample PDF has 3 pages", len(pages) == 3, f"(got {len(pages)})"))
    results.append(
        check("Page numbers are 1, 2, 3", [p["page"] for p in pages] == [1, 2, 3])
    )
    results.append(
        check("Page 2 mentions FAISS", "FAISS" in pages[1]["text"])
    )
    results.append(
        check("Document name is kept", all(p["document"] == "sample.pdf" for p in pages))
    )

    # ---- Test 2: bad inputs ----
    results.append(expect_error("Empty file", b"", EmptyPDFError))
    results.append(expect_error("Not a PDF (plain text)", b"hello world", InvalidPDFError))

    # Looks like a PDF at the start but is broken inside
    results.append(
        expect_error("Corrupted PDF", b"%PDF-1.4\nthis is not a real pdf", PDFError)
    )

    # A valid PDF whose page has no text
    blank = pymupdf.open()
    blank.new_page()
    blank_bytes = blank.tobytes()
    blank.close()
    results.append(expect_error("PDF with no text", blank_bytes, NoTextError))

    print()
    print(f"{sum(results)} of {len(results)} checks passed")


if __name__ == "__main__":
    main()
