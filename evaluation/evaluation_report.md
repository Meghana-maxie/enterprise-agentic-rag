# Enterprise Agentic Hybrid RAG - LLMOps Benchmark Report

Generated at: 2026-08-26 01:00:00
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
| **Faithfulness (Groundedness)** | >= 0.85 | **0.578** | [FAIL] |
| **Answer Relevance** | >= 0.80 | **0.819** | [PASS] |
| **Context Precision@K** | >= 0.80 | **0.577** | [FAIL] |
| **Context Recall** | >= 0.80 | **0.490** | [FAIL] |

---

## 1b. Score Breakdown by Question Category

| Category | Count | Avg Faithfulness | Avg Recall |
| :--- | :--- | :--- | :--- |
| `adversarial_citation_stress` | 2 | 0.585 | 0.165 |
| `direct_lookup` | 8 | 0.650 | 0.516 |
| `distractor_heavy` | 2 | 0.835 | 0.975 |
| `multi_hop` | 2 | 0.330 | 0.405 |
| `paraphrased` | 2 | 0.650 | 0.800 |
| `unanswerable` | 2 | 0.200 | 0.000 |

---

## 2. Latency & Throughput Profile

| Percentile | Latency (ms) |
| :--- | :--- |
| **P50 (Median)** | **35761.4 ms** |
| **P90** | **41717.9 ms** |
| **P99** | **54428.4 ms** |

---

## 3. Detailed Query Breakdown

| ID | Query | Faithfulness | Precision | Recall | Latency | Critic |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `eval_001` | What are the three primary active-active... | `0.80` | `0.70` | `0.80` | 23958ms | PASS |
| `eval_002` | What are the latency budgets for the int... | `0.50` | `0.80` | `0.60` | 17609ms | PASS |
| `eval_003` | What are the exact RTO and RPO targets d... | `0.67` | `0.56` | `0.80` | 19633ms | PASS |
| `eval_004` | How often are vector index backups taken... | `0.50` | `0.80` | `0.20` | 16789ms | PASS |
| `eval_005` | What encryption standard is required for... | `0.80` | `0.40` | `0.80` | 38813ms | PASS |
| `eval_006` | What is the maximum time-to-live (TTL) f... | `0.80` | `0.70` | `0.60` | 17624ms | PASS |
| `eval_007` | What is the data retention schedule for ... | `0.80` | `0.00` | `0.00` | 40963ms | PASS |
| `eval_008` | What is the remediation SLA for critical... | `0.33` | `0.67` | `0.33` | 35655ms | PASS |
| `eval_009` | Which regions is the platform live in si... | `0.50` | `0.60` | `0.80` | 39808ms | FAIL |
| `eval_010` | How is data protected while it's sitting... | `0.80` | `0.90` | `0.80` | 56995ms | FAIL |
| `eval_011` | If a customer tenant's account is delete... | `0.33` | `0.50` | `0.00` | 35868ms | FAIL |
| `eval_012` | How does the 2-minute RTO for a full reg... | `0.33` | `0.56` | `0.81` | 41897ms | PASS |
| `eval_013` | Specifically, what is the p99 latency bu... | `1.00` | `1.00` | `1.00` | 17700ms | PASS |
| `eval_014` | What is the remediation deadline specifi... | `0.67` | `0.90` | `0.95` | 18162ms | PASS |
| `eval_015` | What is the required SLA uptime percenta... | `0.40` | `0.80` | `0.00` | 41641ms | FAIL |
| `eval_016` | How many employees are required to compl... | `0.00` | `0.00` | `0.00` | 34765ms | FAIL |
| `eval_017` | According to the cloud architecture docu... | `0.50` | `0.00` | `0.00` | 40176ms | PASS |
| `eval_018` | Per the security compliance policy, what... | `0.67` | `0.50` | `0.33` | 37820ms | FAIL |

---

## 4. Per-Query Reasoning (Judge Commentary)

