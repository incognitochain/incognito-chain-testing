import sys
from ctypes import ArgumentError

from IncognitoChain.Configs.Constants import coin, ChainConfig
from IncognitoChain.Helpers.Logging import INFO_HEADLINE, INFO
from IncognitoChain.Objects.AccountObject import COIN_MASTER
from IncognitoChain.Objects.IncognitoTestCase import ACCOUNTS, SUT
from IncognitoChain.Objects.NodeObject import Node

# -----------------------------------------
# this block of codes is for bypassing the testbed loading procedure in IncognitoTestCase for Sanity test module
try:
    # noinspection PyProtectedMember
    full_node_url = sys._xoptions.get('fullNodeUrl')
    # noinspection PyProtectedMember
    ws_port = int(sys._xoptions.get('wsPort'))
    if not full_node_url:
        raise ArgumentError('Must specify a full node url to run the test')

    SUT.full_node = Node().parse_url(full_node_url)
    SUT.full_node.set_web_socket_port(ws_port)
    SUT.REQUEST_HANDLER = SUT.full_node
except:
    pass
# -----------------------------------------

INFO_HEADLINE("Setup from Testcase init")

INFO("CONVERT to COIN V2")
convert_tx = COIN_MASTER.convert_prv_to_v2()
if convert_tx.get_error_msg() == "Method not found":
    ChainConfig.PRIVACY_VERSION = 1
elif convert_tx.get_error_msg() == "Can not create tx":
    ChainConfig.PRIVACY_VERSION = 2
else:
    ChainConfig.PRIVACY_VERSION = 2
    convert_tx.subscribe_transaction()

COIN_MASTER.top_him_up_prv_to_amount_if(coin(2), coin(5), ACCOUNTS)

INFO_HEADLINE("END setup from Testcase init")
