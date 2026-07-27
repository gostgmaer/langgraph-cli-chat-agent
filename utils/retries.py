import time
import functools


def with_retry(max_attempts=3, base_delay=1.0):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last_exc = None
            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception as exc:  # noqa: BLE001
                    last_exc = exc
                    time.sleep(base_delay * (2**attempt))
            raise last_exc

        return wrapper

    return decorator
