from notifiers.base import BaseNotifier
from models import Alert


class ConsoleNotifier(BaseNotifier):
    """Prints alerts to stdout."""

    def notify(self, alert: Alert) -> None:
        print(alert)
