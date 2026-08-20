"""Observation: the current time. First real caller is flow/probe_site.py's probe
timestamp; the runtime WAF path (backoff/retry) gets this for free later.
"""

import time


def read_clock() -> float:
    return time.time()
