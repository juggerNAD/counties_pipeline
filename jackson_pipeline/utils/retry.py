# utils/retry.py
import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

def retry(attempts=3, delay=2, exceptions=(Exception,)):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    logger.warning(
                        f"{func.__name__} failed "
                        f"(attempt {attempt}/{attempts}): {e}"
                    )
                    if attempt == attempts:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator
