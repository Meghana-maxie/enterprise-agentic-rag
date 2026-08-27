# Enterprise Agentic Hybrid RAG - LLMOps Benchmark Report

Generated at: 2026-08-27 22:28:47
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
| **Faithfulness (Groundedness)** | >= 0.85 | **0.588** | [FAIL] |
| **Answer Relevance** | >= 0.80 | **0.726** | [FAIL] |
| **Context Precision@K** | >= 0.80 | **0.601** | [FAIL] |
| **Context Recall** | >= 0.80 | **0.457** | [FAIL] |
| **Refusal Accuracy** | 100% | **0.500** | [FAIL] |

---

## 1b. Score Breakdown by Question Category

| Category | Count | Answerable | Unanswerable | Avg Faithfulness | Avg Recall | Refusal Accuracy |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: |
| `adversarial_citation_stress` | 2 | 2 | 0 | 0.125 | 0.250 | N/A |
| `direct_lookup` | 8 | 8 | 0 | 0.664 | 0.520 | N/A |
| `distractor_heavy` | 2 | 2 | 0 | 0.775 | 0.500 | N/A |
| `multi_hop` | 2 | 2 | 0 | 0.335 | 0.000 | N/A |
| `paraphrased` | 2 | 2 | 0 | 0.815 | 0.825 | N/A |
| `unanswerable` | 2 | 0 | 2 | N/A | N/A | 0.500 |

---

## 2. Latency & Throughput Profile

| Percentile | Latency (ms) |
| :--- | :--- |
| **P50 (Median)** | **21130.0 ms** |
| **P90** | **38024.4 ms** |
| **P99** | **44686.1 ms** |

---

## 3. Detailed Query Breakdown

| ID | Query | Faithfulness | Precision | Recall | Latency | Critic |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `eval_001` | What are the three primary active-active... | `0.83` | `0.81` | `0.91` | 30368ms | PASS |
| `eval_002` | What are the latency budgets for the int... | `0.50` | `0.80` | `0.80` | 16115ms | PASS |
| `eval_003` | What are the exact RTO and RPO targets d... | `0.80` | `0.70` | `0.40` | 18863ms | PASS |
| `eval_004` | How often are vector index backups taken... | `0.80` | `0.70` | `0.95` | 31105ms | FAIL |
| `eval_005` | What encryption standard is required for... | `0.40` | `0.60` | `0.00` | 18392ms | PASS |
| `eval_006` | What is the maximum time-to-live (TTL) f... | `0.40` | `0.20` | `0.60` | 16465ms | PASS |
| `eval_007` | What is the data retention schedule for ... | `0.75` | `0.80` | `0.50` | 20018ms | PASS |
| `eval_008` | What is the remediation SLA for critical... | `0.83` | `0.50` | `0.00` | 18693ms | PASS |
| `eval_009` | Which regions is the platform live in si... | `0.83` | `0.95` | `0.90` | 24329ms | PASS |
| `eval_010` | How is data protected while it's sitting... | `0.80` | `0.95` | `0.75` | 45761ms | FAIL |
| `eval_011` | If a customer tenant's account is delete... | `0.67` | `0.50` | `0.00` | 37184ms | PASS |
| `eval_012` | How does the 2-minute RTO for a full reg... | `0.00` | `0.00` | `0.00` | 37419ms | FAIL |
| `eval_013` | Specifically, what is the p99 latency bu... | `0.80` | `0.40` | `0.50` | 19778ms | PASS |
| `eval_014` | What is the remediation deadline specifi... | `0.75` | `0.95` | `0.50` | 17463ms | PASS |
| `eval_015` | What is the required SLA uptime percenta... | `N/A` | `N/A` | `N/A` | 39438ms | FAIL |
| `eval_016` | How many employees are required to compl... | `N/A` | `N/A` | `N/A` | 32230ms | FAIL |
| `eval_017` | According to the cloud architecture docu... | `0.00` | `0.00` | `0.00` | 17523ms | PASS |
| `eval_018` | Per the security compliance policy, what... | `0.25` | `0.75` | `0.50` | 22242ms | PASS |

