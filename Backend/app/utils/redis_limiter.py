"""
Optional Redis-based sliding-window rate limiter.

Falls back gracefully to ``None`` when:
  - the ``redis`` package is not installed, OR
  - ``REDIS_URL`` is not configured, OR
  - Redis is unreachable at startup.

When ``None`` is returned by ``RedisRateLimiter.from_url()``, the caller
should continue using the existing MongoDB-based limiter.

Usage::

    limiter = RedisRateLimiter.from_url(app.config["REDIS_URL"])
    if limiter:
        limited, retry_after = limiter.consume(key, max_attempts=5, window_seconds=900)
"""

import logging
import time

logger = logging.getLogger(__name__)

_REDIS_AVAILABLE = False
try:
    import redis as _redis_lib  # type: ignore
    _REDIS_AVAILABLE = True
except ImportError:
    pass


class RedisRateLimiter:
    """Sliding-window rate limiter backed by Redis sorted sets."""

    def __init__(self, client) -> None:
        self._r = client

    # ── factory ───────────────────────────────────────────────────────────────

    @classmethod
    def from_url(cls, url: str) -> "RedisRateLimiter | None":
        """Return a connected limiter, or ``None`` if unavailable."""
        if not _REDIS_AVAILABLE or not url:
            return None
        try:
            client = _redis_lib.from_url(
                url,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2,
            )
            client.ping()
            logger.info("Redis rate limiter connected")
            return cls(client)
        except Exception as exc:
            logger.warning(
                "Redis rate limiter unavailable (%s) — falling back to MongoDB limiter", exc
            )
            return None

    # ── public API ────────────────────────────────────────────────────────────

    def consume(
        self,
        key: str,
        *,
        max_attempts: int,
        window_seconds: int,
    ) -> tuple[bool, int]:
        """
        Attempt to consume one slot in the rate-limit window.

        Returns ``(is_limited, retry_after_seconds)``.
        ``retry_after_seconds`` is 0 when not limited.
        """
        now = time.time()
        window_start = now - window_seconds
        redis_key = f"rl:{key}"

        try:
            pipe = self._r.pipeline(True)
            # Remove timestamps outside the current window
            pipe.zremrangebyscore(redis_key, 0, window_start)
            # Count remaining slots in the window BEFORE adding the new one
            pipe.zcard(redis_key)
            # Record this attempt
            pipe.zadd(redis_key, {f"{now}:{id(pipe)}": now})
            # Auto-expire the key a little after the window closes
            pipe.expire(redis_key, window_seconds + 30)
            _, count, *_ = pipe.execute()

            if count >= max(1, max_attempts):
                # Find when the oldest entry in the window expires
                oldest = self._r.zrange(redis_key, 0, 0, withscores=True)
                retry_after = window_seconds
                if oldest:
                    _, oldest_ts = oldest[0]
                    retry_after = max(1, int(float(oldest_ts) + window_seconds - now))
                return True, retry_after

            return False, 0

        except Exception as exc:
            logger.warning(
                "Redis rate-limit check failed (%s) — allowing request through", exc
            )
            return False, 0

    def reset(self, key: str) -> None:
        """Clear a rate-limit bucket (admin / test use)."""
        try:
            self._r.delete(f"rl:{key}")
        except Exception:
            pass
