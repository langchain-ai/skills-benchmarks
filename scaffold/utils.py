"""General utilities for the scaffold framework."""

import random
import time


def retry_with_backoff(func, max_retries=3, base_delay=1.0, max_delay=10.0, retry_on=None):
    """Retry a function with exponential backoff and jitter.

    Args:
        func: Callable to retry
        max_retries: Maximum number of retry attempts
        base_delay: Base delay in seconds
        max_delay: Maximum delay cap in seconds
        retry_on: Optional callable(exception) -> bool to determine if retry should happen.
                  If None, retries on rate limit errors (429, "rate limit").

    Returns:
        Result of func() or raises last exception
    """
    if retry_on is None:
        def retry_on(e):
            error_str = str(e).lower()
            return "429" in str(e) or "rate limit" in error_str

    last_exception = None
    for attempt in range(max_retries + 1):
        try:
            return func()
        except Exception as e:
            last_exception = e
            if not retry_on(e):
                raise
            if attempt < max_retries:
                # Exponential backoff with jitter
                delay = min(base_delay * (2 ** attempt) + random.uniform(0, 1), max_delay)
                time.sleep(delay)
    raise last_exception
