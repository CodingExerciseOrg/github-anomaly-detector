from datetime import datetime, timezone
from typing import Optional

from detectors.base import BaseDetector
from config_loader import RepoLifecycleConfig
from models import Alert


class RepoLifecycleDetector(BaseDetector):
    """
    Flags a repository that is deleted within a configured number of seconds of being created.

    State is kept in memory (a dict of repo_full_name -> created_at). This is
    sufficient for a single-process deployment; swap for Redis or a DB
    if you need multi-process or persistent state.
    """

    github_event_types = ["repository"]

    def __init__(self, config: RepoLifecycleConfig) -> None:
        self._config = config
        # Maps repo full_name -> UTC creation datetime
        self._creation_times: dict[str, datetime] = {}

    def analyze(self, event_type: str, payload: dict) -> Optional[Alert]:
        action = payload.get("action")
        repo = payload.get("repository", {})
        repo_name = repo.get("full_name", "unknown")
        sender = payload.get("sender", {}).get("login", "unknown")

        if action == "created":
            self._creation_times[repo_name] = datetime.now(timezone.utc)
            return None

        if action == "deleted":
            created_at = self._creation_times.pop(repo_name, None)
            if created_at is None:
                # We didn't observe the creation; can't measure lifetime.
                return None

            deleted_at = datetime.now(timezone.utc)
            lifetime_seconds = (deleted_at - created_at).total_seconds()
            threshold = self._config.deletion_threshold_seconds

            if lifetime_seconds < threshold:
                return Alert(
                    title=f"Repository deleted within {threshold}s of creation",
                    event_type=event_type,
                    details={
                        "repository": repo_name,
                        "created_by": sender,
                        "lifetime_seconds": round(lifetime_seconds, 1),
                        "threshold_seconds": threshold,
                        "created_at_utc": created_at.strftime("%H:%M:%S"),
                        "deleted_at_utc": deleted_at.strftime("%H:%M:%S"),
                    },
                )
        return None
