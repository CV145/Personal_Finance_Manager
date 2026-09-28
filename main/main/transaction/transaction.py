# transaction.py

import math
from transaction.transaction_category import TransactionCategory

class Transaction:
    """Represents a financial transaction with an amount and category."""

    def __init__(self, amount, category: TransactionCategory):
        self.amount = self._validate_amount(amount)
        self.category = category


    def __str__(self):
        # Introspection by retrieving the class name Transaction
        return f"{self.__class__.__name__}(${self.amount}, category='{self.category}')"

    def __eq__(self, other):

        # Short-circuit for O(1) performance
        if self is other:
            return True

        # For incompatible types
        if not isinstance(other, Transaction):
            return NotImplemented

        return (self.amount, self.category) == (other.amount, other.category)
    
    @staticmethod
    def _validate_amount(amount):
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise TypeError("Amount must be an int or float.")
        if not math.isfinite(amount) or amount < 0:
            raise ValueError("Amount must be a finite, non-negative number.")
        return amount

