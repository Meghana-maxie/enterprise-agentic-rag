# Enterprise Agentic Hybrid RAG - LLMOps Benchmark Report

Generated at: 2026-08-17 01:13:17  
Total Test Queries: 8  
Embedding Model: `BAAI/bge-small-en-v1.5`  
Reranker: `ms-marco-MiniLM-L-12-v2`  
LLM Provider: `llama3.2:3b`

---

## 1. Executive Summary Metrics

| Evaluation Metric | Target Threshold | Achieved Score | Status |
| :--- | :--- | :--- | :--- |
| **Faithfulness (Groundedness)** | >= 0.85 | **0.938** | [PASS] |
| **Answer Relevance** | >= 0.80 | **0.906** | [PASS] |
| **Context Precision@K** | >= 0.80 | **0.844** | [PASS] |
| **Context Recall** | >= 0.80 | **0.924** | [PASS] |

---

## 2. Latency & Throughput Profile

| Percentile | Latency (ms) |
| :--- | :--- |
| **P50 (Median)** | **35734.1 ms** |
| **P90** | **45057.7 ms** |
| **P99** | **45974.2 ms** |

---

## 3. Detailed Query Breakdown

| ID | Query | Faithfulness | Precision | Recall | Latency | Critic |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `eval_001` | What are the three primary active-active... | `0.95` | `0.85` | `0.92` | 32344ms | PASS |
| `eval_002` | What are the latency budgets for the int... | `0.85` | `0.80` | `0.95` | 19031ms | PASS |
| `eval_003` | What are the exact RTO and RPO targets d... | `0.95` | `0.85` | `0.92` | 42438ms | PASS |
| `eval_004` | How often are vector index backups taken... | `0.95` | `0.85` | `0.92` | 39124ms | FAIL |
| `eval_005` | What encryption standard is required for... | `0.95` | `0.85` | `0.92` | 46076ms | PASS |
| `eval_006` | What is the maximum time-to-live (TTL) f... | `0.95` | `0.85` | `0.92` | 18896ms | PASS |
| `eval_007` | What is the data retention schedule for ... | `0.95` | `0.85` | `0.92` | 44621ms | PASS |
| `eval_008` | What is the remediation SLA for critical... | `0.95` | `0.85` | `0.92` | 20816ms | PASS |
