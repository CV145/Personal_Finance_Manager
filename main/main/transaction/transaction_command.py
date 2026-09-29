

from transaction.transaction_category import TransactionCategory
class ApplyTransactionCommand:
    """
    Command that applies a financial transaction as a balance receiver.
    """

    @staticmethod
    def _validate_balance(balance):
        if balance is None or not hasattr(balance, "apply_transaction"):
            raise TypeError("Balance receiver must implement 'apply_transaction'.")
        return balance

    @staticmethod
    def _validate_transaction(transaction):
        if transaction is None or not hasattr(transaction, "amount") or not hasattr(transaction, "category"):
            raise TypeError("Transaction payload must have 'amount' and 'category'.")
        return transaction


    def __init__(self, balance, transaction):
        self.balance = self._validate_balance(balance)
        self.transaction = self._validate_transaction(transaction)
        self._executed = False

    
    def execute(self):
        """Execute the command by applying the transaction to the balance receiver."""
        if self._executed:
            raise RuntimeError("Cannot execute command: transaction has already been applied.")
        
        self.balance.apply_transaction(self.transaction)
        self._executed = True
    
    def undo(self):
        """Revert the recent applied transaction on the balance receiver."""
        if not self._executed:
            raise RuntimeError("Cannot undo command: transaction has not been applied.")
        
        # Function mapping instead of if/else statements
        inverse_dispatch = {
            TransactionCategory.INCOME: self.balance.add_expense,
            TransactionCategory.EXPENSE: self.balance.add_income
        }

        if self.transaction.category not in inverse_dispatch:
            raise ValueError(f"Cannot undo transaction with category: {self.transaction.category}")
        
        inverse_dispatch[self.transaction.category](self.transaction.amount)
        self._executed = False