---

## 4. Per-Query Reasoning (Judge Commentary)

**`eval_001`** (direct_lookup) - F:0.83 R:0.91
- Query: What are the three primary active-active cloud regions and their SLA uptime requirement?
- Answer: The three primary active-active cloud regions and their SLA uptime requirement are as follows:

1.  **us-east-1** (North Virginia):
    The SLA uptime requirement is 99.99% with an annualized unplann
- Judge reasoning: Most claims supported, but SLA details might be slightly condensed.

**`eval_002`** (direct_lookup) - F:0.50 R:0.80
- Query: What are the latency budgets for the internal API Gateway Router and Vector Database engine?
- Answer: Based on the provided context, the latency budgets for the internal API Gateway Router and Vector Database engine are as follows:

- Internal API Gateway Router: 15ms p99 latency
- Vector Database Que
- Judge reasoning: Most claims in answer supported by contexts, but not all.

**`eval_003`** (direct_lookup) - F:0.80 R:0.40
- Query: What are the exact RTO and RPO targets during a total regional outage?
- Answer: The exact RTO and RPO targets during a total regional outage are as follows:

- Recovery Time Objective (RTO): 2 minutes, as stated in [cloud_architecture.md, Page: 1].
- Recovery Point Objective (RPO
- Judge reasoning: Most claims supported by contexts, but not all.

**`eval_004`** (direct_lookup) - F:0.80 R:0.95
- Query: How often are vector index backups taken and where are they stored?
- Answer: Vector index backups are taken asynchronously and snapshotted every 4 hours to Amazon S3 Glacier Flexible Retrieval, with a 30-day retention lock, as stated in the cloud architecture documentation [cl
- Judge reasoning: Most claims in the answer are partially supported by the contexts, lacking detail on 'asynchronous' aspect.

**`eval_005`** (direct_lookup) - F:0.40 R:0.00
- Query: What encryption standard is required for data at rest and how frequently are KMS keys rotated?
- Answer: The encryption standard required for data at rest is AES-256 with customer-managed keys (CMK) [security_compliance.md:1].

KMS keys are rotated automatically every 90 days via AWS KMS [security_compl
- Judge reasoning: Generated answer partially supports ground truth, lacking context on data encryption standards.

**`eval_006`** (direct_lookup) - F:0.40 R:0.60
- Query: What is the maximum time-to-live (TTL) for service account IAM OIDC tokens?
- Answer: The maximum time-to-live (TTL) for service account IAM OIDC tokens is 1 hour, as stated in [security_compliance.md, Page: 1].
- Judge reasoning: Contexts support most claims, but lack direct connection to user query.

**`eval_007`** (direct_lookup) - F:0.75 R:0.50
- Query: What is the data retention schedule for API request logs in hot S3 vs Glacier Deep Archive?
- Answer: The data retention schedule for API request logs in hot S3 is 90 days, followed by automated transition to S3 Glacier Deep Archive for 7 years. [security_compliance.md:3]

In contrast, asynchronous ba
- Judge reasoning: The generated answer mostly aligns with retrieved contexts, but lacks specific Glacier Deep Archive details

**`eval_008`** (direct_lookup) - F:0.83 R:0.00
- Query: What is the remediation SLA for critical severity vulnerabilities with CVSS 9.0-10.0?
- Answer: Critical severity vulnerabilities (CVSS score 9.0 - 10.0) must be mitigated and patched within 24 hours of discovery, as per the security compliance requirements [security_compliance.md:1].
- Judge reasoning: Contexts lack supporting information for critical severity vulnerabilities' remediation SLA specifics.

**`eval_009`** (paraphrased) - F:0.83 R:0.90
- Query: Which regions is the platform live in simultaneously, and what's the yearly downtime cap needed to hit the uptime target?
- Answer: The Global Cloud Platform is live in three primary active-active regions simultaneously: `us-east-1` (North Virginia), `eu-west-1` (Ireland), and `ap-southeast-1` (Singapore) [cloud_architecture.md:1]
- Judge reasoning: Answer mostly faithful, but lacks explicit yearly downtime threshold value.

**`eval_010`** (paraphrased) - F:0.80 R:0.75
- Query: How is data protected while it's sitting in storage, and on what schedule do the keys protecting it get swapped out?
- Answer: According to the Enterprise Security, Compliance & Data Governance Policy, data at rest is encrypted using Customer-Managed Keys (CMK) rotated automatically every 90 days via AWS KMS, as stated in [So
- Judge reasoning: Most claims supported by contexts, but some context details were not included.

**`eval_011`** (multi_hop) - F:0.67 R:0.00
- Query: If a customer tenant's account is deleted, how quickly must their vector embeddings be removed, and what database technology stores those vectors in the first place?
- Answer: According to the enterprise security compliance policy [security_compliance.md, Page: 1], vector embedding records belonging to deleted customer tenants are hard-deleted within 24 hours.

The vector e
- Judge reasoning: Most facts supported, but lack of relevant context reduces faithfulness score.

**`eval_012`** (multi_hop) - F:0.00 R:0.00
- Query: How does the 2-minute RTO for a full regional outage compare to the patching deadline for a critical severity vulnerability?
- Answer: The information is unavailable in the enterprise knowledge base regarding the comparison between the 2-minute RTO for a full regional outage and the patching deadline for a critical severity vulnerabi
- Judge reasoning: Answer not supported by any relevant retrieved context

**`eval_013`** (distractor_heavy) - F:0.80 R:0.50
- Query: Specifically, what is the p99 latency budget for the Service-to-Service gRPC Mesh (Envoy), not the API Gateway or edge termination?
- Answer: The p99 latency budget for the Service-to-Service gRPC Mesh (Envoy) is 5ms, as stated in [cloud_architecture.md, Page: 1].
- Judge reasoning: The answer is mostly faithful but lacks supporting context on latency allocation

**`eval_014`** (distractor_heavy) - F:0.75 R:0.50
- Query: What is the remediation deadline specifically for High severity vulnerabilities (CVSS 7.0-8.9), as distinct from Critical severity ones?
- Answer: High severity vulnerabilities (CVSS 7.0 - 8.9) have a mandatory remediation deadline of 7 calendar days.

[REF]: [security_compliance.md:1]
- Judge reasoning: Generated answer partially matches retrieved contexts, but lacks specificity.

**`eval_015`** (unanswerable) - F:N/A R:N/A
- Query: What is the required SLA uptime percentage for tier-2 and tier-3 microservices?
- Answer: Unfortunately, the provided context does not explicitly mention the required SLA uptime percentage for tier-2 and tier-3 microservices. The context mainly focuses on high availability standards for ti
- Judge reasoning: Should have declined but did not (no refusal language detected) - possible hallucination.

**`eval_016`** (unanswerable) - F:N/A R:N/A
- Query: How many employees are required to complete SOC-2 compliance training each year?
- Answer: Unfortunately, the provided context blocks do not contain any information on the number of employees required to complete SOC-2 compliance training each year. The context blocks focus on security comp
- Judge reasoning: Correctly declined to answer (refusal detected).

**`eval_017`** (adversarial_citation_stress) - F:0.00 R:0.00
- Query: According to the cloud architecture document, how often are third-party SOC-2 Type II audits conducted?
- Answer: Third-party SOC-2 Type II audits are conducted annually in Q3, as stated in the security_compliance.md document [doc_name: Page: 1].
- Judge reasoning: Generated answer fails to accurately reference ground truth document

**`eval_018`** (adversarial_citation_stress) - F:0.25 R:0.50
- Query: Per the security compliance policy, what AWS EKS Kubernetes version and instance type do the autoscaling worker clusters run on?
- Answer: The AWS EKS Kubernetes version for the autoscaling worker clusters is EKS v1.30 [cloud_architecture.md:1]. However, the provided information does not specify the exact Kubernetes version used for auto
- Judge reasoning: Contexts did not specify instance type or version for autoscaling

