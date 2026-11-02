import unittest

from core_ai_tra_son.contract_diagnostics import diagnose_contract
from core_ai_tra_son.integration_contract import IntegrationRequest, validate_request


class DiagnosticBoundsTests(unittest.TestCase):
    def test_field_limit(self):
        data = {f"k{i}": i for i in range(65)}
        result = diagnose_contract(IntegrationRequest("vtnd", data, True))
        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "observation_too_large")

    def test_limit_boundary(self):
        data = {f"k{i}": i for i in range(64)}
        self.assertTrue(diagnose_contract(IntegrationRequest("vtnd", data, True)).accepted)

    def test_oversized_key(self):
        result = diagnose_contract(IntegrationRequest("vtnd", {"x" * 129: 1}, True))
        self.assertEqual(result.reason, "invalid_observation_keys")

    def test_empty_key(self):
        result = diagnose_contract(IntegrationRequest("vtnd", {"": 1}, True))
        self.assertEqual(result.reason, "invalid_observation_keys")

    def test_legacy_contract_unchanged(self):
        request = IntegrationRequest("vtnd", {"march_available": 1}, True)
        self.assertTrue(validate_request(request).accepted)
        self.assertTrue(diagnose_contract(request).accepted)
        self.assertFalse(diagnose_contract(request).independently_verified)

    def test_unverified_stays_blocked(self):
        self.assertFalse(diagnose_contract(IntegrationRequest("nhankhau", {"x": 1})).accepted)


if __name__ == "__main__":
    unittest.main()
