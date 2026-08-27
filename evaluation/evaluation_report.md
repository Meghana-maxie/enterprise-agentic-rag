# Enterprise Agentic Hybrid RAG - LLMOps Benchmark Report

Generated at: 2026-08-27 13:13:54
Total Test Queries: 18 (single run, not averaged across multiple runs)
Source Documents: 2 markdown files, 10 chunks indexed
Question Type Breakdown: adversarial_citation_stress=2, direct_lookup=8, distractor_heavy=2, multi_hop=2, paraphrased=2, unanswerable=2
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
| **Faithfulness (Groundedness)** | >= 0.85 | **0.542** | [FAIL] |
| **Answer Relevance** | >= 0.80 | **0.789** | [FAIL] |
| **Context Precision@K** | >= 0.80 | **0.628** | [FAIL] |
| **Context Recall** | >= 0.80 | **0.531** | [FAIL] |

---

## 1b. Score Breakdown by Question Category

| Category | Count | Avg Faithfulness | Avg Recall |
| :--- | :--- | :--- | :--- |
| `adversarial_citation_stress` | 2 | 0.200 | 0.100 |
| `direct_lookup` | 8 | 0.604 | 0.519 |
| `distractor_heavy` | 2 | 0.300 | 0.350 |
| `multi_hop` | 2 | 0.365 | 0.400 |
| `paraphrased` | 2 | 0.600 | 0.850 |
| `unanswerable` | 2 | 1.000 | 1.000 |

---

## 2. Latency & Throughput Profile

| Percentile | Latency (ms) |
| :--- | :--- |
| **P50 (Median)** | **25890.4 ms** |
| **P90** | **48550.4 ms** |
| **P99** | **53567.6 ms** |

---

## 3. Detailed Query Breakdown

| ID | Query | Faithfulness | Precision | Recall | Latency | Critic |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `eval_001` | What are the three primary active-active... | `0.83` | `0.78` | `0.67` | 23704ms | PASS |
| `eval_002` | What are the latency budgets for the int... | `0.50` | `0.90` | `0.60` | 22579ms | PASS |
| `eval_003` | What are the exact RTO and RPO targets d... | `0.67` | `0.80` | `0.93` | 21935ms | PASS |
| `eval_004` | How often are vector index backups taken... | `0.50` | `0.25` | `0.00` | 36231ms | FAIL |
| `eval_005` | What encryption standard is required for... | `0.50` | `0.90` | `0.70` | 51549ms | PASS |
| `eval_006` | What is the maximum time-to-live (TTL) f... | `0.67` | `0.80` | `0.50` | 22235ms | PASS |
| `eval_007` | What is the data retention schedule for ... | `0.50` | `0.25` | `0.25` | 22058ms | PASS |
| `eval_008` | What is the remediation SLA for critical... | `0.66` | `0.72` | `0.50` | 20888ms | PASS |
| `eval_009` | Which regions is the platform live in si... | `0.80` | `0.70` | `0.90` | 24361ms | PASS |
| `eval_010` | How is data protected while it's sitting... | `0.40` | `0.80` | `0.80` | 47265ms | FAIL |
| `eval_011` | If a customer tenant's account is delete... | `0.33` | `0.00` | `0.00` | 43523ms | FAIL |
| `eval_012` | How does the 2-minute RTO for a full reg... | `0.40` | `0.80` | `0.80` | 53981ms | FAIL |
| `eval_013` | Specifically, what is the p99 latency bu... | `0.00` | `0.00` | `0.00` | 20959ms | PASS |
| `eval_014` | What is the remediation deadline specifi... | `0.60` | `0.80` | `0.70` | 27420ms | PASS |
| `eval_015` | What is the required SLA uptime percenta... | `1.00` | `1.00` | `1.00` | 46614ms | FAIL |
| `eval_016` | How many employees are required to compl... | `1.00` | `1.00` | `1.00` | 37522ms | FAIL |
| `eval_017` | According to the cloud architecture docu... | `0.00` | `0.00` | `0.00` | 19722ms | PASS |
| `eval_018` | Per the security compliance policy, what... | `0.40` | `0.80` | `0.20` | 44873ms | FAIL |

