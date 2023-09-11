from typing import Union

from pyrate_limiter import (
    BucketFullException,
    Duration,
    Limiter,
    InMemoryBucket,
    Rate,
)


class RateLimiter:
    """
    Implement rate limit logic using leaky bucket
    algorithm, via pyrate_limiter.
    (https://pypi.org/project/pyrate-limiter/)
    """

    def __init__(self) -> None:
        # 15 requests per minute.
        self.minute_rate = Rate(15, Duration.MINUTE)

        self.limiter = Limiter(
            self.minute_rate
        )

    async def acquire(self, userid: Union[int, str]) -> bool:
        """
        Acquire rate limit per userid and return True / False
        based on userid ratelimit status.
        """

        try:
            self.limiter.try_acquire(userid)
            return False
        except BucketFullException:
            return True
