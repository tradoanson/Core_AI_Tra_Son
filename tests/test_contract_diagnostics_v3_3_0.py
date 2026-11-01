import unittest

from core_ai_tra_son.contract_diagnostics import diagnose_contract
from core_ai_tra_son.integration_contract import IntegrationRequest


class ContractDiagnosticsTests(unittest.TestCase):
    def test_valid_request_stays_shadow(self):
        result = diagnose_contract(IntegrationRequest("vtnd", {"march_available": 1}, True))
        self.assertTrue(result.accepted)
        self.assertEqual(result.mode, "shadow")
        self.assertFalse(result.independently_verified)

    def test_wrong_type_fails_closed(self):
        for value in (None, {}, [], "vtnd", 1):
            with self.subTest(value=value):
                self.assertEqual(diagnose_contract(value).reason, "invalid_request_type")

    def test_unverified_fails_closed(self):
        self.assertFalse(diagnose_contract(IntegrationRequest("vtnd", {"x": 1})).accepted)

    def test_unsupported_project_fails_closed(self):
        self.assertEqual(diagnose_contract(IntegrationRequest("unknown", {"x": 1}, True)).reason, "unsupported_project")

    def test_version_mismatch_fails_closed(self):
        self.assertEqual(diagnose_contract(IntegrationRequest("vtnd", {"x": 1}, True, "3.3.0")).reason, "unsupported_contract_version")

    def test_empty_observation_fails_closed(self):
        self.assertEqual(diagnose_contract(IntegrationRequest("nhankhau", {}, True)).reason, "empty_observation")

    def test_non_boolean_verification_rejected(self):
        for value in (1, "true", None):
            self.assertEqual(diagnose_contract(IntegrationRequest("vtnd", {"x": 1}, value)).reason, "invalid_verified_type")

    def test_malformed_metadata_rejected(self):
        self.assertEqual(diagnose_contract(IntegrationRequest(1, {"x": 1}, True)).reason, "invalid_metadata_type")

    def test_does_not_mutate_observation(self):
        observation = {"nested": [1, 2]}
        before = repr(observation)
        diagnose_contract(IntegrationRequest("vtnd", observation, True))
        self.assertEqual(repr(observation), before)


if __name__ == "__main__":
    unittest.main()
