# balance.py

from transaction.transaction_category import TransactionCategory
import math

class Balance:
    """Singleton to track the balance."""

    _instance = None

    # Only internal factory methods possessing the sentinel can instantiate
    _sentinel = object()

    @classmethod
    def get_instance(cls):
        """Return the singleton instance, creating it if it does not yet exist."""
        if cls._instance is None:
            # Pass the class sentinel to authorize creation
            cls._instance = cls(cls._sentinel)
        return cls._instance

    def __init__(self, token=None):
        """Initialize the balance. Prevent direct instantiation. It requires an internal sentinel to allow creation."""
        if token is not self._sentinel:
            raise PermissionError("Direct instantiation forbidden. Call Balance.get_instance().")
        self._balance = 0.0
        self._observers = []

    # clear_observers defaults to False so it is backward-compatible with the existing zero-argument tests
    def reset(self, clear_observers: bool = False) -> None:
        """Reset the net balance to zero."""
        
        self._balance = 0.0

        # If true, detaches all registered observers
        if clear_observers:
            self._observers.clear()

    def add_income(self, amount: float) -> None:
        """Add income to the balance and notify all registered observers."""
        sanitized_amount = self._validate_amount(amount)
        self._balance += float(sanitized_amount)
        self._notify_observers()

    def add_expense(self, amount):
        """Subtract expense from the balance and notifies observers."""
        sanitized_amount = self._validate_amount(amount)
        self._balance -= sanitized_amount
        self._notify_observers()

    def apply_transaction(self, transaction) -> None:
        """
        Apply a Transaction object to update the balance.

        Args:
            transaction (Transaction): The transaction to apply.
        """
        if transaction is None or not hasattr(transaction, "category") or not hasattr(transaction, "amount"):
            raise TypeError("A valid Transaction object with amount and cateogry is required.")
        
        # When the category is INCOME, return a positive amount. When a cateogry is EXPENSE, return a negative amount.
        dispatch = {
            TransactionCategory.INCOME: lambda amt: amt,
            TransactionCategory.EXPENSE: lambda amt: -amt
        }

        if not isinstance(transaction.category, TransactionCategory) or transaction.category not in dispatch:
            raise ValueError(f"Invalid transaction category: {transaction.category}")

        sanitized_amount = self._validate_amount(transaction.amount)

        # An Income event has a positive rate of change. An Expense event has a negative rate of change. 
        delta = dispatch[transaction.category](sanitized_amount)
        self._balance += delta

        self._notify_observers(transaction)

    def get_balance(self) -> float:
        """Get the current net balance."""

        # Implemented strict typing 
        return float(self._balance)

    def summary(self) -> str:
        """Return a summary string of the net balance."""
        bal = float(self._balance)
        sign = "-" if bal < 0 else ""
        return f"Current Balance: {sign}${abs(bal):.2f}"


    def _notify_observers(self, transaction=None) -> None:
        """Notify all observers of a balance change, isolating errors per observer."""
        for observer in list(self._observers):
            try:
                observer.update(self._balance, transaction)
            except Exception as e:
                print(f"Error notifying observer {observer}: {e}")
    
  
    def register_observer(self, observer) -> None:
        """Register an observer ensuring structural compliance with the observer contract."""
        if observer is None or not hasattr(observer, "update") or not callable(getattr(observer, "update")):
            raise TypeError("Observer must implement a callable 'update' method.")
        if observer not in self._observers:
            self._observers.append(observer)

    # Validator helper 
    def _validate_amount(self, amount: float) -> float:
        """Validate that amount is a finite, non-negative float."""
        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            raise TypeError("Amount must be an int or float.")
        if amount < 0 or not math.isfinite(amount):
            raise ValueError("Amount must be a finite, non-negative number.")
        return float(amount)