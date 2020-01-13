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
        's00_addr1': [
            "112t8rnXVMJJZzfF1naXvfE9nkTKwUwFWFeh8cfEyViG1vpA8A9khJk3mhyB1hDuJ4RbreDTsZpgJK4YcSxdEpXJKMEd8Vmp5UqKWwBcYzxv",
            "12RyJTSL2G8KvjN7SUFuiS9Ek4pvFFze3EMMic31fmXVw8McwYzpKPpxeW6TLsNo1UoPhCHKV3GDRLQwdLF41PED3LQNCLsGNKzmCE5"
        ],
        's00_addr2': [
            "112t8rnakdKxvk7VMKUB9qmsPY4czwnP24b82BnepcxHLX6kJ1dYQsR8d6xNTzwC9nEhJdocr9u19NAr4iSYXCeTBRu3YET8iADMAP3szdfw",
            "12RxnTs5KqyQUzGF4R2w68j3biJD29iDsFiVgC4GRy5X85anUrq1rg8P4aUyDRuS5desg9WANRptifcissMBPETyMeBE8KEh7LmQ6m7",
        ],
        's01_addr3': [
            "112t8rnXHSFhmnyduga9tE5vh5CpTX1Ydu8murPuyQi3FYwxESW6eCPVG7vy62vjeRuM8PDfDDLf6wfXekJM5QbdHAryj2XcN4JAZq5y1Tri",
            "12Rqdqkv3w4uyfSTYTkoegWSHSoex75QLuHiS4C1MzwMztieSPai59mprYovV6WC963SP4p9sH5uS3eFYomefPrvvMKhuafER6YV3Kv",
        ],
        's02_addr4': [
            "112t8rnZ5UZouZU9nFmYLfpHUp8NrvQkGLPD564mjzNDM8rMp9nc9sXZ6CFxCGEMuvHQpYN7af6KCPJnq9MfEnXQfntbM8hpy9LW8p4qzPxS",
            "12Rw9oesEgd8t5NGrfqxtWTCzh1eDif55miqZ1kFzj5zeQ6UQnNB9JXRn5Vc5QVbBaiFhoYdYPnQZ5tWwcBpse5EJXM3Av6qEV2wspv",
        ],
        'token_amount': 0.123456789 * 1000000000,
        'init_tokenAmount': 1000000 * 1000000000,
        'burning_addr': "15pABFiJVeh9D5uiQEhQX4SVibGGbdAVipQxBdxkmDqAJaoG1EdFKHBrNfs"
    }

    test_data = {
        's00_addr1': [
            "112t8rnazyWhn41sV6BafSkqpYS1QEcFxWrzxBb5CX8f7EZSmjQhZU91uXYtwtGvhrVwf7E4JEgSj2R9dV8eRkWhPL7iBDyWypDWrhb1ucxU",
            "12Ruw9LjyAELz69QZmwssD1XkdR1KB56tSimyRB6UUoYXzskpjBoDjWCKxHpRHncMjRdXRTaUQFK9PcGwLnsDw6jHkjJPZXAK631e5p"
        ],
        's00_addr2': [
            "112t8rnfCAK3moGcy55uZfYZ922CBnNszAi9x97FdcLsmmdSuCQdDZ5gp7E659X1SV8AuFZWc5FzHK9LGprJZufXQgWRLJAL9pMc3zVbRmyk",
            "12S44YZWpwvvpkQUPKsX4skrVNEWf3jUsnRFDUrJMbQe18EBkfXx6RAmqdrfvJBXabmPYfVTsiSYxsDpXy9dHegxapiYjzzfZ5CiXFT",
        ],
        's01_addr3': [
            "112t8rnYN1HoE5mzPc7uzrv15ZTLd8XYzdTodL8aMUof9NHueNrueBuf9SojF3mpGpS7Fe4B3ZthjxkQZUuNtfZbUJCmBuK7ZihnbmArcHuv",
            "12RzkgXFEVEJHZhJKcbwcyTLBtkapMSue8uuF5aBbAj6xSXjHbyhqMBJcu6s9LJxCxXZ5jfqDo4CpHB6FJB1G9tunzpZkhmKF4b193r",
        ],
        's02_addr4': [
            "112t8rnk8ga5FhJ4X5iUHnifwNUX8aBZ6wZA9FNodNicxxxEHy96xKt36gYzJp4HywefhMQyuS9u6nw1NtAPmMi2xBie4ah3f1ZEwXDiviy4",
            "12Rw7NSkRkgqtXSdQ9zW1s7HUduSFUVwFeKKr8EwbxWxi6bHMC1ms76utaY3G4VTXZF2ZKtdexYUPxuhzJrUMvqFNcFzmERfobi8TRa",
        ],
        'token_amount': 0.12345 * 100000,
        'init_tokenAmount': 1000000 * 1000000000,
        'prv_amount': 10,
        'token_fee': 200,
        'burning_addr': "12RxahVABnAVCGP3LGwCn8jkQxgw7z1x14wztHzn455TTVpi1wBq9YGwkRMQg3J4e657AbAnCvYCJSdA9czBUNuCKwGSRQt55Xwz8WA"
    }

    test_data_multi_output = {
        's00_add1': [
            "112t8rnfCAK3moGcy55uZfYZ922CBnNszAi9x97FdcLsmmdSuCQdDZ5gp7E659X1SV8AuFZWc5FzHK9LGprJZufXQgWRLJAL9pMc3zVbRmyk",
            "12S44YZWpwvvpkQUPKsX4skrVNEWf3jUsnRFDUrJMbQe18EBkfXx6RAmqdrfvJBXabmPYfVTsiSYxsDpXy9dHegxapiYjzzfZ5CiXFT",
        ],
        's01_addr2': [
            "112t8rnYZFGFNxoNqgvvy2kgKvbatwLtX2VY4C3ycTFAHgkcmF8cJ446WSJvZxvRpvmrNopKpaNsi5bFWT6osE6yzcuNEWdpjSFbjLGT1Gub",
            "12RtFLvgdkQAwtpLWBKJy8ttdSJ5hRUEEeLNeWMS9E5RHF9PEXbm5xqwWcGfocazM59EF8G6pGvR3XdnWSRtPZ4TTSUVLmsin1SYJLk"
        ], ''
           's02_addr3': [
            "112t8rnmwqoeUwB2c5oF4yUCqXSz23oDAhbsfqbnte1rr9VNME78PupgmnU9TDDZ8YksVek5zefL94vbChDV1bG72K2kB97Ukc8ArKSXQE8k",
            "12S6PwyVcdhCwuMMgaC47QyraY4uXUkqbCas8xoD3usbyamua7KwWuifeiFNop7p5X86KuUx5F92vS5ef6pqfdYSykndgyNUAuGHiBf",
        ],
        's03_addr4': [
            "112t8rnZkN51A8rrwaY2HeMawhDSUoZYdTN4tAJzPfoN7spqS3usy713iczvNFAGn2xE2agG5W3ZRAtiAvD3UkAzPj9S6CfkzJNDDLotWb25",
            "12Ry9zsyJDA4jD4dceG6237LHUNYhJYrtUvmST3978pJ3ao6r4hsVc6cCdmEYuyHqNwi6guMqXZKzTw7x4crcJyofRnTBPX8y1e98Ux",
        ],
        's04_addr5': [
            "112t8rnXhfP27uHv1jmL4X4F3e1uSZC9nK42ZhCmUtAJa8HAzwQafqqJiuNxGkvVV7w5trwo7UBCDGfPcZDR1gFsLtuDiZpMwzJYB6V8Ry3f",
            "12Rs3fZjxAVpfEECkGrEWdVasyQmqkGVSBsKdx3GuzAq2m8hXGZnwG6FAYtQjb1prQktLvqSAFVnDL6R8MPnrRUkyJJBXHuJoNyJX7R",
        ],
        's05_addr6': [
            "112t8rnaNVtd1sZ2YLfeZLWioDpP5udt4D42WPt7TpWEPK9e6q7GrhDz3pNNUQyeKjqTcahX6Gm77swRgEvho84RLHCYjzG3Cwo9rw42mQrS",
            "12Rt2wNPvuY5wHwAy32pfqhyZg6fm5yA1c8tHNntk48yypyaYuJmGKa7XG1tC5DFZQ4cRVSuvKdmfP4iY5mWAbjtd8jsQ6nw71DaUN8",
        ],
        's06_addr7': [
            "112t8rnaA5mNsxNg3g2xuczUg5ptdrwx4nniPwNUPBx2cX6BgZyvoqotRd3KT6T43UhuCyhSjACUWcX53JdpH463ekoNeyQK6Z2R4v9wxfds",
            "12Rxo2zhVrTJcgrnnHkSD9Yfzw1SYFu3yjXjeQaBdNrx4VGF17EkHpSHbAJAQwYtBEVKCF8LuxNXbcrzpxQ8TUaCPoqF1tz6FPwdg8N"
        ],
        's7_addr8': [
            "112t8rndVFqZMHPv4MmqzQ3fmuxk6aSp4Ehk35gNUKR2nLncgWMPD8UAwjCtUirMVKZhpUmQuHUNu4n14soo6SLbJj7PdWnRkVXXstA6qoXL",
            "12RxDtHiHwQrbEUz2gMNRsBQ4N3VXVXpNtRjxA47GkDg4XA1engx6ZZgAZYuL2eXr5PHywrtRSpRdyPa3Vb3CX8xrhKHaeXvKMRhKCC"
        ]
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

    token_id = "b3c9e893efa5595e22f4e9ca54c0efbf8a3b1b6899ceb530fa0590fb6355f34b"  #testnet
    #token_id ="4a3434352e6b03f01f7c5b7de2238e6e5c967f4e776a78ebc42fc0bde54e7832"    #devnet

    @pytest.mark.run
    def est_01_init_pToken(self):
        print('''
        Init a pToken
        Contribute pToken-PRV to pDex (mapping rate) => use pToken to pay fee
        ''')

        STEP(1, "Initial new token")
        token_symbol = strftime("%H%M%S")
        s1rs = self.shard0.init_customToken(self.test_data['s00_addr1'][0], self.test_data['s00_addr1'][1],
                                            token_symbol,
                                            self.test_data['init_tokenAmount'])
        assert_true(len(s1rs[0]) == 64 & len(s1rs[1]) == 64, "Failed to init new token", "Success to init new token")
        test_sendToken.token_id = s1rs[1]
        INFO("token id: %s" % s1rs[1])

        STEP(2, "subcribe transaction")
        self.shard0ws.createConnection()
        self.shard0ws.subcribePendingTransaction(s1rs[0])

        STEP(3, "Get custom token balance")
        token_balance, _ = self.shard0.get_customTokenBalance(self.test_data['s00_addr1'][0], s1rs[1])
        INFO("Token balance: %s" % str(token_balance))

        STEP(4, "contribute token & PRV")
        # Contribute TOKEN:
        contribute_token_tx = self.shard03dex.contribute_token(self.test_data['s00_addr1'][0],
                                                               self.test_data['s00_addr1'][1], s1rs[1],
                                                               10000 * 1000000000, "token1_1prv")
        INFO("Contribute " + s1rs[1] + " Success, TxID: " + contribute_token_tx)
        INFO("Subscribe contribution transaction")
        self.shard0ws.subcribePendingTransaction(contribute_token_tx)
        # Contribute PRV:
        contribute_prv_tx = self.shard03dex.contribute_prv(self.test_data['s00_addr1'][0],
                                                           self.test_data['s00_addr1'][1],
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

        STEP(1, "get sender and receiver balance before sending")
        balance1b, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
        INFO("private_key_sender : " + str(self.test_data["s00_addr1"][0]))
        INFO("token_id : " + str(test_sendToken.token_id))
        INFO("sender_token_balance_before: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", "get wrong token balance add1")

        step1_balancePRV_add1 = self.shard0.getBalance(self.test_data["s00_addr1"][0])
        INFO("sender_prv_balance_before : " + str(step1_balancePRV_add1))
        assert_true(step1_balancePRV_add1 != "Invalid parameters", "get wrong prv balance add1")

        balance2b, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr2"][0], test_sendToken.token_id)
        INFO("receiver_token_balance_before: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get wrong token balance add2")

        step1_balancePRV_add2 = self.shard0.getBalance(self.test_data["s00_addr2"][0])
        INFO("receiver_prv_balance_before : " + str(step1_balancePRV_add2))
        assert_true(step1_balancePRV_add2 != "Invalid parameters", "get wrong prv balance add2")

        STEP(2, "send_token #1 - Fee PRV auto estimated")
        step2_result = self.shard0.send_customTokenTransaction(self.test_data["s00_addr1"][0],
                                                               self.test_data["s00_addr2"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=-1)

        INFO("transaction_id: " + step2_result[0])
        assert_true(step2_result[0] != 'Can not create tx', step2_result[1], "make successfull transaction")

        STEP(3, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(step2_result[0])

        STEP(4, "check sender and receiver balance after sent")
        balance1a, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
        INFO("sender_token_balance_after: " + str(balance1a))
        # Balance after = balance before - amount
        assert_true(balance1a == balance1b - self.test_data["token_amount"], "sender balance incorrect")

        balance2a, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr2"][0], test_sendToken.token_id)
        INFO("receiver_token_balance_after: " + str(balance2a))
        # Balance after = balance before + amount
        assert_true(balance2a == balance2b + self.test_data["token_amount"], "receiver balance incorrect")

        step4_balancePRV_add1 = self.shard0.getBalance(self.test_data["s00_addr1"][0])
        INFO("sender_prv_balance_after : " + str(step4_balancePRV_add1))
        assert_true(step4_balancePRV_add1 == step1_balancePRV_add1 - ws_res[2],
                    "incorrect prv balance of the address 1 ")

        step4_balancePRV_add2 = self.shard0.getBalance(self.test_data["s00_addr2"][0])
        INFO("receiver_prv_balance_after : " + str(step4_balancePRV_add2))
        assert_true(step4_balancePRV_add2 == step1_balancePRV_add2,
                    "incorrect prv balance of the address 2 ")

        INFO("Check transaction prv_privacy")
        step4_result_prv = self.shard0.check_is_privacy_prv(step2_result[0])
        assert_true(step4_result_prv[1] == "noprivacy", "info value PRV must be no privacy",
                    "info value PRV  is not privacy")

        INFO("Check transaction token privacy")
        step4_result_token = self.shard0.check_is_privacy_token(step2_result[0])
        assert_true(step4_result_token[1] == "noprivacy", "info value token  must be no privacy",
                    "info value token is not privacy")

        STEP(5, "send token #2 - no Fee PRV ")

        """
        estimate_transaction_size = self.shard0.estimatefee_token(self.test_data["s00_addr1"][0],self.test_data["s00_addr2"][1],
                                                                  test_sendToken.token_id,
                                                                  self.test_data["token_amount"])
        token_fee = 200000
        INFO("estimate transaction size before send: " + str(estimate_transaction_size[0]) + "KB")
        """

        step5_result = self.shard0.send_customTokenTransaction(self.test_data["s00_addr1"][0],
                                                               self.test_data["s00_addr2"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=1)
        assert_true(step5_result[0] != 'Can not create tx', step5_result[0], "make successfull transaction")

        STEP(6, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res1 = self.shard0ws.subcribePendingTransaction(step5_result[0])
        # assert_true(ws_res[2] % 100 == 0, "tx_fee is not a multiple of 100",
        #             "tx_fee is %d * %d" % (100, ws_res[2] / 100))

        STEP(7, "check sender and receiver after sent #2")
        balance1c, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
        INFO("sender_token_balance_after: " + str(balance1c))
        # Balance after = balance before - amount
        assert_true(balance1c == balance1a - self.test_data["token_amount"], "sender balance incorrect")

        balance2c, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr2"][0], test_sendToken.token_id)
        INFO("receiver_token_balance_after: " + str(balance2c))
        # Balance after = balance before + amount
        assert_true(balance2c == balance2a + self.test_data["token_amount"], "receiver balance incorrect")

        step7_balancePRV_add1 = self.shard0.getBalance(self.test_data["s00_addr1"][0])
        INFO("sender_prv_balance_after : " + str(step7_balancePRV_add1))
        assert_true(step7_balancePRV_add1 == step4_balancePRV_add1 - ws_res1[2],
                    "incorrect prv balance of the address 1 ")

        step7_balancePRV_add2 = self.shard0.getBalance(self.test_data["s00_addr2"][0])
        INFO("receiver_prv_balance_after : " + str(step7_balancePRV_add2))
        assert_true(step7_balancePRV_add2 == step4_balancePRV_add2,
                    "incorrect prv balance of the address 2 ")

        INFO("Check transaction prv_privacy")
        step7_result_prv = self.shard0.check_is_privacy_prv(step5_result[0])
        assert_true(step7_result_prv[1] == "noprivacy", "info value PRV must be no privacy",
                    "info value PRV  is not privacy")

        INFO("Check transaction token privacy")
        step7_result_token = self.shard0.check_is_privacy_token(step5_result[0])
        assert_true(step7_result_token[1] == "noprivacy", "info value token  must be no privacy",
                    "info value token is not privacy")

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
        balance1b, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", "get wrong token balance add1")

        step1_balancePRV_add1 = self.shard0.getBalance(self.test_data["s00_addr1"][0])
        INFO("add1_prv_balance : " + str(step1_balancePRV_add1))
        assert_true(step1_balancePRV_add1 != "Invalid parameters", "get wrong prv balance add1")

        balance2b, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr2"][0], test_sendToken.token_id)
        INFO("addr2_token_balance: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get wrong token balance add2")

        step1_balancePRV_add2 = self.shard0.getBalance(self.test_data["s00_addr2"][0])
        INFO("add2_prv_balance : " + str(step1_balancePRV_add2))
        assert_true(step1_balancePRV_add2 != "Invalid parameters", "get wrong prv balance add2")

        STEP(2, "from address1 send Token to address2 - Fee PRV auto estimated")
        step2_result = self.shard0.send_customTokenTransaction(self.test_data["s00_addr1"][0],
                                                               self.test_data["s00_addr2"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=-1, token_fee=0,
                                                               prv_privacy=1)
        INFO("transaction id: " + step2_result[0])
        assert_true(step2_result[0] != 'Can not create tx', step2_result[1], "make successfull transaction")

        STEP(3, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(step2_result[0])

        STEP(4, "check address1 & 2 balance after sent")
        balance1a, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1a))
        # Balance after = balance before - amount
        assert_true( balance1a == balance1b - self.test_data["token_amount"],"sender token balance incorrect ")

        balance2a, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr2"][0], test_sendToken.token_id)
        INFO("addr2_token_balance: " + str(balance2a))
        # Balance after = balance before + amount
        assert_true( balance2a == balance2b + self.test_data["token_amount"],"receiver token balance incorrect")

        step4_balancePRV_add1 = self.shard0.getBalance(self.test_data["s00_addr1"][0])
        INFO("add1_prv_balance : " + str(step4_balancePRV_add1))
        assert_true(step4_balancePRV_add1 == step1_balancePRV_add1 - ws_res[2],
                    "incorrect prv balance of the address 1 ")

        step4_balancePRV_add2 = self.shard0.getBalance(self.test_data["s00_addr2"][0])
        INFO("add2_prv_balance : " + str(step4_balancePRV_add2))
        assert_true(step4_balancePRV_add2 == step1_balancePRV_add2,
                    "incorrect prv balance of the address 2 ")

        INFO("Check transaction prv_privacy")
        step4_result_prv = self.shard0.check_is_privacy_prv(step2_result[0])
        assert_true(step4_result_prv[1] == "privacy", "info value PRV must be privacy",
                    "info value PRV  is privacy")

        INFO("Check transaction token privacy")
        step4_result_token = self.shard0.check_is_privacy_token(step2_result[0])
        assert_true(step4_result_token[1] == "noprivacy", "info value token  must be no privacy",
                    "info value token is not privacy")

        STEP(5, "from address1 send Token to address2 - no Fee PRV ")

        step5_result = self.shard0.send_customTokenTransaction(self.test_data["s00_addr1"][0],
                                                               self.test_data["s00_addr2"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=1, token_fee=0,
                                                               prv_privacy=1)

        assert_true(step5_result[0] != 'Can not create tx', step5_result[0], "make successfull transaction")

        STEP(6, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res1 = self.shard0ws.subcribePendingTransaction(step5_result[0])
        # assert_true(ws_res[2] % 100 == 0, "tx_fee is not a multiple of 100",
        #             "tx_fee is %d * %d" % (100, ws_res[2] / 100))

        STEP(7, "check address1 & 2 balance after sent")
        balance1c, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
        INFO("addr1_balance: " + str(balance1c))
        # Balance after = balance before - amount
        assert_true( balance1c == balance1a - self.test_data["token_amount"],"sender token balance incorrect")

        balance2c, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr2"][0], test_sendToken.token_id)
        INFO("addr2_balance: " + str(balance2c))
        # Balance after = balance before + amount
        assert_true( balance2c == balance2a + self.test_data["token_amount"],"receiver token balance incorrect")

        step7_balancePRV_add1 = self.shard0.getBalance(self.test_data["s00_addr1"][0])
        INFO("add1_prv_balance : " + str(step7_balancePRV_add1))
        assert_true(step7_balancePRV_add1 == step4_balancePRV_add1 - ws_res1[2],
                    " sender prv balance incorrect")

        step7_balancePRV_add2 = self.shard0.getBalance(self.test_data["s00_addr2"][0])
        INFO("add2_prv_balance : " + str(step7_balancePRV_add2))
        assert_true(step7_balancePRV_add2 == step4_balancePRV_add2,
                    "incorrect prv balance receiver ")

        INFO("Check transaction prv_privacy")
        step7_result_prv = self.shard0.check_is_privacy_prv(step5_result[0])
        assert_true(step7_result_prv[1] == "privacy", "info value PRV must be privacy",
                    "info value PRV  is privacy")

        INFO("Check transaction token privacy")
        step7_result_token = self.shard0.check_is_privacy_token(step5_result[0])
        assert_true(step7_result_token[1] == "noprivacy", "info value token  must be no privacy",
                    "info value token is not privacy")

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
        balance1b, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", "get wrong token balance add1")

        step1_balancePRV_add1 = self.shard0.getBalance(self.test_data["s00_addr1"][0])
        INFO("add1_prv_balance : " + str(step1_balancePRV_add1))
        assert_true(step1_balancePRV_add1 != "Invalid parameters", "get wrong prv balance add1")

        balance2b, _ = self.shard1.get_customTokenBalance(self.test_data["s01_addr3"][0], test_sendToken.token_id)
        INFO("addr3_token_balance: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get wrong token balance add3")

        step1_balancePRV_add3 = self.shard1.getBalance(self.test_data["s01_addr3"][0])
        INFO("add3_prv_balance : " + str(step1_balancePRV_add3))
        assert_true(step1_balancePRV_add3 != "Invalid parameters", "get wrong prv balance add3")

        STEP(2, "from address1 send Token to address3 - Fee PRV auto estimated")
        step2_result = self.shard0.send_customTokenTransaction(self.test_data["s00_addr1"][0],
                                                               self.test_data["s01_addr3"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=-1)
        INFO("transaction id: " + step2_result[0])
        assert_true(step2_result[0] != 'Can not create tx', "make transaction failed", "make successfull transaction")

        STEP(3, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(step2_result[0])

        self.shard1ws.createConnection()
        ws_res3 = self.shard1ws.subcribeCrossCustomTokenPrivacyByPrivatekey(self.test_data["s01_addr3"][0])

        STEP(4, "check address1 & 3 balance after sent")
        balance1a, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1a))
        # Balance after = balance before - amount
        assert_true( balance1a == balance1b - self.test_data["token_amount"],"sender token balance incorrect")

        balance2a, _ = self.shard1.get_customTokenBalance(self.test_data["s01_addr3"][0], test_sendToken.token_id)
        INFO("addr3_token_balance: " + str(balance2a))
        # Balance after = balance before + amount
        assert_true( balance2a == balance2b + self.test_data["token_amount"],"receiver token balance incorrect")

        step4_balancePRV_add1 = self.shard0.getBalance(self.test_data["s00_addr1"][0])
        INFO("add1_prv_balance : " + str(step4_balancePRV_add1))
        assert_true(step4_balancePRV_add1 == step1_balancePRV_add1 - ws_res[2],
                    "incorrect prv balance of the address 1 ")

        step4_balancePRV_add3 = self.shard1.getBalance(self.test_data["s01_addr3"][0])
        INFO("add3_prv_balance : " + str(step4_balancePRV_add3))
        assert_true(step4_balancePRV_add3 == step1_balancePRV_add3,
                    "incorrect prv balance of the address 3 ")

        INFO("Check transaction prv_privacy")
        step4_result_prv = self.shard0.check_is_privacy_prv(step2_result[0])
        assert_true(step4_result_prv[1] == "noprivacy", "info value PRV must be no privacy",
                    "info value PRV  is not privacy")

        INFO("Check transaction token privacy")
        step4_result_token = self.shard0.check_is_privacy_token(step2_result[0])
        assert_true(step4_result_token[1] == "noprivacy", "info value token  must be no privacy",
                    "info value token is not privacy")

        STEP(5, "from address1 send Token to address3 - no Fee PRV ")
        step5_result = self.shard0.send_customTokenTransaction(self.test_data["s00_addr1"][0],
                                                               self.test_data["s01_addr3"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=2)
        assert_true(step5_result[0] != 'Can not create tx', "make transaction failed", "make successfull transaction")

        STEP(6, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res1 = self.shard0ws.subcribePendingTransaction(step5_result[0])
        # assert_true(ws_res[2] % 100 == 0, "tx_fee is not a multiple of 100",
        #             "tx_fee is %d * %d" % (100, ws_res[2] / 100))
        self.shard1ws.createConnection()
        ws_res6 = self.shard1ws.subcribeCrossCustomTokenPrivacyByPrivatekey(self.test_data["s01_addr3"][0])

        STEP(7, "check address1 & 3 balance after sent")
        balance1c, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
        INFO("addr1_balance: " + str(balance1c))
        # Balance after = balance before - amount
        assert_true( balance1c == balance1a - self.test_data["token_amount"],"sender token balance incorrect")

        balance2c, _ = self.shard1.get_customTokenBalance(self.test_data["s01_addr3"][0], test_sendToken.token_id)
        INFO("addr3_balance: " + str(balance2c))
        # Balance after = balance before + amount
        assert_true( balance2c == balance2a + self.test_data["token_amount"],"receiver token balance incorrect")

        step7_balancePRV_add1 = self.shard0.getBalance(self.test_data["s00_addr1"][0])
        INFO("add1_prv_balance : " + str(step7_balancePRV_add1))
        assert_true(step7_balancePRV_add1 == step4_balancePRV_add1 - ws_res1[2],
                    "incorrect prv balance of the address 1 ")

        step7_balancePRV_add3 = self.shard1.getBalance(self.test_data["s01_addr3"][0])
        INFO("add3_prv_balance : " + str(step7_balancePRV_add3))
        assert_true(step7_balancePRV_add3 == step4_balancePRV_add3,
                    "incorrect prv balance of the address 3 ")

        INFO("Check transaction prv_privacy")
        step7_result_prv = self.shard0.check_is_privacy_prv(step5_result[0])
        assert_true(step7_result_prv[1] == "noprivacy", "info value PRV must be no privacy",
                    "info value PRV  is not privacy")

        INFO("Check transaction token privacy")
        step7_result_token = self.shard0.check_is_privacy_token(step5_result[0])
        assert_true(step7_result_token[1] == "noprivacy", "info value token  must be no privacy",
                    "info value token is not privacy")

    @pytest.mark.run
    def test_05_sendToken_Privacy_Xshard_prvFee(self):
        print('''
                Verify send Token to another address XShard successfully
                Fee: PRV (auto estimate)
                Fee: PRV (no auto fee)
                Token_privacy =0
                PRV_privacy =1
                ''')

        STEP(1, "get address1 and address2 balance before sending")
        balance1b, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", "get wrong token balance add1")

        step1_balancePRV_add1 = self.shard0.getBalance(self.test_data["s00_addr1"][0])
        INFO("add1_prv_balance : " + str(step1_balancePRV_add1))
        assert_true(step1_balancePRV_add1 != "Invalid parameters", "get wrong prv balance add1")

        balance2b, _ = self.shard1.get_customTokenBalance(self.test_data["s01_addr3"][0], test_sendToken.token_id)
        INFO("addr3_token_balance: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get wrong token balance add2")

        step1_balancePRV_add3 = self.shard1.getBalance(self.test_data["s01_addr3"][0])
        INFO("add3_prv_balance : " + str(step1_balancePRV_add3))
        assert_true(step1_balancePRV_add3 != "Invalid parameters", "get wrong prv balance add2")

        STEP(2, "from address1 send Token to address3 - Fee PRV auto estimated")
        step2_result = self.shard0.send_customTokenTransaction(self.test_data["s00_addr1"][0],
                                                               self.test_data["s01_addr3"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=-1,
                                                               prv_privacy=1)

        INFO("transaction id: " + step2_result[0])
        assert_true(step2_result[0] != 'Can not create tx', step2_result[1], "make successfull transaction")

        STEP(3, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(step2_result[0])

        self.shard1ws.createConnection()
        ws_res3 = self.shard1ws.subcribeCrossCustomTokenPrivacyByPrivatekey(self.test_data["s01_addr3"][0])

        STEP(4, "check address1 & 2 balance after sent")
        balance1a, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1a))
        # Balance after = balance before - amount
        assert_true( balance1a == balance1b - self.test_data["token_amount"],"sender token balance incorrect")

        balance2a, _ = self.shard0.get_customTokenBalance(self.test_data["s01_addr3"][0], test_sendToken.token_id)
        INFO("addr3_token_balance: " + str(balance2a))
        # Balance after = balance before + amount
        assert_true( balance2a == balance2b + self.test_data["token_amount"],"receiver token balance incorrect")

        step4_balancePRV_add1 = self.shard0.getBalance(self.test_data["s00_addr1"][0])
        INFO("add1_prv_balance : " + str(step4_balancePRV_add1))
        assert_true(step4_balancePRV_add1 == step1_balancePRV_add1 - ws_res[2],
                    "incorrect prv balance of the address 1 ")

        step4_balancePRV_add3 = self.shard1.getBalance(self.test_data["s01_addr3"][0])
        INFO("add3_prv_balance : " + str(step4_balancePRV_add3))
        assert_true(step4_balancePRV_add3 == step1_balancePRV_add3,
                    "incorrect prv balance of the address 3 ")

        INFO("Check transaction prv_privacy")
        step4_result_prv = self.shard0.check_is_privacy_prv(step2_result[0])
        assert_true(step4_result_prv[1] == "privacy", "info value PRV must be privacy",
                    "info value PRV  is privacy")

        INFO("Check transaction token privacy")
        step4_result_token = self.shard0.check_is_privacy_token(step2_result[0])
        assert_true(step4_result_token[1] == "noprivacy", "info value token  must be no privacy",
                    "info value token is not privacy")

        STEP(5, "from address1 send Token to address3 - no Fee PRV ")
        step5_result = self.shard0.send_customTokenTransaction(self.test_data["s00_addr1"][0],
                                                               self.test_data["s01_addr3"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=2, prv_privacy=1)
        assert_true(step5_result[0] != 'Can not create tx', step5_result[0], "make successfull transaction")

        STEP(6, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res1 = self.shard0ws.subcribePendingTransaction(step5_result[0])
        # assert_true(ws_res[2] % 100 == 0, "tx_fee is not a multiple of 100",
        #             "tx_fee is %d * %d" % (100, ws_res[2] / 100))
        self.shard1ws.createConnection()
        ws_res6 = self.shard1ws.subcribeCrossCustomTokenPrivacyByPrivatekey(self.test_data["s01_addr3"][0])

        STEP(7, "check address1 & 2 balance after sent")
        balance1c, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
        INFO("addr1_balance: " + str(balance1c))
        # Balance after = balance before - amount
        assert_true( balance1c == balance1a - self.test_data["token_amount"],"sender token balance incorrect")

        balance2c, _ = self.shard0.get_customTokenBalance(self.test_data["s01_addr3"][0], test_sendToken.token_id)
        INFO("addr3_balance: " + str(balance2c))
        # Balance after = balance before + amount
        assert_true( balance2c == balance2a + self.test_data["token_amount"],"receiver token balance incorrect")

        step7_balancePRV_add1 = self.shard0.getBalance(self.test_data["s00_addr1"][0])
        INFO("add1_prv_balance : " + str(step7_balancePRV_add1))
        assert_true(step7_balancePRV_add1 == step4_balancePRV_add1 - ws_res1[2],
                    "incorrect prv balance of the address 1 ")

        step7_balancePRV_add3 = self.shard0.getBalance(self.test_data["s01_addr3"][0])
        INFO("add3_prv_balance : " + str(step7_balancePRV_add3))
        assert_true(step7_balancePRV_add3 == step4_balancePRV_add3,
                    "incorrect prv balance of the address 3 ")

        INFO("Check transaction prv_privacy")
        step7_result_prv = self.shard0.check_is_privacy_prv(step5_result[0])
        assert_true(step7_result_prv[1] == "privacy", "info value PRV must be privacy",
                    "info value PRV  is privacy")

        INFO("Check transaction token privacy")
        step7_result_token = self.shard0.check_is_privacy_token(step5_result[0])
        assert_true(step7_result_token[1] == "noprivacy", "info value token  must be no privacy",
                    "info value token is not privacy")

    @pytest.mark.run
    def test_06_sendToken_noPrivacy_1shard_tokenFee(self):
        print('''
                Verify send Token to another address 1Shard successfully
                Fee: token
                Token_privacy = 0
                Prv_privacy =0

                ''')

        STEP(1, "get address1 and address2 balance before sending")
        balance1b, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", "get wrong token balance add1")

        step1_balancePRV_add1 = self.shard0.getBalance(self.test_data["s00_addr1"][0])
        INFO("add1_prv_balance : " + str(step1_balancePRV_add1))
        assert_true(step1_balancePRV_add1 != "Invalid parameters", "get wrong prv balance add1")

        balance2b, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr2"][0], test_sendToken.token_id)
        INFO("addr2_token_balance: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get wrong token balance add2")

        step1_balancePRV_add2 = self.shard0.getBalance(self.test_data["s00_addr2"][0])
        INFO("add2_prv_balance : " + str(step1_balancePRV_add2))
        assert_true(step1_balancePRV_add2 != "Invalid parameters", "get wrong prv balance add2")

        STEP(2, "from address1 send Token to address2 - Fee PRV auto estimated")
        step2_result = self.shard0.send_customTokenTransaction(self.test_data["s00_addr1"][0],
                                                               self.test_data["s00_addr2"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=0,
                                                               token_fee=self.test_data["token_fee"])
        INFO("transaction id: " + step2_result[0])
        assert_true(step2_result[0] != 'Can not create tx', step2_result[1], "make successfull transaction")

        STEP(3, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(step2_result[0])

        STEP(4, "check address1 & 2 balance after sent")
        balance1a, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1a))
        # Balance after = balance before - amount -fee
        assert_true( balance1a == balance1b - self.test_data["token_amount"] - self.test_data["token_fee"],"sender token balance incorrect")

        balance2a, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr2"][0], test_sendToken.token_id)
        INFO("addr2_token_balance: " + str(balance2a))
        # Balance after = balance before + amount
        assert_true( balance2a == balance2b + self.test_data["token_amount"],"receiver token balance incorrect")

        step4_balancePRV_add1 = self.shard0.getBalance(self.test_data["s00_addr1"][0])
        INFO("add1_prv_balance : " + str(step4_balancePRV_add1))
        assert_true(step4_balancePRV_add1 == step1_balancePRV_add1 - ws_res[2],
                    "incorrect prv balance of the address 1 ")

        step4_balancePRV_add2 = self.shard0.getBalance(self.test_data["s00_addr2"][0])
        INFO("add2_prv_balance : " + str(step4_balancePRV_add2))
        assert_true(step4_balancePRV_add2 == step1_balancePRV_add2,
                    "incorrect prv balance of the address 2 ")

        STEP(5, "Check transaction privacy")
        INFO("Check transaction prv_privacy")
        step5_result_prv = self.shard0.check_is_privacy_prv(step2_result[0])
        assert_true(step5_result_prv[1] == "noprivacy", "info value PRV must be  no privacy",
                    "info value PRV is not privacy")

        INFO("Check transaction token privacy")
        step5_result_token = self.shard0.check_is_privacy_token(step2_result[0])
        assert_true(step5_result_token[1] == "noprivacy", "info value token  must be no privacy",
                    "info value token is not privacy")

    @pytest.mark.run
    def test_07_sendToken_Privacy_1shard_tokenFee(self):
        print('''
                   Verify send Token to another address 1Shard successfully
                   Fee: token
                   Token_privacy = 1
                   Prv_privacy =0

                   ''')

        STEP(1, "get address1 and address2 balance before sending")
        balance1b, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", "get wrong token balance add1")

        step1_balancePRV_add1 = self.shard0.getBalance(self.test_data["s00_addr1"][0])
        INFO("add1_prv_balance : " + str(step1_balancePRV_add1))
        assert_true(step1_balancePRV_add1 != "Invalid parameters", "get wrong prv balance add1")

        balance2b, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr2"][0], test_sendToken.token_id)
        INFO("addr2_token_balance: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get wrong token balance add2")

        step1_balancePRV_add2 = self.shard0.getBalance(self.test_data["s00_addr2"][0])
        INFO("add2_prv_balance : " + str(step1_balancePRV_add2))
        assert_true(step1_balancePRV_add2 != "Invalid parameters", "get wrong prv balance add2")

        STEP(2, "from address1 send Token to address2 - Fee PRV auto estimated")
        step2_result = self.shard0.send_customTokenTransaction(self.test_data["s00_addr1"][0],
                                                               self.test_data["s00_addr2"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=0,
                                                               token_fee=self.test_data["token_fee"], token_privacy=1)
        INFO("transaction id: " + step2_result[0])
        assert_true(step2_result[0] != 'Can not create tx', step2_result[1], "make successfull transaction")

        STEP(3, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(step2_result[0])

        STEP(4, "check address1 & 2 balance after sent")
        balance1a, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1a))
        # Balance after = balance before - amount -fee
        assert_true( balance1a == balance1b - self.test_data["token_amount"] - self.test_data["token_fee"],"sender token balance incorrect")

        balance2a, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr2"][0], test_sendToken.token_id)
        INFO("addr2_token_balance: " + str(balance2a))
        # Balance after = balance before + amount
        assert_true( balance2a == balance2b + self.test_data["token_amount"],"receiver token balance incorrect")

        step4_balancePRV_add1 = self.shard0.getBalance(self.test_data["s00_addr1"][0])
        INFO("add1_prv_balance : " + str(step4_balancePRV_add1))
        assert_true(step4_balancePRV_add1 == step1_balancePRV_add1 - ws_res[2],
                    "incorrect prv balance of the address 1 ")

        step4_balancePRV_add2 = self.shard0.getBalance(self.test_data["s00_addr2"][0])
        INFO("add2_prv_balance : " + str(step4_balancePRV_add2))
        assert_true(step4_balancePRV_add2 == step1_balancePRV_add2,
                    "incorrect prv balance of the address 2 ")

        STEP(5, "Check transaction privacy")
        INFO("Check transaction prv_privacy")
        step5_result_prv = self.shard0.check_is_privacy_prv(step2_result[0])
        assert_true(step5_result_prv[1] == "noprivacy", "info value PRV must be  no privacy",
                    "info value PRV is not privacy")

        INFO("Check transaction token privacy")
        step5_result_token = self.shard0.check_is_privacy_token(step2_result[0])
        assert_true(step5_result_token[1] == "privacy", "info value token  must be privacy",
                    "info value token is privacy")

    @pytest.mark.run
    def test_08_sendToken_noPrivacy_Xshard_tokenFee(self):
        print('''
                 Verify send Token to another address XShard successfully
                 Fee: token fee
                 Token_privacy = 0
                 PRV_privacy =0
                 ''')

        STEP(1, "get address1 and address4 balance before sending")
        balance1b, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", "get wrong token balance add1")

        step1_balancePRV_add1 = self.shard0.getBalance(self.test_data["s00_addr1"][0])
        INFO("add1_prv_balance : " + str(step1_balancePRV_add1))
        assert_true(step1_balancePRV_add1 != "Invalid parameters", "get wrong prv balance add1")

        balance2b, _ = self.shard2.get_customTokenBalance(self.test_data["s02_addr4"][0], test_sendToken.token_id)
        INFO("addr4_token_balance: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get wrong token balance add2")

        step1_balancePRV_add4 = self.shard2.getBalance(self.test_data["s02_addr4"][0])
        INFO("add4_prv_balance : " + str(step1_balancePRV_add4))
        assert_true(step1_balancePRV_add4 != "Invalid parameters", "get wrong prv balance add2")

        STEP(2, "from address1 send Token to address4 - Fee PRV auto estimated")
        step2_result = self.shard0.send_customTokenTransaction(self.test_data["s00_addr1"][0],
                                                               self.test_data["s02_addr4"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=0,
                                                               token_fee=self.test_data["token_fee"],
                                                               token_privacy=0)
        INFO("transaction id: " + step2_result[0])
        assert_true(step2_result[0] != 'Can not create tx', step2_result[1], "make successfull transaction")

        STEP(3, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(step2_result[0])

        self.shard2ws.createConnection()
        ws_res3 = self.shard2ws.subcribeCrossCustomTokenPrivacyByPrivatekey(self.test_data["s02_addr4"][0])

        STEP(4, "check address1 & 4 balance after sent")
        balance1a, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1a))
        # Balance after = balance before - amount - fee
        assert_true( balance1a == balance1b - self.test_data["token_amount"] - self.test_data["token_fee"],"sender token balance incorrect")

        balance2a, _ = self.shard2.get_customTokenBalance(self.test_data["s02_addr4"][0], test_sendToken.token_id)
        INFO("addr3_token_balance: " + str(balance2a))
        # Balance after = balance before + amount
        assert_true( balance2a == balance2b + self.test_data["token_amount"],"receiver token balance incorrect")

        step4_balancePRV_add1 = self.shard0.getBalance(self.test_data["s00_addr1"][0])
        INFO("add1_prv_balance : " + str(step4_balancePRV_add1))
        assert_true(step4_balancePRV_add1 == step1_balancePRV_add1 - ws_res[2],
                    "incorrect prv balance of the address 1 ")

        step4_balancePRV_add4 = self.shard2.getBalance(self.test_data["s02_addr4"][0])
        INFO("add4_prv_balance : " + str(step4_balancePRV_add4))
        assert_true(step4_balancePRV_add4 == step1_balancePRV_add4,
                    "incorrect prv balance of the address 4 ")

        STEP(5, "Check transaction privacy")
        INFO("Check transaction prv_privacy")
        step5_result_prv = self.shard0.check_is_privacy_prv(step2_result[0])
        assert_true(step5_result_prv[1] == "noprivacy", "info value PRV must be  no privacy",
                    "info value PRV is not privacy")

        INFO("Check transaction token privacy")
        step5_result_token = self.shard0.check_is_privacy_token(step2_result[0])
        assert_true(step5_result_token[1] == "noprivacy", "info value token  must be no privacy",
                    "info value token is not privacy")

    @pytest.mark.run
    def test_09_sendToken_Privacy_Xshard_tokenFee(self):
        print('''
              Verify send Token to another address XShard successfully
              Fee: token fee
              Token_privacy = 1
              PRV_privacy =0
              ''')

        STEP(1, "get address1 and address3 balance before sending")
        balance1b, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", "get wrong token balance add1")

        step1_balancePRV_add1 = self.shard0.getBalance(self.test_data["s00_addr1"][0])
        INFO("add1_prv_balance : " + str(step1_balancePRV_add1))
        assert_true(step1_balancePRV_add1 != "Invalid parameters", "get wrong prv balance add1")

        balance2b, _ = self.shard1.get_customTokenBalance(self.test_data["s01_addr3"][0], test_sendToken.token_id)
        INFO("addr3_token_balance: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get wrong token balance add2")

        step1_balancePRV_add3 = self.shard1.getBalance(self.test_data["s01_addr3"][0])
        INFO("add3_prv_balance : " + str(step1_balancePRV_add3))
        assert_true(step1_balancePRV_add3 != "Invalid parameters", "get wrong prv balance add2")

        STEP(2, "from address1 send Token to address3 - Fee PRV auto estimated")
        step2_result = self.shard0.send_customTokenTransaction(self.test_data["s00_addr1"][0],
                                                               self.test_data["s01_addr3"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=0,
                                                               token_fee=self.test_data["token_fee"],
                                                               token_privacy=1)
        INFO("transaction id: " + step2_result[0])
        assert_true(step2_result[0] != 'Can not create tx', step2_result[1], "make successfull transaction")

        STEP(3, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(step2_result[0])

        self.shard1ws.createConnection()
        ws_res3 = self.shard1ws.subcribeCrossCustomTokenPrivacyByPrivatekey(self.test_data["s01_addr3"][0])

        STEP(4, "check address1 & 3 balance after sent")
        balance1a, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1a))
        # Balance after = balance before - amount -fee
        assert_true(balance1a == balance1b - self.test_data["token_amount"] - self.test_data["token_fee"],"sender token balance incorrect")

        balance2a, _ = self.shard1.get_customTokenBalance(self.test_data["s01_addr3"][0], test_sendToken.token_id)
        for i in range(1, 10):
            balance2a_temp, _ = self.shard1.get_customTokenBalance(self.test_data["s01_addr3"][0],
                                                                   test_sendToken.token_id)
            if balance2a_temp > balance2a:
                balance2a = balance2a_temp
                break
            else:
                WAIT(15)
        INFO("addr3_token_balance: " + str(balance2a))
        # Balance after = balance before + amount
        assert_true( balance2a == balance2b + self.test_data["token_amount"],"receiver token balance incorrect")

        step4_balancePRV_add3 = self.shard1.getBalance(self.test_data["s01_addr3"][0])
        INFO("add3_prv_balance : " + str(step4_balancePRV_add3))
        assert_true(step4_balancePRV_add3 == step1_balancePRV_add3,
                    "incorrect prv balance of the address 3 ")

        step4_balancePRV_add1 = self.shard0.getBalance(self.test_data["s00_addr1"][0])
        INFO("add1_prv_balance : " + str(step4_balancePRV_add1))
        assert_true(step4_balancePRV_add1 == step1_balancePRV_add1 - ws_res[2],
                    "incorrect prv balance of the address 1 ")

        STEP(5, "Check transaction privacy")
        INFO("Check transaction prv_privacy")
        step5_result_prv = self.shard0.check_is_privacy_prv(step2_result[0])
        assert_true(step5_result_prv[1] == "noprivacy", "info value PRV must be  no privacy",
                    "info value PRV is not privacy")

        INFO("Check transaction token privacy")
        step5_result_token = self.shard0.check_is_privacy_token(step2_result[0])
        assert_true(step5_result_token[1] == "privacy", "info value token  must be privacy",
                    "info value token is privacy")

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
        balance1b, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", "get wrong token balance add1")

        step1_balancePRV_add1 = self.shard0.getBalance(self.test_data["s00_addr1"][0])
        INFO("add1_prv_balance : " + str(step1_balancePRV_add1))
        assert_true(step1_balancePRV_add1 != "Invalid parameters", "get wrong prv balance add1")

        balance2b, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr2"][0], test_sendToken.token_id)
        INFO("addr2_token_balance: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get wrong token balance add2")

        step1_balancePRV_add2 = self.shard0.getBalance(self.test_data["s00_addr2"][0])
        INFO("add2_prv_balance : " + str(step1_balancePRV_add2))
        assert_true(step1_balancePRV_add2 != "Invalid parameters", "get wrong prv balance add2")

        STEP(2, "from address1 send Token to address2 - Fee PRV auto estimated")
        step2_result = self.shard0.send_customTokenTransaction(self.test_data["s00_addr1"][0],
                                                               self.test_data["s00_addr2"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=-1,
                                                               token_fee=self.test_data["token_fee"],
                                                               prv_amount=self.test_data["prv_amount"], token_privacy=1,
                                                               prv_privacy=1)
        INFO("transaction id: " + step2_result[0])
        assert_true(step2_result[0] != 'Can not create tx', step2_result[1], "make successfull transaction")

        STEP(3, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(step2_result[0])

        STEP(4, "check address1 & 2 balance after sent")
        balance1a, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1a))
        # Balance after = balance before - amount - fee
        assert_true( balance1a == balance1b - self.test_data["token_amount"] - self.test_data["token_fee"],"sender token balance incorrect")

        balance2a, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr2"][0], test_sendToken.token_id)
        INFO("addr2_token_balance: " + str(balance2a))
        # Balance after = balance before + amount
        assert_true( balance2a == balance2b + self.test_data["token_amount"],"receiver token balance incorrect")

        step4_balancePRV_add1 = self.shard0.getBalance(self.test_data["s00_addr1"][0])
        INFO("add1_prv_balance : " + str(step4_balancePRV_add1))
        assert_true(step4_balancePRV_add1 == step1_balancePRV_add1 - ws_res[2] - self.test_data["prv_amount"],
                    "incorrect prv balance of the address 1 ")

        step4_balancePRV_add2 = self.shard0.getBalance(self.test_data["s00_addr2"][0])
        INFO("add2_prv_balance : " + str(step4_balancePRV_add2))
        assert_true(step4_balancePRV_add2 == step1_balancePRV_add2 + self.test_data["prv_amount"],
                    "incorrect prv balance of the address 2 ")

        STEP(5, "Check transaction privacy")
        INFO("Check transaction prv_privacy")
        step5_result_prv = self.shard0.check_is_privacy_prv(step2_result[0])
        assert_true(step5_result_prv[1] == "privacy", "info value PRV must be privacy",
                    "info value PRV is privacy")

        INFO("Check transaction token privacy")
        step5_result_token = self.shard0.check_is_privacy_token(step2_result[0])
        assert_true(step5_result_token[1] == "privacy", "info value token  must be privacy",
                    "info value token is privacy")

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
        balance1b, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", "get wrong token balance add1")

        step1_balancePRV_add1 = self.shard0.getBalance(self.test_data["s00_addr1"][0])
        INFO("add1_prv_balance : " + str(step1_balancePRV_add1))
        assert_true(step1_balancePRV_add1 != "Invalid parameters", "get wrong prv balance add1")

        balance2b, _ = self.shard1.get_customTokenBalance(self.test_data["s01_addr3"][0], test_sendToken.token_id)
        INFO("addr3_token_balance: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get wrong token balance add3")

        step1_balancePRV_add3 = self.shard1.getBalance(self.test_data["s01_addr3"][0])
        INFO("add3_prv_balance : " + str(step1_balancePRV_add3))
        assert_true(step1_balancePRV_add3 != "Invalid parameters", "get wrong prv balance add3")

        STEP(2, "from address1 send Token to address3 - Fee PRV auto estimated")
        step2_result = self.shard0.send_customTokenTransaction(self.test_data["s00_addr1"][0],
                                                               self.test_data["s01_addr3"][1], test_sendToken.token_id,
                                                               self.test_data["token_amount"], prv_fee=-1,
                                                               token_fee=self.test_data["token_fee"],
                                                               prv_amount=self.test_data["prv_amount"], prv_privacy=1,
                                                               token_privacy=1)
        INFO("transaction id: " + step2_result[0])
        assert_true(step2_result[0] != 'Can not create tx', step2_result[1], "make successfull transaction")

        STEP(3, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(step2_result[0])

        self.shard1ws.createConnection()
        ws_res3 = self.shard1ws.subcribeCrossCustomTokenPrivacyByPrivatekey(self.test_data["s01_addr3"][0])

        STEP(4, "check address1 & 3 balance after sent")
        balance1a, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(balance1a))
        # Balance after = balance before - amount -fee
        assert_true( balance1a == balance1b - self.test_data["token_amount"] - self.test_data["token_fee"],"sender token balance incorrect")

        balance2a, _ = self.shard1.get_customTokenBalance(self.test_data["s01_addr3"][0], test_sendToken.token_id)
        for i in range(1, 10):
            balance2a_temp, _ = self.shard1.get_customTokenBalance(self.test_data["s01_addr3"][0],
                                                                   test_sendToken.token_id)
            if balance2a_temp > balance2a:
                balance2a = balance2a_temp
                break
            else:
                WAIT(10)
        INFO("addr3_token_balance: " + str(balance2a))
        # Balance after = balance before + amount
        assert_true( balance2a == balance2b + self.test_data["token_amount"],"receiver token balance incorrect")

        step4_balancePRV_add3 = self.shard1.getBalance(self.test_data["s01_addr3"][0])
        INFO("add3_prv_balance : " + str(step4_balancePRV_add3))
        assert_true(step4_balancePRV_add3 == step1_balancePRV_add3 + self.test_data["prv_amount"],
                    "incorrect prv balance of the address 3 ")

        step4_balancePRV_add1 = self.shard0.getBalance(self.test_data["s00_addr1"][0])
        INFO("add1_prv_balance : " + str(step4_balancePRV_add1))
        assert_true(step4_balancePRV_add1 == step1_balancePRV_add1 - ws_res[2] - self.test_data["prv_amount"],
                    "incorrect prv balance of the address 1 ")

        STEP(5, "Check transaction privacy")
        INFO("Check transaction prv_privacy")
        step5_result_prv = self.shard0.check_is_privacy_prv(step2_result[0])
        assert_true(step5_result_prv[1] == "privacy", "info value PRV must be privacy",
                    "info value PRV is privacy")

        INFO("Check transaction token privacy")
        step5_result_token = self.shard0.check_is_privacy_token(step2_result[0])
        assert_true(step5_result_token[1] == "privacy", "info value token  must be privacy",
                    "info value token is privacy")

    @pytest.mark.run
    def est_12_send_2Xshard_tx_1beaconblock(self):
        print("""
                Verify send Token Xshard, from Shard_n+1 Shard_n+2 to Shard_n at the same time
                Fee: PRV (fixed * transaction size KB)
                Fee: pToken (fixed)
                """)

        STEP(1, "get address1, 3 and 4 balance before sending")
        balance1b, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
        INFO("addr1_balance: " + str(balance1b))
        assert_true( balance1b != "Invalid parameters","something wrong")

        balance3b, _ = self.shard1.get_customTokenBalance(self.test_data["s01_addr3"][0], test_sendToken.token_id)
        INFO("addr3_balance: " + str(balance3b))
        assert_true( balance3b != "Invalid parameters","something wrong")
        assert_true(balance3b > 0, "addr3 balance = 0")

        balance4b, _ = self.shard2.get_customTokenBalance(self.test_data["s02_addr4"][0], test_sendToken.token_id)
        INFO("addr4_balance: " + str(balance4b))
        assert_true( balance4b != "Invalid parameters","something wrong")
        assert_true(balance4b > 0, "addr4 balance = 0")

        STEP(2, "from address3 & 4 send all Token to address1")
        tx_id3 = self.shard1.send_customTokenTransaction(self.test_data["s01_addr3"][0],
                                                         self.test_data["s00_addr1"][1], test_sendToken.token_id,
                                                         balance3b - 10, 0, 10)
        tx_id4 = self.shard2.send_customTokenTransaction(self.test_data["s02_addr4"][0],
                                                         self.test_data["s00_addr1"][1], test_sendToken.token_id,
                                                         balance4b - 10, 0, 10)
        INFO("transaction id shard1: " + tx_id3[0] + str(tx_id3[1]))

        INFO("transaction id shard2: " + tx_id4[0] + str(tx_id4[1]))
        assert_true( tx_id3[0] != 'Can not create tx',"something wrong")
        assert_true( tx_id4[0] != 'Can not create tx',"something wrong")

        STEP(3, "subcribe transaction")
        self.shard1ws.createConnection()
        ws_res13 = self.shard1ws.subcribePendingTransaction(tx_id3[0])
        self.shard2ws.createConnection()
        ws_res23 = self.shard2ws.subcribePendingTransaction(tx_id4[0])
        self.shard0ws.createConnection()
        ws_res03 = self.shard0ws.subcribeCrossCustomTokenPrivacyByPrivatekey(self.test_data["s00_addr1"][0])

        STEP(4, "check address3 & 4 balance")
        balance4a = "null"
        balance3a = "null"
        for _ in range(0, 6):
            balance4a, _ = self.shard2.get_customTokenBalance(self.test_data["s02_addr4"][0], test_sendToken.token_id)
            balance3a, _ = self.shard1.get_customTokenBalance(self.test_data["s01_addr3"][0], test_sendToken.token_id)
            if balance4a == 0 & balance3a == 0:
                break
            WAIT(10)

        INFO("addr3_balance: " + str(balance3a))
        INFO("addr4_balance: " + str(balance4a))
        assert_true( balance3a == 0,"something wrong")
        assert_true( balance4a == 0,"something wrong")

        STEP(5, "check address1 balance")
        balance1a = "null"
        for _ in range(0, 6):
            balance1a, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
            if balance1a == balance1b + balance3b + balance4b - 10 - 10:
                break
            WAIT(10)
        INFO("addr1_balance: " + str(balance1a))
        # Balance after = balance before + amount + amount
        assert_true(balance1a == balance1b + balance3b + balance4b - 10 - 10,
                    "Balance addr1 invalid: %d != %d + %d + %d" % (balance1a, balance1b, balance3b, balance4b))

    @pytest.mark.run
    def test_13_sendToken_Xshard_insufficient_fund(self):
        """
        Verify send Token to another address:
        - Not enough coin (insufficient fund)
        - Wrong input transaction
        - Valid transaction
        """
        STEP(1, "get address2 and address3 balance before sending")
        step1_token_add3, _ = self.shard2.get_customTokenBalance(self.test_data["s01_addr3"][0],
                                                                 test_sendToken.token_id)
        INFO("addr3_token_balance: " + str(step1_token_add3))
        assert_true(step1_token_add3 != "Invalid parameters", "get wrong token balance add3")

        step1_PRV_add3 = self.shard2.getBalance(self.test_data["s01_addr3"][0])
        INFO("add3_prv_balance : " + str(step1_PRV_add3))
        assert_true(step1_PRV_add3 != "Invalid parameters", "get wrong prv balance add3")

        step1_token_add2, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr2"][0],
                                                                 test_sendToken.token_id)
        INFO("addr2_token_balance: " + str(step1_token_add2))
        assert_true(step1_token_add2 != "Invalid parameters", "get wrong token balance add2")

        step1_PRV_add2 = self.shard0.getBalance(self.test_data["s00_addr2"][0])
        INFO("add2_prv_balance : " + str(step1_PRV_add2))
        assert_true(step1_PRV_add2 != "Invalid parameters", "get wrong prv balance add2")

        STEP(2, "From address3 send prv to address2 - Not enough coin")
        # send current balance + 10
        step2_result = self.shard2.send_customTokenTransaction(self.test_data["s01_addr3"][0],
                                                               self.test_data["s00_addr2"][1], self.token_id,
                                                               amount_customToken=step1_token_add3 + 10)
        INFO("Expecting: " + step2_result[0])
        assert_true(step2_result[0] == 'Can not create tx', "something went wrong, this tx must failed",
                    "make successfull transaction")
        assert_true(re.search(r'Not enough coin', step2_result[1]), "something went so wrong")

        # breakpoint()

        STEP(3, "From address3 send prv to address2 - Wrong input transaction")
        # send current balance (lacking of fee)
        step3_result = self.shard2.send_customTokenTransaction(self.test_data["s01_addr3"][0],
                                                               self.test_data["s00_addr2"][1], self.token_id,
                                                               amount_customToken=step1_token_add3,
                                                               token_fee=self.test_data["token_fee"])
        INFO("Expecting: " + step3_result[0])
        assert_true(step3_result[0] == 'Can not create tx', "something went wrong, this tx must failed",
                    "make successfull transaction")

        # breakpoint()

        STEP(4, "From address2 send prv to address3 - success")
        # send current balance - fee (100)
        estimated_fee = 10
        step4_result = self.shard2.send_customTokenTransaction(self.test_data["s01_addr3"][0],
                                                               self.test_data["s00_addr2"][1], self.token_id,
                                                               amount_customToken=step1_token_add3 - estimated_fee,
                                                               token_fee=estimated_fee)
        assert_true(step4_result[0] != 'Can not create tx', step4_result[1])
        INFO("TxID: " + step4_result[0])

        STEP(5, "Subcribe transaction")
        self.shard2ws.createConnection()
        ws_res6 = self.shard2ws.subcribePendingTransaction(step4_result[0])

        self.shard0ws.createConnection()
        ws_res7 = self.shard0ws.subcribeCrossCustomTokenPrivacyByPrivatekey(self.test_data["s00_addr2"][0])

        STEP(6, "Check address 3 balance")
        step6_result = self.shard2.get_customTokenBalance(self.test_data["s01_addr3"][0], self.token_id)
        INFO("addr3_balance: " + str(step6_result[0]))
        assert_true( step6_result[0] == 0,"sender token balance incorrect")

        STEP(7, "Check address 2 balance")
        step7_result = self.shard0.get_customTokenBalance(self.test_data["s00_addr2"][0], self.token_id)
        for i in range(1, 10):
            step7_result_temp, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr2"][0], self.token_id)
            if step7_result_temp > step7_result[0]:
                step7_result[0] = step7_result_temp
                break
            else:
                WAIT(10)
        INFO("Addr2_balance: " + str(step7_result[0]))
        assert_true( step7_result[0] == step1_token_add2 + step1_token_add3 - estimated_fee,"receiver token balance incorrect")

    @pytest.mark.run
    def test_14_sendToken_1shard_insufficient_fund(self):
        """
        Verify send Token to another address:
        - Not enough coin (insufficient fund)
        - Wrong input transaction
        - Valid transaction
        """
        STEP(1, "get address1 and address2 balance before sending")
        step1_token_add2, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr2"][0],
                                                                 test_sendToken.token_id)
        INFO("addr2_token_balance: " + str(step1_token_add2))
        assert_true(step1_token_add2 != "Invalid parameters", "get wrong token balance add2")

        step1_PRV_add2 = self.shard0.getBalance(self.test_data["s00_addr2"][0])
        INFO("add2_prv_balance : " + str(step1_PRV_add2))
        assert_true(step1_PRV_add2 != "Invalid parameters", "get wrong prv balance add2")

        step1_token_add1, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0],
                                                                 test_sendToken.token_id)
        INFO("addr1_token_balance: " + str(step1_token_add1))
        assert_true(step1_token_add1 != "Invalid parameters", "get wrong token balance add1")

        step1_PRV_add1 = self.shard0.getBalance(self.test_data["s00_addr1"][0])
        INFO("add1_prv_balance : " + str(step1_PRV_add1))
        assert_true(step1_PRV_add1 != "Invalid parameters", "get wrong prv balance add1")

        STEP(2, "From address2 send prv to address1 - Not enough coin")
        # send current balance + 10
        step2_result = self.shard0.send_customTokenTransaction(self.test_data["s00_addr2"][0],
                                                               self.test_data["s00_addr1"][1], self.token_id,
                                                               amount_customToken=step1_token_add2 + 10)
        INFO("Expecting: " + step2_result[0])
        assert_true(step2_result[0] == 'Can not create tx', "something went wrong, this tx must failed",
                    "make successfull transaction")
        assert_true(re.search(r'Not enough coin', step2_result[1]), "something went so wrong")

        # breakpoint()

        STEP(3, "From address2 send prv to address1 - Wrong input transaction")
        # send current balance (lacking of fee)
        step3_result = self.shard0.send_customTokenTransaction(self.test_data["s00_addr2"][0],
                                                               self.test_data["s00_addr1"][1], self.token_id,
                                                               amount_customToken=step1_token_add2,
                                                               token_fee=self.test_data["token_fee"])
        INFO("Expecting: " + step3_result[0])
        assert_true(step3_result[0] == 'Can not create tx', "something went wrong, this tx must failed",
                    "make successfull transaction")

        # breakpoint()

        STEP(4, "From address2 send prv to address1 - success")
        # send current balance - fee (10)
        estimated_fee = 10
        step4_result = self.shard0.send_customTokenTransaction(self.test_data["s00_addr2"][0],
                                                               self.test_data["s00_addr1"][1], self.token_id,
                                                               amount_customToken=step1_token_add2 - estimated_fee,
                                                               token_fee=10)
        step4_result[0] != 'Can not create tx'
        assert_true(step4_result[0] != 'Can not create tx', step4_result[1])
        INFO("TxID: " + step4_result[0])

        STEP(5, "Subcribe transaction")
        self.shard0ws.createConnection()
        ws_res6 = self.shard0ws.subcribePendingTransaction(step4_result[0])

        STEP(6, "Check address1 balance")
        step6_result = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], self.token_id)
        INFO("addr1_balance: " + str(step6_result))
        assert_true( step6_result[0] == step1_token_add1 + step1_token_add2 - estimated_fee,"sender token balance incorrect")

        STEP(7, "Check address2 balance")
        step7_result = self.shard0.get_customTokenBalance(self.test_data["s00_addr2"][0], self.token_id)
        INFO("Addr2_balance: " + str(step7_result[0]))
        assert_true( step7_result[0] == 0,"receiver token balance incorrect")

    @pytest.mark.run
    def test_15_sendToken_sendPRV_Privacy_Xshard_tokenFee_prvFee_multiOutput(self):
        print('''
                          Verify send Token to multi address XShard successfully
                          Fee: token
                          Fee : auto PRV
                          Token_privacy = 1
                          Prv_privacy =1

                          ''')
        output_payment_address = list()
        output_private_address = list()
        for k, v in self.test_data_multi_output.items():
            output_payment_address.append(v[1])
            output_private_address.append(v[0])

        STEP(1, "get sender balance before sending")
        sender_token, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
        INFO("sender_token_balance: " + str(sender_token))
        assert_true(sender_token != "Invalid parameters", "get wrong token balance add1")

        sender_prv = self.shard0.getBalance(self.test_data["s00_addr1"][0])
        INFO("sender_prv_balance : " + str(sender_prv))
        assert_true(sender_prv != "Invalid parameters", "get wrong prv balance add1")

        STEP(2, "get receiver balance before sending")
        list_receiver_prv = list()
        list_receiver_token = list()
        for i in range(0, len(output_private_address)):
            temp_prv = self.shard0.getBalance(output_private_address[i])
            assert_true(temp_prv != "Invalid parameters", "get wrong token balance receiver address " + str(i + 1))
            temp_token, _ = self.shard0.get_customTokenBalance(output_private_address[i], test_sendToken.token_id)
            assert_true(temp_token != "Invalid parameters", "get wrong token balance receiver address " + str(i + 1))
            list_receiver_prv.append(temp_prv)
            INFO("address " + str(i + 1) + " prv balance: " + str(temp_prv))
            list_receiver_token.append(temp_token)
            INFO("address " + str(i + 1) + " token balance: " + str(temp_token))

        STEP(3, "send PRV and Token - Fee PRV auto estimated")
        token_amount = 10  # amount token send for each address
        prv_amount = 1  # amount prv send for each address
        tx_result = self.shard0.send_customTokenTransaction_multioutput(self.test_data["s00_addr1"][0],
                                                                        output_payment_address,
                                                                        test_sendToken.token_id,
                                                                        token_amount=token_amount, prv_fee=-1,
                                                                        token_fee=self.test_data["token_fee"],
                                                                        prv_amount=prv_amount,
                                                                        token_privacy=1,
                                                                        prv_privacy=1)
        INFO("transaction id: " + tx_result[0])
        assert_true(tx_result[0] != 'Can not create tx', tx_result[1], "make successfull transaction")

        STEP(4, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(tx_result[0])

        STEP(5, "check sender balance after sent")
        sender_token_output, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0],
                                                                    test_sendToken.token_id)
        INFO("sender_token_balance: " + str(sender_token_output))
        # Balance token after = balance before - amount * n - fee
        assert_true(sender_token_output == sender_token - (token_amount * len(output_private_address)) - self.test_data[
            "token_fee"],
                    "sender token balance incorrect", "sender token balance correct")

        sender_prv_output = self.shard0.getBalance(self.test_data["s00_addr1"][0])
        INFO("sender_prv_balance : " + str(sender_prv_output))
        # Balance prv after = balance before - amount * n - fee
        assert_true(sender_prv_output == sender_prv - ws_res[2] - (prv_amount * len(output_private_address)),
                    "sender prv balance incorrect ", "sender prv balance correct")

        STEP(6, "check receiver balance ")
        for i in range(0, len(output_private_address)):
            temp_prv = self.shard0.getBalance(output_private_address[i])
            temp_token, _ = self.shard0.get_customTokenBalance(output_private_address[i],
                                                               test_sendToken.token_id)
            for j in range(0, 10):
                temp, _ = self.shard0.get_customTokenBalance(output_private_address[i],
                                                             test_sendToken.token_id)
                if temp > temp_token:
                    temp_token = temp
                    break
                else:
                    WAIT(10)
            INFO("token balance address " + str(i + 1) + " after send: " + str(temp_token))
            # Balance after = balance before + amount
            assert_true(temp_token == list_receiver_token[i] + token_amount,
                        "token balance addresss " + str(i + 1) + " incorrect",
                        "token balance addresss " + str(i + 1) + " correct")
            for t in range(0, 10):
                temp = self.shard0.getBalance(output_private_address[i])
                if temp > temp_prv:
                    temp_prv = temp
                    break
                else:
                    WAIT(10)
            INFO("prv balance address " + str(i + 1) + " after send: " + str(temp_prv))
            # Balance after = balance before + amount
            assert_true(temp_prv == list_receiver_prv[i] + prv_amount,
                        "prv balance addresss " + str(i + 1) + " incorrect",
                        "prv balance addresss " + str(i + 1) + " correct")

        STEP(7, "Check transaction privacy")
        INFO("Check transaction prv_privacy")
        check_privacy_prv = self.shard0.check_is_privacy_prv(tx_result[0])
        assert_true(check_privacy_prv[1] == "privacy", "info value PRV must be privacy",
                    "info value PRV is privacy")

        INFO("Check transaction token privacy")
        check_privacy_token = self.shard0.check_is_privacy_token(tx_result[0])
        assert_true(check_privacy_token[1] == "privacy", "info value token  must be privacy",
                    "info value token is privacy")

    @pytest.mark.run
    def est_xx_burn_pToken(self):
        print("\n")
        STEP(0, "check address1 balance")
        balance1b, _ = self.shard0.get_customTokenBalance(self.test_data["s00_addr1"][0], test_sendToken.token_id)
        INFO("addr1_balance: " + str(balance1b))

        STEP(1, "Burn token")
        txid, shard = self.shard0.send_customTokenTransaction(self.test_data['s00_addr1'][0],
                                                              self.test_data['burning_addr'],
                                                              test_sendToken.token_id, balance1b)
        assert_true(len(txid) == 64, "Burning not success")

        STEP(2, "subcribe transaction")
        self.shard0ws.createConnection()
        self.shard0ws.subcribePendingTransaction(txid)

        STEP(3, "Get custom token balance")
        token_balance, _ = self.shard0.get_customTokenBalance(self.test_data['s00_addr1'][0], test_sendToken.token_id)
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
