import math
import unittest

import pytest

import topology.NodeList as NodeList
from libs.AutoLog import INFO, WAIT, STEP, assert_true
from libs.DecentralizedExchange import DEX
from libs.Transaction import Transaction


class test_dex(unittest.TestCase):
    print(
        """
        TEST SUITE DECENTRALIZED EXCHANGE
        """)
    testData = {
        "count": 100,
        "tx_fee": 5,
        "trading_fee": 6,
        "slippage": 7,
        "ApETH": "4129f4ca2b2eba286a3bd1b96716d64e0bc02bd2cc1837776b66f67eb5797d79",
        "ApUSDT": "85d584ae672a733067b3500381a783099f48ce52d4993774e6a1dad6784fc316",
        "ApBTC": "ae438b237c6fb6bd19dcc12b9c0d71ea9aeaaf0c389ce081a099c1affdca9b85",
        "ApUSDT_e": "1413cd254dbbe7edb06f2de2ac95ca2582237fa6b482e2a14b25b074262e7d41",
        "ApBTC_e": "0b0d10498475c32848b9352a756a06e6dac3cf65a2b05d2398621e111e8e794e",
        "amount_contributionApUSDT": 59214,
        "amount_contributionApBTC": 21348,
        "token_ownerPrivateKey": [
            "112t8rnX6ThEU1nYpyYeerYU47EmrTA1AWJguAAbJLyot8ETdUydT4yT4zahyyme78bAAbNZmhzHGva57b7XTf6BFiA9uzGiQMdxFfSGDdwi",
            "112t8rnX5E2Mkqywuid4r4Nb2XTeLu3NJda43cuUM1ck2brpHrufi4Vi42EGybFhzfmouNbej81YJVoWewJqbR4rPhq2H945BXCLS2aDLBTA",
        ],
        "token_ownerPaymentAddress": [
            "12RxiiobVPEoo4djdueSsDcT79BgcBQtiZfwMTwTt9a6tfN9gEbsor7BgxsHxb8DeufMo2BTDxn11wnm3ANDHGL1e8Y7NXWZmQLMiLC",
            "12RxERBySmquLtM1R1Dk2s7J4LyPxqHxcZ956kupQX3FPhVo2KtoUYJWKet2nWqWqSh3asWmgGTYsvz3jX73HqD8Jr2LwhjhJfpG756",
        ],
        "privateKey": [
            "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"
        ],
        "paymentAddr": [
            "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"

        ]
    }
    fullnode = DEX(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['rpc'])
    fullnode_trx = Transaction(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['rpc'])

    @pytest.mark.run
    def est_DEX01_contribute(self):
        print("\n")
        STEP(0, "Checking env - checking waiting contribution list")
        assert_true(self.fullnode.get_waitingContribution(self.testData['ApUSDT'],
                                                          self.testData['token_ownerPaymentAddress'][0]) == False,
                    "Found ApUSDT", "NOT Found ApUSDT")
        assert_true(self.fullnode.get_waitingContribution(self.testData['ApBTC'],
                                                          self.testData['token_ownerPaymentAddress'][0]) == False,
                    "Found ApBTC", "NOT Found ApBTC")
        token1_balance_B = self.fullnode_trx.get_customTokenBalance(self.testData['token_ownerPrivateKey'][0],
                                                                    self.testData['ApUSDT'])
        token2_balance_B = self.fullnode_trx.get_customTokenBalance(self.testData['token_ownerPrivateKey'][0],
                                                                    self.testData['ApBTC'])

        INFO("ApUSDT balance before contribution: " + str(token1_balance_B))
        INFO("ApBTC balance before contribution: " + str(token2_balance_B))

        STEP(1, "Contribute ApUSDT")
        contribute_token1 = self.fullnode.contribute_token(self.testData['token_ownerPrivateKey'][0],
                                                           self.testData['token_ownerPaymentAddress'][0],
                                                           self.testData['ApUSDT'],
                                                           self.testData['amount_contributionApUSDT'], "usdtp5_1btcp")
        INFO("Contribute ApUSDT Success, TxID: " + contribute_token1)

        STEP(2, "Verifying contribution ApUSDT")
        step2_result = False
        for i in range(0, 10):
            WAIT(10)
            if self.fullnode.get_waitingContribution(self.testData['ApUSDT'],
                                                     self.testData['token_ownerPaymentAddress'][0]):
                step2_result = True
                INFO("The ApUSDT found in waiting contribution list")
                break
        assert_true(step2_result == True, "The ApUSDT NOT found in waiting contribution list")

        STEP(3, "Contribute ApBTC")
        contribute_token2 = self.fullnode.contribute_token(self.testData['token_ownerPrivateKey'][0],
                                                           self.testData['token_ownerPaymentAddress'][0],
                                                           self.testData['ApBTC'],
                                                           self.testData['amount_contributionApBTC'], "usdtp5_1btcp")
        INFO("Contribute ApUSDT Success, TxID: " + contribute_token2)

        STEP(4, "Verifying ApUSDT disappeared in waiting list")
        step4_result = False
        for i in range(0, 10):
            WAIT(10)
            if not self.fullnode.get_waitingContribution(self.testData['ApUSDT'],
                                                         self.testData['token_ownerPaymentAddress'][0]):
                step4_result = True
                INFO("The ApUSDT NOT found in waiting contribution list")
                break
        assert_true(step4_result == True, "The ApUSDT is still found in waiting contribution list")

        token1_balance_A = self.fullnode_trx.get_customTokenBalance(self.testData['token_ownerPrivateKey'][0],
                                                                    self.testData['ApUSDT'])
        token2_balance_A = self.fullnode_trx.get_customTokenBalance(self.testData['token_ownerPrivateKey'][0],
                                                                    self.testData['ApBTC'])
        INFO("ApUSDT balance after contribution: " + str(token1_balance_A))
        INFO("ApBTC balance after contribution: " + str(token2_balance_A))

        assert_true((token1_balance_A + self.testData['amount_contributionApUSDT']) == token1_balance_B,
                    "ApUSDT balance is wrong")
        assert_true((token2_balance_A + self.testData[
            'amount_contributionApBTC'] == token2_balance_B), "ApBTC balance is wrong")

        STEP(5, "Check rate ApUSDT vs ApBTC")
        rate = self.fullnode.get_latestRate(self.testData["ApUSDT"], self.testData["ApBTC"])
        INFO("rate pUSDT vs pBTC" + str(rate))

    @pytest.mark.run
    def test_DEX02_bulkSwap(self):
        print("\n")
        STEP(0, "Checking balance")
        token1_balance_B = []
        token2_balance_B = []
        token1_balance_A = []
        token2_balance_A = []
        privatekey_alias = []
        trade_amountApBTC = 2

        for pk in self.testData['privateKey']:
            token1_balance_B.append(self.fullnode_trx.get_customTokenBalance(pk,
                                                                             self.testData['ApUSDT']))
            token2_balance_temp = self.fullnode_trx.get_customTokenBalance(pk,
                                                                           self.testData['ApBTC'])
            # print(token2_balance_temp)
            # print(trade_amountApBTC)
            # assert_true(token2_balance_temp > trade_amountApBTC,
            #             "This " + pk[-6:] + " balance BTC less than trading amount")
            token2_balance_B.append(token2_balance_temp)
            privatekey_alias.append(pk[-6:])

        INFO("Privatekey_alias                  : " + str(privatekey_alias))
        INFO("ApUSDT balance before trade       : " + str(token1_balance_B))
        INFO("ApBTC balance before trade        : " + str(token2_balance_B))
        rate_B = self.fullnode.get_latestRate(self.testData["ApUSDT"], self.testData["ApBTC"])
        INFO("Rate pUSDT vs pBTC - Before Trade : " + str(rate_B))

        # breakpoint()

        STEP(2, "trade BTC at same time")
        txid_list = []
        for i in range(0, len(privatekey_alias)):
            trade_txid = self.fullnode.trade_token(self.testData['privateKey'][i], self.testData['paymentAddr'][i],
                                                   self.testData['ApBTC'], trade_amountApBTC, self.testData['ApUSDT'],
                                                   1, 0)
            txid_list.append(trade_txid)
        INFO("Transaction id list               : " + str(txid_list))

        STEP(3, "Wait for Tx to be confirmed")
        step3_result = False
        for txid in txid_list:
            for i in range(0, 10):
                if self.fullnode_trx.get_txbyhash(txid) != "":
                    step3_result = True
                    INFO("the " + txid + " is confirmed")
                    break
                WAIT(10)
            assert_true(step3_result == True, "The " + txid + " is NOT yet confirmed")

        STEP(4, "CHECK BALANCE AFTER")
        for i in range(0, len(self.testData['privateKey'])):
            tmp_token1Balance_A = False
            for _ in range(0, 10):
                tmp_token1Balance_A = self.fullnode_trx.get_customTokenBalance(self.testData['privateKey'][i],
                                                                               self.testData['ApUSDT'])
                if tmp_token1Balance_A > token1_balance_B[i]:
                    break
                if i < 3:
                    WAIT(10)
            if tmp_token1Balance_A is not False:
                token1_balance_A.append(tmp_token1Balance_A)
                token2_balance_A.append(self.fullnode_trx.get_customTokenBalance(self.testData['privateKey'][i],
                                                                                 self.testData['ApBTC']))
            else:
                # ERROR("Wait time expired, ApUSDT did NOT increasse")
                assert_true(tmp_token1Balance_A == True, "Wait time expired, ApUSDT did NOT increase")

        INFO("Privatekey_alias                  : " + str(privatekey_alias))
        INFO("ApUSDT balance after trade        : " + str(token1_balance_A))
        INFO("ApBTC balance after trade         : " + str(token2_balance_A))

        STEP(5, "Check rate ApUSDT vs ApBTC")
        rate_A = self.fullnode.get_latestRate(self.testData["ApUSDT"], self.testData["ApBTC"])
        INFO("rate pUSDT vs pBTC - After Trade  : " + str(rate_A))

        STEP(6, "Double check the algorithm ")
        result_ApUSDT = []
        result_ApBTC = []
        result_rate = rate_B
        # received_amountApUSDT = trade_amountApBTC * (rate_B[0] / rate_B[1])
        # print("-received_amountApUSDT before math.floor: " + str(received_amountApUSDT))
        # received_amountApUSDT = math.floor(received_amountApUSDT)

        received_amountApUSDT = rate_B[0] - (rate_B[0] * (rate_B[1] / (trade_amountApBTC + rate_B[1])))
        print("-received_amountApUSDT before math.floor: " + str(received_amountApUSDT))
        received_amountApUSDT = math.floor(received_amountApUSDT)

        for i in range(0, len(self.testData['privateKey'])):
            INFO("received_amountApUSDT: " + str(received_amountApUSDT))
            result_rate[0] = result_rate[0] - received_amountApUSDT
            result_rate[1] = result_rate[1] + trade_amountApBTC
            if received_amountApUSDT == token1_balance_A[i] - token1_balance_B[i]:
                result_ApUSDT.append(True)
            else:
                result_ApUSDT.append(False)
            if trade_amountApBTC == token2_balance_B[i] - token2_balance_A[i]:
                result_ApBTC.append(True)
            else:
                result_ApBTC.append(False)
            received_amountApUSDT = result_rate[0] - (
                        result_rate[0] * (result_rate[1] / (trade_amountApBTC + result_rate[1])))
            print("received_amountApUSDT before math.floor: " + str(received_amountApUSDT))
            received_amountApUSDT = math.floor(received_amountApUSDT)

        INFO("result_ApUSDT : " + str(result_ApUSDT))
        INFO("result_ApBTC  : " + str(result_ApBTC))
        assert_true(result_rate == rate_A, "Pair Rate is WRONG after Trade", "Pair Rate is correct")

    def est_DEX03_addLiquidity(self):
        pass

    def est_DEX04_bulkSwap(self, count):
        pass

    def est_DEX05_withdrawalLiquidity(self):
        pass
