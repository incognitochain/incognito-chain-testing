import pytest
from Configs.Constants import PBTC_ID
from Helpers.Logging import INFO
from Helpers.Time import WAIT
from Objects.IncognitoTestCase import ACCOUNTS
from TestCases.PortalV4.test_PTV4_001_shield_new_flow import test_shield_new_flow as shield_btc


def test_worker():
    INFO("Start process ")
    for i in range(5):
        INFO(f"shield #{i+1}")
        shield_btc(PBTC_ID, 0.1, ACCOUNTS[2], "P2SH", "worker")
    INFO("End process")




