import tempfile
import unittest
from pathlib import Path
from core_ai_tra_son.memory import AdaptiveMemory

class AdaptiveMemoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "adaptive.sqlite3"
        self.a = AdaptiveMemory(self.path, "vtnd", alpha=0.5)

    def test_initialize_is_explicit(self):
        self.assertFalse(self.path.exists())
        self.assertEqual(self.a.state()["samples"], 0)
        self.assertFalse(self.path.exists())
        self.a.initialize()
        self.assertTrue(self.path.exists())

    def test_verified_only(self):
        self.a.initialize()
        self.assertFalse(self.a.observe(60, 80))
        self.assertEqual(self.a.state()["samples"], 0)

    def test_persistence_after_restart(self):
        self.a.initialize()
        self.assertTrue(self.a.observe(60, 80, verified=True))
        other = AdaptiveMemory(self.path, "vtnd", alpha=0.5)
        self.assertEqual(other.state()["samples"], 1)
        self.assertEqual(other.correct(60), 70)

    def test_namespace_isolation(self):
        self.a.initialize()
        self.a.observe(60, 80, verified=True)
        b = AdaptiveMemory(self.path, "nhankhau")
        self.assertEqual(b.state()["samples"], 0)
        self.assertEqual(b.state()["bias_seconds"], 0)

    def test_outlier_rejected(self):
        self.a.initialize()
        self.assertFalse(self.a.observe(60, 5000, verified=True))
        self.assertEqual(self.a.state()["samples"], 0)

    def test_nan_inf_and_bool_rejected(self):
        self.a.initialize()
        for value in (float("nan"), float("inf"), -1, True, 604801):
            with self.subTest(value=value), self.assertRaises(ValueError):
                self.a.observe(value, 10, verified=True)
        self.assertEqual(self.a.state()["samples"], 0)

    def test_no_file_created_by_unverified_observation(self):
        self.assertFalse(self.a.observe(60, 80, verified=False))
        self.assertFalse(self.path.exists())

    def test_observe_before_initialize_fails(self):
        with self.assertRaises(Exception):
            self.a.observe(60, 80, verified=True)

    def test_invalid_namespace(self):
        with self.assertRaises(ValueError):
            AdaptiveMemory(self.path, "")

    def test_invalid_alpha(self):
        for value in (0, 2, float("nan"), True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                AdaptiveMemory(self.path, "vtnd", alpha=value)

    def test_refuse_unrecognized_existing_db(self):
        import sqlite3
        with sqlite3.connect(self.path) as db:
            db.execute("CREATE TABLE unrelated (id INTEGER)")
        with self.assertRaises(ValueError):
            self.a.initialize()

    def test_no_host_app_mutation(self):
        self.a.initialize()
        self.a.observe(60, 80, verified=True)
        self.assertTrue(self.path.exists())
