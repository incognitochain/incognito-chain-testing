"""
un-customized logging
"""
import logging.config

LOG_SEPARATOR = '=========================================================================='


def DEBUG(msg):
    logging.debug(msg)


def INFO(msg=None):
    if msg is None:
        msg = LOG_SEPARATOR
    logging.info(msg)
    return True


def WARNING(msg):
    logging.warning(msg)


def ERROR(msg):
    logging.error(msg)


def CRITICAL(msg):
    logging.critical(msg)


def INFO_HEADLINE(msg):
    INFO(f"""
        {LOG_SEPARATOR}
        | {msg.upper()}
        {LOG_SEPARATOR}""")


def STEP(num, msg):
    logging.info(f'Step {num}: {msg}')


logging.Logger.step = STEP
