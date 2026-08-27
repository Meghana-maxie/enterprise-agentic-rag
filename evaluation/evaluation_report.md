# Enterprise Agentic Hybrid RAG - LLMOps Benchmark Report

Generated at: 2026-08-28 00:22:47
Total Test Queries: 18 (single run, not averaged across multiple runs)
Source Documents: 2 markdown files, 10 chunks indexed
Question Type Breakdown: adversarial_citation_stress=2, direct_lookup=8, distractor_heavy=2, multi_hop=2, paraphrased=2, unanswerable=2
Answerable Questions: 16
Unanswerable Questions: 2
Embedding Model: `BAAI/bge-small-en-v1.5`
Reranker: `ms-marco-MiniLM-L-12-v2`
Synthesis + Judge LLM: `llama3.2:3b` (same model used for both - see Known Limitations)
Hardware: CPU-only local inference (no GPU acceleration)
Top-K Retrieval: `12`
Faithfulness Threshold: `0.85`

---

## 1. Executive Summary Metrics

| Evaluation Metric | Target Threshold | Achieved Score | Status |
| :--- | :--- | :--- | :--- |
| **Faithfulness (Groundedness)** | >= 0.85 | **0.597** | [FAIL] |
| **Answer Relevance** | >= 0.80 | **0.791** | [FAIL] |
| **Context Precision@K** | >= 0.80 | **0.722** | [FAIL] |
| **Context Recall** | >= 0.80 | **0.558** | [FAIL] |
| **Refusal Accuracy** | 100% | **1.000** | [PASS] |

---

## 1b. Score Breakdown by Question Category

| Category | Count | Answerable | Unanswerable | Avg Faithfulness | Avg Recall | Refusal Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| `adversarial_citation_stress` | 2 | 2 | 0 | 0.125 | 0.000 | N/A |
| `direct_lookup` | 8 | 8 | 0 | 0.637 | 0.635 | N/A |
| `distractor_heavy` | 2 | 2 | 0 | 0.800 | 0.850 | N/A |
| `multi_hop` | 2 | 2 | 0 | 0.500 | 0.500 | N/A |
| `paraphrased` | 2 | 2 | 0 | 0.800 | 0.575 | N/A |
| `unanswerable` | 2 | 0 | 2 | N/A | N/A | 1.000 |

---

## 2. Latency & Throughput Profile

| Percentile | Latency (ms) |
| :--- | :--- |
| **P50 (Median)** | **40797.6 ms** |
| **P90** | **54244.1 ms** |
| **P99** | **56840.8 ms** |

---

## 3. Detailed Query Breakdown

| ID | Query | Faithfulness | Precision | Recall | Latency | Critic |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `eval_001` | What are the three primary active-active... | `0.50` | `0.25` | `0.50` | 37154ms | PASS |
| `eval_002` | What are the latency budgets for the int... | `0.67` | `0.93` | `0.93` | 22604ms | PASS |
| `eval_003` | What are the exact RTO and RPO targets d... | `0.80` | `0.60` | `0.80` | 23811ms | PASS |
| `eval_004` | How often are vector index backups taken... | `0.50` | `0.90` | `0.00` | 19778ms | PASS |
| `eval_005` | What encryption standard is required for... | `0.67` | `0.92` | `0.80` | 50183ms | PASS |
| `eval_006` | What is the maximum time-to-live (TTL) f... | `0.80` | `0.90` | `0.90` | 22020ms | PASS |
| `eval_007` | What is the data retention schedule for ... | `0.33` | `0.75` | `0.58` | 44441ms | FAIL |
| `eval_008` | What is the remediation SLA for critical... | `0.83` | `0.76` | `0.57` | 24191ms | PASS |
| `eval_009` | Which regions is the platform live in si... | `0.80` | `0.95` | `0.95` | 57121ms | FAIL |
| `eval_010` | How is data protected while it's sitting... | `0.80` | `0.60` | `0.20` | 55471ms | FAIL |
| `eval_011` | If a customer tenant's account is delete... | `0.75` | `0.95` | `0.90` | 49808ms | FAIL |
| `eval_012` | How does the 2-minute RTO for a full reg... | `0.25` | `0.50` | `0.10` | 47785ms | FAIL |
| `eval_013` | Specifically, what is the p99 latency bu... | `0.80` | `0.90` | `1.00` | 21292ms | PASS |
| `eval_014` | What is the remediation deadline specifi... | `0.80` | `0.90` | `0.70` | 20687ms | PASS |
| `eval_015` | What is the required SLA uptime percenta... | `N/A` | `N/A` | `N/A` | 49068ms | FAIL |
| `eval_016` | How many employees are required to compl... | `N/A` | `N/A` | `N/A` | 45958ms | FAIL |
| `eval_017` | According to the cloud architecture docu... | `0.25` | `0.75` | `0.00` | 21706ms | PASS |
| `eval_018` | Per the security compliance policy, what... | `0.00` | `0.00` | `0.00` | 53719ms | PASS |

