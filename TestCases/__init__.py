"""
This package should contain all integration/business test.
"""
import sys

from Configs.Constants import coin
from Helpers.Logging import INFO_HEADLINE, INFO
from Helpers.Time import WAIT
from Objects.AccountObject import COIN_MASTER, PORTAL_FEEDER, AccountGroup
from Objects.IncognitoTestCase import SUT, ACCOUNTS
from Objects.NodeObject import Node
from Objects.TestBedObject import TestBed

logger = "Test Init"
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
INFO_HEADLINE("Setup from Testcase init", logger)

COIN_MASTER.submit_key()
PORTAL_FEEDER.submit_key()
for c in COIN_MASTER.list_unspent_coin():
    if c.get_version() == 1:
        INFO("CONVERT to COIN V2", logger)
        COIN_MASTER.convert_token_to_v2().subscribe_transaction()
        break
ACCOUNTS.submit_key('ota')
WAIT(60)

if isinstance(ACCOUNTS, AccountGroup) or isinstance(ACCOUNTS, list):
    COIN_MASTER.top_up_if_lower_than(ACCOUNTS, coin(2), coin(5))

INFO_HEADLINE("END setup from Testcase init", logger)
