# Recovery Audit v0.8.0

HMAC-SHA256 chained audit entries record reviewer ID, evidence digest and approved recovery transition. The caller must independently verify reviewers and evidence, persist the complete chain in tamper-resistant storage and retain an independent latest-head anchor to detect truncation. The library itself does not provide durable storage, verified identities, or automatic unfreeze. No host actions or production integration.
