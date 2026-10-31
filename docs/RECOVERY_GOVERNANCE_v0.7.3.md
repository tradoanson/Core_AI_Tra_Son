# Recovery Governance v0.7.3

Pure lifecycle policy: PROPOSED -> REVIEWED -> APPROVED -> ACTIVE -> CLOSED. Every transition requires explicit evidence and/or independent review/approval. A CLOSED label **does not** delete an authenticated rollback override or resume learning. The class does not persist approvals, audit logs, or host actions. Such durable lifecycle evidence is a separate future gate. No production integration.
