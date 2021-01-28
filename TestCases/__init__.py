import sys

from Configs.Constants import coin, ChainConfig
from Helpers.Logging import INFO_HEADLINE
from Objects.AccountObject import COIN_MASTER, PORTAL_FEEDER, AccountGroup
from Objects.IncognitoTestCase import ACCOUNTS, SUT
from Objects.NodeObject import Node
from Objects.TestBedObject import TestBed

# -----------------------------------------
# this block of codes is for bypassing the testbed loading procedure in IncognitoTestCase for Sanity test module
try:
    # noinspection PyProtectedMember
    full_node_url = sys._xoptions.get('fullNodeUrl')
    # noinspection PyProtectedMember
    ws_port = int(sys._xoptions.get('wsPort'))
    SUT.full_node = Node().parse_url(full_node_url)
    SUT.full_node.set_web_socket_port(ws_port)
    TestBed.REQUEST_HANDLER = SUT.full_node
except:
    pass

# update SUT
PORTAL_FEEDER.req_to(SUT())
COIN_MASTER.req_to(SUT())
# -----------------------------------------

INFO_HEADLINE("Setup from Testcase init")

# INFO("CONVERT to COIN V2")
# convert_tx = COIN_MASTER.convert_prv_to_v2()
# if convert_tx.get_error_msg() == "Method not found":
#     ChainConfig.PRIVACY_VERSION = 1
# elif convert_tx.get_error_msg() == "Can not create tx":
#     ChainConfig.PRIVACY_VERSION = 2
# else:
#     ChainConfig.PRIVACY_VERSION = 2
#     convert_tx.subscribe_transaction()

if ChainConfig.PRIVACY_VERSION == 2:
    COIN_MASTER.submit_key()
    PORTAL_FEEDER.submit_key()

if isinstance(ACCOUNTS, AccountGroup) or isinstance(ACCOUNTS, list):
    COIN_MASTER.top_him_up_prv_to_amount_if(coin(2), coin(5), ACCOUNTS)

INFO_HEADLINE("END setup from Testcase init")