---

## 4. Per-Query Reasoning (Judge Commentary)

**`eval_001`** (direct_lookup) - F:0.83 R:0.67
- Query: What are the three primary active-active cloud regions and their SLA uptime requirement?
- Answer: The three primary active-active cloud regions for the Global Cloud Platform are:

1. `us-east-1` (North Virginia)
2. `eu-west-1` (Ireland)
3. `ap-southeast-1` (Singapore)

Their SLA uptime requirement
- Judge reasoning: Most claims in the answer are supported, but some context is missing for precision and recall.

**`eval_002`** (direct_lookup) - F:0.50 R:0.60
- Query: What are the latency budgets for the internal API Gateway Router and Vector Database engine?
- Answer: The latency budgets for the internal API Gateway Router and Vector Database engine are as follows:
- Internal API Gateway Router: 15ms p99 latency
- Vector Database Query Engine: 30ms p95 latency

Not
- Judge reasoning: Retrieved contexts are mostly relevant and faithful, but contain some irrelevant information.

**`eval_003`** (direct_lookup) - F:0.67 R:0.93
- Query: What are the exact RTO and RPO targets during a total regional outage?
- Answer: The exact RTO and RPO targets during a total regional outage are as follows:
- Recovery Time Objective (RTO): 2 minutes [cloud_architecture.md:1]
- Recovery Point Objective (RPO): 0 seconds for transa
- Judge reasoning: Most claims supported, but some minor contextual oversights exist.

**`eval_004`** (direct_lookup) - F:0.50 R:0.00
- Query: How often are vector index backups taken and where are they stored?
- Answer: Vector index backups are taken every 4 hours, as specified in the asynchronous backups of vector indexes, which are snapshotted in Amazon S3 Glacier Flexible Retrieval [cloud_architecture.md:1]. 

Unf
- Judge reasoning: Context lacks specific storage location for vector index backups, reducing faithfulness.

**`eval_005`** (direct_lookup) - F:0.50 R:0.70
- Query: What encryption standard is required for data at rest and how frequently are KMS keys rotated?
- Answer: **Encryption Standard for Data at Rest**

According to the Enterprise Security, Compliance & Data Governance Policy, data at rest across all persistent storage volumes (EBS, S3, Qdrant Vector DB, RDS)
- Judge reasoning: The answer partially aligns with the context, missing specific policy details

**`eval_006`** (direct_lookup) - F:0.67 R:0.50
- Query: What is the maximum time-to-live (TTL) for service account IAM OIDC tokens?
- Answer: The maximum time-to-live (TTL) for service account IAM OIDC tokens is 1 hour, as stated in the security compliance policy [security_compliance.md:1].
- Judge reasoning: Generated answer partially aligns with retrieved context on TTL for IAM OIDC tokens.

**`eval_007`** (direct_lookup) - F:0.50 R:0.25
- Query: What is the data retention schedule for API request logs in hot S3 vs Glacier Deep Archive?
- Answer: API request logs in hot S3 are retained for 90 days [security_compliance.md:1]. After this period, they are automatically transitioned to S3 Glacier Deep Archive for 7 years [security_compliance.md:1]
- Judge reasoning: Only part of the claim is strictly supported by the retrieved contexts

**`eval_008`** (direct_lookup) - F:0.66 R:0.50
- Query: What is the remediation SLA for critical severity vulnerabilities with CVSS 9.0-10.0?
- Answer: According to [security_compliance.md:1], the remediation SLA for critical severity vulnerabilities with CVSS 9.0-10.0 is within 24 hours of discovery.
- Judge reasoning: The answer is mostly faithful, but lacks direct context for critical severity vulnerabilities.

**`eval_009`** (paraphrased) - F:0.80 R:0.90
- Query: Which regions is the platform live in simultaneously, and what's the yearly downtime cap needed to hit the uptime target?
- Answer: The Global Cloud Platform is live in three primary active-active regions simultaneously: `us-east-1` (North Virginia), `eu-west-1` (Ireland), and `ap-southeast-1` (Singapore). To hit the uptime target
- Judge reasoning: Most context support, but lacks detail in downtime calculation methodology

