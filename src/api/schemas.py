"""Pydantic schemas for FastAPI endpoints."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """User query input payload."""
    query: str = Field(..., min_length=1, description="Raw query string", example="What is the data retention policy?")


class CitationDetail(BaseModel):
    """Citation metadata returned to caller."""
    doc_name: str
    page_number: int
    matched_chunk_id: Optional[str] = None
    is_valid: bool = True


class QueryResponse(BaseModel):
    """Standardized response schema."""
    answer: str
    is_safe: bool
    refusal_reason: Optional[str] = None
    redacted_pii: List[str] = Field(default_factory=list)
    citations: List[CitationDetail] = Field(default_factory=list)
    faithfulness_score: float = 1.0
    critic_verdict: str = "PASS"
    execution_trace: List[str] = Field(default_factory=list)


class IngestResponse(BaseModel):
    """Response returned upon document ingestion."""
    status: str
    filename: str
    chunks_created: int
    dense_indexed: int
    bm25_indexed: int


class HealthResponse(BaseModel):
    """System health check response."""
    status: str
    version: str
    embedding_model: str
    reranker_model: str
    llm_provider: str
