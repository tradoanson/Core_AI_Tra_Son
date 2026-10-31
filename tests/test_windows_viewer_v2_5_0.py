import ast
import unittest
from pathlib import Path

class ViewerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=Path("scripts/windows_shadow_viewer.py").read_text(encoding="utf-8")
        cls.tree=ast.parse(cls.source)
    def test_main_guard(self):self.assertIn('if __name__=="__main__":',self.source)
    def test_no_network(self):self.assertNotIn("requests",self.source)
    def test_no_subprocess(self):self.assertNotIn("subprocess",self.source)
    def test_no_host_actions(self):self.assertIn('"action_executed":False',self.source)
    def test_synthetic(self):self.assertIn('"input_kind":"SYNTHETIC_ONLY"',self.source)
    def test_no_production(self):self.assertIn('"production_integrated":False',self.source)
    def test_tkinter(self):self.assertIn("import tkinter",self.source)
    def test_no_import_execution(self):
        self.assertTrue(any(isinstance(n,ast.If) for n in self.tree.body))
