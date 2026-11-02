import unittest
from dataclasses import replace

from core_ai_tra_son.model_memory_v1 import (
    ModelMemoryEvent, ModelMemoryRecord, ModelMemoryV1,
    remember_model_event, verify_model_memory
)


def event(id="e1", value=10):
    return ModelMemoryEvent(id, "tiny-ml-v1", "a" * 64, "mae_seconds", value)


class ModelMemoryV1Tests(unittest.TestCase):
    def test_append_and_verify(self):
        m = remember_model_event(ModelMemoryV1(), event())
        self.assertTrue(verify_model_memory(m))
        self.assertEqual(len(m.records), 1)

    def test_idempotent_replay(self):
        m = remember_model_event(ModelMemoryV1(), event())
        self.assertIs(remember_model_event(m, event()), m)

    def test_conflicting_replay(self):
        m = remember_model_event(ModelMemoryV1(), event())
        with self.assertRaisesRegex(ValueError, "conflicting"):
            remember_model_event(m, event(value=11))

    def test_chain_links(self):
        m = remember_model_event(remember_model_event(ModelMemoryV1(), event()), event("e2"))
        self.assertEqual(m.records[1].previous_hash, m.records[0].record_hash)

    def test_tampering_rejected(self):
        m = remember_model_event(ModelMemoryV1(), event())
        bad = ModelMemoryV1((replace(m.records[0], record_hash="0" * 64),))
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            verify_model_memory(bad)

    def test_broken_chain_rejected(self):
        m = remember_model_event(remember_model_event(ModelMemoryV1(), event()), event("e2"))
        bad = ModelMemoryV1((m.records[0], replace(m.records[1], previous_hash="0" * 64)))
        with self.assertRaises(ValueError):
            verify_model_memory(bad)

    def test_duplicate_id_rejected(self):
        m = remember_model_event(ModelMemoryV1(), event())
        bad = ModelMemoryV1((m.records[0], m.records[0]))
        with self.assertRaises(ValueError):
            verify_model_memory(bad)

    def test_invalid_digest_rejected(self):
        with self.assertRaises(ValueError):
            remember_model_event(ModelMemoryV1(), replace(event(), dataset_sha256="bad"))

    def test_nonfinite_rejected(self):
        with self.assertRaises(ValueError):
            remember_model_event(ModelMemoryV1(), event(value=float("nan")))

    def test_original_unchanged(self):
        initial = ModelMemoryV1()
        remember_model_event(initial, event())
        self.assertEqual(initial.records, ())


if __name__ == "__main__":
    unittest.main()
