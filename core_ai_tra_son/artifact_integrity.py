"""Offline artifact integrity verifier; does not install or deploy packages."""
import hashlib
import re
from pathlib import Path

def verify_wheel(wheel_path, expected_sha256):
    path=Path(wheel_path)
    if not path.is_file() or path.suffix != ".whl":
        raise ValueError("wheel artifact required")
    if type(expected_sha256) is not str or not re.fullmatch("[0-9a-f]{64}",expected_sha256):
        raise ValueError("expected sha256 required")
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != expected_sha256:
        raise ValueError("wheel checksum mismatch")
    return True
