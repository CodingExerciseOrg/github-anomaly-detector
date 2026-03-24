"""
Entry point for the GitHub anomaly detection app.

Run with:
    python main.py

Environment variables (all optional):
    PORT            Port to listen on (default: 5125)
    WEBHOOK_SECRET  GitHub webhook secret for payload verification
    CONFIG_PATH     Path to config.json (default: ./config.json)
    LOG_LEVEL       Logging level (default: INFO)
"""

import logging
import os

from config_loader import load_config
from dispatcher import EventDispatcher
from webhook_server import create_app

# --- Detectors ---
from detectors.push_time_detector import PushTimeDetector
from detectors.team_name_detector import TeamNameDetector
from detectors.repo_lifecycle_detector import RepoLifecycleDetector

# --- Notifiers ---
from notifiers.console_notifier import ConsoleNotifier
from notifiers.email_notifier import EmailNotifier


def build_dispatcher() -> EventDispatcher:
    config = load_config()
    dispatcher = EventDispatcher()

    # Register detectors — add new ones here as the system grows.
    # Each detector receives only the slice of config it needs.
    # Detectors with enabled=false in config.json are skipped entirely.
    if config.push_time.enabled:
        dispatcher.register_detector(PushTimeDetector(config.push_time))
    if config.team_name.enabled:
        dispatcher.register_detector(TeamNameDetector(config.team_name))
    if config.repo_lifecycle.enabled:
        dispatcher.register_detector(RepoLifecycleDetector(config.repo_lifecycle))

    # Register notifiers 
    dispatcher.register_notifier(ConsoleNotifier())
    dispatcher.register_notifier(EmailNotifier())

    return dispatcher


def main() -> None:
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    webhook_secret = os.getenv("WEBHOOK_SECRET")


    port = int(os.getenv("PORT", 5125))

    dispatcher = build_dispatcher()
    app = create_app(dispatcher, webhook_secret=webhook_secret)

    logging.info("Starting GitHub anomaly detector on port %d", port)
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
