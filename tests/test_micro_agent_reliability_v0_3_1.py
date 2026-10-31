import concurrent.futures
import json
import unittest
from core_ai_tra_son.agent import MicroAgent, AgentResult
from core_ai_tra_son.audit import SafeAuditLog

class AgentReliabilityTests(unittest.TestCase):
    def test_repeatability(self):
        agent = MicroAgent("vtnd")
        obs = {"verified": True, "march_available": 2, "secret": "PRIVATE"}
        outputs = [agent.evaluate(obs).to_dict() for _ in range(100)]
        self.assertTrue(all(output == outputs[0] for output in outputs))

    def test_parallel_evaluations_consistent(self):
        agent = MicroAgent("vtnd")
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            outputs = list(pool.map(lambda _: agent.evaluate({"verified": True, "march_available": 0}).to_dict(), range(100)))
        self.assertEqual(len({json.dumps(x, sort_keys=True) for x in outputs}), 1)

    def test_observation_key_limit(self):
        obs = {"verified": True, "march_available": 0, **{str(i): i for i in range(70)}}
        r = MicroAgent("vtnd").evaluate(obs)
        self.assertEqual(r.reason_codes, ("RESOURCE_LIMIT",))

    def test_required_fields_limit(self):
        obs = {"required_fields": [str(i) for i in range(129)], "record": {}}
        self.assertEqual(MicroAgent("nhankhau").evaluate(obs).status, "UNRESOLVED")

    def test_record_key_limit(self):
        obs = {"required_fields": ["name"], "record": {str(i): i for i in range(257)}}
        self.assertEqual(MicroAgent("nhankhau").evaluate(obs).status, "UNRESOLVED")

    def test_duplicate_required_fields_rejected(self):
        obs = {"required_fields": ["name", "name"], "record": {"name": "x"}}
        self.assertEqual(MicroAgent("nhankhau").evaluate(obs).status, "UNRESOLVED")

    def test_memory_samples_limit(self):
        r = MicroAgent("vtnd").evaluate({"verified": True, "march_available": 1},
            memory_state={"namespace": "vtnd", "samples": 10**100, "bias_seconds": 5})
        self.assertFalse(r.memory_used)

    def test_ring_capacity(self):
        log = SafeAuditLog(capacity=3)
        agent = MicroAgent("vtnd")
        for i in range(8):
            log.record(agent.evaluate({"verified": True, "march_available": i}))
        self.assertEqual(len(log), 3)
        self.assertEqual([x["sequence"] for x in log.snapshot()], [6, 7, 8])

    def test_audit_never_records_private_fields(self):
        log = SafeAuditLog()
        r = MicroAgent("nhankhau").evaluate({"required_fields": ["name"], "record": {"name": "SECRET_NAME"}})
        log.record(r)
        self.assertNotIn("SECRET", json.dumps(log.snapshot()))
        self.assertNotIn("name", json.dumps(log.snapshot()))

    def test_audit_rejects_executed_actions(self):
        log = SafeAuditLog()
        bad = AgentResult("vtnd", "REVIEW", "x", 1.0, ("MARCH_EMPTY",), {}, False, True)
        with self.assertRaises(ValueError):
            log.record(bad)

    def test_audit_rejects_unknown_reasons(self):
        log = SafeAuditLog()
        bad = AgentResult("vtnd", "REVIEW", "x", 1.0, ("PERSONAL_INFO",), {}, False)
        with self.assertRaises(ValueError):
            log.record(bad)

    def test_audit_capacity_validation(self):
        for capacity in (0, -1, 4097, True, 1.5):
            with self.subTest(capacity=capacity), self.assertRaises(ValueError):
                SafeAuditLog(capacity)

    def test_bad_input_type(self):
        with self.assertRaises(TypeError):
            MicroAgent("vtnd").evaluate(None)

    def test_log_is_memory_only(self):
        log = SafeAuditLog(1)
        self.assertEqual(log.snapshot(), [])

if __name__ == "__main__":
    unittest.main()
