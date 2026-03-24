from abc import ABC, abstractmethod
from models import Alert


class BaseNotifier(ABC):
    """
    Abstract base class for all notifiers.

    To add a new notification channel (e.g. email, Slack):
      1. Subclass BaseNotifier
      2. Implement notify()
      3. Add an instance to the notifiers list in main.py
    """

    @abstractmethod
    def notify(self, alert: Alert) -> None:
        """
        Deliver an alert to the user.

        Args:
            alert: The Alert to deliver.
        """
