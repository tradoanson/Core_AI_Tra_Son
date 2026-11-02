import unittest

from core_ai_tra_son.contract_diagnostics import diagnose_contract
from core_ai_tra_son.integration_contract import IntegrationRequest


class NestedDepthTests(unittest.TestCase):
    def diagnose(self, value):
        return diagnose_contract(IntegrationRequest("vtnd", {"nested": value}, True))

    def test_excessive_depth_rejected(self):
        value = 1
        for _ in range(9):
            value = [value]
        r = self.diagnose(value)
        self.assertFalse(r.accepted)
        self.assertEqual(r.reason, "observation_too_deep")
        self.assertEqual(r.mode, "shadow")

    def test_depth_boundary(self):
        value = 1
        for _ in range(8):
            value = [value]
        self.assertNotEqual(self.diagnose(value).reason, "observation_too_deep")

    def test_cycle_terminates(self):
        value = []
        value.append(value)
        self.assertNotEqual(self.diagnose(value).reason, "observation_too_deep")

    def test_deep_dict(self):
        value = 0
        for _ in range(9):
            value = {"next": value}
        self.assertEqual(self.diagnose(value).reason, "observation_too_deep")

    def test_legacy_accepted(self):
        r = diagnose_contract(IntegrationRequest("vtnd", {"march_available": 1}, True))
        self.assertTrue(r.accepted)
        self.assertFalse(r.independently_verified)


if __name__ == "__main__":
    unittest.main()
