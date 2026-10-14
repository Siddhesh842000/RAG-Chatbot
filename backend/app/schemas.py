from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    message: str
    filename: str
    pages: int = Field(description="Number of pages that contain text")
    chunks: int = Field(description="Number of chunks created")


class ChatRequest(BaseModel):
    question: str = Field(max_length=1000, description="The question about the uploaded PDF")


class Source(BaseModel):
    document: str
    page: int
    score: float = Field(description="Similarity score, higher means more relevant")
    snippet: str = Field(description="Start of the chunk text")


class ChatResponse(BaseModel):
    answer: str
    found: bool = Field(description="False when the answer is not in the document")
    sources: list[Source]


class ClearResponse(BaseModel):
    message: str
    cleared: bool
