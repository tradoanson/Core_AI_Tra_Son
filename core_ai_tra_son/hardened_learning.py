"""Opt-in POSIX multi-process locking and crash-safe checkpoint publication.

Only supported on local POSIX filesystems with flock and atomic same-directory
rename; unsupported platforms fail closed. No production integration.
"""
import contextlib
import os
import stat
import threading
from pathlib import Path

from .secure_learning import SecureLearningStore

try:
    import fcntl
except ImportError:  # Windows deliberately unsupported until native locking tested.
    fcntl = None


class HardenedLearningStore(SecureLearningStore):
    def __init__(self, db_path, checkpoint_path, key):
        if fcntl is None:
            raise RuntimeError("POSIX flock required; platform not validated")
        super().__init__(db_path, checkpoint_path, key)
        self.lock_path = Path(str(self.checkpoint_path) + ".lock")
        if self.lock_path.resolve() in (self.path.resolve(), self.checkpoint_path.resolve()):
            raise ValueError("lock path collides with ledger or checkpoint")
        self._process_lock = threading.RLock()

    @contextlib.contextmanager
    def _guard(self):
        with self._process_lock:
            if not self.lock_path.parent.is_dir():
                raise FileNotFoundError("lock directory missing")
            fd = os.open(self.lock_path, os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0), 0o600)
            try:
                info = os.fstat(fd)
                if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                    raise ValueError("unsafe lock file")
                fcntl.flock(fd, fcntl.LOCK_EX)
                try:
                    yield
                finally:
                    fcntl.flock(fd, fcntl.LOCK_UN)
            finally:
                os.close(fd)

    def _publish(self, state, count, head):
        super()._publish(state, count, head)
        # fsync the directory after atomic replace, to harden durability on
        # POSIX filesystems that support directory fsync.
        fd = os.open(self.checkpoint_path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(fd)
        finally:
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
            # A previous writer may have committed an event before crashing
            # ahead of checkpoint publication. Validate and anchor its suffix
            # under the same inter-process lock before appending.
            with self._readonly() as db:
                state, count, head = self._incremental(db)
                anchor, _ = self._load()
            if count != anchor["count"]:
                self._publish(state, count, head)
            return super().observe(event_id, option, successful=successful, verified=True)
