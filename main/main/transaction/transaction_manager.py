class TransactionManager:
    """Transaction command invoker managing undo and redo history."""

    def __init__(self, max_history: int = None):
        """Initialize TransactionManager with an optional history limit."""
        if max_history is not None:
            if (
                not isinstance(max_history, int)
                or isinstance(max_history, bool)
                or max_history <= 0
            ):
                raise ValueError(
                    "max_history must be a positive integer or None."
                )
        self._max_history = max_history
        self._undo_stack = []
        self._redo_stack = []

    def _prune_history(self):
        """Prune undo stack to enforce max_history limit."""
        if (
            self._max_history is not None
            and len(self._undo_stack) > self._max_history
        ):
            self._undo_stack.pop(0)

    def execute_command(self, command):
        """Execute command, record in history, and clear redo stack."""
        if (
            command is None
            or not hasattr(command, "execute")
            or not callable(command.execute)
        ):
            raise TypeError(
                "Command must implement a callable 'execute' method."
            )
        if not hasattr(command, "undo") or not callable(command.undo):
            raise TypeError(
                "Command must implement a callable 'undo' method."
            )

        command.execute()
        self._undo_stack.append(command)
        self._redo_stack.clear()
        self._prune_history()

    def undo(self):
        """Revert the most recent executed command to the redo stack."""
        if not self.can_undo:
            raise RuntimeError(
                "Cannot undo: no executed commands available in history."
            )
        cmd = self._undo_stack.pop()
        cmd.undo()
        self._redo_stack.append(cmd)
        return cmd

    def redo(self):
        """Re-execute the most recent undone command."""
        if not self.can_redo:
            raise RuntimeError(
                "Cannot redo: no undone commands available in history."
            )

        cmd = self._redo_stack.pop()
        cmd.execute()
        self._undo_stack.append(cmd)
        self._prune_history()
        return cmd

    @property
    def can_undo(self) -> bool:
        """Return true if there are executed commands to undo."""
        return len(self._undo_stack) > 0

    @property
    def can_redo(self) -> bool:
        """Return true if there are undone commands to redo."""
        return len(self._redo_stack) > 0
