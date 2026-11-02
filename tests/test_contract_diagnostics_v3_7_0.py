import unittest

from core_ai_tra_son.contract_diagnostics import diagnose_contract
from core_ai_tra_son.integration_contract import IntegrationRequest


class CollectionBoundsTests(unittest.TestCase):
    def check(self, observation):
        return diagnose_contract(IntegrationRequest("vtnd", observation, True))

    def test_oversized_list(self):
        self.assertEqual(self.check({"items": [0] * 257}).reason, "observation_collection_too_large")

    def test_oversized_tuple(self):
        self.assertEqual(self.check({"items": (0,) * 257}).reason, "observation_collection_too_large")

    def test_oversized_dict(self):
        self.assertEqual(self.check({"items": {str(i): i for i in range(257)}}).reason, "observation_collection_too_large")

    def test_boundary_list(self):
        self.assertTrue(self.check({"items": [0] * 256}).accepted)

    def test_unverified_remains_blocked(self):
        self.assertFalse(diagnose_contract(IntegrationRequest("vtnd", {"items": [0]}, False)).accepted)

    def test_independent_verification_never_claimed(self):
        self.assertFalse(self.check({"items": [0]}).independently_verified)


if __name__ == "__main__":
    unittest.main()
