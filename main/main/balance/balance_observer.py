# balance_observer.py
import math


def validate_number(number) -> None:
        if not isinstance(number, (int, float)) or isinstance(number, bool):
            raise TypeError("Number must be a numeric int or float.")

class IBalanceObserver:
    def update(self, balance, transaction):
        """Handle balance updates."""
        raise NotImplementedError("Subclasses must implement update method.")


class PrintObserver(IBalanceObserver):
    def update(self, balance, transaction):
        """Print balance update message."""
        validate_number(balance)

        sign = "-" if balance < 0 else ""

        formatted_balance = f"{sign}${abs(balance):.2f}"

        if transaction is not None and hasattr(transaction, "amount") and hasattr(transaction, "category"):
            cat_name = getattr(transaction.category, "name", str(transaction.category))
            amt = getattr(transaction, "amount", 0.0)
            print(f"[Balance Update] Applied {cat_name}: ${amt:.2f} | Current Balance: {formatted_balance}")
        else:
            print(f"[Balance Update] Current Balance: {formatted_balance}")


class LowBalanceAlertObserver(IBalanceObserver):
    def __init__(self, threshold: float):
        """
        Initialize LowBalanceAlertObserver with validated threshold and state flag.
        """
        validate_number(threshold)
        if threshold < 0 or not math.isfinite(threshold):
            raise ValueError("Threshold must be a finite, non-negative number.")
        
        self.threshold: float = float(threshold)
        self.alert_triggered: bool = False

    def update(self, balance, transaction=None) -> None:
        """Alert if balance drops below threshold."""
        
        validate_number(balance)
        
        is_below_threshold = float(balance) < self.threshold

        # Trigger alert on state transition: False -> True
        if is_below_threshold and not self.alert_triggered:
            print(f"ALERT: Balance dropped below ${self.threshold:.2f}! Current balance: ${balance:.2f}")
        
        self.alert_triggered = is_below_threshold
