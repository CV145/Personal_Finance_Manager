from main.main.transaction import transaction_manager
import unittest
from balance.balance import Balance
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory
from transaction.transaction_command import ApplyTransactionCommand
from transaction.transaction_manager import TransactionManager


class TestTransactionCommand(unittest.TestCase):

    def setUp(self):
        self.balance = Balance.get_instance()
        self.balance.reset(clear_observers=True)

    
    def test_apply_transaction_command_execute(self):
        """
        Verify that executing ApplyTransactionCommand applies the transaction to the receiver.
        """

        # Arrange
        initial_balance = self.balance.get_balance()
        amount = 100.0
        txn = Transaction(amount, TransactionCategory.INCOME)
        cmd = ApplyTransactionCommand(self.balance, txn)

        # Act
        cmd.execute()

        # Assert
        expected_balance = initial_balance + amount
        self.assertEqual(self.balance.get_balance(), expected_balance)


    def test_apply_transaction_command_undo(self):
        """
        Verify the calling undo() reverts the applied transaction on the balance receiver.
        """
        # Arrange
        initial_balance = self.balance.get_balance()
        txn = Transaction(100, TransactionCategory.INCOME)
        cmd = ApplyTransactionCommand(self.balance, txn)
        cmd.execute()

        # Act
        cmd.undo()

        # Assert
        self.assertEqual(self.balance.get_balance(), initial_balance)

    def test_transaction_manager_execute(self):
        """Verify that TransactionManager executes the command and updates undo availability."""
        # Arrange
        manager = TransactionManager()
        initial_balance = self.balance.get_balance()
        amount = 100.0
        txn = Transaction(amount, TransactionCategory.INCOME)
        cmd = ApplyTransactionCommand(self.balance, txn)

        # Act
        manager.execute_command(cmd)

        # Assert
        self.assertEqual(self.balance.get_balance(), initial_balance + amount)
        self.assertTrue(manager.can_undo)
        self.assertFalse(manager.can_redo)
    

    def test_transaction_manager_undo(self):
        """
        Verify that TransactionManager reverts the last command executed and updates redo.
        """
        # Arrange
        manager = TransactionManager()
        initial_balance = self.balance.get_balance()
        cmd = ApplyTransactionCommand(self.balance, Transaction(100, TransactionCategory.INCOME))
        manager.execute_command(cmd)

        # Act
        undone_command = manager.undo()

        # Assert
        self.assertEqual(self.balance.get_balance(), initial_balance)
        self.assertFalse(manager.can_undo)
        self.assertTrue(manager.can_redo)
        self.assertIs(undone_command, cmd)

    def tearDown(self):
        self.balance.reset(clear_observers=True)