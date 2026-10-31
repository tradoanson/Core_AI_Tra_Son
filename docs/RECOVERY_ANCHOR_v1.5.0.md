# Recovery Anchor v1.5.0

Issue and verify signed audit chain head with a distinct >=32 byte HMAC key. The caller MUST persist the anchor outside the audit chain in independently durable storage; the library cannot detect deletion of both the audit and the external anchor. No automatic learning unlock or host action.
