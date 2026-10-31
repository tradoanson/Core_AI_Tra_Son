import unittest
from dataclasses import replace
from core_ai_tra_son.recovery_audit import RecoveryAudit
from core_ai_tra_son.recovery_anchor import issue_anchor,verify_anchor
class AnchorTests(unittest.TestCase):
    def setUp(self):
        self.audit=RecoveryAudit(b"a"*32);self.key=b"b"*32
        self.entries=self.audit.append((),target="REVIEWED",reviewer="reviewer",evidence=b"proof",evidence_valid=True,independent_reviewer=True)
    def test_verify(self):
        a=issue_anchor(self.audit,self.entries,anchor_key=self.key)
        self.assertTrue(verify_anchor(self.audit,self.entries,a,anchor_key=self.key))
    def test_truncation(self):
        a=issue_anchor(self.audit,self.entries,anchor_key=self.key)
        with self.assertRaises(ValueError):verify_anchor(self.audit,(),a,anchor_key=self.key)
    def test_wrong_key(self):
        a=issue_anchor(self.audit,self.entries,anchor_key=self.key)
        with self.assertRaises(ValueError):verify_anchor(self.audit,self.entries,a,anchor_key=b"z"*32)
    def test_tamper(self):
        a=issue_anchor(self.audit,self.entries,anchor_key=self.key)
        with self.assertRaises(ValueError):verify_anchor(self.audit,self.entries,replace(a,count=2),anchor_key=self.key)
    def test_short_key(self):
        with self.assertRaises(ValueError):issue_anchor(self.audit,self.entries,anchor_key=b"k")
    def test_empty(self):
        a=issue_anchor(self.audit,(),anchor_key=self.key)
        self.assertTrue(verify_anchor(self.audit,(),a,anchor_key=self.key))
