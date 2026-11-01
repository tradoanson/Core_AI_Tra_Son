import importlib
import subprocess
import sys
import unittest
from pathlib import Path
from core_ai_tra_son.shadow_snapshot import shadow_snapshot

class ModularCoreTests(unittest.TestCase):
    def test_snapshot_synthetic(self):
        self.assertEqual(shadow_snapshot()["input_kind"],"SYNTHETIC_ONLY")
    def test_no_actions(self):
        self.assertFalse(shadow_snapshot()["action_executed"])
    def test_no_production(self):
        self.assertFalse(shadow_snapshot()["production_integrated"])
    def test_reject_bool(self):
        with self.assertRaises(ValueError):shadow_snapshot(True)
    def test_reject_negative(self):
        with self.assertRaises(ValueError):shadow_snapshot(-1)
    def test_reject_string(self):
        with self.assertRaises(ValueError):shadow_snapshot("1")
    def test_viewer_backward_compat(self):
        from scripts.windows_shadow_viewer import snapshot
        self.assertEqual(snapshot(0),shadow_snapshot(0))
    def test_import_does_not_load_tkinter(self):
        code="import sys; from core_ai_tra_son.shadow_snapshot import shadow_snapshot; assert 'tkinter' not in sys.modules; assert not shadow_snapshot()['action_executed']"
        p=subprocess.run([sys.executable,"-c",code],cwd=Path.cwd(),capture_output=True,text=True,timeout=20)
        self.assertEqual(p.returncode,0,p.stderr)
    def test_package_core_without_gui(self):
        self.assertTrue(callable(importlib.import_module("core_ai_tra_son").CoreAI))
    def test_core_module_has_no_gui_import(self):
        source=Path("core_ai_tra_son/shadow_snapshot.py").read_text(encoding="utf-8")
        self.assertNotIn("tkinter",source.replace("No Tkinter",""))
