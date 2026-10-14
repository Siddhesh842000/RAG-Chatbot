import re

from fastapi import Header, HTTPException

from app.services.vector_service import DEFAULT_SESSION

_SESSION_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def get_session_id(x_session_id: str | None = Header(default=None)) -> str:
    """
    Read the visitor's session id from the X-Session-ID header.
    Each visitor gets their own document. Without a header we use "default".
    """
    if not x_session_id:
        return DEFAULT_SESSION
    if not _SESSION_PATTERN.match(x_session_id):
        raise HTTPException(
            status_code=400,
            detail="Invalid X-Session-ID header. Use 1-64 letters, numbers, - or _.",
        )
    return x_session_id
