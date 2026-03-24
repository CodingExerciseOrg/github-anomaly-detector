from datetime import datetime, timezone
from typing import Optional
from zoneinfo import ZoneInfo

from detectors.base import BaseDetector
from config_loader import PushTimeConfig
from models import Alert


class PushTimeDetector(BaseDetector):
    """
    Flags push events that occur within any configured suspicious time window.

    Supports multiple windows, e.g.:
        [{"start": "14:00", "end": "16:00"}, {"start": "02:00", "end": "04:00"}]
    """

    github_event_types = ["push"]

    def __init__(self, config: PushTimeConfig) -> None:
        self._config = config

    def analyze(self, event_type: str, payload: dict) -> Optional[Alert]:
        timestamp_str = payload.get("head_commit", {}).get("timestamp")

        print("PushTimeDetector analyzing event with timestamp:", timestamp_str)

        if timestamp_str:
            push_time = datetime.fromisoformat(timestamp_str).astimezone(ZoneInfo("America/New_York"))

        else:
            push_time = datetime.now(ZoneInfo("America/New_York"))


        matched_window = self._find_matching_window(push_time)
        print("Matched window:", matched_window)

        if matched_window is None:
            return None

        pusher = payload.get("pusher", {}).get("name", "unknown")
        ref = payload.get("ref", "unknown")
        repo = payload.get("repository", {}).get("full_name", "unknown")
        commits = payload.get("commits", [])

        return Alert(
            title=f"Code pushed during restricted window ({matched_window})",
            event_type=event_type,
            details={
                "pusher": pusher,
                "repository": repo,
                "branch": ref,
                "push_time_ET": push_time.strftime("%H:%M:%S"),
                "matched_window": str(matched_window),
                "commit_count": len(commits),
            },
        )

    def _find_matching_window(self, push_time: datetime):
        """Return the first TimeWindow that contains push_time, or None."""
        push_clock = push_time.time().replace(second=0, microsecond=0)
        for window in self._config.suspicious_windows:
            if window.start <= push_clock < window.end:
                return window
        return None
