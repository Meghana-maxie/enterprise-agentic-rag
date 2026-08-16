import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Any

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import numpy as np
from src.ingestion.loaders import DocumentLoader
from src.ingestion.chunker import RecursiveChunker
from src.retrieval.hybrid_engine import HybridSearchEngine
from src.agents.graph import build_rag_graph
from src.agents.nodes import AgentNodeRunner
from src.evaluation.llm_judge import ClaudeLLMJudge, BenchmarkMetrics
from config.settings import settings


def run_benchmark_suite(
    golden_dataset_path: Path = Path(__file__).parent / "golden_dataset.json",
    docs_dir: Path = Path(__file__).parent / "sample_docs",
    report_output_path: Path = Path(__file__).parent / "evaluation_report.md"
) -> Dict[str, Any]:
    """Execute complete offline evaluation benchmark across the golden test suite."""
    print("=" * 70)
    print("[LLMOps] ENTERPRISE AGENTIC HYBRID RAG - OFFLINE BENCHMARK HARNESS")
    print("=" * 70)

    # 1. Ingest sample documents into hybrid indices
    print(f"\n[1/3] Ingesting evaluation documents from: {docs_dir}")
    pages = DocumentLoader.load_directory(docs_dir)
    chunker = RecursiveChunker()
    chunks = chunker.chunk_pages(pages)

    hybrid_engine = HybridSearchEngine()
    hybrid_engine.index_chunks(chunks)
    print(f"      [OK] Indexed {len(chunks)} chunks across Qdrant Dense & BM25 Sparse stores.")

    # 2. Build LangGraph and Judge
    node_runner = AgentNodeRunner(hybrid_engine=hybrid_engine)
    rag_graph = build_rag_graph(node_runner=node_runner)
    judge = ClaudeLLMJudge()

    # 3. Load golden dataset
    print(f"\n[2/3] Loading test queries from: {golden_dataset_path}")
    with open(golden_dataset_path, "r", encoding="utf-8") as f:
        test_samples = json.load(f)

    print(f"      [OK] Loaded {len(test_samples)} golden test triplets.\n")

    results: List[Dict[str, Any]] = []
    latencies_ms: List[float] = []

    print("[3/3] Executing pipeline & LLM-judge evaluations...")
    for idx, sample in enumerate(test_samples, start=1):
        query = sample["query"]
        ground_truth = sample["ground_truth"]

        # Run LangGraph pipeline with latency timing
        start_time = time.perf_counter()
        initial_state = {
            "raw_query": query,
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

        final_state = rag_graph.invoke(initial_state)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        latencies_ms.append(elapsed_ms)

        gen_answer = final_state.get("synthesized_answer", "")
        retrieved_contexts = [c.get("content", "") for c in final_state.get("reranked_chunks", [])]

        # LLM-as-a-judge scoring
        metrics: BenchmarkMetrics = judge.evaluate_sample(
            query=query,
            retrieved_contexts=retrieved_contexts,
            generated_answer=gen_answer,
            ground_truth=ground_truth
        )

        results.append({
            "id": sample["id"],
            "query": query,
            "faithfulness": metrics.faithfulness,
            "answer_relevance": metrics.answer_relevance,
            "context_precision": metrics.context_precision,
            "context_recall": metrics.context_recall,
            "latency_ms": elapsed_ms,
            "citations_count": len(final_state.get("verified_citations", [])),
            "critic_verdict": final_state.get("critic_verdict", "PASS"),
        })

        print(f"  [{idx:02d}/{len(test_samples):02d}] '{query[:40]}...' -> Faithfulness: {metrics.faithfulness:.2f} | Precision: {metrics.context_precision:.2f} | {elapsed_ms:.1f}ms")

    # 4. Compute Aggregate Statistics
    avg_faithfulness = float(np.mean([r["faithfulness"] for r in results]))
    avg_relevance = float(np.mean([r["answer_relevance"] for r in results]))
    avg_precision = float(np.mean([r["context_precision"] for r in results]))
    avg_recall = float(np.mean([r["context_recall"] for r in results]))

    p50_latency = float(np.percentile(latencies_ms, 50))
    p90_latency = float(np.percentile(latencies_ms, 90))
    p99_latency = float(np.percentile(latencies_ms, 99))

    # 5. Generate Markdown Report
    report_content = f"""# Enterprise Agentic Hybrid RAG - LLMOps Benchmark Report

Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}  
Total Test Queries: {len(test_samples)}  
Embedding Model: `{settings.EMBEDDING_MODEL}`  
Reranker: `{settings.RERANKER_MODEL}`  
LLM Provider: `{settings.OLLAMA_MODEL if settings.LLM_PROVIDER == "ollama" else settings.ANTHROPIC_MODEL}`

---

## 1. Executive Summary Metrics

| Evaluation Metric | Target Threshold | Achieved Score | Status |
| :--- | :--- | :--- | :--- |
| **Faithfulness (Groundedness)** | >= 0.85 | **{avg_faithfulness:.3f}** | {'[PASS]' if avg_faithfulness >= 0.85 else '[FAIL]'} |
| **Answer Relevance** | >= 0.80 | **{avg_relevance:.3f}** | {'[PASS]' if avg_relevance >= 0.80 else '[FAIL]'} |
| **Context Precision@K** | >= 0.80 | **{avg_precision:.3f}** | {'[PASS]' if avg_precision >= 0.80 else '[FAIL]'} |
| **Context Recall** | >= 0.80 | **{avg_recall:.3f}** | {'[PASS]' if avg_recall >= 0.80 else '[FAIL]'} |

---

## 2. Latency & Throughput Profile

| Percentile | Latency (ms) |
| :--- | :--- |
| **P50 (Median)** | **{p50_latency:.1f} ms** |
| **P90** | **{p90_latency:.1f} ms** |
| **P99** | **{p99_latency:.1f} ms** |

---

## 3. Detailed Query Breakdown

| ID | Query | Faithfulness | Precision | Recall | Latency | Critic |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
"""
    for r in results:
        report_content += f"| `{r['id']}` | {r['query'][:40]}... | `{r['faithfulness']:.2f}` | `{r['context_precision']:.2f}` | `{r['context_recall']:.2f}` | {r['latency_ms']:.0f}ms | {r['critic_verdict']} |\n"

    report_output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_output_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    print(f"\n[Done] Benchmark report generated at: {report_output_path}")
    print(f"Mean Faithfulness: {avg_faithfulness:.3f} | P50 Latency: {p50_latency:.1f}ms")

    return {
        "avg_faithfulness": avg_faithfulness,
        "avg_relevance": avg_relevance,
        "avg_precision": avg_precision,
        "avg_recall": avg_recall,
        "p50_latency": p50_latency,
        "p90_latency": p90_latency,
    }


if __name__ == "__main__":
    run_benchmark_suite()
