import logging
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.config import settings
from app.schemas import UploadResponse
from app.services import vector_service
from app.services.chunk_service import chunk_pages
from app.services.embedding_service import embed_texts
from app.services.pdf_service import (
    EmptyPDFError,
    InvalidPDFError,
    NoTextError,
    extract_pages,
)
from app.utils.session import get_session_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Upload"])


@router.post("/upload", response_model=UploadResponse)
def upload_pdf(
    file: UploadFile = File(...),
    session_id: str = Depends(get_session_id),
):
    """Upload a PDF: extract text, split into chunks, embed, and store in FAISS."""
    filename = Path(file.filename or "document.pdf").name[:200]

    # 1. File type
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF file.")

    # 2. File size (we never read more than the limit + 1 byte)
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    data = file.file.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File is too large. The maximum size is {settings.MAX_FILE_SIZE_MB} MB.",
        )

    # 3. Extract text
    try:
        pages = extract_pages(data, filename)
    except NoTextError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except (EmptyPDFError, InvalidPDFError) as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    if len(pages) > settings.MAX_PAGES:
        raise HTTPException(
            status_code=413,
            detail=f"The PDF has too many pages. The maximum is {settings.MAX_PAGES} pages.",
        )

    # 4. Chunk, embed, and store
    chunks = chunk_pages(pages)
    try:
        vectors = embed_texts([c["text"] for c in chunks])
        vector_service.build_index(chunks, vectors, session_id)
    except Exception:
        logger.exception("Failed to embed or index the document")
        raise HTTPException(status_code=500, detail="Failed to process the document. Please try again.")

    return UploadResponse(
        message="PDF uploaded and processed successfully.",
        filename=filename,
        pages=len(pages),
        chunks=len(chunks),
    )
