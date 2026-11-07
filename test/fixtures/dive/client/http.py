import time


def wait_before_retry(timeout_ms: int) -> None:
    time.sleep(timeout_ms * 1000)
