import unittest
from core_ai_tra_son import CoreAI
from core_ai_tra_son.adaptive import EtaAdaptive
from core_ai_tra_son.tiny_ai import TinyPredictor

class CoreTests(unittest.TestCase):
    def test_vtnd_unverified(self):
        self.assertEqual(CoreAI('vtnd').evaluate({'march_available': 1}).status, 'UNRESOLVED')
    def test_vtnd_waiting(self):
        self.assertEqual(CoreAI('vtnd').evaluate({'march_available': 0, 'verified': True}).status, 'WAITING')
    def test_missing_fields(self):
        result = CoreAI('nhankhau').evaluate({'record': {'name': 'A'}, 'required_fields': ['name', 'birth_date']})
        self.assertEqual(result.details['missing_fields'], ['birth_date'])
    def test_adaptive_only_verified(self):
        a = EtaAdaptive()
        self.assertFalse(a.observe(60, 90))
        self.assertEqual(a.samples, 0)
        self.assertTrue(a.observe(60, 90, verified=True))
        self.assertGreater(a.correct(60), 60)
    def test_predictor(self):
        self.assertEqual(TinyPredictor().predict_eta(60, 5)['eta_seconds'], 65)

if __name__ == '__main__': unittest.main()
