import os

from Configs.Configs import TestConfig
from Helpers.Logging import config_logger
from Objects.AccountObject import AccountGroup, Account
from Objects.TestBedObject import TestBed, load_test_data

logger = config_logger(__name__)
SUT = TestBed()
ACCOUNTS = AccountGroup()
BEACON_ACCOUNTS = AccountGroup()
COMMITTEE_ACCOUNTS = AccountGroup()
STAKER_ACCOUNTS = AccountGroup()


def __handle_data(test_data, data_name):
    try:
        data = getattr(test_data, data_name)
    except AttributeError as e:
        logger.error(f'{type(e)}: {e}')
        logger.warning(f"Not found {data_name} in test data, create an empty list now")
        return AccountGroup()
    if isinstance(data, AccountGroup):
        return data
    if isinstance(data[0], Account):
        return AccountGroup(*data)
    else:
        return AccountGroup().load_from_list(data)


def init_test_accounts(account_file=None):
    # load account list
    if not account_file:
        account_file = os.getenv('TESTDATA', TestConfig.TEST_DATA).rstrip('y').rstrip('p').rstrip('.')
    TestConfig.TEST_DATA = account_file

    TEST_DATA = load_test_data(account_file)
    global ACCOUNTS, BEACON_ACCOUNTS, STAKER_ACCOUNTS, COMMITTEE_ACCOUNTS

    ACCOUNTS = __handle_data(TEST_DATA, "account_list")
    BEACON_ACCOUNTS = __handle_data(TEST_DATA, "beacons")
    COMMITTEE_ACCOUNTS = __handle_data(TEST_DATA, "committees")
    STAKER_ACCOUNTS = __handle_data(TEST_DATA, "stakers")


def init_test_bed(testbed_file=None):
    global SUT
    if not testbed_file:
        testbed_file = os.getenv("TESTBED", TestConfig.TEST_BED).rstrip('y').rstrip('p').rstrip('.')
    TestConfig.TEST_BED = testbed_file
    SUT = TestBed(testbed_file)
