import inspect
import logging.config
import os

from datetime import datetime

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(levelname)-8s %(threadName)s:%(name)s:%(lineno)d %(message)s',
            'datefmt': '%H:%M:%S'}, },
    'handlers': {
        'console': {
            'level': 'INFO',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout', },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
            'filename': f'logs/run_{datetime.now().strftime("%y%m%d_%H%M%S")}.log',
            'mode': 'w',
            'maxBytes': 10485760,
            'backupCount': 5, }, },
    'loggers': {
        '': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False}, }}

_FMT_WIDTH = 100
_FMT_CHR = '='
_STEP_LVL = 12


def config_logger(logger_name):
    logging.config.dictConfig(LOGGING_CONFIG)
    return logging.getLogger(logger_name)


class LoggerManager:
    LOGGERS = {}

    @staticmethod
    def get_logger():
        logger_name = os.path.basename(inspect.stack()[2][1])
        try:
            logger = LoggerManager.LOGGERS[logger_name]
        except (KeyError, AttributeError):
            logger = config_logger(logger_name)
            LoggerManager.LOGGERS[logger_name] = logger
        return logger


def DEBUG(msg):
    LoggerManager.get_logger().debug(msg)


def INFO(msg=_FMT_CHR * _FMT_WIDTH):
    LoggerManager.get_logger().info(msg)
    return True


def WARNING(msg):
    LoggerManager.get_logger().warning(msg)


def ERROR(msg):
    LoggerManager.get_logger().error(msg)


def CRITICAL(msg):
    LoggerManager.get_logger().critical(msg)


def INFO_HEADLINE(msg):
    l_msg = len(msg)
    width = l_msg + 6 if l_msg > _FMT_WIDTH else _FMT_WIDTH
    mid = int(((width - 6 + l_msg) / 2))
    end = width - mid - 4
    fmt_str = _FMT_CHR * width
    new_msg = ('\n{}\n{} {:>%d} {:>%d}\n{}' % (mid, end)).format(fmt_str, '||', msg, '||', fmt_str)
    LoggerManager.get_logger().info(new_msg)


def STEP(num, msg, *args, **kws):
    LoggerManager.get_logger().info(f"Step {num}: {msg}", *args, **kws)
