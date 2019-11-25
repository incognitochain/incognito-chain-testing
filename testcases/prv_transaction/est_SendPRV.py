"""
Created Oct 11 2019
@Author: Khanh Le
"""
# pylint: disable = too-many-public-methods
import re
import unittest

# from Automation.pages.sign_up.base_sign_up import BaseSignUp
# from Automation.util.utils import Utils
# from Automation.util.mail_checking import MailChecking
# from Automation.pages.menu.main_menu import MainMenu
# from Automation.pages.login.base_login import BaseLogin
# from Automation.pages.user_profile.base_user_profile import BaseUserProfile
# from Automation.workflow.sign_up import SignUp
import pytest

import topology.NodeList as NodeList
# from ddt import ddt, data
from libs.AutoLog import INFO, STEP, assert_true
from libs.Transaction import Transaction
from libs.WebSocket import WebSocket


class test_sendPRV(unittest.TestCase):
    """
    Test case: Send PRV
    """

    test_data = {
        'address1_privatekey':
            "112t8rnX5E2Mkqywuid4r4Nb2XTeLu3NJda43cuUM1ck2brpHrufi4Vi42EGybFhzfmouNbej81YJVoWewJqbR4rPhq2H945BXCLS2aDLBTA",
        'address1_payment':
            "12RxERBySmquLtM1R1Dk2s7J4LyPxqHxcZ956kupQX3FPhVo2KtoUYJWKet2nWqWqSh3asWmgGTYsvz3jX73HqD8Jr2LwhjhJfpG756",
        'address2_payment':
            "12RyJTSL2G8KvjN7SUFuiS9Ek4pvFFze3EMMic31fmXVw8McwYzpKPpxeW6TLsNo1UoPhCHKV3GDRLQwdLF41PED3LQNCLsGNKzmCE5",
        'address2_privatekey':
            "112t8rnXVMJJZzfF1naXvfE9nkTKwUwFWFeh8cfEyViG1vpA8A9khJk3mhyB1hDuJ4RbreDTsZpgJK4YcSxdEpXJKMEd8Vmp5UqKWwBcYzxv",
        'address3_payment':
            "12S11S8hSMBci33Qbq62Fr9sbSfMpeYrPivAwHQt6VVm4mUxDsvLbCWTijZ5h9w58gyTzo8QLFztYNxxR5wx5PSPRx2Z81CWDicg7qx",
        'address3_privatekey':
            "112t8rnYzQ1WsqSEPtRxMbxqEyn5QtACqN1oCa2SRQc3tY6unSeh4SwUqSuTKu6pi2ZDx6JP8JV2Zd6wQUvfSZQHSZK9MXVxTwxTzvgkp6Vw",
        'prv_amount': 1 * 1000000000

    }

    shard03 = Transaction(NodeList.shard0[3]['ip'], NodeList.shard0[3]['rpc'])
    shard03ws = WebSocket(NodeList.shard0[3]['ip'], NodeList.shard0[3]['ws'])
    shard13 = Transaction(NodeList.shard1[4]['ip'], NodeList.shard1[4]['rpc'])
    shard13ws = WebSocket(NodeList.shard1[4]['ip'], NodeList.shard1[4]['ws'])

    @pytest.mark.run
    def test_2sendPRV_privacy_1shard(self):
        """
        Verify send PRV to another address 1Shard successfully
        """
        print("\n")
        STEP(1, "get address1 and address2 balance before sending")
        balance1b = self.shard03.getBalance(self.test_data["address1_privatekey"])
        INFO("addr1_balance: " + str(balance1b))
        assert balance1b != "Invalid parameters"

        balance2b = self.shard03.getBalance(self.test_data["address2_privatekey"])
        INFO("addr2_balance: " + str(balance2b))
        assert balance2b != "Invalid parameters"

        STEP(2, "from address1 send prv to address2")
        tx_id = self.shard03.sendTransaction(self.test_data["address1_privatekey"],
                                             self.test_data["address2_payment"], self.test_data["prv_amount"])
        INFO("transaction id: " + tx_id[0])
        assert tx_id[0] != 'Can not create tx'

        STEP(3, "subcribe transaction")
        self.shard03ws.createConnection()
        ws_res = self.shard03ws.subcribePendingTransaction(tx_id[0])

        STEP(4, "check address1 balance")
        balance1a = self.shard03.getBalance(self.test_data["address1_privatekey"])
        INFO("addr1_balance: " + str(balance1a))
        # Balance after = balance before - amount - fee
        assert balance1a == balance1b - self.test_data["prv_amount"] - ws_res[2]

        STEP(5, "check address2 balance")
        balance2a = self.shard03.getBalance(self.test_data["address2_privatekey"])
        INFO("addr2_balance: " + str(balance2a))
        # Balance after = balance before + amount
        assert balance2a == balance2b + self.test_data["prv_amount"]

    @pytest.mark.run
    def test_3sendPRV_privacy_Xshard(self):
        """
        Verify send PRV to another address Xshard successfully
        """
        print("\n")
        STEP(1, "Get address1 balance")
        step1_result = self.shard03.getBalance(self.test_data["address1_privatekey"])
        INFO("addr1_balance: " + str(step1_result))
        assert step1_result != "Invalid parameters"

        STEP(2, "Get address3 balance")
        step2_result = self.shard13.getBalance(self.test_data["address3_privatekey"])
        INFO("addr3_balance: " + str(step2_result))
        assert step2_result != "Invalid parameters"

        STEP(3, "From address1 send prv to address3")
        step3_result = self.shard03.sendTransaction(self.test_data["address1_privatekey"],
                                                    self.test_data["address3_payment"], self.test_data["prv_amount"])
        INFO("Transaction ID: " + step3_result[0])
        assert step3_result[0] != 'Can not create tx'

        STEP(4, "Subcribe transaction")
        self.shard03ws.createConnection()
        ws_res4 = self.shard03ws.subcribePendingTransaction(step3_result[0])

        STEP(5, "Subcribe cross transaction by privatekey")
        self.shard13ws.createConnection()
        ws_res5 = self.shard13ws.subcribeCrossOutputCoinByPrivatekey(self.test_data["address3_privatekey"])

        STEP(6, "Check address1 balance")
        step4_result = self.shard03.getBalance(self.test_data["address1_privatekey"])
        INFO("addr1_balance: " + str(step4_result))
        assert step4_result == step1_result - self.test_data["prv_amount"] - ws_res4[2]

        STEP(7, "Check address3 balance")
        step5_result = self.shard13.getBalance(self.test_data["address3_privatekey"])
        INFO("Addr3_balance: " + str(step5_result))
        assert step5_result == step2_result + self.test_data["prv_amount"]

    @pytest.mark.run
    def test_4sendPRV_Xshard_insufficient_fund(self):
        """
        Verify send PRV to another address:
        - Not enough coin (insufficient fund)
        - Wrong input transaction
        """
        print("\n")
        STEP(1, "Get address1 balance")
        step1_result = self.shard03.getBalance(self.test_data["address1_privatekey"])
        INFO("addr1_balance: " + str(step1_result))
        assert step1_result != "Invalid parameters"

        STEP(2, "Get address3 balance")
        step2_result = self.shard13.getBalance(self.test_data["address3_privatekey"])
        INFO("addr3_balance: " + str(step2_result))
        assert step2_result != "Invalid parameters"

        STEP(3, "From address3 send prv to address1 - Not enough coin")
        # send current balance + 10
        step3_result = self.shard13.sendTransaction(self.test_data["address3_privatekey"],
                                                    self.test_data["address1_payment"], step2_result + 10)
        INFO("Expecting: " + step3_result[0])
        assert_true(step3_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'Not enough coin', step3_result[1]), "something went so wrong")

        # breakpoint()

        STEP(4, "From address3 send prv to address1 - Wrong input transaction")
        # send current balance (lacking of fee)
        step4_result = self.shard13.sendTransaction(self.test_data["address3_privatekey"],
                                                    self.test_data["address1_payment"], step2_result)
        INFO("Expecting: " + step4_result[0])
        assert_true(step4_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'Wrong input transaction', step4_result[1]), "something went so wrong")
        estimated_fee = re.search(r'fee=(\d+)\n', step4_result[1])
        estimated_fee = estimated_fee.group(1)
        INFO("Estimated fee: " + estimated_fee)

        # breakpoint()

        STEP(5, "From address3 send prv to address1 - success")
        # send current balance - fee
        step5_result = self.shard13.sendTransaction(self.test_data["address3_privatekey"],
                                                    self.test_data["address1_payment"],
                                                    step2_result - int(estimated_fee))
        assert_true(step5_result[0] != 'Can not create tx', "something went wrong, this tx must succeeded")
        INFO("TxID: " + step5_result[0])

        STEP(6, "Subcribe transaction")
        self.shard13ws.createConnection()
        ws_res6 = self.shard13ws.subcribePendingTransaction(step5_result[0])

        STEP(7, "Subcribe cross transaction by privatekey")
        self.shard03ws.createConnection()
        ws_res7 = self.shard03ws.subcribeCrossOutputCoinByPrivatekey(self.test_data["address1_privatekey"])

        STEP(8, "Check address1 balance")
        step8_result = self.shard03.getBalance(self.test_data["address1_privatekey"])
        INFO("addr1_balance: " + str(step8_result))
        assert step8_result == step1_result + step2_result - ws_res6[2]

        STEP(7, "Check address3 balance")
        step7_result = self.shard13.getBalance(self.test_data["address3_privatekey"])
        INFO("Addr3_balance: " + str(step7_result))
        assert step7_result == 0

    @pytest.mark.run
    def test_cleanup(self):
        """
        CLEAN UP
        """
        self.shard03ws.closeConnection()
        self.shard13ws.closeConnection()
