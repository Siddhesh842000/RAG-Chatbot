import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routes import chat, upload
from app.services.embedding_service import get_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the embedding model in the background, so the server starts fast
    threading.Thread(target=get_model, daemon=True).start()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="Upload a PDF and ask questions about it.",
    lifespan=lifespan,
)

# Allow the frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(chat.router)


@app.get("/")
def root():
    return {"message": "RAG Chatbot API is running", "docs": "/docs"}


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.VERSION,
    }
