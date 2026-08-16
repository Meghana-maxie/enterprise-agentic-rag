import sys
import time
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.retrieval.reranker import LocalReranker

def run_reranker_benchmark():
    reranker = LocalReranker(model_name="ms-marco-MiniLM-L-12-v2")

    # 10 document candidates per query
    sample_docs = [
        {"chunk_id": f"c_{i}", "content": f"Enterprise infrastructure specification and regional availability parameters for tier-{i} microservices."}
        for i in range(10)
    ]

    # Warmup run
    reranker.rerank("What is the SLA uptime for cloud regions?", sample_docs, top_n=4)

    # 10 distinct queries
    queries = [
        "What is the SLA uptime for cloud regions?",
        "What are the latency budgets for API Gateway?",
        "What are the RTO and RPO targets during failover?",
        "How often are vector index backups taken?",
        "What encryption standard is required for data at rest?",
        "What is the maximum time-to-live for IAM OIDC tokens?",
        "What is the data retention schedule for API request logs?",
        "What is the remediation SLA for critical severity vulnerabilities?",
        "How does Karpenter handle autoscaling on AMD EPYC nodes?",
        "What are the Zero-Trust Network Access and FIDO2 MFA rules?"
    ]

    latencies = []
    for q in queries:
        t0 = time.perf_counter()
        res = reranker.rerank(q, sample_docs, top_n=4)
        elapsed_ms = (time.perf_counter() - t0) * 1000.0
        latencies.append(elapsed_ms)
        print(f'Query: "{q[:45]}..." -> {elapsed_ms:.2f} ms')

    avg_ms = sum(latencies) / len(latencies)
    p50_ms = sorted(latencies)[len(latencies)//2]
    min_ms = min(latencies)
    max_ms = max(latencies)

    print("\n--- FlashRank (ms-marco-MiniLM-L-12-v2) Latency Benchmark (10 queries, 10 candidates -> top 4) ---")
    print(f"Mean Latency: {avg_ms:.2f} ms")
    print(f"Median (P50): {p50_ms:.2f} ms")
    print(f"Min Latency:  {min_ms:.2f} ms")
    print(f"Max Latency:  {max_ms:.2f} ms")

if __name__ == "__main__":
    run_reranker_benchmark()
