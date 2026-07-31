import asyncio
import functools
import time
from collections.abc import Awaitable, Callable
from typing import TypeVar

from shared.logger import logger

T = TypeVar("T")


def with_retry(max_attempts: int = 2, base_delay: float = 1.0):
    """Sync retry decorator with exponential backoff.

    Safe to use on LangGraph nodes that are plain (non-async) functions --
    LangGraph runs sync nodes off the main event loop, so the blocking
    time.sleep here doesn't stall the CLI's spinner/input loop.
    """

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            last_exc: Exception | None = None
            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception as exc:  # noqa: BLE001
                    last_exc = exc
                    if attempt < max_attempts - 1:
                        delay = base_delay * (2**attempt)
                        logger.warning(
                            "%s failed (attempt %d/%d): %s -- retrying in %.1fs",
                            fn.__name__, attempt + 1, max_attempts, exc, delay,
                        )
                        time.sleep(delay)
            raise last_exc

        return wrapper

    return decorator


async def async_retry(
    fn: Callable[..., Awaitable[T]],
    *args,
    max_attempts: int = 2,
    base_delay: float = 1.0,
    **kwargs,
) -> T:
    """Retry an async callable with exponential backoff.
        response = await async_retry(model.ainvoke, messages)
    """
    last_exc: Exception | None = None
    for attempt in range(max_attempts):
        try:
            return await fn(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            if attempt < max_attempts - 1:
                delay = base_delay * (2**attempt)
                logger.warning(
                    "%s failed (attempt %d/%d): %s -- retrying in %.1fs",
                    getattr(fn, "__name__", repr(fn)), attempt + 1, max_attempts, exc, delay,
                )
                await asyncio.sleep(delay)
    raise last_exc
