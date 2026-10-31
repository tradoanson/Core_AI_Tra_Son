import hashlib
import tempfile
import unittest
from pathlib import Path
from core_ai_tra_son.artifact_integrity import verify_wheel
class ArtifactTests(unittest.TestCase):
    def test_checksum(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"test.whl";p.write_bytes(b"synthetic")
            self.assertTrue(verify_wheel(p,hashlib.sha256(b"synthetic").hexdigest()))
    def test_tamper(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"test.whl";p.write_bytes(b"synthetic")
            with self.assertRaises(ValueError):verify_wheel(p,"0"*64)
    def test_invalid_hash(self):
        with self.assertRaises(ValueError):verify_wheel("fake.whl","bad")
    def test_invalid_suffix(self):
        with self.assertRaises(ValueError):verify_wheel("fake.txt","0"*64)
