# Backup and recovery — Adaptive Memory v0.2.1

```python
from core_ai_tra_son.memory import AdaptiveMemory

m = AdaptiveMemory("dedicated-memory.sqlite3", "vtnd")
m.initialize()
m.observe(300, 320, verified=True)
m.backup("backup-001.sqlite3")  # new filename only, never overwrites
```

To recover: stop all writers; preserve any damaged original file and its evidence; restore into an *absent* dedicated path using `m.restore("backup-001.sqlite3")`. The restore validates SQLite integrity and schema before publication. Do not point it at application DBs or existing targets. This API does not delete the damaged file.

Concurrent writes are serialized using SQLite `BEGIN IMMEDIATE`, 30-second busy timeout, and a transaction. Backup uses SQLite online backup API, not a raw copy of a potentially active database.

No automatic backup schedule and no production integration in this release.
