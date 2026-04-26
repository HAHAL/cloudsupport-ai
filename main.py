from functools import lru_cache

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from rag_service import RAGService


app = FastAPI(
    title="CloudSupport AI",
    description="FastAPI backend for technical support RAG assistant.",
    version="0.1.0",
)


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=2, description="用户的技术支持问题")


class Reference(BaseModel):
    source: str
    category: str
    score: float | None = None
    page: int | None = None
    content_preview: str


class RetrievedContent(BaseModel):
    content: str
    source: str
    category: str
    score: float | None = None
    page: int | None = None


class ChatResponse(BaseModel):
    question: str
    category: str
    answer: str
    retrieved_contents: list[RetrievedContent]
    references: list[Reference]
    metadata: dict


@lru_cache(maxsize=1)
def get_rag_service() -> RAGService:
    """Create the RAG service once and reuse Chroma/LLM clients."""
    return RAGService()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    """Answer a technical support question through the RAG pipeline."""
    try:
        result = get_rag_service().answer(payload.question)
        return ChatResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
