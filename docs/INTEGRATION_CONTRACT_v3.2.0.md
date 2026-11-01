# v3.2.0 — Read-only integration contract (initial implementation)

This release branch adds an optional, versioned boundary. It does not connect to any live application, database, game process, or GUI.

## API
`IntegrationRequest(project, observation, verified=False, contract_version="3.2.0")`
`validate_request(request) -> IntegrationResult`

Supported project identifiers: `vtnd`, `nhankhau`. Unknown projects, contract-version mismatches, empty observations, and unverified observations are rejected. Accepted means the envelope passed basic validation, **not** that its content is safe, legally correct, or actionable. Result mode is always `shadow`.

## Boundaries
- No live citizen data, no writes, no host invocation, no network or process access.
- Does not change existing `CoreAI.evaluate`, Managed V3, CT01 or CT13 behavior.
- Further schema validation, audit policy, Windows/EXE compatibility tests and CI evidence are required before v3.2.0 can be accepted.
