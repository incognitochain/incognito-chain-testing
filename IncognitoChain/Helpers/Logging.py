import inspect
import logging.config
import os
import sys
from datetime import datetime
from logging import Logger

log_level = logging.DEBUG


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
            log.info(pass_msg)


def __dummy():
    i = 0
    for info in inspect.stack():
        print(f' {i} = {info}')
        i += 1


class Log:
    def __init__(self):
        self._logger: Logger = None
        self._log_file = datetime.now().strftime("run_%d%m%y_%H%M%S.log")

    def __log(self, level=logging.DEBUG):
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
        self._logger = logging.getLogger(logger_name)
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(name)s: %(message)s',
                                      datefmt='%H:%M:%S')
        if self._logger.hasHandlers():
            # Logger is already configured, remove all handlers
            self._logger.handlers = []

        # By default, log all messages
        self._logger.setLevel(log_level)

        # create and add file logging handle
        file_handler = logging.FileHandler(filename=os.path.join('log', self._log_file))
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)

        # create and add system out logging handle
        sys_out_handler = logging.StreamHandler(sys.stdout)
        sys_out_handler.setFormatter(formatter)
        self._logger.addHandler(sys_out_handler)
        return self

    def debug(self, msg):
        self.__log()._logger.debug(msg)

    def info(self, msg):
        self.__log()._logger.info(msg)

    def warning(self, msg):
        self.__log()._logger.warning(msg)

    def error(self, msg):
        self.__log()._logger.error(msg)

    def critical(self, msg):
        self.__log()._logger.critical(msg)

    def STEP(self, no, msg):
        self.__log()._logger.info(f"[STEP {no}] {msg}")

    def RESULT(self, msg):
        self.__log()._logger.info(f"[RESULT] {msg}")


log = Log()


def STEP(num, msg):
    log.STEP(num, msg)


def RESULT(msg):
    log.RESULT(msg)
