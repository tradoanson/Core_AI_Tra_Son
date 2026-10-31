"""Bounded online ETA correction, held in memory only."""
class EtaAdaptive:
    def __init__(self, alpha: float = 0.2):
        if not 0 < alpha <= 1:
            raise ValueError("alpha must be in (0, 1]")
        self.alpha = alpha
        self.bias_seconds = 0.0
        self.samples = 0

    def observe(self, predicted_seconds: float, actual_seconds: float, verified: bool = False):
        if not verified:
            return False
        if not (0 <= predicted_seconds <= 86400 * 7 and 0 <= actual_seconds <= 86400 * 7):
            raise ValueError("ETA outside accepted range")
        error = actual_seconds - predicted_seconds
        self.bias_seconds = max(-3600, min(3600, self.alpha * error + (1 - self.alpha) * self.bias_seconds))
        self.samples += 1
        return True

    def correct(self, predicted_seconds: float) -> float:
        if predicted_seconds < 0:
            raise ValueError("ETA must be nonnegative")
        return max(0.0, predicted_seconds + self.bias_seconds)
