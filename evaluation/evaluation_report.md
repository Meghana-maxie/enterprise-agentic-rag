# Enterprise Agentic Hybrid RAG - LLMOps Benchmark Report

Generated at: 2026-08-26 00:32:26  
Total Test Queries: 18  
Embedding Model: `BAAI/bge-small-en-v1.5`  
Reranker: `ms-marco-MiniLM-L-12-v2`  
LLM Provider: `llama3.2:3b`

---

## 1. Executive Summary Metrics

| Evaluation Metric | Target Threshold | Achieved Score | Status |
| :--- | :--- | :--- | :--- |
| **Faithfulness (Groundedness)** | >= 0.85 | **0.634** | [FAIL] |
| **Answer Relevance** | >= 0.80 | **0.827** | [PASS] |
| **Context Precision@K** | >= 0.80 | **0.678** | [FAIL] |
| **Context Recall** | >= 0.80 | **0.562** | [FAIL] |

---

## 2. Latency & Throughput Profile

| Percentile | Latency (ms) |
| :--- | :--- |
| **P50 (Median)** | **24328.7 ms** |
| **P90** | **51906.5 ms** |
| **P99** | **57306.2 ms** |

---

## 3. Detailed Query Breakdown

| ID | Query | Faithfulness | Precision | Recall | Latency | Critic |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `eval_001` | What are the three primary active-active... | `0.80` | `0.95` | `0.90` | 22639ms | PASS |
| `eval_002` | What are the latency budgets for the int... | `0.80` | `0.90` | `0.80` | 18562ms | PASS |
| `eval_003` | What are the exact RTO and RPO targets d... | `0.80` | `0.75` | `0.75` | 20251ms | PASS |
| `eval_004` | How often are vector index backups taken... | `0.67` | `0.50` | `0.33` | 19925ms | PASS |
| `eval_005` | What encryption standard is required for... | `0.80` | `0.90` | `0.75` | 22098ms | PASS |
| `eval_006` | What is the maximum time-to-live (TTL) f... | `0.83` | `0.98` | `0.83` | 20475ms | PASS |
| `eval_007` | What is the data retention schedule for ... | `0.83` | `0.67` | `0.50` | 51396ms | PASS |
| `eval_008` | What is the remediation SLA for critical... | `0.80` | `0.70` | `0.40` | 20738ms | PASS |
| `eval_009` | Which regions is the platform live in si... | `0.83` | `0.97` | `0.98` | 53098ms | FAIL |
| `eval_010` | How is data protected while it's sitting... | `0.60` | `0.40` | `0.80` | 58168ms | FAIL |
| `eval_011` | If a customer tenant's account is delete... | `0.80` | `0.60` | `0.50` | 46752ms | FAIL |
| `eval_012` | How does the 2-minute RTO for a full reg... | `0.40` | `0.20` | `0.00` | 49840ms | FAIL |
| `eval_013` | Specifically, what is the p99 latency bu... | `0.80` | `0.70` | `0.80` | 24393ms | PASS |
| `eval_014` | What is the remediation deadline specifi... | `0.33` | `0.78` | `0.78` | 24264ms | PASS |
| `eval_015` | What is the required SLA uptime percenta... | `0.75` | `0.60` | `0.00` | 47644ms | FAIL |
| `eval_016` | How many employees are required to compl... | `0.40` | `0.80` | `0.60` | 45116ms | FAIL |
| `eval_017` | According to the cloud architecture docu... | `0.00` | `0.00` | `0.00` | 18125ms | PASS |
| `eval_018` | Per the security compliance policy, what... | `0.17` | `0.80` | `0.40` | 37687ms | FAIL |

---

## 4. Per-Query Reasoning (Judge Commentary)

**`eval_001`** (direct_lookup) - F:0.80 R:0.90
- Query: What are the three primary active-active cloud regions and their SLA uptime requirement?
- Answer: The three primary active-active cloud regions are:

