# ACCEPTANCE v3.2.0 — pending CI verification

- Baseline: merged PR #43, commit `66eb6cbd56c4aa92b8832c0e8ab42d4faf222619`.
- Scope: versioned fail-closed read-only integration contract, six synthetic unit tests, version alignment and dedicated release CI.
- Branch: `release/v3.2.0-acceptance`.
- Test command: `python -m unittest discover -s tests -p "test_*.py" -v`.
- Mandatory gates: Python 3.11/3.12/3.13; >=492 discovered tests; installed package import outside repo; original files preserved; tracked filename scan; Windows native tests; wheel SHA256 verification; Windows EXE self-test.
- No live system integration, no real citizen data, no host actions.
- **Current verdict: PENDING.** Never infer acceptance from legacy green checks. Fill in run URL, commit SHA, actual test counts, artifacts, and results after CI completes.
- Merge policy: no merge unless every required v3.2.0 job succeeds. Tag/release only after verified evidence.
- Rollback target: v3.1.0 merged commit `b993905cfcbeefd67f6a08cabfb3a975126874e2` (tag status must be verified separately).
