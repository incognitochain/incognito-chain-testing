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
    test_data_khanh = {
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

    test_data = {
        's0_addr1': [
            "112t8rnX3VTd3MTWMpfbYP8HGY4ToAaLjrmUYzfjJBrAcb8iPLkNqvVDXWrLNiFV5yb2NBpR3FDZj3VW8GcLUwRdQ61hPMWP3YrREZAZ1UbH",
            "12S6R8HfTyL74bggg47LX88RSvBPaMPBMEMoo6yx9WQ4EgLiYERXXcE2Mv2HrCsFuKhBsTfrYMeH82Bus5MHQGt3xHwoxX4v2qM5jRE"
        ],
        's0_addr2': [
            "112t8rndq3phbUG44goJZyYSy9Qvm6nEJr8N672tD8E5VyzqPuJVQBb1wcHQSrQibsbBLkrGfQ14fzw8iNoAtu13gqKjktffPrw9ZxcoNsbk",
            "12Rq6XDGQVYcxop7krJUJZCgsWCCU2UpgDDWdhjtxfeuWbcuksHNdjDkBVBz5t98q9UKjTS77Y6BZDeVeKuvw7QZfMBT7wb3M3YWS4k",
        ],
        's1_addr3': [
            "112t8rngNKpZHv6WsKqaYqKPi8JvfEVY9oqob3QiSKmbHbfDrDFXZZtmqLAacnmfqTJKKR9P2UJ1kYvkmdHAHU4zPRHpv38kHRRjLtHNv4yN",
            "12S2NxoLzvEsKBpvL6g3gjECvErpxVQoAg7VpnhojLXa6S3TchxbwM5aHQYJoT3K1nkq7C7VjAwgVwn2De3uLzD1J8VkmWe3cDRLPef",
        ],
        's2_addr4': [
            "112t8rnendREF3cg2vuRC248dFymXonwBC7TMmfppXEzz9wFziktHj8NhsGebcRmtquyg2zbytkecPMSHFBVcw4yJewv7E3J6cHgDzYiHoJj",
            "12S4YzSA6hC12zuMF8L2rC7Tks1TtcfDUSWjcPeKeyT1ApV1KXqQnmtpCNEYbta88GrjhPiS6yFfuyfViDW5cmooqsZ5tvC8SRJZdCF",
        ],
        'token_amount': 0.12345 * 100000,
        'init_tokenAmount': 1000000 * 1000000000,
        'prv_amount': 10,
        'token_fee': 20000,
        'burning_addr': "15pABFiJVeh9D5uiQEhQX4SVibGGbdAVipQxBdxkmDqAJaoG1EdFKHBrNfs"
    }

    # shard03dex = DEX(NodeList.shard0[3]['ip'], NodeList.shard0[3]['rpc'])
    # # fullnode_trx = Transaction(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['rpc'])
    # shard0 = Transaction(NodeList.shard0[3]['ip'], NodeList.shard0[3]['rpc'])
    # shard0ws = WebSocket(NodeList.shard0[3]['ip'], NodeList.shard0[3]['ws'])
    # shard1 = Transaction(NodeList.shard1[3]['ip'], NodeList.shard1[3]['rpc'])
    # shard1ws = WebSocket(NodeList.shard1[3]['ip'], NodeList.shard1[3]['ws'])
    # shard2 = Transaction(NodeList.shard2[3]['ip'], NodeList.shard2[3]['rpc'])
    # shard2ws = WebSocket(NodeList.shard2[3]['ip'], NodeList.shard2[3]['ws'])

    shard03dex = DEX(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['rpc'])
    shard0 = Transaction(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['rpc'])
    shard0ws = WebSocket(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['ws'])
    shard1 = Transaction(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['rpc'])
    shard1ws = WebSocket(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['ws'])
    shard2 = Transaction(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['rpc'])
    shard2ws = WebSocket(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['ws'])

    print("\nENV: " + str(NodeList.shard0[3]))
    print("ENV: " + str(NodeList.shard1[3]))
    print("ENV: " + str(NodeList.shard2[3]))

    token_id = "a198b3da0c24b0928afebcd2510e7b4c9f81e3c91385bd9f0ebaeb714833454e"

    @pytest.mark.run
    def est_01_init_pToken(self):
        print('''
        Init a pToken
        Contribute pToken-PRV to pDex (mapping rate) => use pToken to pay fee
        ''')

        STEP(1, "Initial new token")
        token_symbol = strftime("%H%M%S")
        s1rs = self.shard0.init_customToken(self.test_data['s0_addr1'][0], self.test_data['s0_addr1'][1], token_symbol,
                                            self.test_data['init_tokenAmount'])
        assert_true(len(s1rs[0]) == 64 & len(s1rs[1]) == 64, "Failed to init new token", "Success to init new token")
        test_sendToken.token_id = s1rs[1]
        INFO("token id: %s" % s1rs[1])

        STEP(2, "subcribe transaction")
        self.shard0ws.createConnection()
        self.shard0ws.subcribePendingTransaction(s1rs[0])

        STEP(3, "Get custom token balance")
        token_balance, _ = self.shard0.get_customTokenBalance(self.test_data['s0_addr1'][0], s1rs[1])
        INFO("Token balance: %s" % str(token_balance))

        STEP(4, "contribute token & PRV")
        # Contribute TOKEN:
        contribute_token_tx = self.shard03dex.contribute_token(self.test_data['s0_addr1'][0],
                                                               self.test_data['s0_addr1'][1], s1rs[1],
                                                               10000 * 1000000000, "token1_1prv")
        INFO("Contribute " + s1rs[1] + " Success, TxID: " + contribute_token_tx)
        INFO("Subscribe contribution transaction")
        self.shard0ws.subcribePendingTransaction(contribute_token_tx)
        # Contribute PRV:
        contribute_prv_tx = self.shard03dex.contribute_prv(self.test_data['s0_addr1'][0],
                                                           self.test_data['s0_addr1'][1],
                                                           10000 * 1000000000, "token1_1prv")
        INFO("Contribute PRV Success, TxID: " + contribute_prv_tx)
        INFO("Subscribe contribution transaction")
        self.shard0ws.subcribePendingTransaction(contribute_prv_tx)

        STEP(5, "Verify Contribution")
        rate = []
        for _ in range(0, 10):
            WAIT(10)
            rate = self.shard03dex.get_latestRate("0000000000000000000000000000000000000000000000000000000000000004",
                                                  s1rs[1])
            if rate == [10000 * 1000000000, 10000 * 1000000000]:
                break
        INFO("rate prv vs token: " + str(rate))
        assert_true(rate == [10000 * 1000000000, 10000 * 1000000000], "Contribution Failed")

    @pytest.mark.run
    def test_02_sendToken_noPrivacy_1shard_prvFee(self):
        print('''
            Verify send Token to another address 1Shard successfully
            Fee: PRV (auto estimate)
            Fee: PRV (fixed number * transaction size(KB))
            Token_privacy =0
            PRV_privacy =0
            ''')

        STEP(1, "get address1 and address2 balance before sending")
        balance1b, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("private_key : " + str(self.test_data["s0_addr1"][0]))
        INFO("token_id : " + str(test_sendToken.token_id))
        INFO("addr1_token_balance: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", "get wrong token balance add1")

        step1_balancePRV_add1 = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("add1_prv_balance : " + str(step1_balancePRV_add1))
        assert_true(step1_balancePRV_add1 != "Invalid parameters", "get wrong prv balance add1")

        balance2b, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr2"][0], test_sendToken.token_id)
        INFO("addr2_token_balance: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get wrong token balance add2")

        step1_balancePRV_add2 = self.shard0.getBalance(self.test_data["s0_addr2"][0])
        INFO("add2_prv_balance : " + str(step1_balancePRV_add2))
        assert_true(step1_balancePRV_add2 != "Invalid parameters", "get wrong prv balance add2")

        STEP(2, "from address1 send Token to address2 - Fee PRV auto estimated")
        step2_result = self.shard0.send_customTokenTransaction(self.test_data["s0_addr1"][0],
                                                               self.test_data["s0_addr2"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=-1)

        INFO("transaction id: " + step2_result[0])
        assert_true(step2_result[0] != 'Can not create tx', step2_result[1])

        STEP(3, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(step2_result[0])

        STEP(4, "check address1 & 2 balance after sent")
        balance1a, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1a))
        # Balance after = balance before - amount
        assert balance1a == balance1b - self.test_data["token_amount"]

        balance2a, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr2"][0], test_sendToken.token_id)
        INFO("addr2_token_balance: " + str(balance2a))
        # Balance after = balance before + amount
        assert balance2a == balance2b + self.test_data["token_amount"]

        step4_balancePRV_add1 = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("add1_prv_balance : " + str(step4_balancePRV_add1))
        assert_true(step4_balancePRV_add1 == step1_balancePRV_add1 - ws_res[2],
                    "incorrect prv balance of the address 1 ")


        step4_balancePRV_add2 = self.shard0.getBalance(self.test_data["s0_addr2"][0])
        INFO("add2_prv_balance : " + str(step4_balancePRV_add2))
        assert_true(step4_balancePRV_add2 == step1_balancePRV_add2,
                    "incorrect prv balance of the address 2 ")

        INFO("Check transaction prv_privacy")
        step4_result = self.shard0.get_txbyhash(step2_result[0])
        assert_true(step4_result[2] == False, "transaction must be no prv_privacy ")

        INFO("Check transaction token_privacy")
        assert_true(step4_result[3] == False, "transaction must be no token_privacy ")

        STEP(5, "from address1 send Token to address2 - no Fee PRV ")

        """
        estimate_transaction_size = self.shard0.estimatefee_token(self.test_data["s0_addr1"][0],self.test_data["s0_addr2"][1],
                                                                  test_sendToken.token_id,
                                                                  self.test_data["token_amount"])
        token_fee = 200000
        INFO("estimate transaction size before send: " + str(estimate_transaction_size[0]) + "KB")
        """

        step5_result = self.shard0.send_customTokenTransaction(self.test_data["s0_addr1"][0],
                                                               self.test_data["s0_addr2"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=1)
        assert_true(step5_result[0] != 'Can not create tx', step5_result[0], step5_result[1])

        STEP(6, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res1 = self.shard0ws.subcribePendingTransaction(step5_result[0])
        # assert_true(ws_res[2] % 100 == 0, "tx_fee is not a multiple of 100",
        #             "tx_fee is %d * %d" % (100, ws_res[2] / 100))

        STEP(7, "check address1 & 2 balance after sent")
        balance1c, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_balance: " + str(balance1c))
        # Balance after = balance before - amount
        assert balance1c == balance1a - self.test_data["token_amount"]

        balance2c, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr2"][0], test_sendToken.token_id)
        INFO("addr2_balance: " + str(balance2c))
        # Balance after = balance before + amount
        assert balance2c == balance2a + self.test_data["token_amount"]

        step7_balancePRV_add1 = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("add1_prv_balance : " + str(step7_balancePRV_add1))
        assert_true(step7_balancePRV_add1 == step4_balancePRV_add1 - ws_res1[2],
                    "incorrect prv balance of the address 1 ")

        step7_balancePRV_add2 = self.shard0.getBalance(self.test_data["s0_addr2"][0])
        INFO("add2_prv_balance : " + str(step7_balancePRV_add2))
        assert_true(step7_balancePRV_add2 == step4_balancePRV_add2,
                    "incorrect prv balance of the address 2 ")

        INFO("Check transaction prv privacy")
        step7_result = self.shard0.get_txbyhash(step5_result[0])
        assert_true(step7_result[2] == False, "transaction must be no prv_privacy ")

        INFO("Check transaction token privacy")
        assert_true(step7_result[3] == False, "transaction must be no token_privacy ")

    @pytest.mark.run
    def test_03_sendToken_Privacy_1shard_prvFee(self):
        print('''
               Verify send Token to another address 1Shard successfully
               Fee: PRV (auto estimate)
               Fee: PRV (fixed number * transaction size(KB))
               token_privacy =0
               prv_privacy=1
               ''')

        STEP(1, "get address1 and address2 balance before sending")
        balance1b, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", "get wrong token balance add1")

        step1_balancePRV_add1 = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("add1_prv_balance : " + str(step1_balancePRV_add1))
        assert_true(step1_balancePRV_add1 != "Invalid parameters", "get wrong prv balance add1")

        balance2b, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr2"][0], test_sendToken.token_id)
        INFO("addr2_token_balance: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get wrong token balance add2")

        step1_balancePRV_add2 = self.shard0.getBalance(self.test_data["s0_addr2"][0])
        INFO("add2_prv_balance : " + str(step1_balancePRV_add2))
        assert_true(step1_balancePRV_add2 != "Invalid parameters", "get wrong prv balance add2")

        STEP(2, "from address1 send Token to address2 - Fee PRV auto estimated")
        step2_result = self.shard0.send_customTokenTransaction(self.test_data["s0_addr1"][0],
                                                               self.test_data["s0_addr2"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=-1, token_fee=0,
                                                               prv_privacy=1)
        INFO("transaction id: " + step2_result[0])
        assert_true(step2_result[0] != 'Can not create tx', step2_result[1])

        STEP(3, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(step2_result[0])

        STEP(4, "check address1 & 2 balance after sent")
        balance1a, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1a))
        # Balance after = balance before - amount
        assert balance1a == balance1b - self.test_data["token_amount"]

        balance2a, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr2"][0], test_sendToken.token_id)
        INFO("addr2_token_balance: " + str(balance2a))
        # Balance after = balance before + amount
        assert balance2a == balance2b + self.test_data["token_amount"]

        step4_balancePRV_add1 = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("add1_prv_balance : " + str(step4_balancePRV_add1))
        assert_true(step4_balancePRV_add1 == step1_balancePRV_add1 - ws_res[2],
                    "incorrect prv balance of the address 1 ")

        step4_balancePRV_add2 = self.shard0.getBalance(self.test_data["s0_addr2"][0])
        INFO("add2_prv_balance : " + str(step4_balancePRV_add2))
        assert_true(step4_balancePRV_add2 == step1_balancePRV_add2,
                    "incorrect prv balance of the address 2 ")

        INFO("Check transaction prv_privacy")
        step4_result = self.shard0.get_txbyhash(step2_result[0])
        assert_true(step4_result[2] == True, "transaction must be privacy ")

        INFO("Check transaction token_privacy")
        assert_true(step4_result[3] == False, "transaction must be no token_privacy ")

        STEP(5, "from address1 send Token to address2 - no Fee PRV ")

        step5_result = self.shard0.send_customTokenTransaction(self.test_data["s0_addr1"][0],
                                                               self.test_data["s0_addr2"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=1, token_fee=0,
                                                               prv_privacy=1)

        assert_true(step5_result[0] != 'Can not create tx', step5_result[0], step5_result[1])

        STEP(6, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res1 = self.shard0ws.subcribePendingTransaction(step5_result[0])
        # assert_true(ws_res[2] % 100 == 0, "tx_fee is not a multiple of 100",
        #             "tx_fee is %d * %d" % (100, ws_res[2] / 100))

        STEP(7, "check address1 & 2 balance after sent")
        balance1c, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_balance: " + str(balance1c))
        # Balance after = balance before - amount
        assert balance1c == balance1a - self.test_data["token_amount"]

        balance2c, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr2"][0], test_sendToken.token_id)
        INFO("addr2_balance: " + str(balance2c))
        # Balance after = balance before + amount
        assert balance2c == balance2a + self.test_data["token_amount"]

        step7_balancePRV_add1 = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("add1_prv_balance : " + str(step7_balancePRV_add1))
        assert_true(step7_balancePRV_add1 == step4_balancePRV_add1 - ws_res1[2],
                    "incorrect prv balance of the address 1 ")

        step7_balancePRV_add2 = self.shard0.getBalance(self.test_data["s0_addr2"][0])
        INFO("add2_prv_balance : " + str(step7_balancePRV_add2))
        assert_true(step7_balancePRV_add2 == step4_balancePRV_add2,
                    "incorrect prv balance of the address 2 ")

        INFO("Check transaction prv_privacy")
        step7_result = self.shard0.get_txbyhash(step5_result[0])
        assert_true(step7_result[2] == True, "transaction must be privacy ")

        INFO("Check transaction token_privacy")
        assert_true(step7_result[3] == False, "transaction must be no token_privacy ")

    @pytest.mark.run
    def test_04_sendToken_noPrivacy_Xshard_prvFee(self):
        print('''
              Verify send Token to another address XShard successfully
              Fee: PRV (auto estimate)
              Fee: PRV (no auto fee)
              Token_privacy =0
              PRV_privacy=0
              ''')

        STEP(1, "get address1 and address2 balance before sending")
        balance1b, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", "get wrong token balance add1")

        step1_balancePRV_add1 = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("add1_prv_balance : " + str(step1_balancePRV_add1))
        assert_true(step1_balancePRV_add1 != "Invalid parameters", "get wrong prv balance add1")

        balance2b, _ = self.shard1.get_customTokenBalance(self.test_data["s1_addr3"][0], test_sendToken.token_id)
        INFO("addr3_token_balance: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get wrong token balance add2")

        step1_balancePRV_add3 = self.shard1.getBalance(self.test_data["s1_addr3"][0])
        INFO("add3_prv_balance : " + str(step1_balancePRV_add3))
        assert_true(step1_balancePRV_add3 != "Invalid parameters", "get wrong prv balance add2")

        STEP(2, "from address1 send Token to address3 - Fee PRV auto estimated")
        step2_result = self.shard0.send_customTokenTransaction(self.test_data["s0_addr1"][0],
                                                               self.test_data["s1_addr3"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=-1)
        INFO("transaction id: " + step2_result[0])
        assert_true(step2_result[0] != 'Can not create tx', step2_result[1])

        STEP(3, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(step2_result[0])

        self.shard1ws.createConnection()
        ws_res3 = self.shard1ws.subcribeCrossCustomTokenPrivacyByPrivatekey(self.test_data["s1_addr3"][0])

        STEP(4, "check address1 & 2 balance after sent")
        balance1a, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1a))
        # Balance after = balance before - amount
        assert balance1a == balance1b - self.test_data["token_amount"]

        balance2a, _ = self.shard0.get_customTokenBalance(self.test_data["s1_addr3"][0], test_sendToken.token_id)
        INFO("addr3_token_balance: " + str(balance2a))
        # Balance after = balance before + amount
        assert balance2a == balance2b + self.test_data["token_amount"]

        step4_balancePRV_add1 = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("add1_prv_balance : " + str(step4_balancePRV_add1))
        assert_true(step4_balancePRV_add1 == step1_balancePRV_add1 - ws_res[2],
                    "incorrect prv balance of the address 1 ")

        step4_balancePRV_add3 = self.shard1.getBalance(self.test_data["s1_addr3"][0])
        INFO("add3_prv_balance : " + str(step4_balancePRV_add3))
        assert_true(step4_balancePRV_add3 == step1_balancePRV_add3,
                    "incorrect prv balance of the address 3 ")

        INFO("Check transaction prv_privacy")
        step4_result = self.shard0.get_txbyhash(step2_result[0])
        assert_true(step4_result[2] == False, "transaction must be no privacy ")

        INFO("Check transaction token_privacy")
        assert_true(step4_result[3] == False, "transaction must be no privacy ")

        STEP(5, "from address1 send Token to address3 - no Fee PRV ")
        step5_result = self.shard0.send_customTokenTransaction(self.test_data["s0_addr1"][0],
                                                               self.test_data["s1_addr3"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=2)
        assert_true(step5_result[0] != 'Can not create tx', step5_result[0], step5_result[1])

        STEP(6, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res1 = self.shard0ws.subcribePendingTransaction(step5_result[0])
        # assert_true(ws_res[2] % 100 == 0, "tx_fee is not a multiple of 100",
        #             "tx_fee is %d * %d" % (100, ws_res[2] / 100))
        self.shard1ws.createConnection()
        ws_res6 = self.shard1ws.subcribeCrossCustomTokenPrivacyByPrivatekey(self.test_data["s1_addr3"][0])

        STEP(7, "check address1 & 2 balance after sent")
        balance1c, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_balance: " + str(balance1c))
        # Balance after = balance before - amount
        assert balance1c == balance1a - self.test_data["token_amount"]

        balance2c, _ = self.shard0.get_customTokenBalance(self.test_data["s1_addr3"][0], test_sendToken.token_id)
        INFO("addr3_balance: " + str(balance2c))
        # Balance after = balance before + amount
        assert balance2c == balance2a + self.test_data["token_amount"]

        step7_balancePRV_add1 = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("add1_prv_balance : " + str(step7_balancePRV_add1))
        assert_true(step7_balancePRV_add1 == step4_balancePRV_add1 - ws_res1[2],
                    "incorrect prv balance of the address 1 ")

        step7_balancePRV_add3 = self.shard0.getBalance(self.test_data["s1_addr3"][0])
        INFO("add3_prv_balance : " + str(step7_balancePRV_add3))
        assert_true(step7_balancePRV_add3 == step4_balancePRV_add3,
                    "incorrect prv balance of the address 3 ")

        INFO("Check transaction prv_privacy")
        step7_result = self.shard0.get_txbyhash(step5_result[0])
        assert_true(step7_result[2] == False, "transaction must be no privacy ")

        INFO("Check transaction token privacy")
        assert_true(step7_result[3] == False, "transaction must be no privacy ")

    @pytest.mark.run
    def est_05_sendToken_Privacy_Xshard_prvFee(self):
        print('''
                Verify send Token to another address XShard successfully
                Fee: PRV (auto estimate)
                Fee: PRV (no auto fee)
                Token_privacy =0
                PRV_privacy =1
                ''')

        STEP(1, "get address1 and address2 balance before sending")
        balance1b, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", "get wrong token balance add1")

        step1_balancePRV_add1 = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("add1_prv_balance : " + str(step1_balancePRV_add1))
        assert_true(step1_balancePRV_add1 != "Invalid parameters", "get wrong prv balance add1")

        balance2b, _ = self.shard1.get_customTokenBalance(self.test_data["s1_addr3"][0], test_sendToken.token_id)
        INFO("addr3_token_balance: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get wrong token balance add2")

        step1_balancePRV_add3 = self.shard1.getBalance(self.test_data["s1_addr3"][0])
        INFO("add3_prv_balance : " + str(step1_balancePRV_add3))
        assert_true(step1_balancePRV_add3 != "Invalid parameters", "get wrong prv balance add2")

        STEP(2, "from address1 send Token to address3 - Fee PRV auto estimated")
        step2_result = self.shard0.send_customTokenTransaction(self.test_data["s0_addr1"][0],
                                                               self.test_data["s1_addr3"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=-1,
                                                               prv_privacy=1)

        INFO("transaction id: " + step2_result[0])
        assert_true(step2_result[0] != 'Can not create tx', step2_result[1])

        STEP(3, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(step2_result[0])

        self.shard1ws.createConnection()
        ws_res3 = self.shard1ws.subcribeCrossCustomTokenPrivacyByPrivatekey(self.test_data["s1_addr3"][0])

        STEP(4, "check address1 & 2 balance after sent")
        balance1a, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1a))
        # Balance after = balance before - amount
        assert balance1a == balance1b - self.test_data["token_amount"]

        balance2a, _ = self.shard0.get_customTokenBalance(self.test_data["s1_addr3"][0], test_sendToken.token_id)
        INFO("addr3_token_balance: " + str(balance2a))
        # Balance after = balance before + amount
        assert balance2a == balance2b + self.test_data["token_amount"]

        step4_balancePRV_add1 = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("add1_prv_balance : " + str(step4_balancePRV_add1))
        assert_true(step4_balancePRV_add1 == step1_balancePRV_add1 - ws_res[2],
                    "incorrect prv balance of the address 1 ")

        step4_balancePRV_add3 = self.shard1.getBalance(self.test_data["s1_addr3"][0])
        INFO("add3_prv_balance : " + str(step4_balancePRV_add3))
        assert_true(step4_balancePRV_add3 == step1_balancePRV_add3,
                    "incorrect prv balance of the address 3 ")

        INFO("Check transaction PRV privacy")
        step4_result = self.shard0.get_txbyhash(step2_result[0])
        assert_true(step4_result[2] == True, "transaction must be privacy ")

        INFO("Check transaction token privacy")
        assert_true(step4_result[3] == False, "transaction must be no privacy ")

        STEP(5, "from address1 send Token to address3 - no Fee PRV ")
        step5_result = self.shard0.send_customTokenTransaction(self.test_data["s0_addr1"][0],
                                                               self.test_data["s1_addr3"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=2, prv_privacy=1)
        assert_true(step5_result[0] != 'Can not create tx', step5_result[0], step5_result[1])

        STEP(6, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res1 = self.shard0ws.subcribePendingTransaction(step5_result[0])
        # assert_true(ws_res[2] % 100 == 0, "tx_fee is not a multiple of 100",
        #             "tx_fee is %d * %d" % (100, ws_res[2] / 100))
        self.shard1ws.createConnection()
        ws_res6 = self.shard1ws.subcribeCrossCustomTokenPrivacyByPrivatekey(self.test_data["s1_addr3"][0])

        STEP(7, "check address1 & 2 balance after sent")
        balance1c, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_balance: " + str(balance1c))
        # Balance after = balance before - amount
        assert balance1c == balance1a - self.test_data["token_amount"]

        balance2c, _ = self.shard0.get_customTokenBalance(self.test_data["s1_addr3"][0], test_sendToken.token_id)
        INFO("addr3_balance: " + str(balance2c))
        # Balance after = balance before + amount
        assert balance2c == balance2a + self.test_data["token_amount"]

        step7_balancePRV_add1 = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("add1_prv_balance : " + str(step7_balancePRV_add1))
        assert_true(step7_balancePRV_add1 == step4_balancePRV_add1 - ws_res1[2],
                    "incorrect prv balance of the address 1 ")

        step7_balancePRV_add3 = self.shard0.getBalance(self.test_data["s1_addr3"][0])
        INFO("add3_prv_balance : " + str(step7_balancePRV_add3))
        assert_true(step7_balancePRV_add3 == step4_balancePRV_add3,
                    "incorrect prv balance of the address 3 ")

        INFO("Check transaction PRV privacy")
        step7_result = self.shard0.get_txbyhash(step5_result[0])
        assert_true(step7_result[2] == True, "transaction must be privacy ")

        INFO("Check transaction Token privacy")
        assert_true(step7_result[3] == False, "transaction must be privacy ")

    @pytest.mark.run
    def test_06_sendToken_noPrivacy_1shard_tokenFee(self):
        print('''
                Verify send Token to another address 1Shard successfully
                Fee: token
                Token_privacy = 0
                Prv_privacy =0

                ''')

        STEP(1, "get address1 and address2 balance before sending")
        balance1b, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", "get wrong token balance add1")

        step1_balancePRV_add1 = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("add1_prv_balance : " + str(step1_balancePRV_add1))
        assert_true(step1_balancePRV_add1 != "Invalid parameters", "get wrong prv balance add1")

        balance2b, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr2"][0], test_sendToken.token_id)
        INFO("addr2_token_balance: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get wrong token balance add2")

        step1_balancePRV_add2 = self.shard0.getBalance(self.test_data["s0_addr2"][0])
        INFO("add2_prv_balance : " + str(step1_balancePRV_add2))
        assert_true(step1_balancePRV_add2 != "Invalid parameters", "get wrong prv balance add2")

        STEP(2, "from address1 send Token to address2 - Fee PRV auto estimated")
        step2_result = self.shard0.send_customTokenTransaction(self.test_data["s0_addr1"][0],
                                                               self.test_data["s0_addr2"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=0,
                                                               token_fee=self.test_data["token_fee"])
        INFO("transaction id: " + step2_result[0])
        assert_true(step2_result[0] != 'Can not create tx', step2_result[1])

        STEP(3, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(step2_result[0])

        STEP(4, "check address1 & 2 balance after sent")
        balance1a, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1a))
        # Balance after = balance before - amount -fee
        assert balance1a == balance1b - self.test_data["token_amount"] - self.test_data["token_fee"]

        balance2a, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr2"][0], test_sendToken.token_id)
        INFO("addr2_token_balance: " + str(balance2a))
        # Balance after = balance before + amount
        assert balance2a == balance2b + self.test_data["token_amount"]

        step4_balancePRV_add1 = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("add1_prv_balance : " + str(step4_balancePRV_add1))
        assert_true(step4_balancePRV_add1 == step1_balancePRV_add1 - ws_res[2],
                    "incorrect prv balance of the address 1 ")

        step4_balancePRV_add2 = self.shard0.getBalance(self.test_data["s0_addr2"][0])
        INFO("add2_prv_balance : " + str(step4_balancePRV_add2))
        assert_true(step4_balancePRV_add2 == step1_balancePRV_add2,
                    "incorrect prv balance of the address 2 ")

        STEP(5, "Check transaction privacy")
        step5_result = self.shard0.get_txbyhash(step2_result[0])
        assert_true(step5_result[3] == False, "transaction must be no token_privacy ")
        assert_true(step5_result[2] == False, "transaction must be no prv_privacy ")

    @pytest.mark.run
    def test_07_sendToken_Privacy_1shard_tokenFee(self):
        print('''
                   Verify send Token to another address 1Shard successfully
                   Fee: token
                   Token_privacy = 1
                   Prv_privacy =0

                   ''')

        STEP(1, "get address1 and address2 balance before sending")
        balance1b, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", "get wrong token balance add1")

        step1_balancePRV_add1 = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("add1_prv_balance : " + str(step1_balancePRV_add1))
        assert_true(step1_balancePRV_add1 != "Invalid parameters", "get wrong prv balance add1")

        balance2b, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr2"][0], test_sendToken.token_id)
        INFO("addr2_token_balance: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get wrong token balance add2")

        step1_balancePRV_add2 = self.shard0.getBalance(self.test_data["s0_addr2"][0])
        INFO("add2_prv_balance : " + str(step1_balancePRV_add2))
        assert_true(step1_balancePRV_add2 != "Invalid parameters", "get wrong prv balance add2")

        STEP(2, "from address1 send Token to address2 - Fee PRV auto estimated")
        step2_result = self.shard0.send_customTokenTransaction(self.test_data["s0_addr1"][0],
                                                               self.test_data["s0_addr2"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=0,
                                                               token_fee=self.test_data["token_fee"], token_privacy=1)
        INFO("transaction id: " + step2_result[0])
        assert_true(step2_result[0] != 'Can not create tx', step2_result[1])

        STEP(3, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(step2_result[0])

        STEP(4, "check address1 & 2 balance after sent")
        balance1a, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1a))
        # Balance after = balance before - amount -fee
        assert balance1a == balance1b - self.test_data["token_amount"] - self.test_data["token_fee"]

        balance2a, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr2"][0], test_sendToken.token_id)
        INFO("addr2_token_balance: " + str(balance2a))
        # Balance after = balance before + amount
        assert balance2a == balance2b + self.test_data["token_amount"]

        step4_balancePRV_add1 = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("add1_prv_balance : " + str(step4_balancePRV_add1))
        assert_true(step4_balancePRV_add1 == step1_balancePRV_add1 - ws_res[2],
                    "incorrect prv balance of the address 1 ")

        step4_balancePRV_add2 = self.shard0.getBalance(self.test_data["s0_addr2"][0])
        INFO("add2_prv_balance : " + str(step4_balancePRV_add2))
        assert_true(step4_balancePRV_add2 == step1_balancePRV_add2,
                    "incorrect prv balance of the address 2 ")

        STEP(5, "Check transaction privacy")
        step5_result = self.shard0.get_txbyhash(step2_result[0])
        assert_true(step5_result[2] == False, "transaction must be no prv_privacy ")
        assert_true(step5_result[3] == True, "transaction must be token_privacy ")

    @pytest.mark.run
    def est_08_sendToken_noPrivacy_Xshard_tokenFee(self):
        print('''
                 Verify send Token to another address XShard successfully
                 Fee: token fee
                 Token_privacy = 0
                 PRV_privacy =0
                 ''')

        STEP(1, "get address1 and address4 balance before sending")
        balance1b, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", "get wrong token balance add1")

        step1_balancePRV_add1 = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("add1_prv_balance : " + str(step1_balancePRV_add1))
        assert_true(step1_balancePRV_add1 != "Invalid parameters", "get wrong prv balance add1")

        balance2b, _ = self.shard2.get_customTokenBalance(self.test_data["s2_addr4"][0], test_sendToken.token_id)
        INFO("addr4_token_balance: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get wrong token balance add2")

        step1_balancePRV_add4 = self.shard2.getBalance(self.test_data["s2_addr4"][0])
        INFO("add4_prv_balance : " + str(step1_balancePRV_add4))
        assert_true(step1_balancePRV_add4 != "Invalid parameters", "get wrong prv balance add2")

        STEP(2, "from address1 send Token to address4 - Fee PRV auto estimated")
        step2_result = self.shard0.send_customTokenTransaction(self.test_data["s0_addr1"][0],
                                                               self.test_data["s2_addr4"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=0,
                                                               token_fee=self.test_data["token_fee"],
                                                               token_privacy=0)
        INFO("transaction id: " + step2_result[0])
        assert_true(step2_result[0] != 'Can not create tx', step2_result[1])

        STEP(3, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(step2_result[0])

        self.shard2ws.createConnection()
        ws_res3 = self.shard2ws.subcribeCrossCustomTokenPrivacyByPrivatekey(self.test_data["s2_addr4"][0])

        STEP(4, "check address1 & 4 balance after sent")
        balance1a, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1a))
        # Balance after = balance before - amount - fee
        assert balance1a == balance1b - self.test_data["token_amount"] - self.test_data["token_fee"]

        balance2a, _ = self.shard2.get_customTokenBalance(self.test_data["s2_addr4"][0], test_sendToken.token_id)
        INFO("addr3_token_balance: " + str(balance2a))
        # Balance after = balance before + amount
        assert balance2a == balance2b + self.test_data["token_amount"]

        step4_balancePRV_add1 = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("add1_prv_balance : " + str(step4_balancePRV_add1))
        assert_true(step4_balancePRV_add1 == step1_balancePRV_add1 - ws_res[2],
                    "incorrect prv balance of the address 1 ")

        step4_balancePRV_add4 = self.shard2.getBalance(self.test_data["s2_addr4"][0])
        INFO("add4_prv_balance : " + str(step4_balancePRV_add4))
        assert_true(step4_balancePRV_add4 == step1_balancePRV_add4,
                    "incorrect prv balance of the address 4 ")

        STEP(5, "Check transaction privacy")
        step5_result = self.shard0.get_txbyhash(step2_result[0])
        assert_true(step5_result[2] == False, "transaction must be no prv_privacy ")
        assert_true(step5_result[3] == False, "transaction must be no token_privacy ")

    @pytest.mark.run
    def est_09_sendToken_Privacy_Xshard_tokenFee(self):
        print('''
              Verify send Token to another address XShard successfully
              Fee: token fee
              Token_privacy = 1
              PRV_privacy =0
              ''')

        STEP(1, "get address1 and address3 balance before sending")
        balance1b, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", "get wrong token balance add1")

        step1_balancePRV_add1 = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("add1_prv_balance : " + str(step1_balancePRV_add1))
        assert_true(step1_balancePRV_add1 != "Invalid parameters", "get wrong prv balance add1")

        balance2b, _ = self.shard1.get_customTokenBalance(self.test_data["s1_addr3"][0], test_sendToken.token_id)
        INFO("addr3_token_balance: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get wrong token balance add2")

        step1_balancePRV_add3 = self.shard1.getBalance(self.test_data["s1_addr3"][0])
        INFO("add3_prv_balance : " + str(step1_balancePRV_add3))
        assert_true(step1_balancePRV_add3 != "Invalid parameters", "get wrong prv balance add2")

        STEP(2, "from address1 send Token to address3 - Fee PRV auto estimated")
        step2_result = self.shard0.send_customTokenTransaction(self.test_data["s0_addr1"][0],
                                                               self.test_data["s1_addr3"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=0,token_fee=self.test_data["token_fee"],
                                                               token_privacy=1)
        INFO("transaction id: " + step2_result[0])
        assert_true(step2_result[0] != 'Can not create tx', step2_result[1])

        STEP(3, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(step2_result[0])

        self.shard1ws.createConnection()
        ws_res3 = self.shard1ws.subcribeCrossCustomTokenPrivacyByPrivatekey(self.test_data["s1_addr3"][0])

        STEP(4, "check address1 & 3 balance after sent")
        balance1a, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1a))
        # Balance after = balance before - amount -fee
        assert balance1a == balance1b - self.test_data["token_amount"] -self.test_data["token_fee"]

        balance2a, _ = self.shard0.get_customTokenBalance(self.test_data["s1_addr3"][0], test_sendToken.token_id)
        INFO("addr3_token_balance: " + str(balance2a))
        # Balance after = balance before + amount
        assert balance2a == balance2b + self.test_data["token_amount"]

        step4_balancePRV_add1 = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("add1_prv_balance : " + str(step4_balancePRV_add1))
        assert_true(step4_balancePRV_add1 == step1_balancePRV_add1 - ws_res[2],
                    "incorrect prv balance of the address 1 ")

        step4_balancePRV_add3 = self.shard1.getBalance(self.test_data["s1_addr3"][0])
        INFO("add3_prv_balance : " + str(step4_balancePRV_add3))
        assert_true(step4_balancePRV_add3 == step1_balancePRV_add3,
                    "incorrect prv balance of the address 3 ")

        STEP(5, "Check transaction privacy")
        step5_result = self.shard0.get_txbyhash(step2_result[0])
        assert_true(step5_result[3] == True, "transaction must be toekn_privacy ")
        assert_true(step5_result[2] == False, "transaction must be no prv_privacy ")

    @pytest.mark.run
    def test_10_sendToken_sendPRV_Privacy_1shard_tokenFee_prvFee(self):
        print('''
                      Verify send Token to another address 1Shard successfully
                      Fee: token
                      Fee : auto PRV
                      Token_privacy = 1
                      Prv_privacy =1

                      ''')

        STEP(1, "get address1 and address2 balance before sending")
        balance1b, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", "get wrong token balance add1")

        step1_balancePRV_add1 = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("add1_prv_balance : " + str(step1_balancePRV_add1))
        assert_true(step1_balancePRV_add1 != "Invalid parameters", "get wrong prv balance add1")


        balance2b, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr2"][0], test_sendToken.token_id)
        INFO("addr2_token_balance: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get wrong token balance add2")

        step1_balancePRV_add2 = self.shard0.getBalance(self.test_data["s0_addr2"][0])
        INFO("add2_prv_balance : " + str(step1_balancePRV_add2))
        assert_true(step1_balancePRV_add2 != "Invalid parameters", "get wrong prv balance add2")

        STEP(2, "from address1 send Token to address2 - Fee PRV auto estimated")
        step2_result = self.shard0.send_customTokenTransaction(self.test_data["s0_addr1"][0],
                                                               self.test_data["s0_addr2"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=-1,
                                                               token_fee=self.test_data["token_fee"],
                                                               prv_amount=self.test_data["prv_amount"], token_privacy=1,
                                                               prv_privacy=1)
        INFO("transaction id: " + step2_result[0])
        assert_true(step2_result[0] != 'Can not create tx', step2_result[1])

        STEP(3, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(step2_result[0])

        STEP(4, "check address1 & 2 balance after sent")
        balance1a, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1a))
        # Balance after = balance before - amount - fee
        assert balance1a == balance1b - self.test_data["token_amount"] - self.test_data["token_fee"]

        balance2a, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr2"][0], test_sendToken.token_id)
        INFO("addr2_token_balance: " + str(balance2a))
        # Balance after = balance before + amount
        assert balance2a == balance2b + self.test_data["token_amount"]

        step4_balancePRV_add1 = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("add1_prv_balance : " + str(step4_balancePRV_add1))
        assert_true(step4_balancePRV_add1 == step1_balancePRV_add1 - ws_res[2] - self.test_data["prv_amount"],
                    "incorrect prv balance of the address 1 ")

        step4_balancePRV_add2 = self.shard0.getBalance(self.test_data["s0_addr2"][0])
        INFO("add2_prv_balance : " + str(step4_balancePRV_add2))
        assert_true(step4_balancePRV_add2 == step1_balancePRV_add2 + self.test_data["prv_amount"],
                    "incorrect prv balance of the address 2 ")

        STEP(5, "Check transaction privacy")
        step5_result = self.shard0.get_txbyhash(step2_result[0])
        assert_true(step5_result[2] == True, "transaction must be prv_privacy ")
        assert_true(step5_result[3] == True, "transaction must be token_privacy ")

    @pytest.mark.run
    def test_11_sendToken_sendPRV_Privacy_Xshard_tokenFee_prvFee(self):
        print('''
                     Verify send Token to another address XShard successfully
                     Fee: token fee
                     Fee : auto prv
                     Token_privacy = 1
                     PRV_privacy =1
                     ''')

        STEP(1, "get address1 and address3 balance before sending")
        balance1b, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", "get wrong token balance add1")

        step1_balancePRV_add1 = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("add1_prv_balance : " + str(step1_balancePRV_add1))
        assert_true(step1_balancePRV_add1 != "Invalid parameters", "get wrong prv balance add1")

        balance2b, _ = self.shard1.get_customTokenBalance(self.test_data["s1_addr3"][0], test_sendToken.token_id)
        INFO("addr3_token_balance: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get wrong token balance add3")

        step1_balancePRV_add3 = self.shard1.getBalance(self.test_data["s1_addr3"][0])
        INFO("add3_prv_balance : " + str(step1_balancePRV_add3))
        assert_true(step1_balancePRV_add3 != "Invalid parameters", "get wrong prv balance add3")

        STEP(2, "from address1 send Token to address3 - Fee PRV auto estimated")
        step2_result = self.shard0.send_customTokenTransaction(self.test_data["s0_addr1"][0],
                                                               self.test_data["s1_addr3"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=-1,
                                                               token_fee=self.test_data["token_fee"],
                                                               prv_amount=self.test_data["prv_amount"], prv_privacy=1,
                                                               token_privacy=1)
        INFO("transaction id: " + step2_result[0])
        assert_true(step2_result[0] != 'Can not create tx', step2_result[1])

        STEP(3, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(step2_result[0])

        self.shard1ws.createConnection()
        ws_res3 = self.shard1ws.subcribeCrossCustomTokenPrivacyByPrivatekey(self.test_data["s1_addr3"][0])

        STEP(4, "check address1 & 3 balance after sent")
        balance1a, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1a))
        # Balance after = balance before - amount -fee
        assert balance1a == balance1b - self.test_data["token_amount"] - self.test_data["token_fee"]

        balance2a, _ = self.shard1.get_customTokenBalance(self.test_data["s1_addr3"][0], test_sendToken.token_id)
        INFO("addr3_token_balance: " + str(balance2a))
        # Balance after = balance before + amount
        assert balance2a == balance2b + self.test_data["token_amount"]

        step4_balancePRV_add1 = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("add1_prv_balance : " + str(step4_balancePRV_add1))
        assert_true(step4_balancePRV_add1 == step1_balancePRV_add1 - ws_res[2] - self.test_data["prv_amount"],
                    "incorrect prv balance of the address 1 ")

        step4_balancePRV_add3 = self.shard1.getBalance(self.test_data["s1_addr3"][0])
        INFO("add3_prv_balance : " + str(step4_balancePRV_add3))
        assert_true(step4_balancePRV_add3 == step1_balancePRV_add3 + self.test_data["prv_amount"],
                    "incorrect prv balance of the address 3 ")

        STEP(5, "Check transaction privacy")
        step5_result = self.shard0.get_txbyhash(step2_result[0])
        assert_true(step5_result[3] == True, "transaction must be token_privacy ")
        assert_true(step5_result[2] == True, "transaction must be prv_privacy ")

    @pytest.mark.run
    def est_12_send_2Xshard_tx_1beaconblock(self):
        print("""
                Verify send Token Xshard, from Shard_n+1 Shard_n+2 to Shard_n at the same time
                Fee: PRV (fixed * transaction size KB)
                Fee: pToken (fixed)
                """)

        STEP(1, "get address1, 3 and 4 balance before sending")
        balance1b, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_balance: " + str(balance1b))
        assert balance1b != "Invalid parameters"

        balance3b, _ = self.shard1.get_customTokenBalance(self.test_data["s1_addr3"][0], test_sendToken.token_id)
        INFO("addr3_balance: " + str(balance3b))
        assert balance3b != "Invalid parameters"
        assert_true(balance3b > 0, "addr3 balance = 0")

        balance4b, _ = self.shard2.get_customTokenBalance(self.test_data["s2_addr4"][0], test_sendToken.token_id)
        INFO("addr4_balance: " + str(balance4b))
        assert balance4b != "Invalid parameters"
        assert_true(balance4b > 0, "addr4 balance = 0")

        STEP(2, "from address3 & 4 send all Token to address1")
        tx_id3 = self.shard1.send_customTokenTransaction(self.test_data["s1_addr3"][0],
                                                         self.test_data["s0_addr1"][1], test_sendToken.token_id,
                                                         balance3b - 10, 0, 10)
        tx_id4 = self.shard2.send_customTokenTransaction(self.test_data["s2_addr4"][0],
                                                         self.test_data["s0_addr1"][1], test_sendToken.token_id,
                                                         balance4b - 10, 0, 10)
        INFO("transaction id shard1: " + tx_id3[0] + str(tx_id3[1]))

        INFO("transaction id shard2: " + tx_id4[0] + str(tx_id4[1]))
        assert tx_id3[0] != 'Can not create tx'
        assert tx_id4[0] != 'Can not create tx'

        STEP(3, "subcribe transaction")
        self.shard1ws.createConnection()
        ws_res13 = self.shard1ws.subcribePendingTransaction(tx_id3[0])
        self.shard2ws.createConnection()
        ws_res23 = self.shard2ws.subcribePendingTransaction(tx_id4[0])
        self.shard0ws.createConnection()
        ws_res03 = self.shard0ws.subcribeCrossCustomTokenPrivacyByPrivatekey(self.test_data["s0_addr1"][0])

        STEP(4, "check address3 & 4 balance")
        balance4a = "null"
        balance3a = "null"
        for _ in range(0, 6):
            balance4a, _ = self.shard2.get_customTokenBalance(self.test_data["s2_addr4"][0], test_sendToken.token_id)
            balance3a, _ = self.shard1.get_customTokenBalance(self.test_data["s1_addr3"][0], test_sendToken.token_id)
            if balance4a == 0 & balance3a == 0:
                break
            WAIT(10)

        INFO("addr3_balance: " + str(balance3a))
        INFO("addr4_balance: " + str(balance4a))
        assert balance3a == 0
        assert balance4a == 0

        STEP(5, "check address1 balance")
        balance1a = "null"
        for _ in range(0, 6):
            balance1a, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
            if balance1a == balance1b + balance3b + balance4b - 10 - 10:
                break
            WAIT(10)
        INFO("addr1_balance: " + str(balance1a))
        # Balance after = balance before + amount + amount
        assert_true(balance1a == balance1b + balance3b + balance4b - 10 - 10,
                    "Balance addr1 invalid: %d != %d + %d + %d" % (balance1a, balance1b, balance3b, balance4b))

    @pytest.mark.run
    def est_13_sendToken_Xshard_insufficient_fund(self):
        """
        Verify send Token to another address:
        - Not enough coin (insufficient fund)
        - Wrong input transaction
        - Valid transaction
        """
        STEP(1, "get address2 and address3 balance before sending")
        step1_token_add3, _ = self.shard1.get_customTokenBalance(self.test_data["s1_addr3"][0], test_sendToken.token_id)
        INFO("addr3_token_balance: " + str(step1_token_add3))
        assert_true(step1_token_add3 != "Invalid parameters", "get wrong token balance add3")

        step1_PRV_add3 = self.shard1.getBalance(self.test_data["s1_addr3"][0])
        INFO("add3_prv_balance : " + str(step1_PRV_add3))
        assert_true(step1_PRV_add3 != "Invalid parameters", "get wrong prv balance add3")

        step1_token_add2, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr2"][0], test_sendToken.token_id)
        INFO("addr2_token_balance: " + str(step1_token_add2))
        assert_true(step1_token_add2 != "Invalid parameters", "get wrong token balance add2")

        step1_PRV_add2 = self.shard0.getBalance(self.test_data["s0_addr2"][0])
        INFO("add2_prv_balance : " + str(step1_PRV_add2))
        assert_true(step1_PRV_add2 != "Invalid parameters", "get wrong prv balance add2")

        STEP(2, "From address3 send prv to address2 - Not enough coin")
        # send current balance + 10
        step2_result = self.shard0.send_customTokenTransaction(self.test_data["s1_addr3"][0],
                                                               self.test_data["s0_addr2"][1], self.token_id,
                                                               amount_customToken=step1_token_add3 + 10)
        INFO("Expecting: " + step2_result[0])
        assert_true(step2_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'Not enough coin', step2_result[1]), "something went so wrong")

        # breakpoint()

        STEP(3, "From address3 send prv to address2 - Wrong input transaction")
        # send current balance (lacking of fee)
        step3_result = self.shard0.send_customTokenTransaction(self.test_data["s1_addr3"][0],
                                                               self.test_data["s0_addr2"][1], self.token_id,
                                                               amount_customToken=step1_token_add3,
                                                               token_fee=self.test_data["token_fee"])
        INFO("Expecting: " + step3_result[0])
        assert_true(step3_result[0] == 'Can not create tx', "something went wrong, this tx must failed")

        # breakpoint()

        STEP(4, "From address2 send prv to address3 - success")
        # send current balance - fee (100)
        estimated_fee = 10
        step4_result = self.shard0.send_customTokenTransaction(self.test_data["s1_addr3"][0],
                                                               self.test_data["s0_addr2"][1], self.token_id,
                                                               amount_customToken=step1_token_add3 - estimated_fee,
                                                               token_fee=estimated_fee)
        step4_result[0] != 'Can not create tx'
        assert_true(step4_result[0] != 'Can not create tx', step4_result[1])
        INFO("TxID: " + step4_result[0])

        STEP(5, "Subcribe transaction")
        self.shard1ws.createConnection()
        ws_res6 = self.shard1ws.subcribePendingTransaction(step4_result[0])

        self.shard0ws.createConnection()
        ws_res7 = self.shard0ws.subcribeCrossCustomTokenPrivacyByPrivatekey(self.test_data["s0_addr2"][0])

        STEP(6, "Check address1 balance")
        step6_result = self.shard1.get_customTokenBalance(self.test_data["s1_addr3"][0], self.token_id)
        INFO("addr3_balance: " + str(step6_result[0]))
        assert step6_result[0] == 0

        STEP(7, "Check address2 balance")
        step7_result = self.shard0.get_customTokenBalance(self.test_data["s0_addr2"][0], self.token_id)
        INFO("Addr2_balance: " + str(step7_result[0]))
        assert step7_result[0] == step1_token_add2 + step1_token_add3 - estimated_fee

    @pytest.mark.run
    def est_14_sendToken_1shard_insufficient_fund(self):
        """
        Verify send Token to another address:
        - Not enough coin (insufficient fund)
        - Wrong input transaction
        - Valid transaction
        """
        STEP(1, "get address1 and address2 balance before sending")
        step1_token_add2, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr2"][0], test_sendToken.token_id)
        INFO("addr2_token_balance: " + str(step1_token_add2))
        assert_true(step1_token_add2 != "Invalid parameters", "get wrong token balance add2")

        step1_PRV_add2 = self.shard0.getBalance(self.test_data["s0_addr2"][0])
        INFO("add2_prv_balance : " + str(step1_PRV_add2))
        assert_true(step1_PRV_add2 != "Invalid parameters", "get wrong prv balance add2")

        step1_token_add1, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(step1_token_add1))
        assert_true(step1_token_add1 != "Invalid parameters", "get wrong token balance add1")

        step1_PRV_add1 = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("add1_prv_balance : " + str(step1_PRV_add1))
        assert_true(step1_PRV_add1 != "Invalid parameters", "get wrong prv balance add1")

        STEP(2, "From address2 send prv to address1 - Not enough coin")
        # send current balance + 10
        step2_result = self.shard0.send_customTokenTransaction(self.test_data["s0_addr2"][0],
                                                               self.test_data["s0_addr1"][1], self.token_id,
                                                               amount_customToken=step1_token_add2 + 10)
        INFO("Expecting: " + step2_result[0])
        assert_true(step2_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'Not enough coin', step2_result[1]), "something went so wrong")

        # breakpoint()

        STEP(3, "From address2 send prv to address1 - Wrong input transaction")
        # send current balance (lacking of fee)
        step3_result = self.shard0.send_customTokenTransaction(self.test_data["s0_addr2"][0],
                                                               self.test_data["s0_addr1"][1], self.token_id,
                                                               amount_customToken=step1_token_add2,
                                                               token_fee=self.test_data["token_fee"])
        INFO("Expecting: " + step3_result[0])
        assert_true(step3_result[0] == 'Can not create tx', "something went wrong, this tx must failed")

        # breakpoint()

        STEP(4, "From address2 send prv to address1 - success")
        # send current balance - fee (10)
        estimated_fee = 10
        step4_result = self.shard0.send_customTokenTransaction(self.test_data["s0_addr2"][0],
                                                               self.test_data["s0_addr1"][1], self.token_id,
                                                               amount_customToken=step1_token_add2 - estimated_fee,
                                                               token_fee=10)
        step4_result[0] != 'Can not create tx'
        assert_true(step4_result[0] != 'Can not create tx', step4_result[1])
        INFO("TxID: " + step4_result[0])

        STEP(5, "Subcribe transaction")
        self.shard0ws.createConnection()
        ws_res6 = self.shard0ws.subcribePendingTransaction(step4_result[0])

        STEP(6, "Check address1 balance")
        step6_result = self.shard1.get_customTokenBalance(self.test_data["s0_addr1"][0], self.token_id)
        INFO("addr1_balance: " + str(step6_result))
        assert step6_result[0] == step1_token_add1 + step1_token_add2 - estimated_fee

        STEP(7, "Check address2 balance")
        step7_result = self.shard0.get_customTokenBalance(self.test_data["s0_addr2"][0], self.token_id)
        INFO("Addr2_balance: " + str(step7_result[0]))
        assert step7_result[0] == 0

    @pytest.mark.run
    def est_xx_burn_pToken(self):
        print("\n")
        STEP(0, "check address1 balance")
        balance1b, _ = self.shard0.get_customTokenBalance(self.test_data["s0_addr1"][0], test_sendToken.token_id)
        INFO("addr1_balance: " + str(balance1b))

        STEP(1, "Burn token")
        txid, shard = self.shard0.send_customTokenTransaction(self.test_data['s0_addr1'][0],
                                                              self.test_data['burning_addr'],
                                                              test_sendToken.token_id, balance1b)
        assert_true(len(txid) == 64, "Burning not success")

        STEP(2, "subcribe transaction")
        self.shard0ws.createConnection()
        self.shard0ws.subcribePendingTransaction(txid)

        STEP(3, "Get custom token balance")
        token_balance, _ = self.shard0.get_customTokenBalance(self.test_data['s0_addr1'][0], test_sendToken.token_id)
        INFO("Token balance after burn: " + str(token_balance))
        assert_true(token_balance == 0, "Token Balance != 0", "Burning success")

    @pytest.mark.run
    def test_cleanup(self):
        """
        CLEAN UP
        """
        self.shard0ws.closeConnection()
        self.shard1ws.closeConnection()
        self.shard2ws.closeConnection()
