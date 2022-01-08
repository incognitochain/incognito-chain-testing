"""
This package should contain all integration/business test.
"""
import os

from Configs.Configs import ChainConfig
from Configs.Constants import coin
from Helpers.Logging import config_logger
from Objects.AccountObject import COIN_MASTER, PORTAL_FEEDER, AccountGroup
from Objects.IncognitoTestCase import init_test_bed, init_test_accounts

logger = config_logger(__name__)
# update SUT
init_test_bed()
init_test_accounts()
ChainConfig.get_running_config()

from Objects.IncognitoTestCase import ACCOUNTS, SUT

ACCOUNTS.change_req_handler(SUT())
PORTAL_FEEDER.req_to(SUT())
COIN_MASTER.req_to(SUT())
# -----------------------------------------
logger.info("!!!!!!!!!!!!!!!!!!! Setup from Testcase init")

if int(os.getenv("SUBMIT", False)):
    AccountGroup(COIN_MASTER, PORTAL_FEEDER).submit_key('ota')
    ACCOUNTS.submit_key('ota') if len(ACCOUNTS) <= 100 else None

if int(os.getenv("CONVERT", False)):
    for c in COIN_MASTER.list_utxo().get_coins():
        if c.get_version() == 1:
            logger.info("CONVERT to COIN V2")
            COIN_MASTER.convert_token_to_v2().subscribe_transaction()
            break

if (isinstance(ACCOUNTS, AccountGroup) or isinstance(ACCOUNTS, list)) and int(os.getenv("TOPUP", False)):
    COIN_MASTER.top_up_if_lower_than(ACCOUNTS, coin(2), coin(5))

logger.info("END setup from Testcase init")
