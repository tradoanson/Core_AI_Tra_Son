# CHANGELOG — Core AI Trà Sơn

All releases are append-only records. Never rewrite historical release sections.

## [Unreleased] — v0.1.1-governance
- Authorized by repository owner in ChatGPT on 2026-10-31 to edit GitHub directly and record all changes in logs.
- Created an isolated release branch; no production VTND or Nhân Hộ Khẩu integrations.
- Added version policy, future baseline, acceptance protocol, and read-only CI checks.
- Acceptance status: PENDING — repository source/test inventory and GitHub Actions results not yet independently verified.
- Existing v0.1.0 README preserved; no historical release claimed to be certified.

## [0.1.0] — prototype (historical, not certified)
- README describes Micro Agent suggestions, in-memory ETA Adaptive and deterministic TinyPredictor placeholder.
- Do not describe TinyPredictor as trained ML.
- Do not claim PASS without linked commit SHA, command output, test counts, and CI run URL.

## Audit log
| Date (UTC+7) | Actor | Authorization | Action | Target | Result |
|---|---|---|---|---|---|
| 2026-10-31 | ChatGPT via connected GitHub | User explicitly authorized full GitHub edits and required log | Created release/v0.1.1-governance from main | Core_AI_Tra_Son | SUCCESS |
| 2026-10-31 | ChatGPT via connected GitHub | Same authorization | Add governance documents and CI workflow without replacing v0.1.0 | release/v0.1.1-governance | See Git commits and PR |

| 2026-10-31 | ChatGPT via connected GitHub | Owner authorization | Inventoried main: original Python modules and test_core.py are at repository root; ZIP also present | main | VERIFIED via GitHub Git tree |
| 2026-10-31 | ChatGPT via connected GitHub | Owner authorization | Copied original modules into core_ai_tra_son/ and test_core.py into tests/ without deleting root originals | release/v0.1.1-governance | SUCCESS |
| 2026-10-31 | ChatGPT via connected GitHub | Owner authorization | Added twelve safety/regression checks | tests/test_safety_v0_1_1.py | SUCCESS; CI pending |

| 2026-10-31 | ChatGPT via connected GitHub | Owner authorized GitHub-only acceptance | Added isolated clean-install, smoke, static safety and preservation checks; initial 3.12/3.13 venv setuptools issue fixed | release/v0.1.1-final-acceptance | PASS on https://github.com/tradoanson/Core_AI_Tra_Son/actions/runs/41197588822 |
| 2026-10-31 | ChatGPT via connected GitHub | Same authorization | Appended acceptance evidence; physical-device and host-app tests explicitly deferred | acceptance/ACCEPTANCE_v0.1.1.md | PASS GitHub-only; tag pending |

## [0.2.0] — Adaptive Memory (in development, 2026-10-31)
- Add explicit, dedicated SQLite-backed AdaptiveMemory with namespace isolation, persistence and verified-only EMA learning.
- Add outlier and invalid-input rejection, 12 new tests, offline CI on Python 3.11–3.13, usage guide and acceptance evidence file.
- No production integration; v0.1.1 source and tests retained. Final CI/tag pending.

## [0.2.1] — Memory resilience (2026-10-31)
- SQLite concurrent-writer transaction tests, 30-second busy timeout and read-only state access.
- Consistent integrity-checked SQLite online backup; refuses overwrite; recovery validates backup and restores only to absent target.
- Corrupt source/backup fails closed; no automatic destructive recovery. Ten resilience tests, 3-version CI, recovery guide and acceptance record.
- Production machine tests and Micro Agent Engine deliberately out of scope.

## [0.3.0] — Micro Agent Engine (2026-10-31)
- Add pure SHADOW Observer -> Memory context -> CoreAI Reasoner -> Safety Gate -> structured decision result.
- No host actions, network, persistent logs or citizen-record output. Twelve micro-agent tests, clean-install and Python 3.11–3.13 CI.
- Production integration and Micro Agent execution explicitly excluded.

