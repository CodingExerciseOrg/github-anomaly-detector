import smtplib
import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from notifiers.base import BaseNotifier
from config_loader import EmailConfig
from models import Alert

logger = logging.getLogger(__name__)


class EmailNotifier(BaseNotifier):
    """Sends alerts via email using SMTP."""

    def __init__(self, config: EmailConfig) -> None:
        self._sender = config.sender
        self._destination = config.destination
        self._smtp_host = config.smtp_host
        self._smtp_port = config.smtp_port
        self._password = os.getenv("EMAIL_APPLICATION_PASSWORD")

    def notify(self, alert: Alert) -> None:
        subject = f"[GitHub Alert] {alert.title}"
        body = str(alert)

        msg = MIMEMultipart()
        msg["From"] = self._sender
        msg["To"] = self._destination
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP(self._smtp_host, self._smtp_port) as server:
                server.ehlo()
                server.starttls()
                server.login(self._sender, self._password)
                server.sendmail(self._sender, self._destination, msg.as_string())
            logger.info("Alert email sent to %s", self._destination)
        except smtplib.SMTPException as e:
            logger.error("Failed to send alert email: %s", e)
