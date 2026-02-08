"""Retry при 429/500 с exponential backoff."""
import functools
import logging
import time
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")
RETRY_CODES = (429, 500, 502, 503)
DEFAULT_MAX_RETRIES = 3
DEFAULT_INITIAL_DELAY = 1.0
DEFAULT_BACKOFF_FACTOR = 2.0


def with_retry(
    max_retries: int = DEFAULT_MAX_RETRIES,
    initial_delay: float = DEFAULT_INITIAL_DELAY,
    backoff_factor: float = DEFAULT_BACKOFF_FACTOR,
    retry_codes: tuple[int, ...] = RETRY_CODES,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """Декоратор: retry с exponential backoff при ошибках API."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            delay = initial_delay
            last_err: Exception | None = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_err = e
                    if attempt == max_retries:
                        raise
                    code = getattr(e, "status_code", None) or getattr(
                        getattr(e, "response", None), "status_code", None
                    ) or getattr(e, "code", None)
                    retryable = (
                        code in retry_codes
                        or "429" in str(e)
                        or "500" in str(e)
                        or "rate" in str(e).lower()
                    )
                    if retryable:
                        logger.warning(
                            "Retry %s/%s after %s (code=%s): %s",
                            attempt + 1,
                            max_retries,
                            delay,
                            code,
                            e,
                        )
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        raise
            raise last_err or RuntimeError("Retry failed")

        return wrapper

    return decorator