## [0.3.1] — Micro Agent Reliability (2026-10-31)
- Bound observation/record/required-field inputs and memory sample counts; fail closed on excessive input.
- Add deterministic and parallel evaluation tests, sanitized in-memory ring audit and strict audit allowlists.
- 14 reliability tests, versioned GitHub Actions acceptance; no persistent logging or production integration.

## [0.4.0] — Reasoning Engine (2026-10-31)
- Deterministic multi-signal verified reasoning with bounded confidence, explicit reasons and allowlisted evidence.
- Optional ETA bias memory context without confidence inflation; no host actions or persistent writes.
- 14 reasoning tests, 3-version CI and release acceptance.

## [0.4.1] — Reasoning Validation & Calibration diagnostics (2026-10-31)
- Detect contradictory march availability/capacity signals and fail closed.
- Add synthetic benchmark agreement by confidence bin, repeatability and parallel stability tests.
- Confidence is not probabilistically calibrated; no host actions or production integration.

## [0.5.0] — Advanced Reasoning (2026-10-31)
- Add deterministic comparison and ranking of allowlisted human-review alternatives with reason codes and fixed policy scores.
- Fail closed on contradictory/unverified signals, unknown options and missing return context.
- 15 new ranking tests; GitHub-only 3-version acceptance; SHADOW only.

## [0.5.1] — Decision Quality & Safety Validation (2026-10-31)
- Block gather review without explicitly verified resource availability and return review when resources are explicitly unavailable.
- Improve ranked-option explanations; test boundary, adversarial, missing-signal and concurrent decision cases.
- GitHub-only Python 3.11–3.13 acceptance; SHADOW only.

## [0.6.0] — Adaptive Decision Learning (2026-10-31)
- Add immutable, caller-owned verified-outcome preference state with bounded updates for REVIEW_GATHER and REVIEW_RETURN.
- Integrate learned adjustments only after existing SHADOW safety and eligibility gates; WAIT and blocked options remain unchanged.
- Add 19 verified-only, saturation, isolation, concurrency and non-execution tests; GitHub-only acceptance.

## [0.6.1] — Learning Integrity & Persistence (2026-10-31)
- Explicit isolated SQLite verified-outcome ledger with transactional deduplication and hash-linked replay validation.
- Consistent backup and fail-closed restore to absent target; reject corrupt, conflicting or unrecognized data.
- 20 persistence/integrity tests and Python 3.11–3.13 GitHub-only acceptance; SHADOW only.

## [0.6.2] — Learning Security & Performance (2026-10-31)
- Add optional HMAC-SHA256 external checkpoint and anchored rollback detection with caller-managed key.
- Add incremental suffix replay and explicit crash reconciliation without relaxing SHADOW safety gates.
- Add 25 synthetic security, concurrency, recovery and compatibility tests on GitHub Actions.

## [0.6.3] — Learning Recovery & Concurrency Hardening (2026-10-31)
- Add opt-in POSIX multi-process lock and durable checkpoint directory fsync.
- Validate and reconcile post-crash suffix before new writes; protect against stale checkpoint publication.
- Add 19 synthetic multi-process, failure, integrity and bounded growth tests; SHADOW only.

## [0.7.0] — Decision Evaluation & Learning Quality (2026-10-31)
- Add bounded, verified holdout comparison of baseline and learned SHADOW advisory rankings.
- Report improvements, regressions, abstentions and deterministic quality gates.
- Add explicit immutable in-memory rollback on degradation; no persistence or host actions.
- Add 25 synthetic quality and regression tests, GitHub Actions acceptance.

## [0.7.1] — Evaluation Integrity & Persistent Rollback (2026-10-31)
- Reject exact training/holdout event-ID overlap and duplicate holdout identifiers.
- HMAC-sign create-only evaluation summary bound to ledger head and count; no raw signals persisted.
- Persist non-destructive, authenticated rollback selection override and freeze further learning.
- Add 25 synthetic integrity/rollback tests; SHADOW only.

## [0.7.3] — Recovery Governance
- Explicit manual lifecycle gates; no automatic unfreeze or host action.

## [0.8.0] — Recovery Audit
- Signed, caller-persisted audit chain for manual recovery governance.

## [0.9.0] — Quality Gates
- Conservative exact paired sign-test gate on synthetic holdout improvements and regressions.
