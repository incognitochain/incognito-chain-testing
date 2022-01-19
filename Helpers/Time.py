import time
from datetime import datetime

from Helpers.Logging import config_logger

logger = config_logger(__name__)


def get_current_date_time(date_format="%y%m%d%H%M%S"):
    return datetime.now().strftime(date_format)


def WAIT(_time, unit='s'):
    """

    :param _time:
    :param unit: s (second), m (minute) or h (hour)
    :return:
    """
    logger.info(f"Wait for {_time}{unit}")

    _unit = {"s": 1,
             "m": 60,
             "h": 60 * 60}
    try:
        _time = int(_time * _unit[unit])
    except KeyError:
        raise Exception(f"Expect time unit to be [s/m/h], got {unit} instead") from None

    gap = 5
    print(f'{_time:>10}s', end="\r", flush=True)
    time.sleep(_time % gap)
    _time -= (_time % gap)
    while _time >= gap:
        print(f'{_time:>10}s', end="\r", flush=True)
        time.sleep(gap)
        _time -= gap
    print(f'{0:>10}s', end="\r", flush=True)
