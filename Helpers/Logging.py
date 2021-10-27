import inspect
import logging.config
import os
import sys
import threading
from datetime import datetime

_FMT_WIDTH = 100
_FMT_CHR = '='
_STEP_LVL = 12

log_level_console = _STEP_LVL

_now = datetime.now().strftime("%y%m%d_%H%M%S")
_log_file_full = f'run_{_now}.log'
_log_file_short = f'run_{_now}_short.log'

_formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(name)-20s:%(line)d %(message)s', datefmt='%H:%M:%S')
# create file logging handle: full log
_file_handler_full = logging.FileHandler(filename=os.path.join('log', _log_file_full))
_file_handler_full.setFormatter(_formatter)
_file_handler_full.setLevel(logging.DEBUG)
# create file logging handle: short log
_file_handler_short = logging.FileHandler(filename=os.path.join('log', _log_file_short))
_file_handler_short.setFormatter(_formatter)
_file_handler_short.setLevel(_STEP_LVL)
# create system out logging handle
_sys_out_handler = logging.StreamHandler(sys.stdout)
_sys_out_handler.setFormatter(_formatter)
_sys_out_handler.setLevel(log_level_console)

LOGGERS = {}


def _log(logger_name=None):
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
    if not logger_name:
        # Gets the name of the class / method from where this method is called
        logger_name = f"{threading.currentThread().getName()}:{os.path.basename(inspect.stack()[2][1])[:20]}"
    line = {'line': inspect.stack()[2][2]}
    try:
        logger = LOGGERS[logger_name]
    except (KeyError, AttributeError):
        logger = logging.getLogger(logger_name)
        # By default, log all messages
        logger.setLevel(logging.DEBUG)
        logger.addHandler(_file_handler_full)
        logger.addHandler(_file_handler_short)
        logger.addHandler(_sys_out_handler)
        LOGGERS[logger_name] = logger
    return logging.LoggerAdapter(logger, line)


def DEBUG(msg, logger_name=None):
    _log(logger_name).debug(msg)


def INFO(msg=None, logger_name=None):
    if msg is None:
        msg = _FMT_CHR * _FMT_WIDTH
    _log(logger_name).info(msg)
    return True


def WARNING(msg, logger_name=None):
    _log(logger_name).warning(msg)


def ERROR(msg, logger_name=None):
    _log(logger_name).error(msg)


def CRITICAL(msg, logger_name=None):
    _log(logger_name).critical(msg)


def INFO_HEADLINE(msg, logger_name=None):
    l_msg = len(msg)
    width = l_msg + 6 if l_msg > _FMT_WIDTH else _FMT_WIDTH
    mid = int(((width - 6 + l_msg) / 2))
    end = width - mid - 4
    fmt_str = _FMT_CHR * width
    new_msg = ('\n{}\n{} {:>%d} {:>%d}\n{}' % (mid, end)).format(fmt_str, '||', msg, '||', fmt_str)
    _log(logger_name).info(new_msg)


def STEP(num, msg, *args, **kws):
    logging.addLevelName(_STEP_LVL, f"STEP {num}")
    _log().log(_STEP_LVL, msg, *args, **kws)


logging.Logger.step = STEP
