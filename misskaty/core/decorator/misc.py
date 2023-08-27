import asyncio
import logging
from functools import wraps

LOGGER = logging.getLogger("MissKaty")


def asyncify(func):
    async def inner(*args, **kwargs):
        loop = asyncio.get_running_loop()
        func_out = await loop.run_in_executor(None, func, *args, **kwargs)
        return func_out

    return inner


def new_task(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_running_loop()
            return loop.create_task(func(*args, **kwargs))
        except Exception as e:
            LOGGER.error(
                f"Failed to create task for {func.__name__} : {e}"
            )  # skipcq: PYL-E0602

    return wrapper
