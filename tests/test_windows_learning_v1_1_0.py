import os
import sys
import tempfile
import unittest
from pathlib import Path
from core_ai_tra_son.windows_learning import WindowsLearningStore

class WindowsLearningTests(unittest.TestCase):
    def create(self, root):
        return WindowsLearningStore(root/"ledger.sqlite3",root/"anchor.json",b"k"*32)

    def test_unsupported_platform_fails_closed(self):
        if sys.platform != "win32":
            with tempfile.TemporaryDirectory() as d:
                with self.assertRaises(RuntimeError): self.create(Path(d))

    @unittest.skipUnless(sys.platform == "win32", "Windows-only native test")
    def test_bootstrap_and_replay(self):
        with tempfile.TemporaryDirectory() as d:
            s=self.create(Path(d));s.initialize();s.bootstrap()
            self.assertTrue(s.observe("event1","REVIEW_GATHER",successful=True,verified=True))
            self.assertEqual(self.create(Path(d)).state().gather_samples,1)

    @unittest.skipUnless(sys.platform == "win32", "Windows-only native test")
    def test_dedup_and_freeze_unverified(self):
        with tempfile.TemporaryDirectory() as d:
            s=self.create(Path(d));s.initialize();s.bootstrap()
            self.assertFalse(s.observe("event1","REVIEW_GATHER",successful=True,verified=False))
            self.assertTrue(s.observe("event1","REVIEW_GATHER",successful=True,verified=True))
            self.assertFalse(s.observe("event1","REVIEW_GATHER",successful=True,verified=True))

    @unittest.skipUnless(sys.platform == "win32", "Windows-only native test")
    def test_recovery_after_committed_suffix(self):
        with tempfile.TemporaryDirectory() as d:
            s=self.create(Path(d));s.initialize();s.bootstrap()
            original=s._publish
            def fail(*args):
                raise RuntimeError("simulated post-commit crash")
            s._publish=fail
            with self.assertRaises(RuntimeError):
                s.observe("event1","REVIEW_GATHER",successful=True,verified=True)
            recovered=self.create(Path(d))
            self.assertEqual(recovered.reconcile().gather_samples,1)
            self.assertFalse(recovered.observe("event1","REVIEW_GATHER",successful=True,verified=True))

    @unittest.skipUnless(sys.platform == "win32", "Windows-only native test")
    def test_concurrent_writers(self):
        import threading
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);s=self.create(root);s.initialize();s.bootstrap()
            errors=[]
            def writer(i):
                try:
                    self.create(root).observe("event"+str(i),"REVIEW_GATHER",successful=True,verified=True)
                except Exception as e:
                    errors.append(e)
            threads=[threading.Thread(target=writer,args=(i,)) for i in range(16)]
            for t in threads:t.start()
            for t in threads:t.join()
            self.assertEqual(errors,[])
            self.assertEqual(self.create(root).state().gather_samples,16)

    @unittest.skipUnless(sys.platform == "win32", "Windows-only native test")
    def test_wrong_key_fails(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);s=self.create(root);s.initialize();s.bootstrap()
            with self.assertRaises(ValueError):
                WindowsLearningStore(root/"ledger.sqlite3",root/"anchor.json",b"z"*32).state()
