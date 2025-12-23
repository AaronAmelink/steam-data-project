from abc import ABC, abstractmethod

from pipelines.utils.status_codes import StatusCode


class AbstractTask(ABC):
    """
    Base class for all tasks.
    Subclasses must implement the `execute()` method which returns a StatusCode.
    """

    @abstractmethod
    def execute(self) -> StatusCode:
        """Execute the task and return a StatusCode result."""
        pass