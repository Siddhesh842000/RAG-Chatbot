import re

import pymupdf  # PyMuPDF


# ---------------------------------------------------------------
# Custom errors. The routes will turn these into HTTP responses
# later (Phase 7). Each one carries a clear message for the user.
# ---------------------------------------------------------------
class PDFError(Exception):
    """Base class for all PDF problems."""


class InvalidPDFError(PDFError):
    """The file is not a real PDF, is corrupted, or is password protected."""


class EmptyPDFError(PDFError):
    """The file is empty or the PDF has no pages."""


class NoTextError(PDFError):
    """The PDF has pages but no extractable text (for example, scanned images)."""


def clean_text(text: str) -> str:
    """Make PDF text tidy so chunking and embeddings work better."""
    # Remove null characters that some PDFs contain
    text = text.replace("\x00", "")

    # Join words that were split across lines: "informa-\ntion" -> "information"
    text = re.sub(r"-\n(?=[a-z])", "", text)

    # A single newline inside a paragraph is just a line wrap -> make it a space.
    # A blank line (two newlines) is a real paragraph break -> keep it.
    text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)

    # Collapse repeated spaces and tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Remove spaces around newlines and limit blank lines to one
    text = re.sub(r" ?\n ?", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def extract_pages(pdf_bytes: bytes, filename: str) -> list[dict]:
    """
    Read a PDF (given as bytes) and return one item per page that has text.

    Each item looks like:
        {"text": "...", "page": 3, "document": "example.pdf"}

    Page numbers start at 1, like in a normal PDF viewer.
    """
    if not pdf_bytes:
        raise EmptyPDFError("The uploaded file is empty.")

    # Every real PDF starts with "%PDF-"
    if not pdf_bytes.lstrip()[:5] == b"%PDF-":
        raise InvalidPDFError("The file is not a valid PDF.")

    pages: list[dict] = []

    try:
        doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
        with doc:
            if doc.needs_pass:
                raise InvalidPDFError("The PDF is password protected.")

            if doc.page_count == 0:
                raise EmptyPDFError("The PDF has no pages.")

            for page in doc:
                text = clean_text(page.get_text("text"))
                if text:  # skip pages with no text
                    pages.append(
                        {
                            "text": text,
                            "page": page.number + 1,  # PyMuPDF counts from 0
                            "document": filename,
                        }
                    )
    except PDFError:
        raise
    except Exception as exc:
        raise InvalidPDFError("The PDF is corrupted and could not be read.") from exc

    if not pages:
        raise NoTextError(
            "No text could be extracted. The PDF may contain only scanned images."
        )

    return pages