1. `us-east-1` (North Virginia)
2. `eu-west-1` (Ireland)
3. `ap-southeast-1` (Singapore)

According to the Enterprise Cloud Infrastructure & Archite
- Judge reasoning: Most claims in the answer are supported, but one minor omission noted.

**`eval_002`** (direct_lookup) - F:0.80 R:0.80
- Query: What are the latency budgets for the internal API Gateway Router and Vector Database engine?
- Answer: The latency budgets for the internal API Gateway Router and Vector Database engine are as follows:
- Internal API Gateway Router: 15ms p99 latency
- Vector Database Query Engine: 30ms p95 latency
- Judge reasoning: Most context facts support answer claims, but some nuances are missing.

**`eval_003`** (direct_lookup) - F:0.80 R:0.75
- Query: What are the exact RTO and RPO targets during a total regional outage?
- Answer: The Recovery Time Objective (RTO) during a total regional outage is 2 minutes, as stated in [cloud_architecture.md:1]. The Recovery Point Objective (RPO) for transactional data is 0 seconds via synchr
- Judge reasoning: Generated answer mostly supports retrieved contexts with minor omissions.

**`eval_004`** (direct_lookup) - F:0.67 R:0.33
- Query: How often are vector index backups taken and where are they stored?
- Answer: Vector index backups are taken asynchronously every 4 hours [cloud_architecture.md:1] and are stored in Amazon S3 Glacier Flexible Retrieval with a 30-day retention lock [cloud_architecture.md:1].
- Judge reasoning: Context is partially relevant, but contains unrelated information about data encryption policies.

**`eval_005`** (direct_lookup) - F:0.80 R:0.75
- Query: What encryption standard is required for data at rest and how frequently are KMS keys rotated?
- Answer: According to the Enterprise Security, Compliance & Data Governance Policy [security_compliance.md:1], data at rest must be encrypted using AES-256 with customer-managed keys (CMK) rotated automaticall
- Judge reasoning: Most claims in the answer are supported, but some details lack precision

**`eval_006`** (direct_lookup) - F:0.83 R:0.83
- Query: What is the maximum time-to-live (TTL) for service account IAM OIDC tokens?
- Answer: The maximum time-to-live (TTL) for service account IAM OIDC tokens is 1 hour, as stated in the security compliance policies. [security_compliance.md:2]
- Judge reasoning: Generated answer strictly supported by retrieved contexts, but slightly broadened in scope.

