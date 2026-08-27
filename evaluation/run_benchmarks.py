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

        if sample.get("unanswerable", False):
            refusal_phrases = [
                "not available",
                "unavailable",
                "does not contain",
                "does not mention",
                "doesn't mention",
                "does not explicitly mention",
                "doesn't explicitly mention",
                "not explicitly stated",
                "not explicitly mentioned",
                "not mentioned",
                "not specified",
                "not provided",
                "no information",
                "no information provided",
                "not covered",
                "cannot be determined",
                "unable to determine",
            ]
            answer_lower = gen_answer.lower()
            correctly_refused = any(
                phrase in answer_lower for phrase in refusal_phrases
            )

            results.append({
                "id": sample["id"],
                "query": query,
                "category": sample.get("category", "uncategorized"),
                "generated_answer": gen_answer,
                "faithfulness": None,
                "answer_relevance": None,
                "context_precision": None,
                "context_recall": None,
                "refusal_correct": correctly_refused,
                "reasoning": (
                    "Correctly declined to answer (refusal detected)."
                    if correctly_refused
                    else
                    "Should have declined but did not "
                    "(no refusal language detected) - possible hallucination."
                ),
                "latency_ms": elapsed_ms,
                "citations_count": len(final_state.get("verified_citations", [])),
                "critic_verdict": final_state.get("critic_verdict", "PASS"),
            })

            print(
                f"  [{idx:02d}/{len(test_samples):02d}] "
                f"'{query[:40]}...' -> Unanswerable check: "
                f"{'PASS' if correctly_refused else 'FAIL'} | "
                f"{elapsed_ms:.1f}ms"
            )
            continue

        # LLM-as-a-judge scoring
        try:
            metrics: BenchmarkMetrics = judge.evaluate_sample(
                query=query,
                retrieved_contexts=retrieved_contexts,
                generated_answer=gen_answer,
                ground_truth=ground_truth
            )
        except Exception as e:
            print(f"  [{idx:02d}/{len(test_samples):02d}] JUDGE FAILED for '{sample['id']}': {e}")
            results.append({
                "id": sample["id"],
                "query": query,
                "category": sample.get("category", "uncategorized"),
                "generated_answer": gen_answer,
                "faithfulness": 0.0,
                "answer_relevance": 0.0,
                "context_precision": 0.0,
                "context_recall": 0.0,
                "reasoning": f"JUDGE FAILED: {e}",
                "latency_ms": elapsed_ms,
                "citations_count": len(final_state.get("verified_citations", [])),
                "critic_verdict": final_state.get("critic_verdict", "PASS"),
            })
            continue

        results.append({
            "id": sample["id"],
            "query": query,
            "category": sample.get("category", "uncategorized"),
            "generated_answer": gen_answer,
            "faithfulness": metrics.faithfulness,
            "answer_relevance": metrics.answer_relevance,
            "context_precision": metrics.context_precision,
            "context_recall": metrics.context_recall,
            "reasoning": metrics.reasoning,
            "latency_ms": elapsed_ms,
            "citations_count": len(final_state.get("verified_citations", [])),
            "critic_verdict": final_state.get("critic_verdict", "PASS"),
        })

        print(f"  [{idx:02d}/{len(test_samples):02d}] '{query[:40]}...' -> Faithfulness: {metrics.faithfulness:.2f} | Precision: {metrics.context_precision:.2f} | {elapsed_ms:.1f}ms")

    # 4. Compute Aggregate Statistics
    answerable_results = [
        r for r in results if r.get("refusal_correct") is None
    ]

    unanswerable_results = [
        r for r in results if r.get("refusal_correct") is not None
    ]

    avg_faithfulness = float(
        np.mean([r["faithfulness"] for r in answerable_results])
    )
    avg_relevance = float(
        np.mean([r["answer_relevance"] for r in answerable_results])
    )
    avg_precision = float(
        np.mean([r["context_precision"] for r in answerable_results])
    )
    avg_recall = float(
        np.mean([r["context_recall"] for r in answerable_results])
    )

    refusal_accuracy = (
        float(np.mean([r["refusal_correct"] for r in unanswerable_results]))
        if unanswerable_results
        else None
    )

    p50_latency = float(np.percentile(latencies_ms, 50))
    p90_latency = float(np.percentile(latencies_ms, 90))
    p99_latency = float(np.percentile(latencies_ms, 99))

    # Per-category breakdown
    categories = sorted(set(r["category"] for r in results))
    category_stats = {}

    for cat in categories:
        cat_results = [r for r in results if r["category"] == cat]
        cat_answerable = [
            r for r in cat_results if r.get("refusal_correct") is None
        ]
        cat_unanswerable = [
            r for r in cat_results if r.get("refusal_correct") is not None
        ]

        category_stats[cat] = {
            "count": len(cat_results),
            "answerable_count": len(cat_answerable),
            "unanswerable_count": len(cat_unanswerable),
            "avg_faithfulness": (
                float(np.mean([r["faithfulness"] for r in cat_answerable]))
                if cat_answerable
                else None
            ),
            "avg_recall": (
                float(np.mean([r["context_recall"] for r in cat_answerable]))
                if cat_answerable
                else None
            ),
            "refusal_accuracy": (
                float(np.mean([r["refusal_correct"] for r in cat_unanswerable]))
                if cat_unanswerable
                else None
            ),
        }

    # 5. Generate Markdown Report
    report_content = f"""# Enterprise Agentic Hybrid RAG - LLMOps Benchmark Report

Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}
Total Test Queries: {len(test_samples)} (single run, not averaged across multiple runs)
Source Documents: {len(list(docs_dir.glob('*.md')))} markdown files, {len(chunks)} chunks indexed
Question Type Breakdown: {', '.join(f"{cat}={category_stats[cat]['count']}" for cat in categories)}
Answerable Questions: {len(answerable_results)}
Unanswerable Questions: {len(unanswerable_results)}
Embedding Model: `{settings.EMBEDDING_MODEL}`
Reranker: `{settings.RERANKER_MODEL}`
Synthesis + Judge LLM: `{settings.OLLAMA_MODEL if settings.LLM_PROVIDER == "ollama" else settings.ANTHROPIC_MODEL}` (same model used for both - see Known Limitations)
Hardware: CPU-only local inference (no GPU acceleration)
Top-K Retrieval: `{settings.TOP_K_RETRIEVAL}`
Faithfulness Threshold: `{settings.FAITHFULNESS_THRESHOLD}`

---

## 1. Executive Summary Metrics

| Evaluation Metric | Target Threshold | Achieved Score | Status |
| :--- | :--- | :--- | :--- |
| **Faithfulness (Groundedness)** | >= 0.85 | **{avg_faithfulness:.3f}** | {'[PASS]' if avg_faithfulness >= 0.85 else '[FAIL]'} |
| **Answer Relevance** | >= 0.80 | **{avg_relevance:.3f}** | {'[PASS]' if avg_relevance >= 0.80 else '[FAIL]'} |
| **Context Precision@K** | >= 0.80 | **{avg_precision:.3f}** | {'[PASS]' if avg_precision >= 0.80 else '[FAIL]'} |
| **Context Recall** | >= 0.80 | **{avg_recall:.3f}** | {'[PASS]' if avg_recall >= 0.80 else '[FAIL]'} |
| **Refusal Accuracy** | 100% | **{refusal_accuracy:.3f}** | {'[PASS]' if refusal_accuracy is not None and refusal_accuracy >= 1.0 else '[FAIL]'} |

---

## 1b. Score Breakdown by Question Category

| Category | Count | Answerable | Unanswerable | Avg Faithfulness | Avg Recall | Refusal Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
"""
    for cat in categories:
        stats = category_stats[cat]

        faithfulness = (
            f"{stats['avg_faithfulness']:.3f}"
            if stats["avg_faithfulness"] is not None
            else "N/A"
        )
        recall = (
            f"{stats['avg_recall']:.3f}"
            if stats["avg_recall"] is not None
            else "N/A"
        )
        refusal = (
            f"{stats['refusal_accuracy']:.3f}"
            if stats["refusal_accuracy"] is not None
            else "N/A"
        )

        report_content += (
            f"| `{cat}` | {stats['count']} | "
            f"{stats['answerable_count']} | {stats['unanswerable_count']} | "
            f"{faithfulness} | {recall} | {refusal} |\n"
        )

    report_content += f"""
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
        faithfulness = (
            f"{r['faithfulness']:.2f}"
            if r["faithfulness"] is not None
            else "N/A"
        )
        precision = (
            f"{r['context_precision']:.2f}"
            if r["context_precision"] is not None
            else "N/A"
        )
        recall = (
            f"{r['context_recall']:.2f}"
            if r["context_recall"] is not None
            else "N/A"
        )

        report_content += (
            f"| `{r['id']}` | {r['query'][:40]}... | "
            f"`{faithfulness}` | `{precision}` | `{recall}` | "
            f"{r['latency_ms']:.0f}ms | {r['critic_verdict']} |\n"
        )

    report_content += "\n---\n\n## 4. Per-Query Reasoning (Judge Commentary)\n\n"
    for r in results:
        faithfulness = (
            f"{r['faithfulness']:.2f}"
            if r["faithfulness"] is not None
            else "N/A"
        )
        recall = (
            f"{r['context_recall']:.2f}"
            if r["context_recall"] is not None
            else "N/A"
        )

        report_content += (
            f"**`{r['id']}`** "
            f"({r.get('category', 'uncategorized')}) - "
            f"F:{faithfulness} R:{recall}\n"
        )
        report_content += f"- Query: {r['query']}\n"
        report_content += f"- Answer: {r.get('generated_answer', '')[:200]}\n"
        report_content += f"- Judge reasoning: {r.get('reasoning', '')}\n\n"

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
