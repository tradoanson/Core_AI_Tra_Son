# Core AI Trà Sơn v2.0.0 — Stable SHADOW acceptance

Status: PENDING CI and PR merge (check GitHub Actions for authoritative result).

Release gates: >=411 unit tests; Linux Python 3.11, 3.12, 3.13; Windows native byte-range lock tests; wheel build and SHA256 artifact; versioned verification; isolated installation and smoke; static safety checks.

**Meaning of Stable:** stability of the offline, read-only SHADOW prototype within tested synthetic scenarios. NOT production readiness, operational security certification, or validation on real-world data.

Remaining limitations: Windows power-loss and multi-process stress not comprehensively certified; caller-supplied provenance and reviewer assertions; independent audit anchor requires external durable storage; semantic near-duplicate leakage undetected; no calibrated confidence; drift pause is advisory; CI artifacts expire; no signed immutable release tag established; no integration with Auto VTND PC or Web Nhân Khẩu.
