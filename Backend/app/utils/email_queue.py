"""
Background email queue using a daemon worker thread.

Emails submitted via ``enqueue_or_send()`` are placed in a thread-safe
in-memory queue and processed by a single background thread, so password-
reset requests return immediately without waiting for SMTP.

Upgrade path
------------
Replace the ``ThreadedEmailQueue`` with an RQ (Redis Queue) or Celery
worker when the application scales beyond a single process:

    pip install rq redis
    # then replace enqueue_or_send() to call rq.Queue.enqueue(...)
    # and run:  rq worker emails

The interface (``enqueue_or_send``) stays the same — only the backend changes.
"""

import logging
import queue
import threading

logger = logging.getLogger(__name__)


class ThreadedEmailQueue:
    """Thread-safe in-process email queue with a single daemon consumer."""

    def __init__(self, max_size: int = 500) -> None:
        self._q: queue.Queue = queue.Queue(maxsize=max_size)
        self._thread = threading.Thread(
            target=self._worker,
            daemon=True,
            name="email-worker",
        )
        self._thread.start()
        logger.info("Background email worker started")

    # ── public ────────────────────────────────────────────────────────────────

    def enqueue(
        self,
        email_service,
        *,
        to: str,
        subject: str,
        body: str,
        html_body: str | None = None,
    ) -> bool:
        """
        Add an email task to the queue.

        Returns True if queued, False if the queue is full (caller should
        fall back to synchronous sending).
        """
        try:
            self._q.put_nowait((email_service, to, subject, body, html_body))
            logger.debug("Email to %s queued for background delivery", to)
            return True
        except queue.Full:
            logger.warning(
                "Email queue full — delivering synchronously to %s", to
            )
            return False

    # ── internal worker ───────────────────────────────────────────────────────

    def _worker(self) -> None:
        while True:
            try:
                email_service, to, subject, body, html_body = self._q.get(timeout=5)
                try:
                    ok = email_service.send_email(to, subject, body, html_body=html_body)
                    if not ok:
                        logger.warning("Background email delivery failed for %s", to)
                except Exception:
                    logger.exception(
                        "Unexpected error in background email delivery to %s", to
                    )
                finally:
                    self._q.task_done()
            except queue.Empty:
                continue  # normal timeout — keep waiting
            except Exception:
                logger.exception("Email worker thread encountered an unexpected error")


# ── module-level singleton ────────────────────────────────────────────────────
# Initialised once in create_app(); None means synchronous sending.

_email_queue: ThreadedEmailQueue | None = None


def init_email_queue(enabled: bool = True) -> None:
    """Start the background email worker (call once from the app factory)."""
    global _email_queue
    if enabled and _email_queue is None:
        _email_queue = ThreadedEmailQueue()


def enqueue_or_send(
    email_service,
    *,
    to: str,
    subject: str,
    body: str,
    html_body: str | None = None,
) -> bool:
    """
    Deliver an email via the background queue when available, otherwise
    fall back to synchronous SMTP (same as before).

    Returns True if the email was queued or sent successfully.
    """
    if _email_queue is not None:
        queued = _email_queue.enqueue(
            email_service, to=to, subject=subject, body=body, html_body=html_body
        )
        if queued:
            return True
        # Queue full — fall through to synchronous send

    return email_service.send_email(to, subject, body, html_body=html_body)
