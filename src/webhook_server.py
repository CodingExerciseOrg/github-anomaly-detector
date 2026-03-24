import hashlib
import hmac
import json
import logging

from flask import Flask, request, abort

from dispatcher import EventDispatcher

logger = logging.getLogger(__name__)


def create_app(dispatcher: EventDispatcher, webhook_secret: str | None = None) -> Flask:
    """
    Factory that creates the Flask app wired to the given dispatcher.

    Args:
        dispatcher:      The EventDispatcher instance to route events through.
        webhook_secret:  Optional GitHub webhook secret for payload verification.
                         Set this in GitHub and pass it here to reject forged requests.
    """
    app = Flask(__name__)

    @app.route("/webhook", methods=["POST"])
    def webhook():
        # --- Optional signature verification ---
        if webhook_secret:
            sig_header = request.headers.get("X-Hub-Signature-256", "")
            expected = "sha256=" + hmac.new(
                webhook_secret.encode(), request.data, hashlib.sha256
            ).hexdigest()
            if not hmac.compare_digest(sig_header, expected):
                logger.warning("Webhook signature mismatch — request rejected.")
                abort(403)

        event_type = request.headers.get("X-GitHub-Event", "unknown")
        try:
            payload = request.get_json(force=True) or {}
        except Exception:
            logger.error("Failed to parse webhook payload as JSON.")
            abort(400)

        logger.info("Received event: %s", event_type)
        dispatcher.dispatch(event_type, payload)
        return "", 200

    return app
