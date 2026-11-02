import unittest

from core_ai_tra_son.contract_diagnostics import diagnose_contract
from core_ai_tra_son.integration_contract import IntegrationRequest


class DiagnosticTextBoundsTests(unittest.TestCase):
    def test_oversized_text_rejected(self):
        result = diagnose_contract(IntegrationRequest("vtnd", {"note": "x" * 4097}, True))
        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "observation_text_too_large")
        self.assertEqual(result.mode, "shadow")
        self.assertFalse(result.independently_verified)

    def test_boundary_text_accepted(self):
        result = diagnose_contract(IntegrationRequest("vtnd", {"note": "x" * 4096}, True))
        self.assertTrue(result.accepted)
        self.assertFalse(result.independently_verified)

    def test_unverified_never_accepted(self):
        result = diagnose_contract(IntegrationRequest("vtnd", {"note": "ok"}, False))
        self.assertFalse(result.accepted)

    def test_previous_field_bounds_still_apply(self):
        result = diagnose_contract(IntegrationRequest("vtnd", {"x" * 129: "ok"}, True))
        self.assertEqual(result.reason, "invalid_observation_keys")


if __name__ == "__main__":
    unittest.main()
