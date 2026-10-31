# Core AI Trà Sơn v0.2.1 — Memory Resilience Acceptance

Status: PENDING final GitHub Actions on branch head and merge commit.

Scope: dedicated SQLite memory only. No machine, VTND or Nhân Hộ Khẩu integration.

Acceptance gates:
- Parallel verified writers preserve exact sample count (60 workers/tasks, eight threads).
- Separate namespace writes remain isolated.
- Online SQLite backup produces integrity-checked consistent snapshot while writers run.
- Existing backup cannot be overwritten.
- Restore only when target database does not exist; corrupted backup fails without publishing a target.
- Corrupted source fails closed; no automatic overwrite or deletion of original database.
- Read of missing database does not create a file.
- Python 3.11, 3.12, 3.13: clean install, regression and >=40 tests.

Recovery procedure: stop writes, retain corrupted DB for forensic analysis, select last known-good backup, restore to a *missing dedicated DB path*, validate state, then resume writes. No automatic destructive recovery.

Limitations: This does not protect against disk failure without external backup retention. The backup is an explicit method, not a scheduled service. No cross-host backup, encryption, durability guarantees beyond SQLite and filesystem behavior, or full stress/load benchmark.
