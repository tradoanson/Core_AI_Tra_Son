import tempfile
import unittest
from pathlib import Path
from core_ai_tra_son.source_integrity import build_integrity_manifest

class SourceIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        (self.root/"a.py").write_text("a=1\n",encoding="utf-8")
    def test_deterministic(self):
        self.assertEqual(build_integrity_manifest(self.root,["a.py"]).digest,build_integrity_manifest(self.root,["a.py"]).digest)
    def test_digest_changes(self):
        before=build_integrity_manifest(self.root,["a.py"]).digest
        (self.root/"a.py").write_text("a=2\n",encoding="utf-8")
        self.assertNotEqual(before,build_integrity_manifest(self.root,["a.py"]).digest)
    def test_traversal(self):
        with self.assertRaises(ValueError):build_integrity_manifest(self.root,["../a.py"])
    def test_absolute(self):
        with self.assertRaises(ValueError):build_integrity_manifest(self.root,[str(self.root/"a.py")])
    def test_duplicate(self):
        with self.assertRaises(ValueError):build_integrity_manifest(self.root,["a.py","a.py"])
    def test_non_python(self):
        with self.assertRaises(ValueError):build_integrity_manifest(self.root,["a.txt"])
    def test_empty(self):
        with self.assertRaises(ValueError):build_integrity_manifest(self.root,[])
    def test_no_actions(self):
        self.assertFalse(build_integrity_manifest(self.root,["a.py"]).action_executed)
