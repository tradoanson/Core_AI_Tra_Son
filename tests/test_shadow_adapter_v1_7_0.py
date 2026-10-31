import unittest
from core_ai_tra_son.shadow_adapter import shadow_adapter
class AdapterTests(unittest.TestCase):
    def test_wait(self):self.assertEqual(shadow_adapter({"march_available":0},verified=True).selected,"WAIT")
    def test_unverified(self):self.assertEqual(shadow_adapter({"march_available":1}).status,"UNRESOLVED")
    def test_reject_personal(self):
        with self.assertRaises(ValueError):shadow_adapter({"name":"Citizen"},verified=True)
    def test_no_action(self):self.assertFalse(shadow_adapter({"march_available":0},verified=True).action_executed)
    def test_no_mutation(self):
        x={"march_available":0};shadow_adapter(x,verified=True);self.assertEqual(x,{"march_available":0})
    def test_reject_non_dict(self):
        with self.assertRaises(ValueError):shadow_adapter(None,verified=True)
