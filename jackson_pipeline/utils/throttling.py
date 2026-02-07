# utils/throttling.py
import time
import threading

_lock = threading.Lock()
_last_request_time = 0.0

def throttle(min_interval: float = 2.0):
    """
    Ensures at least `min_interval` seconds between requests.
    Thread-safe.
    """
    global _last_request_time

    with _lock:
        elapsed = time.time() - _last_request_time
        if elapsed < min_interval:
            time.sleep(min_interval - elapsed)
        _last_request_time = time.time()
