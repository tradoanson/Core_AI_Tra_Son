import unittest
from core_ai_tra_son.integration_contract import (
    IntegrationRequest, validate_request, CONTRACT_VERSION,
)


class IntegrationContractTests(unittest.TestCase):
    def test_valid_synthetic_request(self):
        result = validate_request(IntegrationRequest("vtnd", {"march_available": 1}, verified=True))
        self.assertTrue(result.accepted)
        self.assertEqual(result.mode, "shadow")

    def test_unverified_fails_closed(self):
        self.assertEqual(validate_request(IntegrationRequest("vtnd", {"x": 1})).reason, "unverified_observation")

    def test_unknown_project_fails_closed(self):
        self.assertFalse(validate_request(IntegrationRequest("unknown", {"x": 1}, True)).accepted)

    def test_version_mismatch_fails_closed(self):
        self.assertFalse(validate_request(IntegrationRequest("vtnd", {"x": 1}, True, "3.1.0")).accepted)

    def test_empty_fails_closed(self):
        self.assertFalse(validate_request(IntegrationRequest("nhankhau", {}, True)).accepted)

    def test_contract_version(self):
        self.assertEqual(CONTRACT_VERSION, "3.2.0")


if __name__ == "__main__":
    unittest.main()
