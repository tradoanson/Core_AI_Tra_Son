"""Opt-in Windows local-process locking for authenticated learning.

Uses Windows CRT byte-range locks, not POSIX flock. This is deliberately
Windows-only, local filesystem only, and never dispatches host actions.
"""
import contextlib
import os
import stat
import sys
import threading
import time
from pathlib import Path

from .secure_learning import SecureLearningStore

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
