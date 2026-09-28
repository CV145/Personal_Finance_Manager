import unittest
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory
from balance.balance import Balance
from balance.balance_observer import LowBalanceAlertObserver, PrintObserver
from unittest.mock import patch
import io

class TestLowBalanceAlertObserver(unittest.TestCase):

    # This is called before every test
    def setUp(self):
        self.balance = Balance.get_instance()
        self.balance.reset()

    def test_alert_triggers_on_low_balance(self):
        observer = LowBalanceAlertObserver(threshold=50)
        self.balance.register_observer(observer)

        self.balance.apply_transaction(Transaction(100, TransactionCategory.INCOME))
        self.assertFalse(observer.alert_triggered)

        self.balance.apply_transaction(Transaction(60, TransactionCategory.EXPENSE))
        self.assertTrue(observer.alert_triggered)

        self.balance.apply_transaction(Transaction(100, TransactionCategory.INCOME))
        self.assertFalse(observer.alert_triggered)

        self.balance.apply_transaction(Transaction(60, TransactionCategory.EXPENSE))
        self.assertFalse(observer.alert_triggered)
        
        self.balance.apply_transaction(Transaction(60, TransactionCategory.EXPENSE))
        self.assertTrue(observer.alert_triggered)
    
    def test_print_observer_income(self):
        """
        Test that PrintObserver correctly reports an income transaction and updated balance.
        """

        # Arrange
        self.balance.reset(clear_observers=True)
        observer = PrintObserver()

        self.balance.register_observer(observer)
        transaction = Transaction(100, TransactionCategory.INCOME)

        # Act
        # We usually inspect the return values of pure functions. However a function like update() does not return a value and instead produces an external side effect by writing text to the terminal. The patch function helps intercept calls to print() and write directly to mock_stdout in memory.
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            self.balance.apply_transaction(transaction)
            captured_output = mock_stdout.getvalue()
        
        # Assert
        self.assertIn("INCOME", captured_output)
        self.assertIn("$100.00", captured_output)
        self.assertIn("Current Balance: $100.00", captured_output)
    
    def test_print_observer_expense_negative_balance(self):
        """
        Test that PrintObserver correctly reports an expense transaction and negative balance format.
        """
        # Arrange
        self.balance.reset(clear_observers=True)
        observer = PrintObserver()

        self.balance.register_observer(observer)
        expense_tx = Transaction(50, TransactionCategory.EXPENSE)

        # Act
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            self.balance.apply_transaction(expense_tx)
            captured_output = mock_stdout.getvalue()
        
        # Assert
        self.assertIn("EXPENSE", captured_output)
        self.assertIn("$50.00", captured_output)
        self.assertIn("Current Balance: -$50.00", captured_output)
    
    # This is called after every test
    def tearDown(self):
        """
        Tear down test fixtures and reset the Singleton balance by detaching all observers.
        """
        self.balance.reset(clear_observers=True)

if __name__ == "__main__":
    unittest.main()


