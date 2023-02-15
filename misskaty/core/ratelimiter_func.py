from typing import Union

from pyrate_limiter import (BucketFullException, Duration, Limiter,
                            MemoryListBucket, RequestRate)


class RateLimiter:
    """
    Implement rate limit logic using leaky bucket
    algorithm, via pyrate_limiter.
    (https://pypi.org/project/pyrate-limiter/)
    """

    def __init__(self) -> None:

        # 3 requests per seconds
        self.second_rate = RequestRate(3, Duration.SECOND)

        # 20 requests per minute.
        self.minute_rate = RequestRate(20, Duration.MINUTE)

        # 1000 requests per hour
        self.hourly_rate = RequestRate(1000, Duration.HOUR)

        # 10000 requests per day
        self.daily_rate = RequestRate(10000, Duration.DAY)

        self.limiter = Limiter(
            self.minute_rate,
            self.hourly_rate,
            self.daily_rate,
            bucket_class=MemoryListBucket,
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