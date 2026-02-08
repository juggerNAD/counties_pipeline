import time
import random

def retry(func, retries=3):
    for attempt in range(retries):
        try:
            return func()
        except Exception:
            time.sleep(random.uniform(2, 5))
    return None

