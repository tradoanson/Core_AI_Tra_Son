# FUTUREBASE — immutable baseline and roadmap

## Invariants
1. Released version = immutable Git tag plus frozen source and acceptance evidence. Never force-push or move release tags.
2. Each new version gets its own branch `release/vX.Y.Z`, its own acceptance report, and a separate Git tag after CI passes.
3. No copying new implementation over old version directories or editing prior release tags. Git history is canonical; optional `releases/vX.Y.Z/` snapshots are read-only.
4. Never deploy to Auto VTND or Web Nhân Hộ Khẩu automatically. Integration requires a separate explicit deployment decision.
5. No live citizen data, credentials, or secrets in GitHub. Repository is PUBLIC.
6. VTND uses Managed V3 only; no revival of V2. Shadow/read-only first.
7. Resident records: no autonomous mutations, classifications, or CT01/CT13 decisions. Authoritative validation and audit remain with host application.

## Planned milestones
### v0.1.1 — governance and repeatability
- Inventory actual source files and test paths.
- Python 3.11–3.13 CI with explicit acceptance evidence.
- Version constants, typed contracts, schema and test fixtures.
- No change to core business behavior.

### v0.2.0 — isolated adapters, SHADOW
- Read-only VTND adapter and Nhân Hộ Khẩu adapter with synthetic data only.
- Per-project policies, audit schema and dry-run gate.
- Benchmarks: memory, CPU, latency, deterministic outputs.
- Reject unknown or unverified observations by default.

### v0.3.0 — Tiny ML optional
- Offline small model only if baseline comparison justifies complexity.
- Train/validation separation, reproducibility, drift detection and rollback.
- Deterministic baseline remains fallback.

## Release gates
- Tests PASS on declared Python matrix.
- Security/secret scan PASS.
- CHANGELOG and version-specific ACCEPTANCE report with commit SHA, commands, output, date, CI URL.
- No unresolved high-severity defects; manual owner review before production deployment.
