import time
import random

def throttle(min_delay, max_delay):
    time.sleep(random.uniform(min_delay, max_delay))