**`eval_001`** (direct_lookup) - F:0.80 R:0.80
- Query: What are the three primary active-active cloud regions and their SLA uptime requirement?
- Answer: The three primary active-active cloud regions of the Global Cloud Platform are:

1. `us-east-1` (North Virginia)
2. `eu-west-1` (Ireland)
3. `ap-southeast-1` (Singapore)

These regions have a minimum 
- Judge reasoning: Most claims match, but context lacks specific uptime requirement details

**`eval_002`** (direct_lookup) - F:0.50 R:0.60
- Query: What are the latency budgets for the internal API Gateway Router and Vector Database engine?
- Answer: Based on the provided context, the latency budgets for the internal API Gateway Router and Vector Database engine are as follows:

* Internal API Gateway Router: 15ms p99 latency
* Vector Database eng
- Judge reasoning: Generated answer mostly matches contexts, but lacks direct relevance to query specifics

**`eval_003`** (direct_lookup) - F:0.67 R:0.80
- Query: What are the exact RTO and RPO targets during a total regional outage?
- Answer: The exact Recovery Time Objective (RTO) and Recovery Point Objective (RPO) targets during a total regional outage are:

- RTO: 2 minutes
- RPO: 0 seconds for transactional data.

These targets are set
- Judge reasoning: Most claims are supported, but some RTO/RPO details are missing context

