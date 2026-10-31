import tracemalloc
import unittest
from core_ai_tra_son.resource_probe import measure_shadow_resources

class ResourceProbeTests(unittest.TestCase):
    def test_measure(self):
        r=measure_shadow_resources({"march_available":0},iterations=2)
        self.assertEqual(r.iterations,2)
        self.assertGreaterEqual(r.wall_ms,0)
        self.assertGreaterEqual(r.cpu_ms,0)
        self.assertGreaterEqual(r.peak_traced_bytes,0)
        self.assertFalse(r.action_executed)
    def test_reject_non_dict(self):
        with self.assertRaises(ValueError):measure_shadow_resources(None)
    def test_reject_zero(self):
        with self.assertRaises(ValueError):measure_shadow_resources({},iterations=0)
    def test_reject_large(self):
        with self.assertRaises(ValueError):measure_shadow_resources({},iterations=201)
    def test_reject_bool(self):
        with self.assertRaises(ValueError):measure_shadow_resources({},iterations=True)
    def test_external_tracer_preserved(self):
        tracemalloc.start()
        try:
            with self.assertRaises(ValueError):measure_shadow_resources({})
            self.assertTrue(tracemalloc.is_tracing())
        finally:tracemalloc.stop()
