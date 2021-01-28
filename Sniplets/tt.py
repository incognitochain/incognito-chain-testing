# test_spam.py

import logging

import allure

LOGGER = logging.getLogger(__name__)


def setup_function():
    LOGGER.info("setup")


def test_eggs():
    LOGGER.info('eggs info')
    LOGGER.warning('eggs warning')
    LOGGER.error('eggs error')
    LOGGER.critical('eggs critical')
    allure.step('dskljjj')
    assert True
