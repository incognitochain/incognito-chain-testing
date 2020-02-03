import sys

from IncognitoChain.Configs import config
from IncognitoChain.Objects.AccountObject import Account
from IncognitoChain.Objects.TestBedObject import *

PARAMS = sys._xoptions
if PARAMS.get("list"):
    print(f'!!! Test data:{sys}')
    print(f'!!! Test bed:')
    raise SystemExit

# load transaction amount param
transaction_amount = PARAMS.get('amount')

# load test bed
test_bed = config.test_bed
if PARAMS.get("testBed") is not None:
    test_bed = PARAMS.get("testBed")
SUT = TestBed(test_bed)

# check test bed
SUT.precondition_check()

# load account list
__account_file = config.test_data
if PARAMS.get('testData') is not None:
    __account_file = PARAMS.get('testData')
ACCOUNTS: List[Account] = load_test_data(__account_file).account_list
