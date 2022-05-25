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

from Objects.IncognitoTestCase import ACCOUNTS, SUT, STAKER_ACCOUNTS, COMMITTEE_ACCOUNTS, BEACON_ACCOUNTS

ACCOUNTS.attach_to_node(SUT())
STAKER_ACCOUNTS.attach_to_node(SUT())
COMMITTEE_ACCOUNTS.attach_to_node(SUT())
BEACON_ACCOUNTS.attach_to_node(SUT())
PORTAL_FEEDER.attach_to_node(SUT())
COIN_MASTER.attach_to_node(SUT())
STAKER_ACCOUNTS.attach_to_node(SUT())
BEACON_ACCOUNTS.attach_to_node(SUT())
# -----------------------------------------
logger.info("!!!!!!!!!!!!!!!!!!! Setup from Testcase init")
if os.getenv("FIRST_TIME", 'no'):
    env_config = {'SUBMIT': os.getenv("SUBMIT", 1),
                  'CONVERT': os.getenv("CONVERT", 1),
                  'TOPUP': int(os.getenv("TOPUP", 1))}
else:
    env_config = {'SUBMIT': os.getenv("SUBMIT", 0),
                  'CONVERT': os.getenv("CONVERT", 0),
                  'TOPUP': int(os.getenv("TOPUP", 0))}

if env_config["SUBMIT"]:
    AccountGroup(COIN_MASTER, PORTAL_FEEDER).submit_key('ota')
    ACCOUNTS.submit_key('ota') if len(ACCOUNTS) <= 100 else None

if env_config["CONVERT"]:
    for c in COIN_MASTER.list_utxo().get_coins():
        if c.get_version() == 1:
            logger.info("CONVERT to COIN V2")
            COIN_MASTER.convert_token_to_v2().subscribe_transaction()
            break

if (isinstance(ACCOUNTS, AccountGroup) or isinstance(ACCOUNTS, list)) and env_config["TOPUP"]:
    COIN_MASTER.top_up_if_lower_than(ACCOUNTS, coin(env_config["TOPUP"]), coin(env_config["TOPUP"]))

logger.info("END setup from Testcase init")
