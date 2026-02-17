import logging
import smtplib
from email.message import EmailMessage


logger = logging.getLogger(__name__)


class EmailService:
    def __init__(self, host: str, port: int, user: str, password: str, sender: str, use_tls: bool):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.sender = sender
        self.use_tls = use_tls

    def send_email(self, to_address: str, subject: str, body: str) -> None:
        if not self.host or not self.sender:
            logger.warning("SMTP settings missing, skipping email")
            return

        message = EmailMessage()
        message["From"] = self.sender
        message["To"] = to_address
        message["Subject"] = subject
        message.set_content(body)

        try:
            logger.info(f"Attempting to send email to {to_address} via {self.host}:{self.port}")
            with smtplib.SMTP(self.host, self.port) as server:
                if self.use_tls:
                    server.starttls()
                if self.user and self.password:
                    server.login(self.user, self.password)
                server.send_message(message)
            logger.info(f"Email sent successfully to {to_address}")
        except Exception as e:
            logger.exception(f"Email send failed to {to_address}: {str(e)}")
