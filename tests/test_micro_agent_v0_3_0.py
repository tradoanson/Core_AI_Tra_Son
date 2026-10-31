import unittest
from core_ai_tra_son.agent import MicroAgent

class MicroAgentTests(unittest.TestCase):
    def test_unverified_fails_closed(self):
        r = MicroAgent("vtnd").evaluate({"verified": False, "march_available": 3})
        self.assertEqual(r.status, "UNRESOLVED")
        self.assertFalse(r.action_executed)

    def test_verified_empty_waiting(self):
        r = MicroAgent("vtnd").evaluate({"verified": True, "march_available": 0})
        self.assertEqual(r.status, "WAITING")

    def test_verified_available_review_not_dispatch(self):
        r = MicroAgent("vtnd").evaluate({"verified": True, "march_available": 2})
        self.assertEqual(r.status, "REVIEW")
        self.assertFalse(r.action_executed)

    def test_invalid_march(self):
        for x in (-1, True, "3", None):
            with self.subTest(x=x):
                self.assertEqual(MicroAgent("vtnd").evaluate({"verified": True, "march_available": x}).status, "UNRESOLVED")

    def test_valid_memory_context(self):
        r = MicroAgent("vtnd").evaluate({"verified": True, "march_available": 1},
            memory_state={"namespace": "vtnd", "bias_seconds": 12.5, "samples": 3})
        self.assertTrue(r.memory_used)
        self.assertEqual(r.details["eta_bias_seconds"], 12.5)

    def test_foreign_memory_rejected(self):
        r = MicroAgent("vtnd").evaluate({"verified": True, "march_available": 1},
            memory_state={"namespace": "nhankhau", "bias_seconds": 12.5, "samples": 3})
        self.assertFalse(r.memory_used)

    def test_nonfinite_memory_rejected(self):
        r = MicroAgent("vtnd").evaluate({"verified": True, "march_available": 1},
            memory_state={"namespace": "vtnd", "bias_seconds": float("nan"), "samples": 3})
        self.assertFalse(r.memory_used)

    def test_no_personal_data_in_nhankhau_output(self):
        r = MicroAgent("nhankhau").evaluate({"required_fields": ["name", "dob"],
            "record": {"name": "SECRET_PERSON", "dob": None, "id": "SECRET_ID"}})
        self.assertEqual(r.status, "REVIEW")
        self.assertEqual(r.details["missing_count"], 1)
        self.assertNotIn("SECRET", str(r.to_dict()))
        self.assertFalse(r.action_executed)

    def test_nhankhau_empty_schema_fails_closed(self):
        self.assertEqual(MicroAgent("nhankhau").evaluate({"record": {}}).status, "UNRESOLVED")

    def test_invalid_profile(self):
        with self.assertRaises(ValueError):
            MicroAgent("unknown")

    def test_no_input_mutation(self):
        obs = {"verified": True, "march_available": 1, "secret": ["x"]}
        before = repr(obs)
        MicroAgent("vtnd").evaluate(obs)
        self.assertEqual(repr(obs), before)

    def test_result_serializable(self):
        import json
        result = MicroAgent("vtnd").evaluate({"verified": True, "march_available": 0})
        self.assertFalse(json.loads(json.dumps(result.to_dict()))["action_executed"])

if __name__ == "__main__":
    unittest.main()
