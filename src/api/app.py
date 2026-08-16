"""FastAPI Application Entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import router
from config.settings import settings

app = FastAPI(
    title="Enterprise Agentic Hybrid RAG API",
    description="Production-grade LangGraph Multi-Agent RAG with Hybrid Search (Qdrant + BM25), Local Reranking, Guardrails, and NLI Critic.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for API consumption
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/")
async def root():
    """Root redirect with status message."""
    return {
        "message": "Enterprise Agentic Hybrid RAG API is live.",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.app:app", host=settings.API_HOST, port=settings.API_PORT, reload=True)
