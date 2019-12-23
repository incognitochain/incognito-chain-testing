"""
Created Oct 11 2019
@Author: Khanh Le
"""

import re
import unittest, math
import pytest
import topology.NodeList as NodeList
from libs.AutoLog import INFO, STEP, assert_true
from libs.Transaction import Transaction
from libs.WebSocket import WebSocket


class test_withdrawReward(unittest.TestCase):
    """
    Test case: withdraw reward
    """
    test_data = {
        's0_addr1': [
            "112t8rnXVMJJZzfF1naXvfE9nkTKwUwFWFeh8cfEyViG1vpA8A9khJk3mhyB1hDuJ4RbreDTsZpgJK4YcSxdEpXJKMEd8Vmp5UqKWwBcYzxv",
            "12RyJTSL2G8KvjN7SUFuiS9Ek4pvFFze3EMMic31fmXVw8McwYzpKPpxeW6TLsNo1UoPhCHKV3GDRLQwdLF41PED3LQNCLsGNKzmCE5"],
        's0_addr2': [
            "112t8rnX6USJnBzswUeuuanesuEEUGsxE8Pj3kkxkqvGRedUUPyocmtsqETX2WMBSvfBCwwsmMpxonhfQm2N5wy3SrNk11eYxEyDtwuGxw2E",
            "12RwbexYzKJwGaJDdDE7rgLEkNC1dL5cJf4xNaQ29EmpPN52C6oepWiTtQCpyHAoo6ZTHMx2Nt3A8p5jYqpYvbrVYGpVTen1rVstCpr"],
        'token_id': 'xxxx'
    }

    fullnode_tx = Transaction(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['rpc'])
    fullnode_ws = WebSocket(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['ws'])
    print("ENV: " + str(NodeList.fullnode[0]))

    @pytest.mark.run
    def test_01_withdraw_reward_PRV(self):
        print("""
        DESCRIPTION: test_01_withdraw_reward_PRV
        - get current reward
        - withdraw all prv
        - try to withdraw prv again
        """)
        pass

    @pytest.mark.run
    def test_02_withdraw_reward_pToken(self):
        pass

    @pytest.mark.run
    def test_99_cleanup(self):
        print("""
            CLEAN UP
            """)
        self.fullnode_ws.closeConnection()
