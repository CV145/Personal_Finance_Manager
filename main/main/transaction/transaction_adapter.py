# transaction_adapter.py

from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory

class TransactionAdapter:
    def __init__(self, external_transaction):
        self.external_transaction = external_transaction

    def to_transaction(self):
        """Convert an external transaction to a standard Transaction."""
        if self.external_transaction is None:
            raise TypeError("External transaction cannot be None.")
        if not hasattr(self.external_transaction, "amount"):
            raise AttributeError("External transaction must have an 'amount' attribute.")
        
        category = self._map_category(self.external_transaction)
        return Transaction(self.external_transaction.amount, category)

    @staticmethod
    def _map_category(external_transaction):
        mapping = {
            "income": TransactionCategory.INCOME,
            "expense": TransactionCategory.EXPENSE
        }
        raw_typ = getattr(external_transaction, "typ", "income")
        normalized_typ = str(raw_typ).strip().lower()
        
        if normalized_typ not in mapping:
            raise ValueError(f"Unsupported external transaction type: {raw_typ}")
        return mapping[normalized_typ]

