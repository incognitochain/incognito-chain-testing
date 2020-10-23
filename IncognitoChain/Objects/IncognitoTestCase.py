import sys
from distutils.util import strtobool

from IncognitoChain.Configs import config
from IncognitoChain.Helpers.Logging import WARNING, ERROR
from IncognitoChain.Objects.TestBedObject import *

# get command args
# noinspection PyProtectedMember
PARAMS = sys._xoptions
xpc = PARAMS.get("prepareCoin")
prepare_coin = config.prepare_coin_precondition if xpc is None else strtobool(str(xpc))

# option to skip loading testbed and test data from both config file and command arg
skip_load = PARAMS.get("skipLoad")
SUT = TestBed()
ACCOUNTS = []
BEACON_ACCOUNTS = []
COMMITTEE_ACCOUNTS = []

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
        ACCOUNTS = TEST_DATA.account_list
    except Exception as e:
        ERROR(e)
        WARNING("Not found accounts list in test data, create an  empty list now")
        ACCOUNTS = []
    try:
        BEACON_ACCOUNTS = TEST_DATA.beacons
    except Exception as e:
        ERROR(e)
        WARNING("Not found beacon accounts list in test data, create an  empty list now")
        BEACON_ACCOUNTS = []
    try:
        COMMITTEE_ACCOUNTS = TEST_DATA.committees
    except Exception as e:
        ERROR(e)
        WARNING("Not found committee accounts list in test data, create an  empty list now")
        COMMITTEE_ACCOUNTS = []

    # -----------------------------------------------
