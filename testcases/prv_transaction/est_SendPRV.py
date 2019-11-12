"""
Created Oct 11 2019
@Author: Khanh Le
"""
# pylint: disable = too-many-public-methods
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
from libs.Transaction import Transaction
from libs.WebSocket import WebSocket
# from ddt import ddt, data
from libs.AutoLog import INFO, STEP, WAIT


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
            "12RtmpqwyzghGQJHXGRhXnNqs7SDhx1wXemgAZNC2xePj9DNpxcTZfpwCeNoBvvyxNU8n2ChVijPhSsNhGCDmFmiwXSjQEMSef4cMFG",
        'address3_privatekey':
            "112t8rnXJgKz6wxuvo6s8aFHFN16j9fvh7y3ZLdrQpN1zRZcubmekm7WHc8KjQS3EWeGBCq8L7qQTuVm3QtnEX66WFHP5e7v6fQunJRJZx2c",
        'prv_amount': 1 * 1000000000

    }

    shard03 = Transaction(NodeList.shard0[3]['ip'], NodeList.shard0[3]['rpc'])
    shard03ws = WebSocket(NodeList.shard0[3]['ip'], NodeList.shard0[3]['ws'])

    @pytest.mark.run
    def test_2sendPRV_privacy_1shard(self):
        """
        Verify send PRV to another address
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
        INFO("transaction id: " + tx_id)
        assert tx_id != 'Can not create tx'

        STEP(3, "subcribe transaction")
        self.shard03ws.createConnection()
        ws_res = self.shard03ws.subcribePendingTransaction(tx_id)

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
    def est_3sendPRV_privacy_Xshard(self):
        """
        Verify send PRV to another address
        """
        print("\n")
        INFO("1. get address1 balance")
        step1_result = self.get_balance(self.test_data["shard0"], self.test_data["address1_privatekey"])
        print("addr1_balance: " + str(step1_result))
        assert step1_result != "Invalid parameters"

        INFO("2. get address3 balance")
        step2_result = self.get_balance(self.test_data["shard4"], self.test_data["address3_privatekey"])
        print("addr3_balance: " + str(step2_result))
        assert step2_result != "Invalid parameters"

        INFO("3. from address1 send prv to address3")
        step3_result = self.send_trx(self.test_data["shard0"], self.test_data["address1_privatekey"],
                                     self.test_data["address3_payment"], self.test_data["prv_amount"])
        print("transaction id: " + step3_result)
        assert step3_result != 'Can not create tx'

        INFO("3.1 subcribe transaction")
        step31 = WebSocket(self.test_data["ws0"])
        step31.createConnection()
        step31_result = step31.subcribePendingTransaction(step3_result)
        step31.closeConnection()

        INFO("3.2 subcribe cross transaction")
        step32 = WebSocket(self.test_data["ws4"])
        step32.createConnection()
        step32_result = step32.subcribeCrossOutputCoinByPrivatekey(self.test_data["address3_privatekey"])
        step32.closeConnection()

        INFO("4. check address1 balance")
        step4_result = self.get_balance(self.test_data["shard0"], self.test_data["address1_privatekey"])
        print("addr1_balance: " + str(step4_result))
        assert step4_result == step1_result - self.test_data["prv_amount"]

        INFO("5. check address3 balance")
        step5_result = self.get_balance(self.test_data["shard4"], self.test_data["address3_privatekey"])
        print("addr3_balance: " + str(step5_result))
        assert step5_result == step2_result + self.test_data["prv_amount"]

    @pytest.mark.run
    def test_cleanup(self):
        """
        CLEAN UP
        """
        self.shard03ws.closeConnection()
