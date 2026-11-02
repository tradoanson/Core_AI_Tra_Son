import unittest

from core_ai_tra_son.contract_diagnostics import diagnose_contract
from core_ai_tra_son.integration_contract import IntegrationRequest


class ContractSafetyTests(unittest.TestCase):
    def test_malformed_observation_fails_closed(self):
        for observation in (None, [], "x", 3):
            with self.subTest(observation=observation):
                result = diagnose_contract(IntegrationRequest("vtnd", observation, True))
                self.assertFalse(result.accepted)
                self.assertEqual(result.reason, "invalid_observation_type")

    def test_non_string_keys_fail_closed(self):
        for observation in ({1: "x"}, {None: "x"}):
            with self.subTest(observation=observation):
                self.assertEqual(diagnose_contract(IntegrationRequest("vtnd", observation, True)).reason, "invalid_observation_keys")

    def test_no_independent_attestation(self):
        result = diagnose_contract(IntegrationRequest("vtnd", {"x": 1}, True))
        self.assertTrue(result.accepted)
        self.assertFalse(result.independently_verified)
        self.assertEqual(result.mode, "shadow")

    def test_unknown_project_rejected(self):
        self.assertFalse(diagnose_contract(IntegrationRequest("other", {"x": 1}, True)).accepted)

    def test_input_not_modified(self):
        data = {"x": [1, 2]}
        original = repr(data)
        diagnose_contract(IntegrationRequest("nhankhau", data, True))
        self.assertEqual(repr(data), original)


if __name__ == "__main__":
    unittest.main()
