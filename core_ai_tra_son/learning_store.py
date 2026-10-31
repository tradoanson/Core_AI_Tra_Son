"""Dedicated SQLite learning ledger: atomic idempotency, integrity and safe backup.

Explicit caller-selected file; no host application access or autonomous actions.
"""
import hashlib
import os
import re
import sqlite3
import tempfile
from pathlib import Path
from urllib.parse import quote

from .decision_learning import DecisionLearner, DecisionLearningState

_ID = re.compile(r"^[A-Za-z0-9_-]{1,96}$")
_SCHEMA = 1
_MAX_EVENTS = 1000000


class LearningStore:
    def __init__(self, db_path):
        self.path = Path(db_path)
        if str(self.path) == ":memory:" or not self.path.name or self.path.suffix not in (".db", ".sqlite3"):
            raise ValueError("explicit dedicated .db or .sqlite3 path required")
        if self.path.exists() and not self.path.is_file():
            raise ValueError("database path must be a file")
        self.learner = DecisionLearner()

    def _readonly(self):
        uri = "file:" + quote(str(self.path.resolve()), safe="/") + "?mode=ro"
        return sqlite3.connect(uri, uri=True, timeout=30)

    @staticmethod
    def _digest(event_id, option, successful, prev_hash):
        payload = "|".join((event_id, option, str(int(successful)), prev_hash))
        return hashlib.sha256(payload.encode("ascii")).hexdigest()

    @staticmethod
    def _schema_check(db):
        if db.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise sqlite3.DatabaseError("learning database corrupt")
        marker = db.execute("SELECT version FROM learning_meta").fetchone()
        if marker is None or marker[0] != _SCHEMA:
            raise ValueError("unsupported learning schema")
        columns = {x[1] for x in db.execute("PRAGMA table_info(learning_events)")}
        if columns != {"seq", "event_id", "option", "successful", "prev_hash", "event_hash"}:
            raise ValueError("unexpected event schema")

    def initialize(self):
        if not self.path.parent.is_dir():
            raise FileNotFoundError("parent directory missing")
        if self.path.exists():
            with self._readonly() as db:
                self._schema_check(db)
            return
        # Exclusive file creation: never adopt or overwrite another DB.
        fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
        try:
            with sqlite3.connect(self.path, timeout=30) as db:
                db.execute("CREATE TABLE learning_meta(version INTEGER NOT NULL)")
                db.execute("INSERT INTO learning_meta VALUES (?)", (_SCHEMA,))
                db.execute("""CREATE TABLE learning_events(
                    seq INTEGER PRIMARY KEY, event_id TEXT UNIQUE NOT NULL,
                    option TEXT NOT NULL, successful INTEGER NOT NULL,
                    prev_hash TEXT NOT NULL, event_hash TEXT NOT NULL)""")
                self._schema_check(db)
        except Exception:
            self.path.unlink(missing_ok=True)
            raise

    def _replay(self, db):
        self._schema_check(db)
        state = DecisionLearningState()
        prev = "0" * 64
        expected = 1
        for seq, event_id, option, successful, previous, digest in db.execute(
                "SELECT seq,event_id,option,successful,prev_hash,event_hash FROM learning_events ORDER BY seq"):
            if (seq != expected or type(event_id) is not str or not _ID.fullmatch(event_id)
                    or option not in ("REVIEW_GATHER", "REVIEW_RETURN")
                    or successful not in (0, 1) or previous != prev
                    or digest != self._digest(event_id, option, successful, prev)):
                raise ValueError("learning event integrity failed")
            state = self.learner.observe(state, option, successful=bool(successful), verified=True)
            prev = digest
            expected += 1
            if expected > _MAX_EVENTS + 1:
                raise ValueError("event limit exceeded")
        return state, expected - 1, prev

    def state(self):
        with self._readonly() as db:
            return self._replay(db)[0]

    def observe(self, event_id, option, *, successful, verified=False):
        if verified is not True:
            return False
        if type(event_id) is not str or not _ID.fullmatch(event_id):
            raise ValueError("invalid opaque event ID")
        if type(successful) is not bool or option not in ("REVIEW_GATHER", "REVIEW_RETURN"):
            raise ValueError("invalid verified outcome")
        with sqlite3.connect(self.path, timeout=30) as db:
            db.execute("BEGIN IMMEDIATE")
            state, count, prev = self._replay(db)
            prior = db.execute("SELECT option,successful FROM learning_events WHERE event_id=?", (event_id,)).fetchone()
            if prior is not None:
                if prior != (option, int(successful)):
                    raise ValueError("conflicting duplicate outcome")
                return False
            if count >= _MAX_EVENTS:
                raise ValueError("event limit reached")
            new_state = self.learner.observe(state, option, successful=successful, verified=True)
            if new_state == state:
                return False
            digest = self._digest(event_id, option, successful, prev)
            db.execute("INSERT INTO learning_events VALUES(?,?,?,?,?,?)",
                       (count + 1, event_id, option, int(successful), prev, digest))
        return True

    def backup(self, destination):
        dest = Path(destination)
        if dest.resolve() == self.path.resolve() or dest.exists():
            raise FileExistsError("backup must be a new distinct file")
        if not dest.parent.is_dir():
            raise FileNotFoundError("backup parent missing")
        fd = os.open(dest, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
        try:
            with self._readonly() as source:
                self._replay(source)
                with sqlite3.connect(dest) as target:
                    source.backup(target)
                    self._replay(target)
        except Exception:
            dest.unlink(missing_ok=True)
            raise
        return dest

    def restore(self, source_path):
        source_path = Path(source_path)
        if self.path.exists():
            raise FileExistsError("restore never overwrites a database")
        if not source_path.is_file() or not self.path.parent.is_dir():
            raise FileNotFoundError("backup or destination parent missing")
        fd, temp_path = tempfile.mkstemp(prefix=".learning-restore-", suffix=".sqlite3", dir=self.path.parent)
        os.close(fd)
        staged = Path(temp_path)
        try:
            uri = "file:" + quote(str(source_path.resolve()), safe="/") + "?mode=ro"
            with sqlite3.connect(uri, uri=True) as source:
                self._replay(source)
                with sqlite3.connect(staged) as target:
                    source.backup(target)
                    self._replay(target)
            os.link(staged, self.path)
        finally:
            staged.unlink(missing_ok=True)
        return self.path
