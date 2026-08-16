"""Qdrant dense vector store utilizing FastEmbed (BAAI/bge-small-en-v1.5)."""

from typing import List, Dict, Any, Tuple
from pathlib import Path
from qdrant_client import QdrantClient
from qdrant_client.http import models
from fastembed import TextEmbedding
from src.ingestion.chunker import TextChunk
from config.settings import settings


class QdrantVectorStore:
    """Dense vector database client powered by FastEmbed and Qdrant."""

    def __init__(
        self,
        collection_name: str = settings.QDRANT_COLLECTION_NAME,
        storage_path: str = settings.QDRANT_STORAGE_PATH,
        url: str | None = settings.QDRANT_URL,
        embedding_model: str = settings.EMBEDDING_MODEL
    ):
        self.collection_name = collection_name
        self.embedding_model_name = embedding_model

        # Initialize FastEmbed ONNX model
        self.embedder = TextEmbedding(model_name=self.embedding_model_name)

        # Initialize Qdrant Client (local persistent storage or remote URL)
        if url:
            self.client = QdrantClient(url=url)
        else:
            Path(storage_path).mkdir(parents=True, exist_ok=True)
            self.client = QdrantClient(path=storage_path)

        self._ensure_collection()

    def _ensure_collection(self) -> None:
        """Create Qdrant collection if not already initialized."""
        collections = self.client.get_collections().collections
        existing_names = [c.name for c in collections]

        if self.collection_name not in existing_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=settings.EMBEDDING_DIM,
                    distance=models.Distance.COSINE
                )
            )

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Generate normalized vector embeddings for a list of strings."""
        if not texts:
            return []
        embeddings = list(self.embedder.embed(texts))
        return [emb.tolist() for emb in embeddings]

    def add_chunks(self, chunks: List[TextChunk]) -> int:
        """Embed and upsert chunks into Qdrant collection."""
        if not chunks:
            return 0

        texts = [chunk.content for chunk in chunks]
        embeddings = self.embed_texts(texts)

        points = [
            models.PointStruct(
                id=i,
                vector=embeddings[i],
                payload={
                    "chunk_id": chunks[i].chunk_id,
                    "content": chunks[i].content,
                    "doc_name": chunks[i].doc_name,
                    "page_number": chunks[i].page_number,
                    "char_start": chunks[i].char_start,
                    "char_end": chunks[i].char_end,
                    "metadata": chunks[i].metadata,
                }
            )
            for i in range(len(chunks))
        ]

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )
        return len(points)

    def search(self, query: str, limit: int = settings.TOP_K_RETRIEVAL) -> List[Dict[str, Any]]:
        """Perform dense cosine similarity search."""
        query_vector = self.embed_texts([query])[0]

        search_results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            limit=limit
        ).points

        results: List[Dict[str, Any]] = []
        for point in search_results:
            payload = point.payload or {}
            results.append({
                "chunk_id": payload.get("chunk_id", str(point.id)),
                "content": payload.get("content", ""),
                "doc_name": payload.get("doc_name", "unknown"),
                "page_number": payload.get("page_number", 1),
                "score": float(point.score),
                "metadata": payload.get("metadata", {}),
            })

        return results
