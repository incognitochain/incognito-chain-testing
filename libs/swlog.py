"""
This is a customized logger module

@Author: Van.Vo
"""
import inspect
import logging
import logging.config
import time

STEP_LEVEL_NUM = 32
RESULT_LEVEL_NUM = 33


def custom_logger(log_level=logging.DEBUG):
    """
    This method use to customize logging
    """
    # Gets the name of the class / method from where this method is called
    logger_name = inspect.stack()[1][3]
    logger = logging.getLogger(logger_name)
    # By default, log all messages
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler("automation.log", 'w')
    file_handler.setLevel(log_level)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s',
                                  datefmt='%m/%d/%Y %I:%M:%S %p')
    file_handler.setFormatter(formatter)
    if logger.hasHandlers():
        logger.handlers.clear()
    logger.addHandler(file_handler)
    return logger


def INFO(msg):
    """Logs an info message.

    Args:
      msg (str): The message to be logged.

    Returns:
      None
    """
    log = custom_logger(logging.INFO)
    log.info(msg)


def WARN(msg):
    """Logs an warning message.

    Args:
      msg (str): The message to be logged.

    Returns:
      None
    """
    log = custom_logger(logging.WARN)
    log.warning(msg)


def DEBUG(msg):
    """Logs an debug message.

    Args:
      msg (str): The message to be logged.

    Returns:
      None
    """
    log = custom_logger(logging.DEBUG)
    log.debug(msg)


def ERROR(msg):
    """Logs an debug message.

    Args:
      msg (str): The message to be logged.

    Returns:
      None
    """
    log = custom_logger(logging.ERROR)
    log.error(msg)


def assert_true(expr, fail_msg, pass_msg=None):
    """
    Throws Test Error with fail_msg if val != True,
    else logs pass_msg

    Args:
      expr(expr evaluating to True / False):
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
            RESULT(pass_msg)


def STEP(msg):
    log = custom_logger(logging.INFO)
    logging.addLevelName(STEP_LEVEL_NUM, 'STEP')
    log.info('=' * 50)
    # logging.log(STEP_LEVEL_NUM, msg)
    log.info('####' + msg)
    log.info('=' * 50)


def RESULT(msg):
    logging.addLevelName(RESULT_LEVEL_NUM, 'RESULT')
    logging.log(RESULT_LEVEL_NUM, msg.upper())


def wait_time(_time):
    """
    Wait time.
    Args:
      _time(num): wait time in second
    """
    time.sleep(_time)
