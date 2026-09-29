


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