**`eval_010`** (paraphrased) - F:0.40 R:0.80
- Query: How is data protected while it's sitting in storage, and on what schedule do the keys protecting it get swapped out?
- Answer: According to the enterprise security policy, data at rest is protected using Customer-Managed Keys (CMK) rotated automatically every 90 days via AWS KMS [security_compliance.md:1]. The keys protecting
- Judge reasoning: Generated answer partially aligns with context, but lacks specificity on key rotation schedule

**`eval_011`** (multi_hop) - F:0.33 R:0.00
- Query: If a customer tenant's account is deleted, how quickly must their vector embeddings be removed, and what database technology stores those vectors in the first place?
- Answer: According to the provided context, if a customer tenant's account is deleted, their vector embeddings are hard-deleted within 24 hours [security_compliance.md:1]. As for the database technology that s
- Judge reasoning: Some claim lack direct support from retrieved contexts and contain unnecessary information.

**`eval_012`** (multi_hop) - F:0.40 R:0.80
- Query: How does the 2-minute RTO for a full regional outage compare to the patching deadline for a critical severity vulnerability?
- Answer: The 2-minute RTO for a full regional outage and the patching deadline for a critical severity vulnerability differ in terms of timeframes.

The 2-minute RTO for a full regional outage is a recovery ti
- Judge reasoning: Generated answer only partially supports retrieved context's critical vulnerability patching deadline

**`eval_013`** (distractor_heavy) - F:0.00 R:0.00
- Query: Specifically, what is the p99 latency budget for the Service-to-Service gRPC Mesh (Envoy), not the API Gateway or edge termination?
- Answer: The p99 latency budget for the Service-to-Service gRPC Mesh (Envoy) is 5ms, as stated in [cloud_architecture.md:1].
- Judge reasoning: Generated answer claims not supported by retrieved contexts, indicating a lack of factual basis

**`eval_014`** (distractor_heavy) - F:0.60 R:0.70
- Query: What is the remediation deadline specifically for High severity vulnerabilities (CVSS 7.0-8.9), as distinct from Critical severity ones?
- Answer: The remediation deadline for High severity vulnerabilities (CVSS 7.0-8.9) is 7 calendar days.

[RATIONALE]: According to the [Source: security_compliance.md, Page: 1], High severity vulnerabilities wi
- Judge reasoning: The generated answer directly matches the context, but lacks supporting context for critical vulnerabilities.

**`eval_015`** (unanswerable) - F:1.00 R:1.00
- Query: What is the required SLA uptime percentage for tier-2 and tier-3 microservices?
- Answer: According to the Enterprise Cloud Infrastructure & Architecture Specification ([cloud_architecture.md:1]), the required SLA uptime percentage for tier-2 and tier-3 microservices is not explicitly stat
- Judge reasoning: Correctly declined to answer (refusal detected).

**`eval_016`** (unanswerable) - F:1.00 R:1.00
- Query: How many employees are required to complete SOC-2 compliance training each year?
- Answer: The provided context blocks do not mention the number of employees required to complete SOC-2 compliance training each year. Therefore, the information is unavailable in the enterprise knowledge base.
- Judge reasoning: Correctly declined to answer (refusal detected).

**`eval_017`** (adversarial_citation_stress) - F:0.00 R:0.00
- Query: According to the cloud architecture document, how often are third-party SOC-2 Type II audits conducted?
- Answer: According to the cloud architecture document, [cloud_architecture.md, Page: 1], third-party SOC-2 Type II audits are conducted annually in Q3.
- Judge reasoning: Generated answer does not cite correct source document

**`eval_018`** (adversarial_citation_stress) - F:0.40 R:0.20
- Query: Per the security compliance policy, what AWS EKS Kubernetes version and instance type do the autoscaling worker clusters run on?
- Answer: According to the Enterprise Cloud Infrastructure & Architecture Specification [cloud_architecture.md:1], the autoscaling worker clusters run on Kubernetes (EKS v1.30) with Karpenter autoscaling nodes 
- Judge reasoning: Answer partially addresses query, missing critical detail about instance type

