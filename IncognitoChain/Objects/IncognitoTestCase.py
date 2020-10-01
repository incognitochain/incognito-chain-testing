import sys
from distutils.util import strtobool

from IncognitoChain.Configs import config
from IncognitoChain.Configs.Constants import ONE_COIN, DAO_private_key, DAO_payment_key, ChainConfig
from IncognitoChain.Helpers.Logging import INFO_HEADLINE
from IncognitoChain.Objects.AccountObject import Account
from IncognitoChain.Objects.TestBedObject import *

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
    test_bed = PARAMS.get("testBed").strip('.py')
SUT: TestBed = TestBed(test_bed)

# check test bed
SUT.precondition_check()

# load account list
__account_file = config.test_data
if PARAMS.get('testData') is not None:
    __account_file = PARAMS.get('testData').strip('.py')

TEST_DATA = load_test_data(__account_file)
try:
    ACCOUNTS: List[Account] = TEST_DATA.account_list
except:
    ACCOUNTS = []
try:
    BEACON_ACCOUNTS: List[Account] = TEST_DATA.beacons
except:
    BEACON_ACCOUNTS = []
try:
    COMMITTEE_ACCOUNTS: List[Account] = TEST_DATA.committees
except:
    COMMITTEE_ACCOUNTS = []

PORTAL_FEEDER = Account(
    '112t8roezimTQwKbmsoxY9h494xhMZNBe94ux6hCH4SaFYBFnFXS9JoNbUjmeFLQiFWHeFP9MLPcy1sEiDasdW4ZkzEDzXDLG3wmwMU551tv',
    '12S2ciPBja9XCnEVEcsPvmCLeQH44vF8DMwSqgkH7wFETem5FiqiEpFfimETcNqDkARfht1Zpph9u5eQkjEnWsmZ5GB5vhc928EoNYH')
COIN_MASTER = Account(DAO_private_key, DAO_payment_key)

convert_tx = COIN_MASTER.convert_prv_to_v2()
if convert_tx.get_error_msg() == "Method not found":
    ChainConfig.PRIVACY_VERSION = 1
elif convert_tx.get_error_msg() == "Can not create tx":
    ChainConfig.PRIVACY_VERSION = 2
else:
    ChainConfig.PRIVACY_VERSION = 2
    convert_tx.subscribe_transaction()

if COIN_MASTER.shard is None:
    COIN_MASTER.calculate_shard_id()

prepare_coin = config.prepare_coin_precondition
if PARAMS.get("prepareCoin") is not None:
    prepare_coin = strtobool(PARAMS.get("prepareCoin"))

if prepare_coin:
    INFO_HEADLINE("Checking test accounts, if balance < 1/5 prv then top up to 1 prv")
    COIN_MASTER.top_him_up_prv_to_amount_if(ONE_COIN / 5, ONE_COIN, ACCOUNTS)

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
