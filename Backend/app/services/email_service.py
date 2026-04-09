import logging
import time
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

    def _resolve_transport(self) -> tuple[str, int, str]:
        """Resolve SMTP transport details with safe fallbacks for common providers."""
        host = (self.host or "").strip()
        sender = (self.sender or self.user or "").strip()
        port = self.port

        if not host and self.user:
            user_domain = self.user.split("@")[-1].lower()
            if user_domain == "gmail.com":
                host = "smtp.gmail.com"
                port = port or 587
            elif user_domain in {"outlook.com", "hotmail.com", "live.com"}:
                host = "smtp.office365.com"
                port = port or 587
            elif user_domain == "yahoo.com":
                host = "smtp.mail.yahoo.com"
                port = port or 587

        return host, port, sender

    def send_email(
        self,
        to_address: str,
        subject: str,
        body: str,
        html_body: str | None = None,
        retries: int = 3,
    ) -> bool:
        host, port, sender = self._resolve_transport()

        if not host or not sender:
            logger.warning("SMTP settings missing, skipping email")
            return False

        message = EmailMessage()
        message["From"] = sender
        message["To"] = to_address
        message["Subject"] = subject
        message.set_content(body)
        if html_body:
            message.add_alternative(html_body, subtype="html")

        try:
            logger.info(f"Attempting to send email to {to_address} via {host}:{port}")
            with smtplib.SMTP(host, port) as server:
                if self.use_tls:
                    server.starttls()
                if self.user and self.password:
                    server.login(self.user, self.password)
                server.send_message(message)
            logger.info("Email sent successfully to %s", to_address)
            return True  # success — done
        except Exception as exc:
            if retries <= 1:
                logger.exception("Email send failed to %s after all retries", to_address)
                return False
            wait = 2 ** (4 - retries)  # 2s, 4s, 8s
            logger.warning(
                "Email to %s failed (%s), retrying in %ds (%d attempts left)...",
                to_address, exc, wait, retries - 1,
            )
            time.sleep(wait)
            return self.send_email(to_address, subject, body, html_body=html_body, retries=retries - 1)
