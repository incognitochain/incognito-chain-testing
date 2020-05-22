import sys

from websocket import WebSocketTimeoutException

from IncognitoChain.Configs import config
from IncognitoChain.Configs.Constants import master_address_private_key, master_address_payment_key, ONE_COIN, coin
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

COIN_MASTER = Account(master_address_private_key, master_address_payment_key)
COIN_MASTER.calculate_shard_id()
for account in ACCOUNTS:
    bal = account.get_prv_balance()
    # check balance and send some money if need
    if bal < ONE_COIN / 5:
        send_amount = ONE_COIN - account.get_prv_balance_cache()
        COIN_MASTER.send_prv_to(account, send_amount, privacy=0).subscribe_transaction()
        if COIN_MASTER.shard != account.shard:
            try:
                account.subscribe_cross_output_coin()
            except WebSocketTimeoutException:
                pass

    # # also send back if already have to much prv
    # elif bal > ONE_COIN:
    #     send_amount = coin(bal // ONE_COIN)
    #     account.send_prv_to(COIN_MASTER, send_amount, privacy=0).subscribe_transaction()
    #     if COIN_MASTER.shard != account.shard:
    #         try:
    #             COIN_MASTER.subscribe_cross_output_coin()
    #         except WebSocketTimeoutException:
    #             pass
