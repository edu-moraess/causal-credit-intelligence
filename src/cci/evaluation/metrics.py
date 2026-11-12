"""Metric registry placeholder; metrics require validated predictions and labels."""
class MetricsRegistry:
    def __init__(self):
        self._metrics = {}

    def register(self, name, metric):
        if not name or not callable(metric):
            raise ValueError("A non-empty name and callable metric are required.")
        self._metrics[name] = metric

    def names(self):
        return tuple(sorted(self._metrics))
