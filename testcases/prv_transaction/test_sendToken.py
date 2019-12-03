"""
Created Nov 25 2019
@Author: Khanh Le
"""

import re
import unittest
from time import strftime

import pytest

import topology.NodeList as NodeList
from libs.AutoLog import INFO, STEP, assert_true, WAIT
from libs.DecentralizedExchange import DEX
from libs.Transaction import Transaction
from libs.WebSocket import WebSocket


class test_sendToken(unittest.TestCase):
    """
    Test case: Send Token
    """

    test_data = {
        's0_addr1': [
            "112t8rnXVMJJZzfF1naXvfE9nkTKwUwFWFeh8cfEyViG1vpA8A9khJk3mhyB1hDuJ4RbreDTsZpgJK4YcSxdEpXJKMEd8Vmp5UqKWwBcYzxv",
            "12RyJTSL2G8KvjN7SUFuiS9Ek4pvFFze3EMMic31fmXVw8McwYzpKPpxeW6TLsNo1UoPhCHKV3GDRLQwdLF41PED3LQNCLsGNKzmCE5"
        ],
        's0_addr2': [
            "112t8rnakdKxvk7VMKUB9qmsPY4czwnP24b82BnepcxHLX6kJ1dYQsR8d6xNTzwC9nEhJdocr9u19NAr4iSYXCeTBRu3YET8iADMAP3szdfw",
            "12RxnTs5KqyQUzGF4R2w68j3biJD29iDsFiVgC4GRy5X85anUrq1rg8P4aUyDRuS5desg9WANRptifcissMBPETyMeBE8KEh7LmQ6m7",
        ],
        's1_addr3': [
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

    shard03dex = DEX(NodeList.shard0[3]['ip'], NodeList.shard0[3]['rpc'])
    # fullnode_trx = Transaction(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['rpc'])
    shard03 = Transaction(NodeList.shard0[3]['ip'], NodeList.shard0[3]['rpc'])
    shard03ws = WebSocket(NodeList.shard0[3]['ip'], NodeList.shard0[3]['ws'])
    shard13 = Transaction(NodeList.shard1[3]['ip'], NodeList.shard1[3]['rpc'])
    shard13ws = WebSocket(NodeList.shard1[3]['ip'], NodeList.shard1[3]['ws'])
    shard23 = Transaction(NodeList.shard2[3]['ip'], NodeList.shard2[3]['rpc'])
    shard23ws = WebSocket(NodeList.shard2[3]['ip'], NodeList.shard2[3]['ws'])

    print("\nENV: " + str(NodeList.shard0[3]))
    print("ENV: " + str(NodeList.shard1[3]))
    print("ENV: " + str(NodeList.shard2[3]))

    token_id = ""

    @pytest.mark.run
    def test_01_init_pToken(self):
        print('''
        Init a pToken
        Contribute pToken-PRV to pDex (mapping rate) => use pToken to pay fee
        ''')

        STEP(1, "Initial new token")
        token_symbol = strftime("%H%M%S")
        s1rs = self.shard03.init_customToken(self.test_data['s0_addr1'][0], self.test_data['s0_addr1'][1], token_symbol,
                                             self.test_data['init_tokenAmount'])
        assert_true(len(s1rs[0]) == 64 & len(s1rs[1]) == 64, "Failed to init new token", "Success to init new token")
        test_sendToken.token_id = s1rs[1]
        INFO("token id: %s" % s1rs[1])

        STEP(2, "subcribe transaction")
        self.shard03ws.createConnection()
        self.shard03ws.subcribePendingTransaction(s1rs[0])

        STEP(3, "Get custom token balance")
        token_balance, _ = self.shard03.get_customTokenBalance(self.test_data['s0_addr1'][0], s1rs[1])
        INFO("Token balance: %s" % str(token_balance))

        STEP(4, "contribute token & PRV")
        # Contribute TOKEN:
        contribute_token_tx = self.shard03dex.contribute_token(self.test_data['s0_addr1'][0],
                                                               self.test_data['s0_addr1'][1], s1rs[1],
                                                               10000000000000, "10token_1prv")
        INFO("Contribute " + s1rs[1] + " Success, TxID: " + contribute_token_tx)
        INFO("Subscribe contribution transaction")
        self.shard03ws.subcribePendingTransaction(contribute_token_tx)
        # Contribute PRV:
        contribute_prv_tx = self.shard03dex.contribute_prv(self.test_data['s0_addr1'][0],
                                                           self.test_data['s0_addr1'][1],
                                                           10000000000000, "10token_1prv")
        INFO("Contribute PRV Success, TxID: " + contribute_prv_tx)
        INFO("Subscribe contribution transaction")
        self.shard03ws.subcribePendingTransaction(contribute_prv_tx)

        STEP(5, "Verify Contribution")
        rate = []
        for _ in range(0, 10):
            WAIT(10)
            rate = self.shard03dex.get_latestRate("0000000000000000000000000000000000000000000000000000000000000004",
                                                  s1rs[1])
            if rate == [10000000000000, 10000000000000]:
                break
        INFO("rate prv vs token" + str(rate))
        assert_true(rate == [10000000000000, 10000000000000], "Contribution Failed")

    @pytest.mark.run
    def test_02_sendToken_privacy_1shard(self):
        print('''
        Verify send Token to another address 1Shard successfully
        Fee: PRV (auto estimate)
        Fee: PRV (fixed number * transaction size(KB))
        ''')

        STEP(1, "get address1 and address2 balance before sending")
        balance1b, _ = self.shard03.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_balance: " + str(balance1b))
        assert balance1b != "Invalid parameters"

        balance2b, _ = self.shard03.get_customTokenBalance(self.test_data["s0_addr2"][0], test_sendToken.token_id)
        INFO("addr2_balance: " + str(balance2b))
        assert balance2b != "Invalid parameters"

        STEP(2, "from address1 send Token to address2 - Fee PRV auto estimated")
        estimate_transaction_size = self.shard03.estimatefee_token(self.test_data["s0_addr1"][0],
                                                                   self.test_data["s0_addr2"][1],
                                                                   test_sendToken.token_id,
                                                                   self.test_data["token_amount"])
        INFO("estimate transaction size before send: " + str(estimate_transaction_size[0]) + "KB")
        tx_id = self.shard03.send_customTokenTransaction(self.test_data["s0_addr1"][0],
                                                         self.test_data["s0_addr2"][1], test_sendToken.token_id,
                                                         self.test_data["token_amount"])
        INFO("transaction id: " + tx_id[0])
        assert tx_id[0] != 'Can not create tx'

        STEP(3, "subcribe transaction")
        self.shard03ws.createConnection()
        ws_res = self.shard03ws.subcribePendingTransaction(tx_id[0])

        STEP(4, "check address1 & 2 balance after sent")
        balance1a, _ = self.shard03.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_balance: " + str(balance1a))
        # Balance after = balance before - amount
        assert balance1a == balance1b - self.test_data["token_amount"]

        balance2a, _ = self.shard03.get_customTokenBalance(self.test_data["s0_addr2"][0], test_sendToken.token_id)
        INFO("addr2_balance: " + str(balance2a))
        # Balance after = balance before + amount
        assert balance2a == balance2b + self.test_data["token_amount"]

        STEP(5, "from address1 send Token to address2 - Fee PRV fixed")
        estimate_transaction_size = self.shard03.estimatefee_token(self.test_data["s0_addr1"][0],
                                                                   self.test_data["s0_addr2"][1],
                                                                   test_sendToken.token_id,
                                                                   self.test_data["token_amount"])
        INFO("estimate transaction size before send: " + str(estimate_transaction_size[0]) + "KB")
        tx_id = self.shard03.send_customTokenTransaction(self.test_data["s0_addr1"][0],
                                                         self.test_data["s0_addr2"][1], test_sendToken.token_id,
                                                         self.test_data["token_amount"], 100)
        INFO("transaction id: " + tx_id[0])
        assert tx_id[0] != 'Can not create tx'

        STEP(6, "subcribe transaction")
        self.shard03ws.createConnection()
        ws_res = self.shard03ws.subcribePendingTransaction(tx_id[0])
        assert_true(ws_res[2] % 100 == 0, "tx_fee is not a multiple of 100",
                    "tx_fee is %d * %d" % (100, ws_res[2] / 100))

        STEP(7, "check address1 & 2 balance after sent")
        balance1c, _ = self.shard03.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_balance: " + str(balance1c))
        # Balance after = balance before - amount
        assert balance1c == balance1a - self.test_data["token_amount"]

        balance2c, _ = self.shard03.get_customTokenBalance(self.test_data["s0_addr2"][0], test_sendToken.token_id)
        INFO("addr2_balance: " + str(balance2c))
        # Balance after = balance before + amount
        assert balance2c == balance2a + self.test_data["token_amount"]

    @pytest.mark.run
    def test_03_sendToken_privacy_Xshard(self):
        print("""
        Verify send Token to another address Xshard successfully
        Fee: PRV (fixed * transaction size KB)
        Fee: pToken (fixed)
        """)

        STEP(1, "get address1 and address3 balance before sending")
        balance1b, _ = self.shard03.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_balance: " + str(balance1b))
        assert balance1b != "Invalid parameters"

        balance3b, _ = self.shard13.get_customTokenBalance(self.test_data["s1_addr3"][0], test_sendToken.token_id)
        INFO("addr3_balance: " + str(balance3b))
        assert balance3b != "Invalid parameters"

        STEP(2, "from address1 send prv to address3 - tx_fee PRV fixed 1PRV")
        estimate_transaction_size = self.shard03.estimatefee_token(self.test_data["s0_addr1"][0],
                                                                   self.test_data["s1_addr3"][1],
                                                                   test_sendToken.token_id,
                                                                   self.test_data["token_amount"])
        INFO("estimate transaction size before send: " + str(estimate_transaction_size[0]) + "KB")
        tx_id = self.shard03.send_customTokenTransaction(self.test_data["s0_addr1"][0],
                                                         self.test_data["s1_addr3"][1], test_sendToken.token_id,
                                                         self.test_data["token_amount"], 1000000000)
        INFO("transaction id: " + tx_id[0])
        assert tx_id[0] != 'Can not create tx'

        STEP(3, "subcribe transaction")
        self.shard03ws.createConnection()
        ws_res = self.shard03ws.subcribePendingTransaction(tx_id[0])
        assert_true(ws_res[2] % 1000000000 == 0, "Invalid tx_fee",
                    "Transaction fee is %d * %d" % (1000000000, ws_res[2] / 1000000000))
        self.shard13ws.createConnection()
        ws_res5 = self.shard13ws.subcribeCrossCustomTokenPrivacyByPrivatekey(self.test_data["s1_addr3"][0])

        STEP(4, "check address1 & 3 balance")
        balance1a, _ = self.shard03.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_balance: " + str(balance1a))
        # Balance after = balance before - amount
        assert balance1a == balance1b - self.test_data["token_amount"]

        balance3a, _ = self.shard13.get_customTokenBalance(self.test_data["s1_addr3"][0], test_sendToken.token_id)
        INFO("addr3_balance: " + str(balance3a))
        # Balance after = balance before + amount
        assert balance3a == balance3b + self.test_data["token_amount"]

        STEP(5, "from address1 send prv to address3 - tx_fee Token fixed 100")
        estimate_transaction_size = self.shard03.estimatefee_token(self.test_data["s0_addr1"][0],
                                                                   self.test_data["s1_addr3"][1],
                                                                   test_sendToken.token_id,
                                                                   self.test_data["token_amount"])
        INFO("estimate transaction size before send: " + str(estimate_transaction_size[0]) + "KB")
        tx_id = self.shard03.send_customTokenTransaction(self.test_data["s0_addr1"][0],
                                                         self.test_data["s1_addr3"][1], test_sendToken.token_id,
                                                         self.test_data["token_amount"], 0, 100)
        INFO("transaction id: " + tx_id[0])
        assert tx_id[0] != 'Can not create tx'

        STEP(6, "subcribe transaction")
        self.shard03ws.createConnection()
        ws_res = self.shard03ws.subcribePendingTransaction(tx_id[0])
        # assert_true(ws_res[2] % 1000000000 == 0, "Invalid tx_fee",
        #             "Transaction fee is %d * %d" % (1000000000, ws_res[2] / 1000000000))
        self.shard13ws.createConnection()
        ws_res5 = self.shard13ws.subcribeCrossCustomTokenPrivacyByPrivatekey(self.test_data["s1_addr3"][0])

        STEP(7, "check address1 & 3 balance")
        balance1c, _ = self.shard03.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_balance: " + str(balance1c))
        # Balance after = balance before - amount
        assert balance1c == balance1a - self.test_data["token_amount"] - 100

        balance3c, _ = self.shard13.get_customTokenBalance(self.test_data["s1_addr3"][0], test_sendToken.token_id)
        INFO("addr3_balance: " + str(balance3c))
        # Balance after = balance before + amount
        assert balance3c == balance3a + self.test_data["token_amount"]

    @pytest.mark.run
    def est_04_sendToken_privacy_Xshard(self):
        print("""
            Verify send Token to another address Xshard successfully
            Fee: PRV (fixed * transaction size KB)
            Fee: pToken (fixed)
            """)

        STEP(1, "get address1 and address4 balance before sending")
        balance1b, _ = self.shard03.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_balance: " + str(balance1b))
        assert balance1b != "Invalid parameters"

        balance4b, _ = self.shard23.get_customTokenBalance(self.test_data["s2_addr4"][0], test_sendToken.token_id)
        INFO("addr4_balance: " + str(balance4b))
        assert balance4b != "Invalid parameters"

        STEP(2, "from address1 send prv to address4")
        tx_id = self.shard03.send_customTokenTransaction(self.test_data["s0_addr1"][0],
                                                         self.test_data["s2_addr4"][1], test_sendToken.token_id,
                                                         self.test_data["token_amount"])
        INFO("transaction id: " + tx_id[0])
        assert tx_id[0] != 'Can not create tx'

        STEP(3, "subcribe transaction")
        self.shard03ws.createConnection()
        ws_res = self.shard03ws.subcribePendingTransaction(tx_id[0])
        self.shard23ws.createConnection()
        ws_res5 = self.shard23ws.subcribeCrossCustomTokenPrivacyByPrivatekey(self.test_data["s2_addr4"][0])

        STEP(4, "check address1 balance")
        balance1a, _ = self.shard03.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_balance: " + str(balance1a))
        # Balance after = balance before - amount
        assert balance1a == balance1b - self.test_data["token_amount"]

        STEP(5, "check address4 balance")
        balance4a = 0
        for _ in range(0, 12):
            balance4a, _ = self.shard23.get_customTokenBalance(self.test_data["s2_addr4"][0], test_sendToken.token_id)
            if balance4a > balance4b:
                break
            WAIT(10)

        INFO("addr4_balance: " + str(balance4a))
        # Balance after = balance before + amount
        assert balance4a == balance4b + self.test_data["token_amount"]

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
    def est_06_burn_pToken(self):
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
        assert_true(token_balance == 0, "Token Balance != 0", "Burning success")

    @pytest.mark.run
    def test_cleanup(self):
        """
        CLEAN UP
        """
        self.shard03ws.closeConnection()
        self.shard13ws.closeConnection()
