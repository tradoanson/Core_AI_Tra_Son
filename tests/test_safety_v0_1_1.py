import math
import unittest
from core_ai_tra_son import CoreAI, Decision
from core_ai_tra_son.adaptive import EtaAdaptive
from core_ai_tra_son.tiny_ai import TinyPredictor

class SafetyTests(unittest.TestCase):
    def test_invalid_profile(self):
        with self.assertRaises(ValueError): CoreAI('unknown')
    def test_invalid_observation(self):
        with self.assertRaises(TypeError): CoreAI('vtnd').evaluate(None)
    def test_bool_march_rejected(self):
        self.assertEqual(CoreAI('vtnd').evaluate({'march_available': True, 'verified': True}).status, 'UNRESOLVED')
    def test_negative_march_rejected(self):
        self.assertEqual(CoreAI('vtnd').evaluate({'march_available': -1, 'verified': True}).status, 'UNRESOLVED')
    def test_available_march_review_only(self):
        self.assertEqual(CoreAI('vtnd').evaluate({'march_available': 1, 'verified': True}).status, 'REVIEW')
    def test_missing_schema(self):
        self.assertEqual(CoreAI('nhankhau').evaluate({'record': None}).status, 'UNRESOLVED')
    def test_blank_field(self):
        self.assertEqual(CoreAI('nhankhau').evaluate({'record': {'name': '  '}, 'required_fields': ['name']}).details['missing_fields'], ['name'])
    def test_decision_serializable(self):
        self.assertEqual(Decision('WAITING','none',1.0,{}).to_dict()['status'], 'WAITING')
    def test_adaptive_range(self):
        with self.assertRaises(ValueError): EtaAdaptive(alpha=0)
    def test_adaptive_bias_cap(self):
        a=EtaAdaptive(alpha=1)
        a.observe(0, 10000, verified=True)
        self.assertEqual(a.bias_seconds, 3600)
    def test_predictor_negative(self):
        with self.assertRaises(ValueError): TinyPredictor().predict_eta(-1)
    def test_predictor_is_not_trained(self):
        self.assertFalse(TinyPredictor().predict_eta(10)['trained_model'])

if __name__ == '__main__':
    unittest.main()
