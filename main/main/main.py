"""This module serves as the entry point for the program."""
from balance.balance import Balance
from balance.balance_observer import LowBalanceAlertObserver
from balance.balance_observer import PrintObserver
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory
from transaction.transaction_adapter import TransactionAdapter
from transaction.external_income_transaction import ExternalFreelanceIncome
from transaction.transaction_command import ApplyTransactionCommand
from transaction.transaction_manager import TransactionManager


def main():
    # Create balance and add observers
    print("=== Starting Personal Finance Manager ===")
    balance = Balance.get_instance()

    balance.reset(clear_observers=True)

    print_observer = PrintObserver()
    alert_observer = LowBalanceAlertObserver(threshold=100.0)

    balance.register_observer(print_observer)
    balance.register_observer(alert_observer)

    # Create standard transactions
    transactions = [
        Transaction(100, TransactionCategory.INCOME),
        Transaction(50, TransactionCategory.EXPENSE),
        Transaction(200, TransactionCategory.INCOME),
        Transaction(75, TransactionCategory.EXPENSE),
    ]

    # Create an external income transaction (via Adapter pattern)
    freelance_income = ExternalFreelanceIncome(
        1200, "INV-98765", "Mobile App Project"
    )
    adapter = TransactionAdapter(freelance_income)
    adapted_transaction = adapter.to_transaction()

    all_transactions = transactions + [adapted_transaction]

    # Command Pattern
    print("\n--- Executing Transactions via Command Invoker ---")
    manager = TransactionManager()
    for txn in all_transactions:
        cmd = ApplyTransactionCommand(balance, txn)
        manager.execute_command(cmd)
    print(f"\nFinal {balance.summary()}")

    # Demonstrating reversibility
    print("\n--- Demonstrating Undo Capability ---")
    manager.undo()
    print(f"Post-Undo {balance.summary()}")
    print("\n--- Demonstrating Redo Capability ---")
    manager.redo()
    print(f"Post-Redo {balance.summary()}")


if __name__ == "__main__":
    main()
