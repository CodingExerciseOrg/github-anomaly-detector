import logging
from datetime import datetime
from typing import Optional
from zoneinfo import ZoneInfo

from detectors.base import BaseDetector
from config_loader import RepoLifecycleConfig
from models import Alert

logger = logging.getLogger(__name__)

ET = ZoneInfo("America/New_York")


class RepoLifecycleDetector(BaseDetector):
    """
    Flags a repository deleted within a configured number of seconds of creation.

    Uses timestamps from the GitHub payload itself (repository.created_at)
    rather than local wall-clock time, eliminating sensitivity to network
    or smee delivery delays.
    """

    github_event_types = ["repository"]

    def __init__(self, config: RepoLifecycleConfig) -> None:
        self._config = config
        self._creation_times: dict[str, str] = {}

    def analyze(self, event_type: str, payload: dict) -> Optional[Alert]:
        action = payload.get("action")
        repo = payload.get("repository", {})
        repo_name = repo.get("full_name", "unknown")
        sender = payload.get("sender", {}).get("login", "unknown")

        if action == "created":
            # created_at is an ISO 8601 string e.g. "2026-03-24T10:00:00Z"
            created_at = repo.get("created_at")
            if created_at is not None:
                self._creation_times[repo_name] = created_at
                logger.debug("Recorded creation of %s at %s", repo_name, created_at)
            return None

        if action == "deleted":
            created_at_str = self._creation_times.pop(repo_name, None)

            if created_at_str is None:
                logger.warning("Delete event for %s but no creation time on record.", repo_name)
                return None

            # Parse ISO string — replace Z suffix for Python < 3.11 compatibility
            created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00")).astimezone(ET)
            deleted_at = datetime.now(ET)
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
                        "created_at_et": created_at.strftime("%Y-%m-%d %H:%M:%S %Z"),
                        "deleted_at_et": deleted_at.strftime("%Y-%m-%d %H:%M:%S %Z"),
                    },
                )
        return None