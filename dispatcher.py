from detectors.base import BaseDetector
from notifiers.base import BaseNotifier


class EventDispatcher:
    """
    Routes incoming GitHub webhook events to registered detectors,
    then passes any resulting alerts to all registered notifiers.

    Adding a new detector:
        dispatcher.register_detector(MyNewDetector())

    Adding a new notifier:
        dispatcher.register_notifier(SlackNotifier())
    """

    def __init__(self) -> None:
        # event_type -> list of detectors interested in that event
        self._detectors: dict[str, list[BaseDetector]] = {}
        self._notifiers: list[BaseNotifier] = []

    def register_detector(self, detector: BaseDetector) -> None:
        for event_type in detector.github_event_types:
            self._detectors.setdefault(event_type, []).append(detector)

    def register_notifier(self, notifier: BaseNotifier) -> None:
        self._notifiers.append(notifier)

    def dispatch(self, event_type: str, payload: dict) -> None:
        """
        Called once per incoming webhook. Runs all matching detectors
        and notifies on any alerts produced.
        """
        print("\n********\nStart detectors\n")
        for detector in self._detectors.get(event_type, []):
            alert = detector.analyze(event_type, payload)
            if alert:
                for notifier in self._notifiers:
                    notifier.notify(alert)
