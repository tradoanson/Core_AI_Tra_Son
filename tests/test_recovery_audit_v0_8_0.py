import unittest
from dataclasses import replace
from core_ai_tra_son.recovery_audit import RecoveryAudit

class RecoveryAuditTests(unittest.TestCase):
    def setUp(self):
        self.audit = RecoveryAudit(b"k"*32)
    def review(self):
        return self.audit.append((), target="REVIEWED", reviewer="reviewer1", evidence=b"verified", evidence_valid=True, independent_reviewer=True)
    def test_review(self):
        self.assertEqual(self.audit.verify(self.review()),"REVIEWED")
    def test_full_chain(self):
        e=self.review()
        e=self.audit.append(e,target="APPROVED",reviewer="approver2",evidence=b"approval",evidence_valid=True,independent_approver=True)
        e=self.audit.append(e,target="ACTIVE",reviewer="operator3",evidence=b"override",evidence_valid=True,override_valid=True)
        e=self.audit.append(e,target="CLOSED",reviewer="approver2",evidence=b"closure",closure_reviewed=True,independent_approver=True)
        self.assertEqual(self.audit.verify(e),"CLOSED")
    def test_reject_tamper(self):
        e=self.review()
        with self.assertRaises(ValueError): self.audit.verify((replace(e[0],reviewer="attacker"),))
    def test_reject_wrong_key(self):
        with self.assertRaises(ValueError): RecoveryAudit(b"z"*32).verify(self.review())
    def test_reject_skip(self):
        with self.assertRaises(ValueError): self.audit.append((),target="ACTIVE",reviewer="a",evidence=b"x",evidence_valid=True,override_valid=True)
    def test_reject_missing_approval(self):
        with self.assertRaises(ValueError): self.audit.append(self.review(),target="APPROVED",reviewer="a",evidence=b"x",evidence_valid=True)
    def test_reject_empty_evidence(self):
        with self.assertRaises(ValueError): self.audit.append((),target="REVIEWED",reviewer="a",evidence=b"",evidence_valid=True,independent_reviewer=True)
    def test_reject_invalid_reviewer(self):
        with self.assertRaises(ValueError): self.audit.append((),target="REVIEWED",reviewer="bad id",evidence=b"x",evidence_valid=True,independent_reviewer=True)
    def test_reject_reorder(self):
        e=self.review()
        e=self.audit.append(e,target="APPROVED",reviewer="a",evidence=b"x",evidence_valid=True,independent_approver=True)
        with self.assertRaises(ValueError): self.audit.verify(e[::-1])
    def test_reject_truncation_as_expected_phase(self):
        e=self.review()
        self.assertNotEqual(self.audit.verify(e),"CLOSED")
    def test_no_host_action(self):
        self.assertFalse(hasattr(self.audit,"dispatch"))
