"""Opt-in Windows local-process locking for authenticated learning.

Uses Windows CRT byte-range locks, not POSIX flock. This is deliberately
Windows-only, local filesystem only, and never dispatches host actions.
"""
import contextlib
import sqlite3
import os
import stat
import sys
import threading
import time
from pathlib import Path

from .secure_learning import SecureLearningStore
from .learning_store import _ID, _MAX_EVENTS

try:
    import msvcrt
except ImportError:
    msvcrt = None


class WindowsLearningStore(SecureLearningStore):
    def __init__(self, db_path, checkpoint_path, key):
        if sys.platform != "win32" or msvcrt is None:
            raise RuntimeError("Windows native byte-range locking required")
        super().__init__(db_path, checkpoint_path, key)
        self.lock_path = Path(str(self.checkpoint_path) + ".winlock")
        if self.lock_path.resolve() in (self.path.resolve(), self.checkpoint_path.resolve()):
            raise ValueError("lock path collision")
        self._process_lock = threading.RLock()

    @contextlib.contextmanager
    def _guard(self):
        with self._process_lock:
            if not self.lock_path.parent.is_dir() or self.lock_path.is_symlink():
                raise ValueError("unsafe lock path")
            fd = os.open(self.lock_path, os.O_CREAT | os.O_RDWR | os.O_BINARY, 0o600)
            acquired = False
            try:
                info = os.fstat(fd)
                if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                    raise ValueError("unsafe lock file")
                if info.st_size == 0:
                    os.write(fd, b"0")
                    os.fsync(fd)
                for attempt in range(100):
                    os.lseek(fd, 0, os.SEEK_SET)
                    try:
                        msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
                        acquired = True
                        break
                    except OSError:
                        if attempt == 99:
                            raise TimeoutError("Windows learning lock timed out")
                        time.sleep(0.1)
                yield
            finally:
                if acquired:
                    os.lseek(fd, 0, os.SEEK_SET)
                    msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
                os.close(fd)

    @contextlib.contextmanager
    def _readonly(self):
        # sqlite3.Connection.__exit__ does not close the file on Windows.
        with contextlib.closing(super()._readonly()) as db:
            yield db

    def _observe_locked(self, event_id, option, *, successful, verified=False):
        if verified is not True:
            return False
        if type(event_id) is not str or not _ID.fullmatch(event_id):
            raise ValueError("invalid opaque event ID")
        if type(successful) is not bool or option not in ("REVIEW_GATHER", "REVIEW_RETURN"):
            raise ValueError("invalid verified outcome")
        with contextlib.closing(sqlite3.connect(self.path, timeout=30)) as db:
            with db:
                db.execute("BEGIN IMMEDIATE")
                state, count, head = self._incremental(db)
                prior = db.execute("SELECT option,successful FROM learning_events WHERE event_id=?", (event_id,)).fetchone()
                if prior is not None:
                    if prior != (option, int(successful)):
                        raise ValueError("conflicting duplicate")
                    return False
                if count >= _MAX_EVENTS:
                    raise ValueError("event limit")
                updated = self.learner.observe(state, option, successful=successful, verified=True)
                if updated == state:
                    return False
                digest = self._digest(event_id, option, successful, head)
                db.execute("INSERT INTO learning_events VALUES(?,?,?,?,?,?)",
                           (count + 1, event_id, option, int(successful), head, digest))
        self._publish(updated, count + 1, digest)
        return True

    def initialize(self):
        if not self.path.parent.is_dir():
            raise FileNotFoundError("parent directory missing")
        if self.path.exists():
            with self._readonly() as db:
                self._schema_check(db)
            return
        fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        os.close(fd)
        try:
            with contextlib.closing(sqlite3.connect(self.path, timeout=30)) as db:
                with db:
                    db.execute("CREATE TABLE learning_meta(version INTEGER NOT NULL)")
                    db.execute("INSERT INTO learning_meta VALUES (1)")
                    db.execute("""CREATE TABLE learning_events(
                        seq INTEGER PRIMARY KEY, event_id TEXT UNIQUE NOT NULL,
                        option TEXT NOT NULL, successful INTEGER NOT NULL,
                        prev_hash TEXT NOT NULL, event_hash TEXT NOT NULL)""")
                    self._schema_check(db)
        except Exception:
            self.path.unlink(missing_ok=True)
            raise

    def bootstrap(self):
        with self._guard():
            return super().bootstrap()

    def state(self):
        with self._guard():
            return super().state()

    def reconcile(self):
        with self._guard():
            return super().reconcile()

    def observe(self, event_id, option, *, successful, verified=False):
        if verified is not True:
            return False
        with self._guard():
            with self._readonly() as db:
                state, count, head = self._incremental(db)
                anchor, _ = self._load()
            if count != anchor["count"]:
                self._publish(state, count, head)
            return super().observe(event_id, option, successful=successful, verified=True)
