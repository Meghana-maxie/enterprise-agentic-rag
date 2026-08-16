"""FastAPI route handlers for query processing and document ingestion."""

import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, HTTPException
from src.api.schemas import QueryRequest, QueryResponse, IngestResponse, HealthResponse, CitationDetail
from src.agents.graph import build_rag_graph
from src.agents.nodes import AgentNodeRunner
from src.ingestion.loaders import DocumentLoader
from src.ingestion.chunker import RecursiveChunker
from src.retrieval.hybrid_engine import HybridSearchEngine
from config.settings import settings

router = APIRouter()

# Shared singletons
hybrid_engine = HybridSearchEngine()
node_runner = AgentNodeRunner(hybrid_engine=hybrid_engine)
rag_graph = build_rag_graph(node_runner=node_runner)
chunker = RecursiveChunker()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint providing model metadata."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        embedding_model=settings.EMBEDDING_MODEL,
        reranker_model=settings.RERANKER_MODEL,
        llm_provider="Anthropic (Claude 3.5 Haiku)"
    )


@router.post("/query", response_model=QueryResponse)
async def process_query(req: QueryRequest):
    """Execute end-to-end Agentic Hybrid RAG graph for a user query."""
    initial_state = {
        "raw_query": req.query,
        "sanitized_query": "",
        "is_safe": True,
        "refusal_reason": None,
        "redacted_pii": [],
        "route": "rag",
        "transformed_query": "",
        "retrieved_chunks": [],
        "reranked_chunks": [],
        "synthesized_answer": "",
        "verified_citations": [],
        "invalid_citations": [],
        "guardrail_warnings": [],
        "faithfulness_score": 1.0,
        "critic_verdict": "PASS",
        "critic_feedback": None,
        "retry_count": 0,
        "execution_trace": [],
    }

    try:
        final_state = rag_graph.invoke(initial_state)

        # Build response payload
        is_safe = final_state.get("is_safe", True)
        if not is_safe:
            return QueryResponse(
                answer="I cannot fulfill this request as it violates safety guidelines.",
                is_safe=False,
                refusal_reason=final_state.get("refusal_reason"),
                redacted_pii=final_state.get("redacted_pii", []),
                citations=[],
                faithfulness_score=0.0,
                critic_verdict="FAIL",
                execution_trace=final_state.get("execution_trace", [])
            )

        citations = [
            CitationDetail(
                doc_name=c.get("doc_name", "unknown"),
                page_number=c.get("page_number", 1),
                matched_chunk_id=c.get("matched_chunk_id"),
                is_valid=c.get("is_valid", True)
            )
            for c in final_state.get("verified_citations", [])
        ]

        return QueryResponse(
            answer=final_state.get("synthesized_answer", ""),
            is_safe=True,
            refusal_reason=None,
            redacted_pii=final_state.get("redacted_pii", []),
            citations=citations,
            faithfulness_score=final_state.get("faithfulness_score", 1.0),
            critic_verdict=final_state.get("critic_verdict", "PASS"),
            execution_trace=final_state.get("execution_trace", [])
        )
    except Exception as e:
        raise HTTPException(status_fmt=500, detail=f"Graph execution failure: {str(e)}")


@router.post("/ingest", response_model=IngestResponse)
async def ingest_document(file: UploadFile = File(...)):
    """Upload and index a document (.txt, .md, .pdf) into Dense Qdrant and Sparse BM25 indices."""
    temp_dir = settings.DATA_DIR / "uploads"
    temp_dir.mkdir(parents=True, exist_ok=True)
    temp_file_path = temp_dir / file.filename

    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        pages = DocumentLoader.load_file(temp_file_path)
        chunks = chunker.chunk_pages(pages)
        index_stats = hybrid_engine.index_chunks(chunks)

        return IngestResponse(
            status="success",
            filename=file.filename,
            chunks_created=len(chunks),
            dense_indexed=index_stats["dense_indexed"],
            bm25_indexed=index_stats["bm25_indexed"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")
    finally:
        if temp_file_path.exists():
            temp_file_path.unlink()
