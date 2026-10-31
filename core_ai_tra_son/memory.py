"""SQLite-backed, isolated and verified-only ETA adaptive memory.

No network access, host DB access, or background tasks. Callers provide an
explicit path to a dedicated local SQLite file. No implicit production writes.
"""
import math
import os
import sqlite3
from pathlib import Path
from urllib.parse import quote

MAX_ETA = 7 * 86400
MAX_BIAS = 3600.0

class AdaptiveMemory:
    def __init__(self, db_path: str | Path, namespace: str, alpha: float = 0.2):
        if not isinstance(namespace, str) or not namespace.strip() or len(namespace) > 128:
            raise ValueError("namespace must be a nonempty string <=128 characters")
        if isinstance(alpha, bool) or not isinstance(alpha, (int, float)) or not math.isfinite(alpha) or not 0 < alpha <= 1:
            raise ValueError("alpha must be finite and in (0, 1]")
        path = Path(db_path)
        if not path.name or str(path) == ":memory:":
            raise ValueError("provide an explicit dedicated database file")
        if path.exists() and not path.is_file():
            raise ValueError("database path is not a file")
        self.db_path = path
        self.namespace = namespace
        self.alpha = float(alpha)

    def _connect(self):
        # sqlite3 URI mode=rw ensures a missing DB is not created by a read.
        return sqlite3.connect(self.db_path, timeout=30)

    def initialize(self):
        """Explicit opt-in schema creation; never touches host application DB."""
        if self.db_path.exists() and self.db_path.stat().st_size > 0:
            # Refuse to adopt unrelated databases without our schema marker.
            with sqlite3.connect(self.db_path, timeout=30) as db:
                found = db.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='adaptive_meta'").fetchone()
                if not found:
                    raise ValueError("refusing to modify an unrecognized SQLite database")
        with self._connect() as db:
            db.execute("CREATE TABLE IF NOT EXISTS adaptive_meta (schema_version INTEGER NOT NULL)")
            if not db.execute("SELECT 1 FROM adaptive_meta").fetchone():
                db.execute("INSERT INTO adaptive_meta(schema_version) VALUES (1)")
            if db.execute("SELECT schema_version FROM adaptive_meta").fetchone()[0] != 1:
                raise ValueError("unsupported schema version")
            db.execute("""CREATE TABLE IF NOT EXISTS adaptive_state (
                namespace TEXT PRIMARY KEY, bias REAL NOT NULL, samples INTEGER NOT NULL
            )""")

    def _read_connect(self):
        uri = "file:" + quote(str(self.db_path.resolve()), safe="/") + "?mode=ro"
        return sqlite3.connect(uri, uri=True, timeout=30)

    def _check_integrity(self, db):
        if db.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise sqlite3.DatabaseError("adaptive memory integrity check failed")
        row = db.execute("SELECT schema_version FROM adaptive_meta").fetchone()
        if row is None or row[0] != 1:
            raise ValueError("unsupported adaptive memory schema")

    def state(self):
        if not self.db_path.is_file():
            return {"namespace": self.namespace, "bias_seconds": 0.0, "samples": 0}
        with self._read_connect() as db:
            self._check_integrity(db)
            row = db.execute("SELECT bias, samples FROM adaptive_state WHERE namespace=?", (self.namespace,)).fetchone()
        return {"namespace": self.namespace, "bias_seconds": row[0] if row else 0.0, "samples": row[1] if row else 0}

    @staticmethod
    def _eta(value):
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not 0 <= value <= MAX_ETA:
            raise ValueError("ETA must be finite and in [0, 604800]")
        return float(value)

    def observe(self, predicted_seconds, actual_seconds, *, verified=False):
        if verified is not True:
            return False
        predicted = self._eta(predicted_seconds)
        actual = self._eta(actual_seconds)
        # Reject extreme outliers rather than learning from a suspect measurement.
        if abs(actual - predicted) > MAX_BIAS:
            return False
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            self._check_integrity(db)
            row = db.execute("SELECT bias, samples FROM adaptive_state WHERE namespace=?", (self.namespace,)).fetchone()
            old_bias, samples = row if row else (0.0, 0)
            new_bias = max(-MAX_BIAS, min(MAX_BIAS, self.alpha * (actual - predicted) + (1 - self.alpha) * old_bias))
            db.execute("""INSERT INTO adaptive_state(namespace,bias,samples) VALUES(?,?,?)
                ON CONFLICT(namespace) DO UPDATE SET bias=excluded.bias,samples=excluded.samples""",
                (self.namespace, new_bias, samples + 1))
        return True

    def correct(self, predicted_seconds):
        predicted = self._eta(predicted_seconds)
        return max(0.0, predicted + self.state()["bias_seconds"])

    def backup(self, destination: str | Path):
        """Consistent SQLite snapshot. Explicit caller-selected new destination only."""
        dest = Path(destination)
        if not self.db_path.is_file():
            raise FileNotFoundError("adaptive memory database is missing")
        if dest.resolve() == self.db_path.resolve():
            raise ValueError("backup destination cannot be source")
        if dest.exists():
            raise FileExistsError("refusing to overwrite an existing backup")
        if not dest.parent.is_dir():
            raise FileNotFoundError("backup parent directory must exist")
        # Exclusive reservation prevents accidental overwrite of an existing file.
        fd = os.open(dest, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
        try:
            with self._read_connect() as source:
                self._check_integrity(source)
                with sqlite3.connect(dest, timeout=30) as target:
                    source.backup(target)
                    self._check_integrity(target)
        except Exception:
            dest.unlink(missing_ok=True)
            raise
        return dest

    def restore(self, backup_path: str | Path):
        """Restore into a missing, dedicated DB only; never overwrite a live DB."""
        source_path = Path(backup_path)
        if self.db_path.exists():
            raise FileExistsError("restore requires an absent target database")
        if not source_path.is_file():
            raise FileNotFoundError("backup file is missing")
        if not self.db_path.parent.is_dir():
            raise FileNotFoundError("target parent directory must exist")
        uri = "file:" + quote(str(source_path.resolve()), safe="/") + "?mode=ro"
        # Stage in a unique sibling file; atomic publish after validation.
        import tempfile
        fd, temp_name = tempfile.mkstemp(prefix=".adaptive-restore-", suffix=".sqlite3", dir=self.db_path.parent)
        os.close(fd)
        staged = Path(temp_name)
        try:
            with sqlite3.connect(uri, uri=True, timeout=30) as source:
                self._check_integrity(source)
                with sqlite3.connect(staged, timeout=30) as target:
                    source.backup(target)
                    self._check_integrity(target)
            # Exclusive creation prevents clobbering a concurrently created DB.
            os.link(staged, self.db_path)
        finally:
            staged.unlink(missing_ok=True)
        return self.db_path