**`eval_007`** (direct_lookup) - F:0.83 R:0.50
- Query: What is the data retention schedule for API request logs in hot S3 vs Glacier Deep Archive?
- Answer: The data retention schedule for API request logs in hot S3 storage is 90 days, followed by automated transition to S3 Glacier Deep Archive for 7 years to comply with SOC-2 and HIPAA regulations [secur
- Judge reasoning: Generated answer accurately supports key query aspects, but misses secondary context details.

**`eval_008`** (direct_lookup) - F:0.80 R:0.40
- Query: What is the remediation SLA for critical severity vulnerabilities with CVSS 9.0-10.0?
- Answer: Critical severity vulnerabilities with CVSS 9.0-10.0 must be mitigated and patched within 24 hours of discovery, as per the security compliance policy [security_compliance.md:1].
- Judge reasoning: Contexts support specific details but lack broader ground truth implications.

**`eval_009`** (paraphrased) - F:0.83 R:0.98
- Query: Which regions is the platform live in simultaneously, and what's the yearly downtime cap needed to hit the uptime target?
- Answer: The Global Cloud Platform is live in three primary active-active regions: `us-east-1` (North Virginia), `eu-west-1` (Ireland), and `ap-southeast-1` (Singapore), simultaneously [cloud_architecture.md:1
- Judge reasoning: Contexts provide sufficient support for the generated answer, but not entirely accurate.

**`eval_010`** (paraphrased) - F:0.60 R:0.80
- Query: How is data protected while it's sitting in storage, and on what schedule do the keys protecting it get swapped out?
- Answer: Data protection while it's sitting in storage is achieved through encryption using AES-256 with customer-managed keys (CMK) that are rotated automatically every 90 days via AWS KMS [security_complianc
- Judge reasoning: Retrieved contexts provide some relevant information, but lack specificity and depth.

**`eval_011`** (multi_hop) - F:0.80 R:0.50
- Query: If a customer tenant's account is deleted, how quickly must their vector embeddings be removed, and what database technology stores those vectors in the first place?
- Answer: The vector embeddings of a deleted customer tenant's account must be removed within 24 hours, as per the security compliance policy [security_compliance.md, Page: 1]. The Qdrant Vector DB technology s
- Judge reasoning: Generated answer partially aligns with contexts, omitting relevant details on vector DB technology.

**`eval_012`** (multi_hop) - F:0.40 R:0.00
- Query: How does the 2-minute RTO for a full regional outage compare to the patching deadline for a critical severity vulnerability?
- Answer: Unfortunately, the provided context does not contain the necessary information to compare the 2-minute RTO for a full regional outage to the patching deadline for a critical severity vulnerability. Th
- Judge reasoning: Answer failed to rely solely on retrieved contexts, introducing external information.

**`eval_013`** (distractor_heavy) - F:0.80 R:0.80
- Query: Specifically, what is the p99 latency budget for the Service-to-Service gRPC Mesh (Envoy), not the API Gateway or edge termination?
- Answer: The p99 latency budget for the Service-to-Service gRPC Mesh (Envoy) is 5ms, as specified in the Enterprise Cloud Infrastructure & Architecture Specification documentation on page 1: [cloud_architectur
- Judge reasoning: Some supporting context information is lacking, but core claim is accurately supported

**`eval_014`** (distractor_heavy) - F:0.33 R:0.78
- Query: What is the remediation deadline specifically for High severity vulnerabilities (CVSS 7.0-8.9), as distinct from Critical severity ones?
- Answer: According to the enterprise security compliance policy, high severity vulnerabilities with a CVSS score between 7.0 and 8.9 have a mandatory remediation SLA of 7 calendar days.
- Judge reasoning: Generated answer partially supported by retrieved contexts, missing specific policy details

**`eval_015`** (unanswerable) - F:0.75 R:0.00
- Query: What is the required SLA uptime percentage for tier-2 and tier-3 microservices?
- Answer: Unfortunately, the required SLA uptime percentage for tier-2 and tier-3 microservices is unavailable in the enterprise knowledge base. The provided context blocks discuss high availability standards f
- Judge reasoning: Generated answer's faithfulness is partially supported by retrieved contexts' absence of tier-2/3 SLA info

**`eval_016`** (unanswerable) - F:0.40 R:0.60
- Query: How many employees are required to complete SOC-2 compliance training each year?
- Answer: The provided context blocks do not mention the specific requirement for SOC-2 compliance training. The context discusses security policies, compliance requirements, and infrastructure standards, but d
- Judge reasoning: Generated answer adequately captures lack of context relevance to user query.

**`eval_017`** (adversarial_citation_stress) - F:0.00 R:0.00
- Query: According to the cloud architecture document, how often are third-party SOC-2 Type II audits conducted?
- Answer: According to the cloud architecture document, third-party SOC-2 Type II audits are conducted annually in Q3.
- Judge reasoning: Generated answer does not strictly support claim and contains unnecessary information.

**`eval_018`** (adversarial_citation_stress) - F:0.17 R:0.40
- Query: Per the security compliance policy, what AWS EKS Kubernetes version and instance type do the autoscaling worker clusters run on?
- Answer: The AWS EKS Kubernetes version for the autoscaling worker clusters is EKS v1.30. However, the provided context does not explicitly state the instance type used for the autoscaling worker clusters.
- Judge reasoning: Contexts contain essential details but lack instance type and cite incorrect document

