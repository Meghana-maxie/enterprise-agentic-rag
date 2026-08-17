"""LangGraph state schemas and data models."""

from typing import List, Dict, Any, Optional
from typing_extensions import TypedDict
from pydantic import BaseModel, Field


class ChunkPayload(BaseModel):
    """Normalized chunk representation passed across agent state transitions."""
    chunk_id: str
    content: str
    doc_name: str
    page_number: int
    score: float = 0.0
    rerank_score: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentState(TypedDict):
    """Complete LangGraph cyclic state schema."""
    # Query lifecycle
    raw_query: str
    sanitized_query: str
    is_safe: bool
    refusal_reason: Optional[str]
    redacted_pii: List[str]

    # Router & Query Evolution
    route: str  # "direct" | "rag"
    transformed_query: str

    # Retrieval State
    retrieved_chunks: List[Dict[str, Any]]
    reranked_chunks: List[Dict[str, Any]]

    # Synthesis & Citations
    synthesized_answer: str
    synthesis_failed: bool
    synthesis_error: Optional[str]
    verified_citations: List[Dict[str, Any]]
    invalid_citations: List[str]
    guardrail_warnings: List[str]

    # Critic & Feedback Loop
    faithfulness_score: float
    critic_verdict: str  # "PASS" | "FAIL"
    critic_feedback: Optional[str]
    retry_count: int

    # Execution Trace / Telemetry
    execution_trace: List[str]
