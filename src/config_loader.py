"""
Loads and validates detector configuration from config.json.

The config file path can be overridden with the CONFIG_PATH environment variable.
"""

import json
import logging
import os
from dataclasses import dataclass, field
from datetime import time

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "../config/config.json")


@dataclass
class TimeWindow:
    start: time
    end: time

    def __str__(self) -> str:
        return f"{self.start.strftime('%H:%M')}–{self.end.strftime('%H:%M')}"


@dataclass
class PushTimeConfig:
    enabled: bool = True
    suspicious_windows: list[TimeWindow] = field(default_factory=list)


@dataclass
class TeamNameConfig:
    enabled: bool = True
    suspicious_prefixes: list[str] = field(default_factory=list)


@dataclass
class RepoLifecycleConfig:
    enabled: bool = True
    deletion_threshold_seconds: int = 600


@dataclass
class EmailConfig:
    enabled: bool = True
    sender: str = ""
    destination: str = ""
    smtp_host: str = "smtp.mail.yahoo.com"
    smtp_port: int = 587


@dataclass
class NotifierConfig:
    email: EmailConfig


@dataclass
class DetectorConfig:
    push_time: PushTimeConfig
    team_name: TeamNameConfig
    repo_lifecycle: RepoLifecycleConfig
    notifiers: NotifierConfig


def _parse_time(value: str) -> time:
    """Parse a 'HH:MM' string into a datetime.time object."""
    try:
        hours, minutes = value.split(":")
        return time(int(hours), int(minutes))
    except (ValueError, AttributeError) as e:
        raise ValueError(f"Invalid time format '{value}'. Expected 'HH:MM'.") from e


def load_config(path: str | None = None) -> DetectorConfig:
    """
    Load detector configuration from a JSON file.

    Args:
        path: Path to the config file. Falls back to CONFIG_PATH env var,
              then to config.json in the project root.

    Returns:
        A fully populated DetectorConfig instance.
    """
    config_path = path or os.getenv("CONFIG_PATH", DEFAULT_CONFIG_PATH)

    with open(config_path) as f:
        raw = json.load(f)

    detectors = raw.get("detectors", {})

    # --- push_time ---
    pt = detectors.get("push_time", {})
    windows = [
        TimeWindow(
            start=_parse_time(w["start"]),
            end=_parse_time(w["end"]),
        )
        for w in pt.get("suspicious_windows", [])
    ]
    push_time_cfg = PushTimeConfig(
        enabled=pt.get("enabled", True),
        suspicious_windows=windows,
    )

    # --- team_name ---
    tn = detectors.get("team_name", {})
    team_name_cfg = TeamNameConfig(
        enabled=tn.get("enabled", True),
        suspicious_prefixes=[p.lower() for p in tn.get("suspicious_prefixes", [])],
    )

    # --- repo_lifecycle ---
    rl = detectors.get("repo_lifecycle", {})
    repo_lifecycle_cfg = RepoLifecycleConfig(
        enabled=rl.get("enabled", True),
        deletion_threshold_seconds=rl.get("deletion_threshold_seconds", 600),
    )

    # --- email notifier ---
    em = raw.get("notifiers", {}).get("email", {})
    email_cfg = EmailConfig(
        enabled=em.get("enabled", True),
        sender=em.get("sender", ""),
        destination=em.get("destination", ""),
        smtp_host=em.get("smtp_host", "smtp.mail.yahoo.com"),
        smtp_port=em.get("smtp_port", 587),
    )

    config = DetectorConfig(
        push_time=push_time_cfg,
        team_name=team_name_cfg,
        repo_lifecycle=repo_lifecycle_cfg,
        notifiers=NotifierConfig(email=email_cfg),
    )

    logger.info("Loaded config from %s", config_path)
    _log_config_summary(config)
    return config


def _log_config_summary(config: DetectorConfig) -> None:
    pt = config.push_time
    if pt.enabled:
        windows_str = ", ".join(str(w) for w in pt.suspicious_windows)
        logger.info("PushTimeDetector     : windows=[%s]", windows_str)
    else:
        logger.info("PushTimeDetector     : disabled")

    tn = config.team_name
    if tn.enabled:
        logger.info("TeamNameDetector     : prefixes=%s", tn.suspicious_prefixes)
    else:
        logger.info("TeamNameDetector     : disabled")

    rl = config.repo_lifecycle
    if rl.enabled:
        logger.info("RepoLifecycleDetector: threshold=%ds", rl.deletion_threshold_seconds)
    else:
        logger.info("RepoLifecycleDetector: disabled")

    em = config.notifiers.email
    if em.enabled:
        logger.info("EmailNotifier        : %s -> %s", em.sender, em.destination)
    else:
        logger.info("EmailNotifier        : disabled")
