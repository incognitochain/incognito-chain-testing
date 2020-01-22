import inspect
import logging.config
import os
import sys
from datetime import datetime

log_level_console = logging.DEBUG
log_level_file = logging.DEBUG
STEP_LVL = 12
RESULT_LVL = 22

_log_file = datetime.now().strftime("run_%d%m%y_%H%M%S.log")


def _log():
    """
    Level       Numeric value
    ----------------------------
    CRITICAL    50
    ERROR       40
    WARNING     30
    INFO        20
    DEBUG       10
    NOTSET      0
    """

    # Gets the name of the class / method from where this method is called
    logger_name = os.path.basename(inspect.stack()[2][1])
    logger = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(name)s: %(message)s', datefmt='%H:%M:%S')
    if logger.hasHandlers():
        # Logger is already configured, remove all handlers
        logger.handlers = []

    # By default, log all messages
    logger.setLevel(logging.DEBUG)

    # create and add file logging handle
    file_handler = logging.FileHandler(filename=os.path.join('log', _log_file))
    file_handler.setFormatter(formatter)
    file_handler.setLevel(log_level_file)
    logger.addHandler(file_handler)

    # create and add system out logging handle
    sys_out_handler = logging.StreamHandler(sys.stdout)
    sys_out_handler.setFormatter(formatter)
    sys_out_handler.setLevel(log_level_console)
    logger.addHandler(sys_out_handler)
    return logger


def DEBUG(msg):
    _log().debug(msg)


def INFO(msg):
    _log().info(msg)


def WARNING(msg):
    _log().warning(msg)


def ERROR(msg):
    _log().error(msg)


def CRITICAL(msg):
    _log().critical(msg)


logging.addLevelName(RESULT_LVL, "RESULT")


def RESULT(msg, *args, **kws):
    _log().log(RESULT_LVL, msg, *args, **kws)


logging.Logger.step = RESULT


def STEP(num, msg, *args, **kws):
    logging.addLevelName(STEP_LVL, f"STEP {num}")
    _log().log(STEP_LVL, msg, *args, **kws)


logging.Logger.step = STEP


def assert_true(expr, fail_msg, pass_msg=None):
    """
    Throws exception with fail_msg if 'expr' not true, else logs pass_msg

    Args:
      expr: True/False expression
      fail_msg(String): Failure message.
      pass_msg(String): Passing message.

    Returns:
      None

    Raises:
      Exception if expr != True
    """
    if not expr:
        raise Exception(fail_msg)
    else:
        if pass_msg is not None:
            INFO(pass_msg)
