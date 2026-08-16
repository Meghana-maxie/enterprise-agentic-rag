"""Local Cross-Encoder reranker using FlashRank (ms-marco-MiniLM-L-6-v2)."""

from typing import List, Dict, Any
from flashrank import Ranker, RerankRequest
from config.settings import settings


class LocalReranker:
    """Local, high-throughput Cross-Encoder reranker via FlashRank."""

    def __init__(self, model_name: str = settings.RERANKER_MODEL):
        self.model_name = model_name
        self.ranker = Ranker(model_name=self.model_name, cache_dir=str(settings.DATA_DIR / "flashrank_cache"))

    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_n: int = settings.TOP_K_RERANK
    ) -> List[Dict[str, Any]]:
        """Rerank a list of candidate documents against the user query."""
        if not documents:
            return []

        # Prepare FlashRank input schema
        passages = [
            {"id": d.get("chunk_id", str(i)), "text": d.get("content", ""), "meta": d}
            for i, d in enumerate(documents)
        ]

        rerank_request = RerankRequest(query=query, passages=passages)
        results = self.ranker.rerank(rerank_request)

        # Re-sort and slice to top_n
        reranked_docs: List[Dict[str, Any]] = []
        for item in results[:top_n]:
            orig_meta = item.get("meta", {})
            orig_meta["rerank_score"] = float(item.get("score", 0.0))
            reranked_docs.append(orig_meta)

        return reranked_docs
