import sys

from IncognitoChain.Configs import config
from IncognitoChain.Configs.Constants import master_address_private_key, master_address_payment_key, ONE_COIN
from IncognitoChain.Objects.AccountObject import Account
from IncognitoChain.Objects.TestBedObject import *
from IncognitoChain.Objects.TestBedObject import TestBed

# noinspection PyProtectedMember
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
SUT: TestBed = TestBed(test_bed)

# check test bed
SUT.precondition_check()

# load account list
__account_file = config.test_data
if PARAMS.get('testData') is not None:
    __account_file = PARAMS.get('testData')
ACCOUNTS: List[Account] = load_test_data(__account_file).account_list

# check balance and send some money
COIN_MASTER = Account(master_address_private_key, master_address_payment_key)
COIN_MASTER.calculate_shard_id()
for account in ACCOUNTS:
    if account.get_prv_balance() < ONE_COIN / 5:
        COIN_MASTER.send_prv_to(account, ONE_COIN - account.get_prv_balance_cache(), privacy=0).subscribe_transaction()
        if COIN_MASTER.shard != account.shard:
            account.subscribe_cross_output_coin()
