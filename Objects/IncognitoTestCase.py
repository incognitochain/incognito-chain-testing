import os

from Configs.Configs import TestConfig
from Helpers.Logging import config_logger
from Objects.AccountObject import AccountGroup
from Objects.TestBedObject import TestBed, load_test_data

logger = config_logger(__name__)
SUT = TestBed()
ACCOUNTS = AccountGroup()
BEACON_ACCOUNTS = AccountGroup()
COMMITTEE_ACCOUNTS = AccountGroup()
STAKER_ACCOUNTS = AccountGroup()


def init_test_accounts(account_file=None):
    # load account list
    if not account_file:
        account_file = os.getenv('TESTDATA', TestConfig.TEST_DATA).rstrip('y').rstrip('p').rstrip('.')
    TestConfig.TEST_DATA = account_file

    TEST_DATA = load_test_data(account_file)
    global ACCOUNTS, BEACON_ACCOUNTS, STAKER_ACCOUNTS, COMMITTEE_ACCOUNTS
    try:
        if isinstance(TEST_DATA.account_list, AccountGroup):
            ACCOUNTS = TEST_DATA.account_list
        else:
            ACCOUNTS = AccountGroup(*TEST_DATA.account_list)
    except AttributeError as e:
        logger.error(f'{type(e)}: {e}')
        logger.warning("Not found accounts list in test data, create an  empty list now")

    try:
        BEACON_ACCOUNTS = AccountGroup(*TEST_DATA.beacons)
    except AttributeError as e:
        logger.error(f'{type(e)}: {e}')
        logger.warning("Not found beacon accounts list in test data, create an  empty list now")
        BEACON_ACCOUNTS = []

    try:
        COMMITTEE_ACCOUNTS = AccountGroup(*TEST_DATA.committees)
    except AttributeError as e:
        logger.error(f'{type(e)}: {e}')
        logger.warning("Not found committee accounts list in test data, create an  empty list now")
        COMMITTEE_ACCOUNTS = []

    try:
        STAKER_ACCOUNTS = AccountGroup(*TEST_DATA.stakers)
    except AttributeError as e:
        logger.error(f'{type(e)}: {e}')
        logger.warning("Not found committee accounts list in test data, create an  empty list now")
        STAKER_ACCOUNTS = []


def init_test_bed(testbed_file=None):
    global SUT
    if not testbed_file:
        testbed_file = os.getenv("TESTBED", TestConfig.TEST_BED).rstrip('y').rstrip('p').rstrip('.')
    TestConfig.TEST_BED = testbed_file
    SUT = TestBed(testbed_file)
