import time
import random

def retry(attempts=3):
    def wrapper(func):
        def inner(*args, **kwargs):
            for i in range(attempts):
                try:
                    return func(*args, **kwargs)
                except Exception:
                    if i == attempts - 1:
                        raise
                    time.sleep(random.uniform(2, 4))
        return inner
    return wrapper
