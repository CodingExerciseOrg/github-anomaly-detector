import smtplib
import logging
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from notifiers.base import BaseNotifier
from models import Alert

logger = logging.getLogger(__name__)


class EmailNotifier(BaseNotifier):
    """Sends alerts via email using SMTP."""

    def __init__(
        self,
        sender: str = "idangin93@yahoo.com",
        destination: str = "githubchecker@yopmail.com",
        password: str = os.getenv("EMAIL_APPLICATION_PASSWORD"),
        smtp_host: str = "smtp.mail.yahoo.com",
        smtp_port: int = 587,
    ) -> None:
        self._sender = sender
        self._destination = destination
        self._password = password
        self._smtp_host = smtp_host
        self._smtp_port = smtp_port

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