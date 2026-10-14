import logging

from fastapi import APIRouter, Depends, HTTPException

from app.config import settings
from app.schemas import ChatRequest, ChatResponse, ClearResponse, Source
from app.services import vector_service
from app.services.embedding_service import embed_query
from app.services.llm_service import LLMError, generate_answer
from app.services.vector_service import VectorStoreNotFoundError
from app.utils.prompts import NOT_FOUND_MESSAGE
from app.utils.session import get_session_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["Chat"])


def _is_not_found(answer: str) -> bool:
    """True when the model answered with the fixed 'not found' sentence."""
    clean = answer.strip().rstrip(".").lower()
    return clean == NOT_FOUND_MESSAGE.rstrip(".").lower()


def _select_sources(results: list[dict]) -> list[dict]:
    """
    Choose which chunks to show as sources.

    The LLM reads all retrieved chunks, but weak matches would only confuse the
    reader. We keep the best chunk, plus any chunk whose score is close to it.
    Results are already sorted best first.
    """
    if not results:
        return []

    threshold = results[0]["score"] * settings.SOURCE_SCORE_RATIO
    return [r for i, r in enumerate(results) if i == 0 or r["score"] >= threshold]


@router.post("/chat", response_model=ChatResponse)
def ask_question(request: ChatRequest, session_id: str = Depends(get_session_id)):
    """Ask a question about the uploaded PDF."""
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # 1. Find the most relevant chunks
    try:
        question_vector = embed_query(question)
        results = vector_service.search(question_vector, settings.TOP_K, session_id)
    except VectorStoreNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception:
        logger.exception("Search failed")
        raise HTTPException(status_code=500, detail="Failed to search the document. Please try again.")

    # 2. Ask the LLM
    try:
        answer = generate_answer(question, results)
    except LLMError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    # 3. Sources are shown only when the document really answered the question
    found = not _is_not_found(answer)
    sources = []
    if found:
        sources = [
            Source(
                document=r["document"],
                page=r["page"],
                score=round(r["score"], 4),
                snippet=r["text"][:300] + ("..." if len(r["text"]) > 300 else ""),
            )
            for r in _select_sources(results)
        ]

    return ChatResponse(answer=answer, found=found, sources=sources)


@router.post("/clear", response_model=ClearResponse)
def clear_document(session_id: str = Depends(get_session_id)):
    """Delete the uploaded document for this visitor."""
    cleared = vector_service.clear_index(session_id)
    return ClearResponse(
        message="Document cleared." if cleared else "There was no document to clear.",
        cleared=cleared,
    )
