"""Offline fail-closed SQLite integrity probe; no repair, no writes.

This does not prove power-loss durability. Run only on caller-approved copies.
"""
import sqlite3
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class IntegrityProbe:
    status: str
    detail: str
    action_executed: bool = False

def inspect_sqlite_copy(path):
    if not isinstance(path,(str,Path)):
        raise ValueError("path required")
    p=Path(path)
    if p.is_symlink() or not p.is_file() or p.stat().st_size > 64*1024*1024:
        return IntegrityProbe("BLOCKED","missing, symlink, or oversized database")
    # Read-only URI mode prevents creating or modifying a DB.
    try:
        with sqlite3.connect(p.resolve().as_uri()+"?mode=ro",uri=True,timeout=1) as db:
            result=db.execute("PRAGMA integrity_check").fetchone()
            if result == ("ok",):
                return IntegrityProbe("PASS","sqlite integrity_check ok")
            return IntegrityProbe("BLOCKED","sqlite integrity check failed")
    except (sqlite3.DatabaseError,sqlite3.OperationalError,OSError,ValueError):
        return IntegrityProbe("BLOCKED","database unreadable or invalid")
