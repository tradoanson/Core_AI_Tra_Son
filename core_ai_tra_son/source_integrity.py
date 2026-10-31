"""Offline source integrity manifest, with bounded file sizes and paths."""
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

MAX_FILES=128
MAX_FILE_BYTES=2_000_000

@dataclass(frozen=True)
class IntegrityManifest:
    entries: tuple[tuple[str,str],...]
    digest: str
    action_executed: bool = False

def build_integrity_manifest(root, relative_paths):
    root=Path(root).resolve(strict=True)
    if not root.is_dir() or type(relative_paths) not in (list,tuple) or not 1 <= len(relative_paths) <= MAX_FILES:
        raise ValueError("invalid manifest scope")
    if any(type(p) is not str or not p or len(p)>256 for p in relative_paths):
        raise ValueError("invalid path")
    if len(set(relative_paths))!=len(relative_paths):
        raise ValueError("duplicate path")
    entries=[]
    for raw in sorted(relative_paths):
        rel=Path(raw)
        if rel.is_absolute() or ".." in rel.parts or rel.suffix!=".py":
            raise ValueError("only relative Python sources permitted")
        path=(root/rel).resolve(strict=True)
        if not path.is_relative_to(root) or not path.is_file() or path.stat().st_size>MAX_FILE_BYTES:
            raise ValueError("unsafe file")
        entries.append((rel.as_posix(),sha256(path.read_bytes()).hexdigest()))
    payload="".join(f"{p} {digest}\n" for p,digest in entries).encode("utf-8")
    return IntegrityManifest(tuple(entries),sha256(payload).hexdigest())
