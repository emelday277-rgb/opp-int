import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)


def with_retry(max_attempts: int = 3, delay: float = 2.0, backoff: float = 2.0):
    """
    Decorator that retries a function on failure.
    delay: initial wait in seconds
    backoff: multiplier applied to delay after each failure
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        logger.error(f"{func.__name__} failed after {max_attempts} attempts: {e}")
                        raise
                    logger.warning(f"{func.__name__} attempt {attempt} failed: {e}. Retrying in {current_delay}s...")
                    time.sleep(current_delay)
                    current_delay *= backoff
        return wrapper
    return decorator