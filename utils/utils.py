import time
import functools
from datetime import datetime

def now_utc_iso():
    return datetime.utcnow().isoformat() + "Z"

def retry(
    tries=4,
    delay=2,
    backoff=2,
    allowed_exceptions=(Exception,),
    logger=None
):
    """
    Exponential backoff retry decorator.
    tries: total attempts (including first)
    delay: initial delay in seconds
    backoff: multiplier
    allowed_exceptions: tuple of exception types to catch and retry
    """
    def deco(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            _tries, _delay = tries, delay
            last_exc = None
            while _tries > 0:
                try:
                    return func(*args, **kwargs)
                except allowed_exceptions as e:
                    last_exc = e
                    if logger:
                        logger.error(f"Retrying {func.__name__} after error: {e}")
                    _tries -= 1
                    if _tries == 0:
                        break
                    time.sleep(_delay)
                    _delay *= backoff
            raise last_exc
        return wrapper
    return deco
