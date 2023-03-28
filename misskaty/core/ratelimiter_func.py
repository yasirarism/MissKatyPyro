from typing import Union

from pyrate_limiter import BucketFullException, Duration, Limiter, MemoryListBucket, RequestRate


class RateLimiter:
    """
    Implement rate limit logic using leaky bucket
    algorithm, via pyrate_limiter.
    (https://pypi.org/project/pyrate-limiter/)
    """

    def __init__(self) -> None:
        # 2 requests per seconds
        self.second_rate = RequestRate(2, Duration.SECOND)

        # 15 requests per minute.
        self.minute_rate = RequestRate(15, Duration.MINUTE)

        # 500 requests per hour
        self.hourly_rate = RequestRate(500, Duration.HOUR)

        # 1500 requests per day
        self.daily_rate = RequestRate(1500, Duration.DAY)

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
