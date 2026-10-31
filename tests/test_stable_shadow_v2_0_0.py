import unittest
from core_ai_tra_son.stable_shadow import assess_stable_shadow,REQUIRED_JOBS

class StableShadowTests(unittest.TestCase):
    def setUp(self):
        self.jobs={name:True for name in REQUIRED_JOBS}
    def assess(self,**kw):
        return assess_stable_shadow(self.jobs,tests_discovered=407,**kw)
    def test_pass(self):self.assertEqual(self.assess().status,"PASS")
    def test_no_actions(self):self.assertFalse(self.assess().action_executed)
    def test_no_production(self):self.assertFalse(self.assess().production_approved)
    def test_missing(self):
        self.jobs.pop("windows-native")
        self.assertIn("windows-native",self.assess().missing)
    def test_failed(self):
        self.jobs["wheel-sha256"]=False
        self.assertIn("wheel-sha256",self.assess().failed)
    def test_low_tests(self):
        self.assertIn("test_count",assess_stable_shadow(self.jobs,tests_discovered=406).failed)
    def test_version(self):
        self.assertIn("version_mismatch",self.assess(package_version="1.9.0").failed)
    def test_boundary(self):
        self.assertIn("shadow_boundary",self.assess(shadow_boundary=False).failed)
    def test_bad_job_value(self):
        self.jobs["python-3.11"]=1
        with self.assertRaises(ValueError):self.assess()
    def test_bad_test_count(self):
        with self.assertRaises(ValueError):assess_stable_shadow(self.jobs,tests_discovered=True)
