"""Release acceptance checks: offline, read-only, reproducible."""
import ast
import math
import pathlib
import subprocess
import sys
import tempfile
import unittest

from core_ai_tra_son import CoreAI
from core_ai_tra_son.adaptive import EtaAdaptive
from core_ai_tra_son.tiny_ai import TinyPredictor

ROOT = pathlib.Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "core_ai_tra_son"

class ReleaseAcceptance(unittest.TestCase):
    def test_release_metadata(self):
        text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('version = "0.7.3"', text)

    def test_public_import(self):
        self.assertTrue(callable(CoreAI))
        self.assertEqual(CoreAI("vtnd").evaluate({"march_available": 0, "verified": True}).status, "WAITING")

    def test_host_data_is_not_mutated(self):
        data = {"record": {"name": "Test"}, "required_fields": ["name", "birth_date"]}
        before = repr(data)
        CoreAI("nhankhau").evaluate(data)
        self.assertEqual(repr(data), before)

    def test_unverified_never_dispatches(self):
        for march in (0, 1, 5, None, -1, True):
            self.assertEqual(CoreAI("vtnd").evaluate({"march_available": march, "verified": False}).status, "UNRESOLVED")

    def test_no_external_dependencies(self):
        text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn("dependencies = []", text)

    def test_package_static_no_execution_or_network(self):
        banned = {"subprocess", "socket", "requests", "urllib", "httpx", "ctypes", "winreg"}
        for file in PACKAGE.glob("*.py"):
            with self.subTest(file=file.name):
                tree = ast.parse(file.read_text(encoding="utf-8"))
                imports = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imports.update(alias.name.split(".")[0] for alias in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imports.add(node.module.split(".")[0])
                self.assertFalse(imports & (banned - ({"urllib"} if file.name in {"memory.py", "learning_store.py", "secure_learning.py", "hardened_learning.py", "evaluation_integrity.py"} else set())), imports & banned)

    def test_package_has_no_host_file_writes(self):
        suspicious = {"open", "write_text", "write_bytes", "unlink", "remove", "rmtree", "system", "popen", "eval", "exec"}
        for file in PACKAGE.glob("*.py"):
            with self.subTest(file=file.name):
                tree = ast.parse(file.read_text(encoding="utf-8"))
                calls = {node.func.id if isinstance(node.func, ast.Name) else node.func.attr
                         for node in ast.walk(tree) if isinstance(node, ast.Call)
                         if isinstance(node.func, (ast.Name, ast.Attribute))}
                self.assertFalse(calls & (suspicious - ({"open", "unlink"} if file.name in {"memory.py", "learning_store.py", "secure_learning.py", "hardened_learning.py", "evaluation_integrity.py"} else set())), calls & suspicious)

    def test_no_secret_like_literals_in_package(self):
        import re
        for file in PACKAGE.glob("*.py"):
            with self.subTest(file=file.name):
                source = file.read_text(encoding="utf-8")
                self.assertNotRegex(source, r"(?i)(?:api_key|secret|password|access_token)\\s*=\\s*['\\\"][^'\\\"]{8,}")

    def test_release_docs_exist(self):
        for path in ("CHANGELOG.md", "FUTUREBASE.md", "VERSIONING_WORKFLOW.md", "acceptance/ACCEPTANCE_v0.1.1.md"):
            with self.subTest(path=path):
                self.assertTrue((ROOT / path).is_file())

if __name__ == "__main__":
    unittest.main()
