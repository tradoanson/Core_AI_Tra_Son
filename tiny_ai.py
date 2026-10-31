"""Dependency-free tiny statistical predictor, not a pretrained AI model."""
class TinyPredictor:
    def predict_eta(self, base_seconds: float, adaptive_bias_seconds: float = 0.0) -> dict:
        if not 0 <= base_seconds <= 86400 * 7:
            raise ValueError("ETA outside accepted range")
        return {"eta_seconds": max(0, base_seconds + adaptive_bias_seconds), "method": "baseline_plus_adaptive", "trained_model": False}