**`eval_004`** (direct_lookup) - F:0.50 R:0.20
- Query: How often are vector index backups taken and where are they stored?
- Answer: Vector index backups are taken asynchronously and snapshotted every 4 hours to Amazon S3 Glacier Flexible Retrieval with a 30-day retention lock, as per the cloud architecture policy [cloud_architectu
- Judge reasoning: Generated answer closely aligns with retrieved contexts, missing specific retention lock details.

**`eval_005`** (direct_lookup) - F:0.80 R:0.80
- Query: What encryption standard is required for data at rest and how frequently are KMS keys rotated?
- Answer: According to the enterprise security policy, data at rest must be encrypted using AES-256 with customer-managed keys (CMK) [1:1]. 

The KMS keys are rotated automatically every 90 days [1:1] via AWS K
- Judge reasoning: Most claims are partially supported, but some are missing or misphrased, impacting overall score.

**`eval_006`** (direct_lookup) - F:0.80 R:0.60
- Query: What is the maximum time-to-live (TTL) for service account IAM OIDC tokens?
- Answer: The maximum time-to-live (TTL) for service account IAM OIDC tokens is 1 hour, as stated in [security_compliance.md:1].
- Judge reasoning: Contexts support key claim, but omit related details about token duration

**`eval_007`** (direct_lookup) - F:0.80 R:0.00
- Query: What is the data retention schedule for API request logs in hot S3 vs Glacier Deep Archive?
- Answer: According to the enterprise knowledge base, the data retention schedule for API request logs in hot S3 is 90 days, followed by transition to S3 Glacier Deep Archive for an additional 7 years, to compl
- Judge reasoning: Context lacks specific information on API request log retention schedule

**`eval_008`** (direct_lookup) - F:0.33 R:0.33
- Query: What is the remediation SLA for critical severity vulnerabilities with CVSS 9.0-10.0?
- Answer: Based on the provided context, the remediation SLA for critical severity vulnerabilities with CVSS 9.0-10.0 is 24 hours. 

[security_compliance.md:1]
- Judge reasoning: The generated answer partially aligns with the retrieved context, missing specific details about mitigation and patching within 24 hours.

**`eval_009`** (paraphrased) - F:0.50 R:0.80
- Query: Which regions is the platform live in simultaneously, and what's the yearly downtime cap needed to hit the uptime target?
- Answer: The Global Cloud Platform is live in three primary active-active regions: `us-east-1` (North Virginia), `eu-west-1` (Ireland), and `ap-southeast-1` (Singapore) [cloud_architecture.md:1].

To meet the 
- Judge reasoning: Contexts support most claims, but lacks detail on downtime cap calculation

**`eval_010`** (paraphrased) - F:0.80 R:0.80
- Query: How is data protected while it's sitting in storage, and on what schedule do the keys protecting it get swapped out?
- Answer: Data protection while it's sitting in storage is achieved through the use of customer-managed keys (CMK) rotated automatically every 90 days via AWS KMS, as stated in the security compliance policy [d
- Judge reasoning: Contexts support key rotation and encryption policies, but lack specific details about CMK usage.

**`eval_011`** (multi_hop) - F:0.33 R:0.00
- Query: If a customer tenant's account is deleted, how quickly must their vector embeddings be removed, and what database technology stores those vectors in the first place?
- Answer: According to the enterprise knowledge base, specifically [Source: security_compliance.md, Page: 1], vector database embedding records belonging to deleted customer tenants are hard-deleted within 24 h
- Judge reasoning: Relevant fact supported, but additional info from contexts is not utilized

**`eval_012`** (multi_hop) - F:0.33 R:0.81
- Query: How does the 2-minute RTO for a full regional outage compare to the patching deadline for a critical severity vulnerability?
- Answer: The 2-minute RTO for a full regional outage is significantly shorter than the patching deadline for a critical severity vulnerability, which is set at 24 hours. 

[DOC_CONTEXT]: 
--- [Source: cloud_ar
- Judge reasoning: Answer partially correct, but lacks direct comparison to vulnerability patching deadline.

**`eval_013`** (distractor_heavy) - F:1.00 R:1.00
- Query: Specifically, what is the p99 latency budget for the Service-to-Service gRPC Mesh (Envoy), not the API Gateway or edge termination?
- Answer: The Service-to-Service gRPC Mesh (Envoy) has a p99 latency budget of 5ms.
- Judge reasoning: All claims in the generated answer are strictly supported by the retrieved contexts.

**`eval_014`** (distractor_heavy) - F:0.67 R:0.95
- Query: What is the remediation deadline specifically for High severity vulnerabilities (CVSS 7.0-8.9), as distinct from Critical severity ones?
- Answer: High severity vulnerabilities (CVSS 7.0 - 8.9) have a mandatory remediation deadline of 7 calendar days from the date of discovery. In contrast, Critical severity vulnerabilities (CVSS score 9.0 - 10.
- Judge reasoning: Answer mostly faithful, with minor contextual variation.

**`eval_015`** (unanswerable) - F:0.40 R:0.00
- Query: What is the required SLA uptime percentage for tier-2 and tier-3 microservices?
- Answer: The required SLA uptime percentage for tier-2 and tier-3 microservices is not explicitly stated in the provided context blocks. However, according to the Enterprise Cloud Infrastructure & Architecture
- Judge reasoning: Generated answer closely aligns with context precision but misses crucial context recall

**`eval_016`** (unanswerable) - F:0.00 R:0.00
- Query: How many employees are required to complete SOC-2 compliance training each year?
- Answer: Unfortunately, the provided context does not contain information on the number of employees required to complete SOC-2 compliance training each year.
- Judge reasoning: Generated answer correctly identifies lack of information in retrieved contexts

**`eval_017`** (adversarial_citation_stress) - F:0.50 R:0.00
- Query: According to the cloud architecture document, how often are third-party SOC-2 Type II audits conducted?
- Answer: According to the cloud architecture document, third-party SOC-2 Type II audits are conducted annually in Q3. [cloud_architecture.md:1]
- Judge reasoning: Generated answer does not cite the correct document, impacting faithfulness and context recall.

**`eval_018`** (adversarial_citation_stress) - F:0.67 R:0.33
- Query: Per the security compliance policy, what AWS EKS Kubernetes version and instance type do the autoscaling worker clusters run on?
- Answer: Unfortunately, the provided context blocks do not contain the specific information about the AWS EKS Kubernetes version and instance type that the autoscaling worker clusters run on. The security comp
- Judge reasoning: Generated answer lacks specificity, citing only policy section relevance, not detail.

