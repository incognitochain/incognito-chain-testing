import sys
from distutils.util import strtobool

from IncognitoChain.Configs import config
from IncognitoChain.Helpers.Logging import WARNING, ERROR
from IncognitoChain.Objects.AccountObject import AccountGroup
from IncognitoChain.Objects.TestBedObject import *

# get command args
# noinspection PyProtectedMember
PARAMS = sys._xoptions
xpc = PARAMS.get("prepareCoin")
prepare_coin = config.prepare_coin_precondition if xpc is None else strtobool(str(xpc))

# option to skip loading testbed and test data from both config file and command arg
skip_load = PARAMS.get("skipLoad")
SUT = TestBed()
ACCOUNTS = AccountGroup()
BEACON_ACCOUNTS = AccountGroup()
COMMITTEE_ACCOUNTS = AccountGroup()

if not skip_load:
    # load test bed
    test_bed = config.test_bed
    if PARAMS.get("testBed") is not None:
        test_bed = PARAMS.get("testBed").strip('.py')
    SUT: TestBed = TestBed(test_bed)

    # load account list
    __account_file = config.test_data
    if PARAMS.get('testData') is not None:
        __account_file = PARAMS.get('testData').strip('.py')

    SUT.precondition_check()  # check test bed

    TEST_DATA = load_test_data(__account_file)
    try:
        if type(TEST_DATA.account_list) is dict:
            ACCOUNTS = TEST_DATA.account_list
        elif type(TEST_DATA.account_list) is AccountGroup:
            ACCOUNTS = TEST_DATA.account_list
        else:
            ACCOUNTS = AccountGroup(*TEST_DATA.account_list)
    except AttributeError as e:
        ERROR(f'{type(e)}: {e}')
        WARNING("Not found accounts list in test data, create an  empty list now")

    try:
        BEACON_ACCOUNTS = AccountGroup(*TEST_DATA.beacons)
    except AttributeError as e:
        ERROR(f'{type(e)}: {e}')
        WARNING("Not found beacon accounts list in test data, create an  empty list now")
        BEACON_ACCOUNTS = []

    try:
        COMMITTEE_ACCOUNTS = AccountGroup(*TEST_DATA.committees)
    except AttributeError as e:
        ERROR(f'{type(e)}: {e}')
        WARNING("Not found committee accounts list in test data, create an  empty list now")
        COMMITTEE_ACCOUNTS = []

    # -----------------------------------------------
