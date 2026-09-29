import streamlit as st
from balance.balance import Balance
from balance.balance_observer import PrintObserver, LowBalanceAlertObserver
from transaction.transaction import Transaction
from transaction.transaction_category import TransactionCategory
from transaction.transaction_adapter import TransactionAdapter
from transaction.external_income_transaction import ExternalFreelanceIncome
from transaction.transaction_command import ApplyTransactionCommand
from transaction.transaction_manager import TransactionManager


def init_session_state():
    """Initialize singleton balance, manager, and UI stores in session."""
    balance = Balance.get_instance()

    if "manager" not in st.session_state:
        st.session_state.manager = TransactionManager()

    if "logs" not in st.session_state:
        st.session_state.logs = []

    if "alerts" not in st.session_state:
        st.session_state.alerts = []

    if "observers_registered" not in st.session_state:
        balance.reset(clear_observers=True)
        balance.register_observer(PrintObserver())
        st.session_state.observers_registered = True

    return balance, st.session_state.manager


def render_header_and_balance(balance, manager, threshold: float = 100.0):
    """Render dashboard header, balance KPI card, and threshold alert."""
    st.title("Personal Finance Manager")

    bal = balance.get_balance()

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        delta_color = "normal" if bal >= threshold else "inverse"
        delta_label = (
            "Healthy" if bal >= threshold else "Low Balance Warning"
        )
        st.metric(
            label="Current Balance",
            value=f"${bal:,.2f}",
            delta=delta_label,
            delta_color=delta_color
        )
    with col2:
        undo_status = "Available" if manager.can_undo else "Empty"
        st.metric(label="Undo State", value=undo_status)
    with col3:
        redo_status = "Available" if manager.can_redo else "Empty"
        st.metric(label="Redo State", value=redo_status)

    if bal < threshold:
        alert_msg = (
            rf"**Low Balance Alert Observer**: Current balance (\${bal:.2f}) "
            rf"is below the \${threshold:.2f} threshold!"
        )
        st.warning(alert_msg)


def render_standard_transaction_form(balance, manager):
    """Render standard transaction creation form and dispatch command."""
    st.subheader("Add Standard Transaction")
    with st.form("standard_tx_form", clear_on_submit=True):
        amount = st.number_input(
            "Amount ($)", min_value=0.01, value=50.0, step=10.0
        )
        category = st.selectbox(
            "Category",
            [TransactionCategory.INCOME, TransactionCategory.EXPENSE],
            format_func=lambda c: c.value
        )
        submitted = st.form_submit_button("Apply Transaction")
        if submitted:
            try:
                txn = Transaction(amount, category)
                cmd = ApplyTransactionCommand(balance, txn)
                manager.execute_command(cmd)
                log_msg = f"Applied {category.value}: ${amount:.2f}"
                st.session_state.logs.append(log_msg)
                st.toast(log_msg)
                st.rerun()
            except Exception as e:
                st.error(f"Transaction failed: {e}")


def render_freelance_adapter_form(balance, manager):
    """Render external invoice form, adapt, and dispatch via invoker."""
    st.subheader("External Freelance Income")
    with st.form("freelance_adapter_form", clear_on_submit=True):
        invoice_id = st.text_input("Invoice ID", value="INV-98765")
        description = st.text_input(
            "Project Description", value="Mobile App Development"
        )
        amount = st.number_input(
            "Invoice Amount ($)", min_value=0.01, value=1200.0, step=50.0
        )
        submitted = st.form_submit_button("Import and Adapt Invoice")
        if submitted:
            try:
                external_payload = ExternalFreelanceIncome(
                    amount, invoice_id, description
                )
                adapter = TransactionAdapter(external_payload)
                adapted_txn = adapter.to_transaction()

                cmd = ApplyTransactionCommand(balance, adapted_txn)
                manager.execute_command(cmd)

                log_entry = (
                    f"Adapted Freelance [{invoice_id}]: +${amount:.2f}"
                )
                st.session_state.logs.append(log_entry)
                st.toast(log_entry)
                st.rerun()
            except Exception as e:
                st.error(f"Adapter processing failed: {e}")


def render_command_controls(balance, manager):
    """Render undo, redo, and reset controls enforcing state invariants."""
    st.subheader("Transaction History Controls")
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        undo_clicked = st.button(
            "Undo Last Transaction",
            disabled=not manager.can_undo,
            use_container_width=True
        )
        if undo_clicked:
            try:
                undone_cmd = manager.undo()
                cat_val = getattr(
                    undone_cmd.transaction.category,
                    "value",
                    str(undone_cmd.transaction.category)
                )
                amt = undone_cmd.transaction.amount
                msg = f"Reverted: {cat_val} (${amt:.2f})"
                st.session_state.logs.append(msg)
                st.toast(msg)
                st.rerun()
            except Exception as e:
                st.error(f"Undo operation failed: {e}")

    with col2:
        redo_clicked = st.button(
            "Redo Transaction",
            disabled=not manager.can_redo,
            use_container_width=True
        )
        if redo_clicked:
            try:
                redone_cmd = manager.redo()
                cat_val = getattr(
                    redone_cmd.transaction.category,
                    "value",
                    str(redone_cmd.transaction.category)
                )
                amt = redone_cmd.transaction.amount
                msg = f"Re-applied: {cat_val} (${amt:.2f})"
                st.session_state.logs.append(msg)
                st.toast(msg)
                st.rerun()
            except Exception as e:
                st.error(f"Redo operation failed: {e}")

    with col3:
        if st.button("Reset Session Ledger", use_container_width=True):
            balance.reset(clear_observers=True)
            st.session_state.manager = TransactionManager()
            st.session_state.logs.clear()
            st.session_state.observers_registered = False
            st.toast("Ledger reset to initial state.")
            st.rerun()


def render_audit_log():
    """Render the chronological activity audit log feed."""
    st.subheader("Activity Audit Log")
    if not st.session_state.logs:
        st.info("No activity recorded yet in this session.")
        return

    with st.expander("View Full Event Log", expanded=True):
        for entry in reversed(st.session_state.logs):
            st.text(entry)


def main():
    """Main application orchestrator uniting all four patterns."""
    st.set_page_config(
        page_title="Personal Finance Manager",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    balance, manager = init_session_state()

    render_header_and_balance(balance, manager)
    st.divider()

    tab_standard, tab_adapter = st.tabs([
        "Standard Transactions",
        "External Freelance Invoices"
    ])

    with tab_standard:
        render_standard_transaction_form(balance, manager)

    with tab_adapter:
        render_freelance_adapter_form(balance, manager)

    st.divider()
    render_command_controls(balance, manager)

    st.divider()
    render_audit_log()


if __name__ == "__main__":
    main()
