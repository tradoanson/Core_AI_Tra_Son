# Reliability Hardening v2.1.0

inspect_sqlite_copy(path) performs bounded read-only SQLite PRAGMA integrity_check on caller-approved offline copies; returns PASS/BLOCKED without repair or host actions. The live database must not be passed in. Real crash/power-loss stress, disk faults, cross-process locking, and storage atomicity remain separate tests.
