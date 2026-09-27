# balance_observer.py
import math

class IBalanceObserver:
    def update(self, balance, transaction):
        """Handle balance updates."""
        raise NotImplementedError("Subclasses must implement update method.")


class PrintObserver(IBalanceObserver):
    def update(self, balance, transaction):
        """Print balance update message."""
        pass


class LowBalanceAlertObserver(IBalanceObserver):
    def __init__(self, threshold: float):
        """
        Initialize LowBalanceAlertObserver with validated threshold and state flag.
        """
        if not isinstance(threshold, (int, float)) or isinstance(threshold, bool):
            raise TypeError("Threshold must be an int or float.")
        if threshold < 0 or not math.isfinite(threshold):
            raise ValueError("Threshold must be a finite, non-negative number.")
        
        self.threshold: float = float(threshold)
        self.alert_triggered: bool = False

    def update(self, balance, transaction):
        """Alert if balance drops below threshold."""
        pass
