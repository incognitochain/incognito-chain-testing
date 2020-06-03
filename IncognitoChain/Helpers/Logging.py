import inspect
import logging.config
import os
import sys
from datetime import datetime

LOG_SEPARATOR = '=========================================================================='

STEP_LVL = 12
RESULT_LVL = 22

log_level_console = STEP_LVL
log_level_file = logging.DEBUG

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
    logger_name = os.path.basename(inspect.stack()[2][1])[:20]
    line = {'line': inspect.stack()[2][2]}
    logger = logging.getLogger(logger_name)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(name)-20s:%(line)d %(message)s', datefmt='%H:%M:%S')
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
    logger = logging.LoggerAdapter(logger, line)
    return logger


def DEBUG(msg):
    _log().debug(msg)


def INFO(msg=None):
    if msg is None:
        msg = LOG_SEPARATOR
    _log().info(msg)
    return True


def WARNING(msg):
    _log().warning(msg)


def ERROR(msg):
    _log().error(msg)


def CRITICAL(msg):
    _log().critical(msg)


def INFO_HEADLINE(msg):
    INFO(f"""
        {LOG_SEPARATOR}
        | {msg}
        {LOG_SEPARATOR}""")


logging.addLevelName(RESULT_LVL, "RESULT")


def RESULT(msg, *args, **kws):
    _log().log(RESULT_LVL, msg, *args, **kws)


logging.Logger.step = RESULT


def STEP(num, msg, *args, **kws):
    logging.addLevelName(STEP_LVL, f"STEP {num}")
    _log().log(STEP_LVL, msg, *args, **kws)


logging.Logger.step = STEP


def format_header(string):
    # TBD
    length = len(string)
