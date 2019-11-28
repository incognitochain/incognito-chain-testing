"""
Created Nov 25 2019
@Author: Khanh Le
"""

import re
import unittest
from time import strftime

import pytest

import topology.NodeList as NodeList
from libs.AutoLog import INFO, STEP, assert_true
from libs.Transaction import Transaction
from libs.WebSocket import WebSocket


class test_sendToken(unittest.TestCase):
    """
    Test case: Send Token
    """

    test_data = {
        's0_addr1': [
            "112t8rnX5E2Mkqywuid4r4Nb2XTeLu3NJda43cuUM1ck2brpHrufi4Vi42EGybFhzfmouNbej81YJVoWewJqbR4rPhq2H945BXCLS2aDLBTA",
            "12RxERBySmquLtM1R1Dk2s7J4LyPxqHxcZ956kupQX3FPhVo2KtoUYJWKet2nWqWqSh3asWmgGTYsvz3jX73HqD8Jr2LwhjhJfpG756"
        ],
        's0_addr2': [
            "112t8rnakdKxvk7VMKUB9qmsPY4czwnP24b82BnepcxHLX6kJ1dYQsR8d6xNTzwC9nEhJdocr9u19NAr4iSYXCeTBRu3YET8iADMAP3szdfw",
            "12RxnTs5KqyQUzGF4R2w68j3biJD29iDsFiVgC4GRy5X85anUrq1rg8P4aUyDRuS5desg9WANRptifcissMBPETyMeBE8KEh7LmQ6m7",
        ],
        's1_addr3_': [
            "112t8rnXHSFhmnyduga9tE5vh5CpTX1Ydu8murPuyQi3FYwxESW6eCPVG7vy62vjeRuM8PDfDDLf6wfXekJM5QbdHAryj2XcN4JAZq5y1Tri",
            "12Rqdqkv3w4uyfSTYTkoegWSHSoex75QLuHiS4C1MzwMztieSPai59mprYovV6WC963SP4p9sH5uS3eFYomefPrvvMKhuafER6YV3Kv",
        ],
        's2_addr4': [
            "112t8rnZ5UZouZU9nFmYLfpHUp8NrvQkGLPD564mjzNDM8rMp9nc9sXZ6CFxCGEMuvHQpYN7af6KCPJnq9MfEnXQfntbM8hpy9LW8p4qzPxS",
            "12Rw9oesEgd8t5NGrfqxtWTCzh1eDif55miqZ1kFzj5zeQ6UQnNB9JXRn5Vc5QVbBaiFhoYdYPnQZ5tWwcBpse5EJXM3Av6qEV2wspv",
        ],
        'token_amount': 0.123456789 * 1000000000,
        'init_tokenAmount': 1000000 * 1000000000,
        'burning_addr': "15pABFiJVeh9D5uiQEhQX4SVibGGbdAVipQxBdxkmDqAJaoG1EdFKHBrNfs"
    }

    shard03 = Transaction(NodeList.shard0[3]['ip'], NodeList.shard0[3]['rpc'])
    shard03ws = WebSocket(NodeList.shard0[3]['ip'], NodeList.shard0[3]['ws'])
    shard13 = Transaction(NodeList.shard1[3]['ip'], NodeList.shard1[3]['rpc'])
    shard13ws = WebSocket(NodeList.shard1[3]['ip'], NodeList.shard1[3]['ws'])

    token_id = ""

    @pytest.mark.run
    def test_01_init_pToken(self):
        '''
        Init a pToken
        Contribute pToken-PRV to pDex (mapping rate) => use pToken to pay fee
        '''
        print("\n")
        STEP(1, "Initial new token")
        token_symbol = strftime("%H%M%S")
        s1rs = self.shard03.init_customToken(self.test_data['s0_addr1'][0], self.test_data['s0_addr1'][1], token_symbol,
                                             self.test_data['init_tokenAmount'])
        assert_true(len(s1rs[0]) == 64 & len(s1rs[1]) == 64, "Failed to init new token", "Success to init new token")
        test_sendToken.token_id = s1rs[1]
        INFO("token id: %s" % test_sendToken.token_id)

        STEP(2, "subcribe transaction")
        self.shard03ws.createConnection()
        self.shard03ws.subcribePendingTransaction(s1rs[0])

        STEP(3, "Get custom token balance")
        token_balance, _ = self.shard03.get_customTokenBalance(self.test_data['s0_addr1'][0], s1rs[1])
        INFO("Token balance: %s" % str(token_balance))

    @pytest.mark.run
    def test_02_sendToken_privacy_1shard(self):
        """
        Verify send Token to another address 1Shard successfully
        Fee: PRV (auto estimate)
        Fee: PRV (fixed number * transaction size(KB))
        """
        print("\n")
        STEP(1, "get address1 and address2 balance before sending")
        balance1b, _ = self.shard03.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_balance: " + str(balance1b))
        assert balance1b != "Invalid parameters"

        balance2b, _ = self.shard03.get_customTokenBalance(self.test_data["s0_addr2"][0], test_sendToken.token_id)
        INFO("addr2_balance: " + str(balance2b))
        assert balance2b != "Invalid parameters"

        STEP(2, "from address1 send prv to address2")
        tx_id = self.shard03.send_customTokenTransaction(self.test_data["s0_addr1"][0],
                                                         self.test_data["s0_addr2"][1], test_sendToken.token_id,
                                                         self.test_data["token_amount"])
        INFO("transaction id: " + tx_id[0])
        assert tx_id[0] != 'Can not create tx'

        STEP(3, "subcribe transaction")
        self.shard03ws.createConnection()
        ws_res = self.shard03ws.subcribePendingTransaction(tx_id[0])

        STEP(4, "check address1 balance")
        balance1a, _ = self.shard03.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_balance: " + str(balance1a))
        # Balance after = balance before - amount
        assert balance1a == balance1b - self.test_data["token_amount"]

        STEP(5, "check address2 balance")
        balance2a, _ = self.shard03.get_customTokenBalance(self.test_data["s0_addr2"][0], test_sendToken.token_id)
        INFO("addr2_balance: " + str(balance2a))
        # Balance after = balance before + amount
        assert balance2a == balance2b + self.test_data["token_amount"]

    @pytest.mark.run
    def est_03_sendToken_privacy_Xshard(self):
        """
        Verify send Token to another address Xshard successfully
        Fee: PRV (fixed * transaction size KB)
        Fee: pToken (fixed)
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
    def est_04_sendToken_Xshard_insufficient_fund(self):
        """
        Verify send Token to another address:
        - Not enough coin (insufficient fund)
        - Wrong input transaction
        - Valid transaction
        """
        print("\n")
        STEP(1, "Get address1 balance")
        step1_result = self.shard03.getBalance(self.test_data["address1_privatekey"])
        INFO("addr1_balance: " + str(step1_result))
        assert step1_result != "Invalid parameters"

        STEP(2, "Get address3 balance")
        step2_result = self.shard13.getBalance(self.test_data["address3_privatekey"])
        INFO("addr3_balance: " + str(step2_result))
        assert_true(step2_result != 0, "addr3_balance = 0, stop this testcase")

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
    def est_05_sendToken_privacy_Xshard(self):
        """
        Verify send Token Xshard, from Shard_n+1 Shard_n+2 to Shard_n at the same time
        Fee: PRV (fixed * transaction size KB)
        Fee: pToken (fixed)
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
    def test_06_burn_pToken(self):
        print("\n")
        STEP(0, "check address1 balance")
        balance1b, _ = self.shard03.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_balance: " + str(balance1b))

        STEP(1, "Burn token")
        txid, shard = self.shard03.send_customTokenTransaction(self.test_data['s0_addr1'][0],
                                                               self.test_data['burning_addr'],
                                                               test_sendToken.token_id, balance1b)
        assert_true(len(txid) == 64, "Burning not success")

        STEP(2, "subcribe transaction")
        self.shard03ws.createConnection()
        self.shard03ws.subcribePendingTransaction(txid)

        STEP(3, "Get custom token balance")
        token_balance, _ = self.shard03.get_customTokenBalance(self.test_data['s0_addr1'][0], test_sendToken.token_id)
        INFO("Token balance after burn: " + str(token_balance))

    @pytest.mark.run
    def test_cleanup(self):
        """
        CLEAN UP
        """
        self.shard03ws.closeConnection()
        self.shard13ws.closeConnection()
