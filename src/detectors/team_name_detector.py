from typing import Optional

from detectors.base import BaseDetector
from config_loader import TeamNameConfig
from models import Alert


class TeamNameDetector(BaseDetector):
    """
    Flags creation of any team whose name starts with a configured suspicious prefix.

    Supports multiple prefixes, e.g.:
        ["hacker", "exploit", "rootkit"]
    """

    github_event_types = ["team"]

    def __init__(self, config: TeamNameConfig) -> None:
        self._config = config

    def analyze(self, event_type: str, payload: dict) -> Optional[Alert]:
        action = payload.get("action")
        if action != "created":
            return None

        team = payload.get("team", {})
        team_name = team.get("name", "")

        matched_prefix = self._find_matching_prefix(team_name)
        if matched_prefix is None:
            return None

        org = payload.get("organization", {}).get("login", "unknown")
        creator = payload.get("sender", {}).get("login", "unknown")
        return Alert(
            title=f'Team created with suspicious prefix "{matched_prefix}"',
            event_type=event_type,
            details={
                "team_name": team_name,
                "matched_prefix": matched_prefix,
                "team_id": team.get("id"),
                "organization": org,
                "created_by": creator,
            },
        )

    def _find_matching_prefix(self, team_name: str) -> Optional[str]:
        """Return the first prefix that matches team_name, or None."""
        name_lower = team_name.lower()
        for prefix in self._config.suspicious_prefixes:
            if name_lower.startswith(prefix):
                return prefix
        return None
