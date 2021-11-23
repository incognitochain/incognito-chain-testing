"""
This package should contain all integration/business test.
"""
from Configs.Configs import ChainConfig
from Configs.Constants import coin
from Helpers.Logging import INFO_HEADLINE, INFO
from Objects.AccountObject import COIN_MASTER, PORTAL_FEEDER, AccountGroup
from Objects.IncognitoTestCase import init_test_bed, init_test_accounts

logger = "Test Init"
# update SUT
init_test_bed()
init_test_accounts()
ChainConfig.get_running_config()

from Objects.IncognitoTestCase import ACCOUNTS, SUT

ACCOUNTS.change_req_handler(SUT())
PORTAL_FEEDER.req_to(SUT())
COIN_MASTER.req_to(SUT())
# -----------------------------------------
INFO_HEADLINE("Setup from Testcase init", logger)

AccountGroup(COIN_MASTER, PORTAL_FEEDER).submit_key('ota')
for c in COIN_MASTER.list_utxo():
    if c.get_version() == 1:
        INFO("CONVERT to COIN V2", logger)
        COIN_MASTER.convert_token_to_v2().subscribe_transaction()
        break
ACCOUNTS.submit_key('ota') if len(ACCOUNTS) <= 100 else None

if isinstance(ACCOUNTS, AccountGroup) or isinstance(ACCOUNTS, list):
    COIN_MASTER.top_up_if_lower_than(ACCOUNTS, coin(2), coin(5))

INFO_HEADLINE("END setup from Testcase init", logger)
