import sys
from typing import List

from IncognitoChain.Configs import config
from IncognitoChain.Objects.AccountObject import Account
from IncognitoChain.Objects.TestBedObject import TestBed, load_test_data

PARAMS = sys._xoptions

# load transaction amount param
transaction_amount = PARAMS.get('amount')

# load test bed
test_bed = config.test_bed
if PARAMS.get("testbed") is not None:
    test_bed = PARAMS.get("testbed")
SUT = TestBed(test_bed)

# check test bed
SUT.precondition_check()

# load account list
__account_file = config.account_file
if PARAMS.get('accountFile') is not None:
    __account_file = PARAMS.get('accountFile')
ACCOUNTS: List[Account] = load_test_data(__account_file).account_list
