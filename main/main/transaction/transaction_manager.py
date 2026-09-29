


class TransactionManager:
    """
    Transaction command invoker.
    """

    def __init__(self, max_history: int = None):
        """
        Initialize TransactionManage with an optional history limit.
        """
        if max_history is not None:
            if not isinstance(max_history, int) or isinstance(max_history, bool) or max_history <= 0:
                raise ValueError("max_history must be a positive integer or None.")
        self._max_history = max_history
        self._undo_stack = []
        self._redo_stack = []
    
    def execute_command(self, command):
        """
        Execute a command, record it in history for undo, and invalidate redo history.
        """
        if command is None or not hasattr(command, "execute") or not callable(command.execute):
            raise TypeError("Command must implement a callable 'execute' method.")
        if not hasattr(command, "undo") or not callable(command.undo):
            raise TypeError("Command must implement a callable 'undo' method.")
        
        command.execute()

        self._undo_stack.append(command)
        self._redo_stack.clear()

        if self._max_history is not None and len(self._undo_stack) > self._max_history:
            self._undo_stack.pop(0)


    @property
    def can_undo(self) -> bool:
        """
        Return true if there are executed commands to undo.
        """
        return len(self._undo_stack) > 0
    
    @property
    def can_redo(self) -> bool:
        """
        Return true if there are undone commands to redo.
        """
        return len(self._redo_stack) > 0
