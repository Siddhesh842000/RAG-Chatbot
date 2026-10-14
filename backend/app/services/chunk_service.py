import re

from app.config import settings


def _split_long_text(text: str, chunk_size: int) -> list[str]:
    """Split one very long sentence into pieces at word boundaries."""
    pieces: list[str] = []
    current = ""

    for word in text.split(" "):
        # A single "word" longer than the limit (for example a long URL)
        while len(word) > chunk_size:
            if current:
                pieces.append(current)
                current = ""
            pieces.append(word[:chunk_size])
            word = word[chunk_size:]

        candidate = f"{current} {word}" if current else word
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            pieces.append(current)
            current = word

    if current:
        pieces.append(current)
    return pieces


def _split_into_units(text: str, chunk_size: int) -> list[str]:
    """Break text into sentences. Each unit is never longer than chunk_size."""
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    units: list[str] = []

    for part in parts:
        part = part.strip()
        if not part:
            continue
        if len(part) <= chunk_size:
            units.append(part)
        else:
            units.extend(_split_long_text(part, chunk_size))
    return units


def _get_overlap(text: str, overlap: int) -> str:
    """
    Take the last `overlap` characters of a finished chunk, but start at a
    clean place (a sentence start if possible, otherwise a word start).
    """
    if overlap <= 0 or not text:
        return ""

    tail = text[-overlap:]

    # Prefer to start at the beginning of a sentence
    match = re.search(r"(?<=[.!?])\s+", tail)
    if match:
        return tail[match.end():].strip()

    # Otherwise start at the next full word
    space = tail.find(" ")
    if space != -1:
        return tail[space + 1:].strip()

    return ""


def chunk_text(text: str, chunk_size: int, overlap: int) -> list[str]:
    """Split one text into chunks of at most `chunk_size` characters."""
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    chunks: list[str] = []
    current = ""

    for unit in _split_into_units(text, chunk_size):
        candidate = f"{current} {unit}" if current else unit

        if len(candidate) <= chunk_size:
            current = candidate
            continue

        # The unit does not fit: finish this chunk and start a new one
        chunks.append(current)
        overlap_text = _get_overlap(current, overlap)
        candidate = f"{overlap_text} {unit}" if overlap_text else unit
        current = candidate if len(candidate) <= chunk_size else unit

    if current:
        chunks.append(current)
    return chunks


def chunk_pages(
    pages: list[dict],
    chunk_size: int = settings.CHUNK_SIZE,
    overlap: int = settings.CHUNK_OVERLAP,
) -> list[dict]:
    """
    Turn the pages from pdf_service into chunks.

    Every page is chunked on its own, so each chunk belongs to exactly one
    page and keeps its page number and document name.

    Each chunk looks like:
        {"chunk_id": 0, "text": "...", "page": 3, "document": "example.pdf"}
    """
    chunks: list[dict] = []

    for page in pages:
        for text in chunk_text(page["text"], chunk_size, overlap):
            chunks.append(
                {
                    "chunk_id": len(chunks),
                    "text": text,
                    "page": page["page"],
                    "document": page["document"],
                }
            )
    return chunks
