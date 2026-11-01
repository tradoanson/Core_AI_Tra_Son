import ast
import os
import subprocess
import sys
import unittest
from pathlib import Path

class StandaloneV3Tests(unittest.TestCase):
    def test_headless_self_test(self):
        p=subprocess.run([sys.executable,"scripts/windows_shadow_viewer.py","--self-test"],capture_output=True,text=True,timeout=20,env={**os.environ,"PYTHONPATH":str(Path.cwd())+os.pathsep+os.environ.get("PYTHONPATH","")})
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn('"OFFLINE_SHADOW"',p.stdout)
        self.assertIn('"action_executed": false',p.stdout)
    def test_version_label(self):
        self.assertIn("v3.1.0",Path("scripts/windows_shadow_viewer.py").read_text(encoding="utf-8"))
    def test_cli_guard(self):
        tree=ast.parse(Path("scripts/windows_shadow_viewer.py").read_text(encoding="utf-8"))
        self.assertTrue(any(isinstance(n,ast.If) for n in tree.body))