---

## 4. Per-Query Reasoning (Judge Commentary)

**`eval_001`** (direct_lookup) - F:0.50 R:0.50
- Query: What are the three primary active-active cloud regions and their SLA uptime requirement?
- Answer: The three primary active-active cloud regions of the Global Cloud Platform are:

1. `us-east-1` (North Virginia)
2. `eu-west-1` (Ireland)
3. `ap-southeast-1` (Singapore)

Unfortunately, the provided c
- Judge reasoning: Contexts support most claims but lack specific SLA uptime requirement details

**`eval_002`** (direct_lookup) - F:0.67 R:0.93
- Query: What are the latency budgets for the internal API Gateway Router and Vector Database engine?
- Answer: The latency budget for the internal API Gateway Router is 15ms p99 latency, as specified in the [cloud_architecture.md, Page: 1].

For the Vector Database engine, the latency budget is 30ms p95 latenc
- Judge reasoning: Most claims supported, but one minor omission on context relevance

**`eval_003`** (direct_lookup) - F:0.80 R:0.80
- Query: What are the exact RTO and RPO targets during a total regional outage?
- Answer: Based on the provided context, the exact RTO and RPO targets during a total regional outage are:

- Recovery Time Objective (RTO): 2 minutes, as specified in the cloud architecture document [cloud_arc
- Judge reasoning: Generated answer strictly supported by context, but lacks surrounding details.

**`eval_004`** (direct_lookup) - F:0.50 R:0.00
- Query: How often are vector index backups taken and where are they stored?
- Answer: According to the enterprise knowledge base, asynchronous backups of vector indexes are taken every 4 hours and are stored in Amazon S3 Glacier Flexible Retrieval with a 30-day retention lock [cloud_ar
- Judge reasoning: Some facts are mentioned, but not all necessary details are present in the retrieved contexts

**`eval_005`** (direct_lookup) - F:0.67 R:0.80
- Query: What encryption standard is required for data at rest and how frequently are KMS keys rotated?
- Answer: **Encryption Standard for Data at Rest:**

Data at rest across all persistent storage volumes (EBS, S3, Qdrant Vector DB, RDS) must be encrypted using AES-256 with customer-managed keys (CMK) [cloud_a
- Judge reasoning: Generated answer mostly aligns with retrieved contexts, with minor omissions on KMS key rotation frequency.

**`eval_006`** (direct_lookup) - F:0.80 R:0.90
- Query: What is the maximum time-to-live (TTL) for service account IAM OIDC tokens?
- Answer: The maximum time-to-live (TTL) for service account IAM OIDC tokens is 1 hour, as stated in the security compliance guidelines [security_compliance.md:1].
- Judge reasoning: Answer directly addresses query, but lacks supporting evidence from retrieved contexts.

**`eval_007`** (direct_lookup) - F:0.33 R:0.58
- Query: What is the data retention schedule for API request logs in hot S3 vs Glacier Deep Archive?
- Answer: According to the enterprise knowledge base, the data retention schedule for API request logs in hot S3 storage is 90 days, followed by a transition to S3 Glacier Deep Archive for 7 years to comply wit
- Judge reasoning: Some context relevance, but not entirely accurate or comprehensive for the query

**`eval_008`** (direct_lookup) - F:0.83 R:0.57
- Query: What is the remediation SLA for critical severity vulnerabilities with CVSS 9.0-10.0?
- Answer: According to the Enterprise Security, Compliance & Data Governance Policy [doc_name: Page 1], critical severity vulnerabilities (CVSS score 9.0 - 10.0) must be mitigated and patched within 24 hours of
- Judge reasoning: The answer strictly supports the context, but recall could be improved.

**`eval_009`** (paraphrased) - F:0.80 R:0.95
- Query: Which regions is the platform live in simultaneously, and what's the yearly downtime cap needed to hit the uptime target?
- Answer: Based on the provided context, the Global Cloud Platform is live in the following three regions simultaneously: `us-east-1` (North Virginia), `eu-west-1` (Ireland), and `ap-southeast-1` (Singapore) [c
- Judge reasoning: Generated answer mostly supported by retrieved contexts, with minor contextual inaccuracy

**`eval_010`** (paraphrased) - F:0.80 R:0.20
- Query: How is data protected while it's sitting in storage, and on what schedule do the keys protecting it get swapped out?
- Answer: According to the Enterprise Security, Compliance & Data Governance Policy, data at rest across all persistent storage volumes must be encrypted using AES-256 with customer-managed keys (CMK) that are 
- Judge reasoning: Most answer facts support retrieved contexts, but some context information is not fully utilized.

**`eval_011`** (multi_hop) - F:0.75 R:0.90
- Query: If a customer tenant's account is deleted, how quickly must their vector embeddings be removed, and what database technology stores those vectors in the first place?
- Answer: Based on the provided context, the vector embeddings of a customer tenant's account are stored in the Qdrant Vector Database. According to [Source: security_compliance.md, Page: 1], these embeddings a
- Judge reasoning: Relevant contexts were mostly supported, but some minor details were missing from the generated answer.

**`eval_012`** (multi_hop) - F:0.25 R:0.10
- Query: How does the 2-minute RTO for a full regional outage compare to the patching deadline for a critical severity vulnerability?
- Answer: Unfortunately, the provided context does not directly compare the 2-minute RTO for a full regional outage to the patching deadline for a critical severity vulnerability.

The Recovery Time Objective (
- Judge reasoning: Failed to find direct comparison between RTO and patching deadline in retrieved contexts.

**`eval_013`** (distractor_heavy) - F:0.80 R:1.00
- Query: Specifically, what is the p99 latency budget for the Service-to-Service gRPC Mesh (Envoy), not the API Gateway or edge termination?
- Answer: According to the Enterprise Cloud Infrastructure & Architecture Specification [cloud_architecture.md:1], the p99 latency budget for the Service-to-Service gRPC Mesh (Envoy) is 5ms.
- Judge reasoning: The answer's faithfulness is high due to direct context support.

**`eval_014`** (distractor_heavy) - F:0.80 R:0.70
- Query: What is the remediation deadline specifically for High severity vulnerabilities (CVSS 7.0-8.9), as distinct from Critical severity ones?
- Answer: For High severity vulnerabilities (CVSS 7.0 - 8.9), the remediation deadline is 7 calendar days.
- Judge reasoning: The answer is mostly faithful to retrieved contexts, with minor contextual details missing

**`eval_015`** (unanswerable) - F:N/A R:N/A
- Query: What is the required SLA uptime percentage for tier-2 and tier-3 microservices?
- Answer: The required SLA uptime percentage for tier-2 and tier-3 microservices is not explicitly stated in the provided context. However, tier-1 core microservices are required to have a minimum service level
- Judge reasoning: Correctly declined to answer (refusal detected).

**`eval_016`** (unanswerable) - F:N/A R:N/A
- Query: How many employees are required to complete SOC-2 compliance training each year?
- Answer: Unfortunately, the provided context blocks do not contain information on the number of employees required to complete SOC-2 compliance training each year. The context focuses on security compliance, i
- Judge reasoning: Correctly declined to answer (refusal detected).

**`eval_017`** (adversarial_citation_stress) - F:0.25 R:0.00
- Query: According to the cloud architecture document, how often are third-party SOC-2 Type II audits conducted?
- Answer: According to the cloud architecture document, [cloud_architecture.md, Page: 1], third-party SOC-2 Type II audits are conducted annually in Q3.
- Judge reasoning: Only one correct reference, but no context mentions audit cadence

**`eval_018`** (adversarial_citation_stress) - F:0.00 R:0.00
- Query: Per the security compliance policy, what AWS EKS Kubernetes version and instance type do the autoscaling worker clusters run on?
- Answer: According to the security compliance policy, the autoscaling worker clusters run on Kubernetes (EKS v1.30) with Karpenter autoscaling nodes configured for AMD EPYC c6a.4xlarge compute instances [cloud
- Judge reasoning: Incorrectly cited context file, failing to provide the correct answer source.

