import sys

from IncognitoChain.Configs import config
from IncognitoChain.Configs.Constants import DAO_private_key, DAO_payment_key, ONE_COIN
from IncognitoChain.Helpers.Logging import INFO_HEADLINE
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

PORTAL_FEEDER = Account(
    '112t8roezimTQwKbmsoxY9h494xhMZNBe94ux6hCH4SaFYBFnFXS9JoNbUjmeFLQiFWHeFP9MLPcy1sEiDasdW4ZkzEDzXDLG3wmwMU551tv',
    '12S2ciPBja9XCnEVEcsPvmCLeQH44vF8DMwSqgkH7wFETem5FiqiEpFfimETcNqDkARfht1Zpph9u5eQkjEnWsmZ5GB5vhc928EoNYH')
COIN_MASTER = Account(DAO_private_key, DAO_payment_key)
if COIN_MASTER.shard is None:
    COIN_MASTER.calculate_shard_id()

INFO_HEADLINE("Checking test accounts, if balance < 1/5 prv then top up to 1 prv")
# check balance and send some money if need
COIN_MASTER.top_him_up_to_amount_if(ONE_COIN / 5, ONE_COIN, ACCOUNTS)

# for account in ACCOUNTS:
    # # also send back if already have to much prv
    # elif bal > ONE_COIN:
    #     send_amount = coin(bal // ONE_COIN)
    #     account.send_prv_to(COIN_MASTER, send_amount, privacy=0).subscribe_transaction()
    #     if COIN_MASTER.shard != account.shard:
    #         try:
    #             COIN_MASTER.subscribe_cross_output_coin()
    #         except WebSocketTimeoutException:
    #             pass
INFO_HEADLINE("Done checking and top up")
