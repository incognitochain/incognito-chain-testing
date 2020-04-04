import time
from datetime import datetime

from IncognitoChain.Helpers.Logging import INFO


def get_current_date_time(my_format=None):
    if my_format is None:
        my_format = "%d%m%y%H%M%S"
    return datetime.now().strftime(my_format)


def WAIT(_time):
    """
    Wait time.
    Args:
      _time(num): wait time in second
    """
    pool = 5
    INFO(f"Wait for {_time} second(s)")
    print(f'{_time:>10}s', end="\r", flush=True)
    time.sleep(_time % pool)
    _time -= (_time % pool)
    while _time >= pool:
        print(f'{_time:>10}s', end="\r", flush=True)
        time.sleep(pool)
        _time -= pool
    print(f'{0:>10}s', end="\r", flush=True)
