"""
This is a customized logger module

@Author: Van.Vo
"""
import inspect
import logging
import logging.config
import os, sys
import time
from datetime import datetime

STEP_LEVEL_NUM = 32
RESULT_LEVEL_NUM = 33


def custom_logger(log_level=logging.DEBUG):
    """
    This method use to customize logging
    """
    # Gets the name of the class / method from where this method is called
    logger_name = inspect.stack()[2][1]
    logger = logging.getLogger(logger_name)
    if logger.hasHandlers():
        # Logger is already configured, remove all handlers
        logger.handlers = []

    # By default, log all messages
    logger.setLevel(logging.DEBUG)

    log_file = datetime.now().strftime("run_%b_%d_%Y.log")

    file_handler = logging.FileHandler(filename=os.path.join('log', log_file))

    file_handler.setLevel(log_level)

    formatter = logging.Formatter('%(asctime)s - %(name)-103s - %(levelname)-8s: %(message)s',
                                  datefmt='%b%d %H:%M:%S')
    file_handler.setFormatter(formatter)
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
    print("  [INFO] " + str(msg))


def WARN(msg):
    """Logs an warning message.

    Args:
      msg (str): The message to be logged.

    Returns:
      None
    """
    log = custom_logger(logging.WARN)
    log.warning(msg)
    print("  [WARNING] " + msg)


def DEBUG(msg):
    """Logs an debug message.

    Args:
      msg (str): The message to be logged.

    Returns:
      None
    """
    log = custom_logger(logging.DEBUG)
    log.debug(msg)
    # print("[DEBUG] " + msg)


def ERROR(msg):
    """Logs an debug message.

    Args:
      msg (str): The message to be logged.

    Returns:
      None
    """
    log = custom_logger(logging.ERROR)
    log.error(msg)
    print("  [ERROR] " + msg)


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
            INFO(pass_msg)

def STEP(no, msg):
    log = custom_logger(logging.INFO)
    log.info("[STEP %d] %s" % (no, msg))
    print("[STEP %d] %s" % (no, msg))

def RESULT(msg):
    log = custom_logger(logging.INFO)
    log.info("[RESULT] %s" % msg)
    print("[RESULT] %s" % msg.upper())


def WAIT(_time):
    """
    Wait time.
    Args:
      _time(num): wait time in second
    """
    log = custom_logger(logging.INFO)
    log.info("[WAIT] " + str(_time) + "second(s)")
    print("  [WAIT] " + str(_time) + "second(s)")
    for i in range(_time, 0, -1):
        print(str(i), end="\r", flush=True)
        time.sleep(1)
