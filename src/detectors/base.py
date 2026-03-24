from abc import ABC, abstractmethod
from typing import Optional
from models import Alert


class BaseDetector(ABC):
    """
    Abstract base class for all anomaly detectors.

    To add a new detector:
      1. Subclass BaseDetector
      2. Declare which github_event_types it handles
      3. Implement the analyze() method
      4. Register it in dispatcher.py
    """

    # Subclasses declare which GitHub event types they care about.
    # e.g. ["push"], ["team"], ["repository"]
    github_event_types: list[str] = []

    @abstractmethod
    def analyze(self, event_type: str, payload: dict) -> Optional[Alert]:
        """
        Analyze a webhook payload and return an Alert if suspicious, else None.

        Args:
            event_type: The GitHub webhook event name (X-GitHub-Event header).
            payload:    The parsed JSON body of the webhook.

        Returns:
            An Alert instance if suspicious behavior is detected, otherwise None.
        """
