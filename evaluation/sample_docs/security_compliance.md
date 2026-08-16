# Enterprise Security, Compliance & Data Governance Policy

## 1. Cryptographic Standards and Key Management
All customer and telemetry data must be encrypted in transit using TLS 1.3 with forward secrecy (ECDHE-RSA-AES128-GCM-SHA256 or higher).
Data at rest across all persistent storage volumes (EBS, S3, Qdrant Vector DB, RDS) must be encrypted using AES-256 with customer-managed keys (CMK) rotated automatically every 90 days via AWS KMS.

## 2. Identity and Access Management (IAM)
The organization enforces the Principle of Least Privilege (PoLP) and Zero-Trust Network Access (ZTNA).
- All human administrative access requires FIDO2 hardware MFA keys (YubiKey 5 Series).
- Service accounts authenticate using short-lived IAM OIDC tokens with a maximum time-to-live (TTL) of 1 hour.
- Root AWS account credentials are locked in a physical vault and require dual-custody authorization for emergency access.

## 3. Data Retention and Deletion Schedules
- Application access and API request logs must be retained in hot S3 storage for 90 days, followed by automated transition to S3 Glacier Deep Archive for 7 years to comply with SOC-2 and HIPAA regulations.
- User PII and deleted account records must be permanently purged within 30 business days upon receipt of a verified GDPR/CCPA erasure request.
- Vector database embedding records belonging to deleted customer tenants are hard-deleted within 24 hours.

## 4. Incident Response and Vulnerability SLA
Critical severity vulnerabilities (CVSS score 9.0 - 10.0) must be mitigated and patched within 24 hours of discovery.
High severity vulnerabilities (CVSS 7.0 - 8.9) have a mandatory remediation SLA of 7 calendar days.
Automated penetration tests and third-party SOC-2 Type II audits are conducted annually in Q3.
