import unittest

from core_ai_tra_son.contract_diagnostics import diagnose_contract
from core_ai_tra_son.integration_contract import IntegrationRequest


class MetadataBoundsTests(unittest.TestCase):
    def test_project_over_limit(self):
        r = diagnose_contract(IntegrationRequest("x" * 129, {"ok": 1}, True))
        self.assertFalse(r.accepted)
        self.assertEqual(r.reason, "metadata_too_large")

    def test_contract_version_over_limit(self):
        request = IntegrationRequest("vtnd", {"ok": 1}, True)
        object.__setattr__(request, "contract_version", "x" * 129)
        self.assertEqual(diagnose_contract(request).reason, "metadata_too_large")

    def test_project_boundary_preserves_normal_validation(self):
        r = diagnose_contract(IntegrationRequest("x" * 128, {"ok": 1}, True))
        self.assertNotEqual(r.reason, "metadata_too_large")

    def test_legacy_request_accepted(self):
        r = diagnose_contract(IntegrationRequest("vtnd", {"march_available": 1}, True))
        self.assertTrue(r.accepted)
        self.assertFalse(r.independently_verified)

    def test_unverified_still_blocked(self):
        self.assertFalse(diagnose_contract(IntegrationRequest("vtnd", {"ok": 1}, False)).accepted)


if __name__ == "__main__":
    unittest.main()
