# transaction.py

from transaction.transaction_category import TransactionCategory

class Transaction:
    """Represents a financial transaction with an amount and category."""

    def __init__(self, amount, category: TransactionCategory):
        self.amount = amount
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
