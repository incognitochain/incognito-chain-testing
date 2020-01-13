"""
Created Oct 11 2019
@Author: Khanh Le
"""

import re
import unittest
import pytest
import topology.NodeList as NodeList
from libs.AutoLog import INFO, STEP, assert_true, WAIT
from libs.Transaction import Transaction
from libs.WebSocket import WebSocket


class test_withdrawReward(unittest.TestCase):
    """
    Test case: withdraw reward
    """
    test_data = {
        's0_addr1': [
            "112t8rnXbsJF4f5xtzM2jPW6dCYHChNksth7X64iUkLR4bGi2JBVjgJQRLeKRsdbiFaYMsxzrfbfKAp4TELGre45QkxHWCnwVXPGnnZjJKVL",
            "12RpnCFbaD9sDcWzAr1McGpbk4u2PgXSGq2chygnUNpyyvPn1VHMJz23449HaWJSHif9DQ4KY9oSBJB6n9mM9GV8cADZqjrUkvirsWk"],
        's0_addr2': [
            "112t8rnY4DeSGZYb8r8sSN5WJr6ZL3NCafYAQ7f7Am9KXQDGSc3Qddpn7BfHW1i6CoVVk8vKEzJ25vA9uc9EdhoLU98eoUw7fMrPPrBdNB7Q",
            "12Rtn5fwsb7pTGn8YTCsouMXm73ouPeyQouJeVaVM9gP6HeyywGGBAFqyxzmYz3q7SNyFso85RV3eAemLnh7Kad93F3kfkoK8hwUqcW"],
        'token_prv_id': "0000000000000000000000000000000000000000000000000000000000000004"
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
        """)

        STEP(1, "get receiver balance before withdraw")
        step1_result = self.fullnode_tx.getBalance(self.test_data["s0_addr1"][0])
        INFO("receiver balance before : " + str(step1_result))
        assert_true(step1_result != "Invalid parameters", "get receiver balance something wrong")

        STEP(2, "get current reward")
        step2_result = self.fullnode_tx.get_reward_prv(self.test_data["s0_addr1"][1])
        INFO("PRV reward : " + str(step2_result[1]))
        assert_true(step2_result[1] != "Unexpected error", " get reward something wrong")

        STEP(3, "withdraw reward")
        step3_result = self.fullnode_tx.withdrawReward(self.test_data["s0_addr1"][0], self.test_data["s0_addr1"][1],
                                                       self.test_data["token_prv_id"])
        assert_true(step3_result[0] != "Can not send tx", "withdraw reward failed","withdraw reward success")

        STEP(4, "subcribe transaction")
        self.fullnode_ws.createConnection()
        wsc = self.fullnode_ws.subcribePendingTransaction(step3_result[0])

        STEP(5, "check remain reward ")
        step5_result = self.fullnode_tx.get_reward_prv(self.test_data["s0_addr1"][1])
        INFO("Remaind reward : " + str(step5_result[1]))
        assert_true(step5_result[1] == 0, "remaind reward != 0 ")

        STEP(6, "Check receiver balance after withdraw")
        step6_result = self.fullnode_tx.getBalance(self.test_data["s0_addr1"][0])
        INFO("receiver balance after: " + str(step6_result))
        assert_true(step6_result == step1_result + step2_result[1], "receiver balance not correct")

    @pytest.mark.run
    def test_02_withdraw_reward_PRV_0(self):
        print("""
        DESCRIPTION: withdraw_reward_PRV when remain reward = 0
        - get current reward = 0
        - withdraw all prv
        """)
        STEP(1, "get receiver balance before sending")
        step1_result = self.fullnode_tx.getBalance(self.test_data["s0_addr1"][0])
        INFO("receiver balance before : " + str(step1_result))
        assert_true(step1_result != "Invalid parameters", "get balance something wrong")

        STEP(2, "get current reward")
        step2_result = self.fullnode_tx.get_reward_prv(self.test_data["s0_addr1"][1])
        INFO("PRV reward : " + str(step2_result[1]))
        assert_true(step2_result[1] != "Invalid parameters", " get reward something wrong")
        assert_true(step2_result[1] == 0, " reward something wrong")

        STEP(3, "withdraw reward")
        step3_result = self.fullnode_tx.withdrawReward(self.test_data["s0_addr1"][0], self.test_data["s0_addr1"][1],
                                                       self.test_data["token_prv_id"])
        assert_true(step3_result[0] == "Can not send tx", "withdraw reward success", "withdraw reward success")

        STEP(5, "check remain reward  ")
        step5_result = self.fullnode_tx.get_reward_prv(self.test_data["s0_addr1"][1])
        INFO("Remaind reward : " + str(step5_result[1]))
        assert_true(step5_result[1] == step2_result[1], "remaind reward != 0 ")

        STEP(6, "Check receiver balance after withdraw ")
        step6_result = self.fullnode_tx.getBalance(self.test_data["s0_addr1"][0])
        INFO("receiver balance after : " + str(step6_result))
        assert_true(step6_result == step1_result, "balance receiver not correct")

    @pytest.mark.run
    def test_03_withdraw_reward_PRV_another_payment_address(self):
        print("""
           DESCRIPTION: withdraw_reward_PRV for another payment address
           - get current reward
           - withdraw all prv
           - reward transfer for main address
           """)
        STEP(1, "get receiver 1 & 2 balance before sending")
        step1_result_add1 = self.fullnode_tx.getBalance(self.test_data["s0_addr1"][0])
        INFO("receiver 1 balance: " + str(step1_result_add1))
        assert_true(step1_result_add1 != "Invalid parameters", "get balance something wrong")

        step1_result_add2 = self.fullnode_tx.getBalance(self.test_data["s0_addr2"][0])
        INFO("receiver 2 balance: " + str(step1_result_add2))
        assert_true(step1_result_add2 != "Invalid parameters", "get balance something wrong")

        STEP(2, "get current reward")
        step2_result = self.fullnode_tx.get_reward_prv(self.test_data["s0_addr2"][1])
        INFO("PRV reward : " + str(step2_result[1]))
        assert_true(step2_result[1] != "Invalid parameters", " get reward something wrong")

        STEP(3, "withdraw reward PRV of receiver 2 for payment receiver 1")
        step3_result = self.fullnode_tx.withdrawReward(self.test_data["s0_addr2"][0], self.test_data["s0_addr1"][1],
                                                       self.test_data["token_prv_id"])
        assert_true(step3_result[0] != "Can not send tx", "withdraw reward failed","withdraw reward success")

        STEP(4, "subcribe transaction")
        self.fullnode_ws.createConnection()
        wsc = self.fullnode_ws.subcribePendingTransaction(step3_result[0])

        STEP(5, "check remaind reward ")
        step5_result = self.fullnode_tx.get_reward_prv(self.test_data["s0_addr2"][1])
        INFO("Remaind PRV reward : " + str(step5_result[1]))
        assert_true(step5_result[1] == 0, "remaind reward != 0 ")

        STEP(6, " check balance receiver 1 & 2 after withdraw")
        step6_result_add1 = self.fullnode_tx.getBalance(self.test_data["s0_addr1"][0])
        INFO("receiver 1 balance : " + str(step6_result_add1))
        assert_true(step6_result_add1 == step1_result_add1, "balance receiver not correct")

        step6_result_add2 = self.fullnode_tx.getBalance(self.test_data["s0_addr2"][0])
        INFO("receiver 2 balance : " + str(step6_result_add2))
        assert_true(step6_result_add2 == step2_result[1] + step1_result_add2, "balance receiver not correct", "reward withdraw into receiver 2")

    @pytest.mark.run
    def test_04_withdraw_reward_pToken(self):
        print("""
        Withdraw reward token
        - check balance prv - token and token reward of address
        - withdraw token
        - check balance token increase - prv not change
        - try withdraw again -> raise "can not sent" -> balance not change     
        """)

        STEP(1, "Check balance prv - token receiver")
        step1_prv_add = self.fullnode_tx.getBalance(self.test_data["s0_addr1"][0])
        assert_true(step1_prv_add != "Invalid parameters", " get balance prv something wrong")
        INFO("Balance PRV : " + str(step1_prv_add))

        step1_token_reward = self.fullnode_tx.get_reward_token(self.test_data["s0_addr1"][1])
        assert_true(step1_token_reward[0] != "NoToken" or not step1_token_reward[0] != "Unexpected error",
                    "don't have token to withdraw")
        INFO("Token id : " + str(step1_token_reward[0]))
        INFO("Token reward : " + str(step1_token_reward[1]))

        step1_token_add = self.fullnode_tx.get_customTokenBalance(self.test_data["s0_addr1"][0], step1_token_reward[0])
        assert_true(step1_token_add[0] != "Invalid parameters", " get balance prv something wrong")
        INFO("Balance token : " + str(step1_token_add[0]))

        STEP(2, "Withdraw token")
        step2_result = self.fullnode_tx.withdrawReward(self.test_data["s0_addr1"][0], self.test_data["s0_addr1"][1],
                                                       step1_token_reward[0])
        assert_true(step2_result[0] != "Can not send tx", "withdraw reward failed")

        STEP(3, "subcribe transaction")
        self.fullnode_ws.createConnection()
        wsc = self.fullnode_ws.subcribePendingTransaction(step2_result[0])

        STEP(4, "Check balance after withdraw token")
        step4_prv_add = self.fullnode_tx.getBalance(self.test_data["s0_addr1"][0])
        INFO("Balance PRV : " + str(step4_prv_add))
        assert_true(step4_prv_add == step1_prv_add, " get balance prv something wrong")

        step4_token_reward = self.fullnode_tx.check_reward_specific_token(self.test_data["s0_addr1"][1],
                                                                          step1_token_reward[0])
        assert_true(step4_token_reward[0] == "token not exist", "token doesn't pay correct yet ")
        INFO("Token pay out")

        step4_token_add = self.fullnode_tx.get_customTokenBalance(self.test_data["s0_addr1"][0], step1_token_reward[0])
        assert_true(step4_token_add[0] == step1_token_add[0] + step1_token_reward[1],
                    " get balance prv something wrong")
        INFO("Balance token : " + str(step4_token_add[0]))

        STEP(5, "retry withdraw reward again")
        step5_result = self.fullnode_tx.withdrawReward(self.test_data["s0_addr1"][0], self.test_data["s0_addr1"][1],
                                                       step1_token_reward[0])
        assert_true(step5_result[0] == "Can not send tx", "withdraw reward must be failed")

        STEP(6, "Check balance after withdraw token again")
        step6_prv_add = self.fullnode_tx.getBalance(self.test_data["s0_addr1"][0])
        INFO("Balance PRV : " + str(step6_prv_add))
        assert_true(step6_prv_add == step1_prv_add, " get balance prv something wrong")

        step6_token_reward = self.fullnode_tx.check_reward_specific_token(self.test_data["s0_addr1"][1],
                                                                          step1_token_reward[0])
        assert_true(step6_token_reward[0] == "token not exist", "token doesn't pay correct yet ")
        INFO("Token pay out")

    @pytest.mark.run
    def test_99_cleanup(self):
        print("""
            CLEAN UP
            """)
        self.fullnode_ws.closeConnection()
