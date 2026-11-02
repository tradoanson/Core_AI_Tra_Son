import unittest

from core_ai_tra_son.contract_diagnostics import diagnose_contract
from core_ai_tra_son.integration_contract import IntegrationRequest


class BinaryBoundsTests(unittest.TestCase):
    def diagnose(self, value, verified=True):
        return diagnose_contract(IntegrationRequest("vtnd", {"payload": value}, verified))

    def test_oversized_bytes(self):
        r = self.diagnose(b"x" * 4097)
        self.assertFalse(r.accepted)
        self.assertEqual(r.reason, "observation_binary_too_large")
        self.assertEqual(r.mode, "shadow")

    def test_oversized_bytearray(self):
        self.assertEqual(self.diagnose(bytearray(4097)).reason, "observation_binary_too_large")

    def test_boundary_bytes(self):
        self.assertNotEqual(self.diagnose(b"x" * 4096).reason, "observation_binary_too_large")

    def test_boundary_bytearray(self):
        self.assertNotEqual(self.diagnose(bytearray(4096)).reason, "observation_binary_too_large")

    def test_unverified_stays_blocked(self):
        self.assertFalse(self.diagnose(b"ok", False).accepted)

    def test_legacy_contract(self):
        r = diagnose_contract(IntegrationRequest("vtnd", {"march_available": 1}, True))
        self.assertTrue(r.accepted)
        self.assertFalse(r.independently_verified)


if __name__ == "__main__":
    unittest.main()
