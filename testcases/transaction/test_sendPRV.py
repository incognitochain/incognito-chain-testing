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

class test_sendPRV(unittest.TestCase):
    """
    Test case: Send PRV
    """
    test_data = {
        's0_addr1': [
            "112t8rnXVMJJZzfF1naXvfE9nkTKwUwFWFeh8cfEyViG1vpA8A9khJk3mhyB1hDuJ4RbreDTsZpgJK4YcSxdEpXJKMEd8Vmp5UqKWwBcYzxv",
            "12RyJTSL2G8KvjN7SUFuiS9Ek4pvFFze3EMMic31fmXVw8McwYzpKPpxeW6TLsNo1UoPhCHKV3GDRLQwdLF41PED3LQNCLsGNKzmCE5"],
        's0_addr2': [
            "112t8rnX6USJnBzswUeuuanesuEEUGsxE8Pj3kkxkqvGRedUUPyocmtsqETX2WMBSvfBCwwsmMpxonhfQm2N5wy3SrNk11eYxEyDtwuGxw2E",
            "12RwbexYzKJwGaJDdDE7rgLEkNC1dL5cJf4xNaQ29EmpPN52C6oepWiTtQCpyHAoo6ZTHMx2Nt3A8p5jYqpYvbrVYGpVTen1rVstCpr"],
        's1_addr3': [
            "112t8rnXoEWG5H8x1odKxSj6sbLXowTBsVVkAxNWr5WnsbSTDkRiVrSdPy8QfMujntKRYBqywKMJCyhMpdr93T3XiUD5QJR1QFtTpYKpjBEx",
            "12RqmK5woGNeBTy16ouYepSw4QEq28gsv2m81ebcPQ82GgS5S8PHEY37NU2aTacLRruFvjTqKCgffTeMDL83snTYz5zDp1MTLwjVhZS"],
        's2_addr4': [
            "112t8rnZ5UZouZU9nFmYLfpHUp8NrvQkGLPD564mjzNDM8rMp9nc9sXZ6CFxCGEMuvHQpYN7af6KCPJnq9MfEnXQfntbM8hpy9LW8p4qzPxS",
            "12Rw9oesEgd8t5NGrfqxtWTCzh1eDif55miqZ1kFzj5zeQ6UQnNB9JXRn5Vc5QVbBaiFhoYdYPnQZ5tWwcBpse5EJXM3Av6qEV2wspv"],
        's2_addr5': [
            "112t8rnan3pbXtdvfKSk3kti1tFcFpVSq5wp7c3hhLk7E4jQih2zsv8ynjpP1UQivExGwbMf9Ezp9qmKBJuHhNZPAzheqX4WTV8LfrdZY5Mh",
            "12RxCyrWFCkpzfnMcnN8MuDrXkFAsEAkhyn4zHhy3n6CNZPYJ4cNDesBGycwu62PJn8rQ8uLiC5zSYDiXFa9hXtQMUJvVCMT2uUNn8G"],
        's2_addr4_d': [
            "112t8rnZ9qPE7C6RbrK6Ygat1H94kEkYGSd84fAGiU396yQHu8CBHmV1DDHE947d7orfHnDtKA9WCffDk7NS5zUu5CMCUHK8nkRtrv4nw6uu",
            "12Rrk9r3Chmt5Wibkmu2VcFSUffGZbkz2rzMWdmmB3GEu8t8RF4v2wc1gBQtkJFZmPfUP29bSXR4Wn8kDveLQBTBK5Hck9BoGRnuM7n"],
        's2_addr5_d': [
            "112t8rnaK4C17Chu8rEAPXHUaPYNeGz8VsjV7BzdeLA9VBc8oiYwQXNrc6XEABb4uNEfG9LFgvVfi4KQmVpQrwMWph4E1YoVS1m37HwrFDsE",
            "12RtmaJMoRbUCsYxLC4RatP2vWVR3QdZXpbkXR7LwZjVrZfXF46ZNL4QgpCU71SXjz2eCeruA7ZiHM91otTJXzqJiztq5mrdHA35yaf"],
        'prv_amount2': 0.123456789 * 1000000000,
        'prv_amount': 10
    }

    test_data_tuan = {
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
        's2_addr5': [
            "112t8rnhdyiruPke58LNeqwpzxn3cGQsfnS4dqec6P9HWPwNH7VKPgdXw9svDXp5djM4mQrMZnxwW7sjk5NLBkHXC3pJHBMsoqJi8sNUd47G",
            "12S4HcgzM2zQeq41Bh9w8Ce5YETiQitoTZmTjCHLvvbwmoy8S9Py66wBjCqTgziWPbMpWEWPA2jRabwDmTk2TYV4nAzBN3SwjYN4zfE"
        ],
        's3_addr6': [
            "112t8rnY8VF8AAbYMDHMva3HLSzT9dhJjZSaAE1fekSx7u9FNDuY5vYggYF4iB7anapWkkxWhHYTf5zPD25BtTBRE79bWb5dw1nCd6Nn2bDc",
            "12RzjL7P6AS1qaGvP5WMdok4Ni6gD2m3XcwH7xucyaS29Vb6CrmGxXMvSwadConDvUGDn7qYHmy1ZNeGrw3Z2GNQySrRRPYm7KBK9rD"
        ],
        's3_addr7': [
            "112t8rnZmJvmrz9pSojV2uyUETShwNoCKvM6yiLiQoC7Fv5dXwpNs7iFBjMTqU2D8HNgF5fuFSudfsKwVAVbCovXZM7APizKZcCQR1jb25Tn",
            "12RrJW7xfnW5r2M6Rf1wM46VWk6f4yyYBtX2GxZoQmYbiXvEf26TgiCgp4yzz94NswRK3mjRPEjKL4yXAnqqYGHRP4mixi1pAJQdrvV"
        ],
        'prv_amount2': 0.123456789 * 1000000000,
        'prv_amount': 10
    }

    # shard0 = Transaction(NodeList.shard0[3]['ip'], NodeList.shard0[3]['rpc'])
    # shard0ws = WebSocket(NodeList.shard0[3]['ip'], NodeList.shard0[3]['ws'])
    # shard1 = Transaction(NodeList.shard1[3]['ip'], NodeList.shard1[3]['rpc'])
    # shard1ws = WebSocket(NodeList.shard1[3]['ip'], NodeList.shard1[3]['ws'])
    shard0 = Transaction(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['rpc'])
    shard0ws = WebSocket(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['ws'])
    shard1 = Transaction(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['rpc'])
    shard1ws = WebSocket(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['ws'])
    shard2 = Transaction(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['rpc'])
    shard2ws = WebSocket(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['ws'])
    shard3 = Transaction(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['rpc'])
    shard3ws = WebSocket(NodeList.fullnode[0]['ip'], NodeList.fullnode[0]['ws'])

    # print("\nENV: " + str(NodeList.shard0[3]))
    # print("ENV: " + str(NodeList.shard1[3]))
    # print("ENV: " + str(NodeList.shard2[3]))
    print("ENV: " + str(NodeList.fullnode[0]))

    @pytest.mark.run
    def test_01_sendPRV_noPrivacy_1shard_with_0_balance(self):
        print("""
                    Verify send PRV form account balance = 0  to another address X1hard with no privacy
                    """)
        INFO("test_01_sendPRV_no_privacy_1shard_with_0_balance")
        STEP(1, "get address1 and address2 balance before sending")
        balance1b = self.shard3.getBalance(self.test_data["s3_addr6"][0])
        INFO("addr1_balance: " + str(balance1b))
        assert balance1b != "Invalid parameters"

        balance2b = self.shard3.getBalance(self.test_data["s3_addr7"][0])
        INFO("addr2_balance: " + str(balance2b))
        assert balance2b != "Invalid parameters"
        # sent with amount >0
        STEP(2, "from address1 send prv to address2 -- amount >0")
        step2_result = self.shard3.sendTransaction(self.test_data["s3_addr6"][0],
                                                   self.test_data["s3_addr7"][1], self.test_data["prv_amount"],
                                                   privacy=0)
        INFO("Expecting: " + step2_result[0])
        INFO("StackTrace: " + step2_result[1])
        assert_true(step2_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'not enough output coin', step2_result[1]), "something went so wrong")

        # sent with amount = 0
        STEP(3, "from address1 send prv to address2 -- amount =0")
        step3_result = self.shard3.sendTransaction(self.test_data["s3_addr6"][0],
                                                   self.test_data["s3_addr7"][1], amount_prv=0,
                                                   privacy=0)
        INFO("Expecting: " + step3_result[0])
        INFO("StackTrace: " + step3_result[1])
        assert_true(step3_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'input value less than output value', step3_result[1]), "something went so wrong")

        # sent with amount < 0
        STEP(4, "from address1 send prv to address2 -- amount < 0")
        step4_result = self.shard3.sendTransaction(self.test_data["s3_addr6"][0],
                                                   self.test_data["s3_addr7"][1], amount_prv=-1,
                                                   privacy=0)
        INFO("Expecting: " + step4_result[0])
        INFO("StackTrace: " + step4_result[1])
        assert_true(step4_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'not enough output coin', step4_result[1]), "something went so wrong")

    @pytest.mark.run
    def test_02_sendPRV_noPrivacy_Xshard_with_0_balance(self):
        print("""
                Verify send PRV form account balance = 0  to another address XShard with no privacy
                """)
        INFO("test_02_sendPRV_no_privacy_Xshard_with_0_balance")
        STEP(1, "get address1 and address2 balance before sending")
        balance1b = self.shard3.getBalance(self.test_data["s3_addr6"][0])
        INFO("addr1_balance: " + str(balance1b))
        assert balance1b != "Invalid parameters"

        balance2b = self.shard0.getBalance(self.test_data["s0_addr2"][0])
        INFO("addr2_balance: " + str(balance2b))
        assert balance2b != "Invalid parameters"
        # sent with amount >0
        STEP(2, "from address1 send prv to address2 -- amount >0")
        step2_result = self.shard3.sendTransaction(self.test_data["s3_addr6"][0],
                                                   self.test_data["s0_addr2"][1], self.test_data["prv_amount"],
                                                   privacy=0)
        INFO("Expecting: " + step2_result[0])
        INFO("StackTrace: " + step2_result[1])
        assert_true(step2_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'not enough output coin', step2_result[1]), "something went so wrong")

        # sent with amount = 0
        STEP(3, "from address1 send prv to address2 -- amount =0")
        step3_result = self.shard3.sendTransaction(self.test_data["s3_addr6"][0],
                                                   self.test_data["s0_addr2"][1], amount_prv=0,
                                                   privacy=0)
        INFO("Expecting: " + step3_result[0])
        INFO("StackTrace: " + step3_result[1])
        assert_true(step3_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'input value less than output value', step3_result[1]), "something went so wrong")

        # sent with amount < 0
        STEP(4, "from address1 send prv to address2 -- amount < 0")
        step4_result = self.shard3.sendTransaction(self.test_data["s3_addr6"][0],
                                                   self.test_data["s0_addr2"][1], amount_prv=-1,
                                                   privacy=0)
        INFO("Expecting: " + step4_result[0])
        INFO("StackTrace: " + step4_result[1])
        assert_true(step4_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'not enough output coin', step4_result[1]), "something went so wrong")

    @pytest.mark.run
    def test_03_sendPRV_privacy_1shard_with_0_balance(self):
        print("""
                        Verify send PRV form account balance = 0  to another address X1hard with privacy
                        """)
        INFO("test_03_sendPRV_privacy_1shard_with_0_balance")
        STEP(1, "get address1 and address2 balance before sending")
        balance1b = self.shard3.getBalance(self.test_data["s3_addr6"][0])
        INFO("addr1_balance: " + str(balance1b))
        assert balance1b != "Invalid parameters"

        balance2b = self.shard3.getBalance(self.test_data["s3_addr7"][0])
        INFO("addr2_balance: " + str(balance2b))
        assert balance2b != "Invalid parameters"
        # sent with amount >0
        STEP(2, "from address1 send prv to address2 -- amount >0")
        step2_result = self.shard3.sendTransaction(self.test_data["s3_addr6"][0],
                                                   self.test_data["s3_addr7"][1], self.test_data["prv_amount"])
        INFO("Expecting: " + step2_result[0])
        INFO("StackTrace: " + step2_result[1])
        assert_true(step2_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'not enough output coin', step2_result[1]), "something went so wrong")

        # sent with amount = 0
        STEP(3, "from address1 send prv to address2 -- amount =0")
        step3_result = self.shard3.sendTransaction(self.test_data["s3_addr6"][0],
                                                   self.test_data["s3_addr7"][1], amount_prv=0)
        INFO("Expecting: " + step3_result[0])
        INFO("StackTrace: " + step3_result[1])
        assert_true(step3_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'input value less than output value', step3_result[1]), "something went so wrong")

        # sent with amount < 0
        STEP(4, "from address1 send prv to address2 -- amount < 0")
        step4_result = self.shard3.sendTransaction(self.test_data["s3_addr6"][0],
                                                   self.test_data["s3_addr7"][1], amount_prv=-1)
        INFO("Expecting: " + step4_result[0])
        INFO("StackTrace: " + step4_result[1])
        assert_true(step4_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'not enough output coin', step4_result[1]), "something went so wrong")

    @pytest.mark.run
    def test_04_sendPRV_privacy_Xshard_with_0_balance(self):
        print("""
                    Verify send PRV form account balance = 0  to another address XShard with no privacy
                    """)
        INFO("test_04_sendPRV_privacy_Xshard_with_0_balance")
        STEP(1, "get address1 and address2 balance before sending")
        balance1b = self.shard3.getBalance(self.test_data["s3_addr6"][0])
        INFO("addr1_balance: " + str(balance1b))
        assert balance1b != "Invalid parameters"

        balance2b = self.shard0.getBalance(self.test_data["s0_addr2"][0])
        INFO("addr2_balance: " + str(balance2b))
        assert balance2b != "Invalid parameters"
        # sent with amount >0
        STEP(2, "from address1 send prv to address2 -- amount >0")
        step2_result = self.shard3.sendTransaction(self.test_data["s3_addr6"][0],
                                                   self.test_data["s0_addr2"][1], self.test_data["prv_amount"])
        INFO("Expecting: " + step2_result[0])
        INFO("StackTrace: " + step2_result[1])
        assert_true(step2_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'not enough output coin', step2_result[1]), "something went so wrong")

        # sent with amount = 0
        STEP(3, "from address1 send prv to address2 -- amount =0")
        step3_result = self.shard3.sendTransaction(self.test_data["s3_addr6"][0],
                                                   self.test_data["s0_addr2"][1], amount_prv=0)
        INFO("Expecting: " + step3_result[0])
        INFO("StackTrace: " + step3_result[1])
        assert_true(step3_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'input value less than output value', step3_result[1]), "something went so wrong")

        # sent with amount < 0
        STEP(4, "from address1 send prv to address2 -- amount < 0")
        step4_result = self.shard3.sendTransaction(self.test_data["s3_addr6"][0],
                                                   self.test_data["s0_addr2"][1], amount_prv=-1)
        INFO("Expecting: " + step4_result[0])
        INFO("StackTrace: " + step4_result[1])
        assert_true(step4_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'not enough output coin', step4_result[1]), "something went so wrong")

    @pytest.mark.run
    def test_05_sendPRV_noPrivacy_1shard_autoFee(self):
        print("""
            Verify send PRV ( no privacy - Auto fee )to another address 1Shard successfully with no privacy
            """)
        INFO("test_05_sendPRV_no_privacy_1shard_auto_fee")
        STEP(1, "get address1 and address2 balance before sending")
        balance1b = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("addr1_balance: " + str(balance1b))
        assert balance1b != "Invalid parameters"

        balance2b = self.shard0.getBalance(self.test_data["s0_addr2"][0])
        INFO("addr2_balance: " + str(balance2b))
        assert balance2b != "Invalid parameters"

        STEP(2, "from address1 send prv to address2")
        tx_id = self.shard0.sendTransaction(self.test_data["s0_addr1"][0],
                                            self.test_data["s0_addr2"][1], self.test_data["prv_amount"], privacy=0)
        INFO("transaction id: " + tx_id[0])
        assert tx_id[0] != 'Can not create tx'

        STEP(3, " subcrib transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(tx_id[0])

        STEP(4, "check address1 balance")
        balance1a = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("addr1_balance: " + str(balance1a))
        # Balance after = balance before - amount - fee
        assert balance1a == balance1b - self.test_data["prv_amount"] - ws_res[2]

        STEP(5, "check address2 balance")
        balance2a = self.shard0.getBalance(self.test_data["s0_addr2"][0])
        INFO("addr2_balance: " + str(balance2a))
        # Balance after = balance before + amount
        assert balance2a == balance2b + self.test_data["prv_amount"]

        STEP(6, "Check transaction privacy")
        step6_result = self.shard0.get_txbyhash(tx_id[0])
        assert_true(step6_result[2] == False, "transaction must be no privacy ")

    @pytest.mark.run
    def test_06_sendPRV_noPivacy_1shard_noAutoFee(self):
        print("""
                Verify send PRV ( no privacy - noAuto fee ) to another address 1Shard successfully with no privacy
                """)
        INFO("test_06_sendPRV_no_privacy_1shard_noAuto_fee")
        STEP(1, "get address1 and address2 balance before sending")
        balance1b = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("addr1_balance: " + str(balance1b))
        assert balance1b != "Invalid parameters"

        balance2b = self.shard0.getBalance(self.test_data["s0_addr2"][0])
        INFO("addr2_balance: " + str(balance2b))
        assert balance2b != "Invalid parameters"

        STEP(2, "from address1 send prv to address2")
        tx_id = self.shard0.sendTransaction(self.test_data["s0_addr1"][0],
                                            self.test_data["s0_addr2"][1], self.test_data["prv_amount"], fee=2, privacy=0)
        INFO("transaction id: " + tx_id[0])
        assert tx_id[0] != 'Can not create tx'

        STEP(3, " subcrib transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(tx_id[0])

        STEP(4, "check address1 balance")
        balance1a = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("addr1_balance: " + str(balance1a))
        # Balance after = balance before - amount - fee
        assert balance1a == balance1b - self.test_data["prv_amount"] - ws_res[2]

        STEP(5, "check address2 balance")
        balance2a = self.shard0.getBalance(self.test_data["s0_addr2"][0])
        INFO("addr2_balance: " + str(balance2a))
        # Balance after = balance before + amount
        assert balance2a == balance2b + self.test_data["prv_amount"]

        STEP(6, "check transaction privacy")
        step6_result = self.shard0.get_txbyhash(tx_id[0])
        assert_true(step6_result[2]== False, "transaction must be no privacy ")

        STEP(7, "Check transaction privacy")
        step6_result = self.shard0.get_txbyhash(tx_id[0])
        assert_true(step6_result[2] == False, "transaction must be no privacy ")

    @pytest.mark.run
    def test_07_sendPRV_privacy_1shard_autoFee(self):
        print("""
        Verify send PRV ( privacy - auto fee ) to another address 1Shard successfully
        """)
        INFO("test_07_sendPRV_privacy_1shard_auto_fee")
        STEP(1, "get address1 and address2 balance before sending")
        balance1b = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("addr1_balance: " + str(balance1b))
        assert balance1b != "Invalid parameters"

        balance2b = self.shard0.getBalance(self.test_data["s0_addr2"][0])
        INFO("addr2_balance: " + str(balance2b))
        assert balance2b != "Invalid parameters"

        STEP(2, "from address1 send prv to address2")
        tx_id = self.shard0.sendTransaction(self.test_data["s0_addr1"][0],
                                            self.test_data["s0_addr2"][1], self.test_data["prv_amount"])
        INFO("transaction id: " + tx_id[0])
        assert tx_id[0] != 'Can not create tx'

        STEP(3, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(tx_id[0])

        STEP(4, "check address1 balance")
        balance1a = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("addr1_balance: " + str(balance1a))
        # Balance after = balance before - amount - fee
        assert balance1a == balance1b - self.test_data["prv_amount"] - ws_res[2]

        STEP(5, "check address2 balance")
        balance2a = self.shard0.getBalance(self.test_data["s0_addr2"][0])
        INFO("addr2_balance: " + str(balance2a))
        # Balance after = balance before + amount
        assert balance2a == balance2b + self.test_data["prv_amount"]

        STEP(6, "check transaction privacy")
        step6_result= self.shard0.get_txbyhash(tx_id[0])
        assert_true(step6_result[2]== True , "transaction must be privacy" )


    @pytest.mark.run
    def test_08_sendPRV_privacy_1shard_noAutoee(self):
        print("""
            Verify send PRV ( privacy - noAuto fee ) to another address 1Shard successfully
            """)
        INFO("test_08_sendPRV_privacy_1shard_noAuto_fee")
        STEP(1, "get address1 and address2 balance before sending")
        balance1b = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("addr1_balance: " + str(balance1b))
        assert balance1b != "Invalid parameters"

        balance2b = self.shard0.getBalance(self.test_data["s0_addr2"][0])
        INFO("addr2_balance: " + str(balance2b))
        assert balance2b != "Invalid parameters"

        STEP(2, "from address1 send prv to address2")
        tx_id = self.shard0.sendTransaction(self.test_data["s0_addr1"][0],
                                            self.test_data["s0_addr2"][1], self.test_data["prv_amount"], fee=5)
        INFO("transaction id: " + tx_id[0])
        assert tx_id[0] != 'Can not create tx'

        STEP(3, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(tx_id[0])

        STEP(4, "check address1 balance")
        balance1a = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("addr1_balance: " + str(balance1a))
        # Balance after = balance before - amount - fee
        assert balance1a == balance1b - self.test_data["prv_amount"] - ws_res[2]

        STEP(5, "check address2 balance")
        balance2a = self.shard0.getBalance(self.test_data["s0_addr2"][0])
        INFO("addr2_balance: " + str(balance2a))
        # Balance after = balance before + amount
        assert balance2a == balance2b + self.test_data["prv_amount"]

        STEP(6, "check transaction privacy")
        step6_result = self.shard0.get_txbyhash(tx_id[0])
        assert_true(step6_result[2] == True, "transaction must be privacy")

    @pytest.mark.run
    def test_09_sendPRV_noPrivacy_Xshard_autoFee(self):
        print("""
         Verify send PRV (no privacy- auto fee ) to another address Xshard successfully with no privacy
         """)
        INFO("test_09_sendPRV_no_privacy_Xshard_auto_fee")
        STEP(1, "Get address1 balance")
        step1_result = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("addr1_balance: " + str(step1_result))
        assert step1_result != "Invalid parameters"

        STEP(2, "Get address3 balance")
        step2_result = self.shard1.getBalance(self.test_data["s1_addr3"][0])
        INFO("addr3_balance: " + str(step2_result))
        assert step2_result != "Invalid parameters"

        STEP(3, "From address1 send prv to address3")
        step3_result = self.shard0.sendTransaction(self.test_data["s0_addr1"][0],
                                                   self.test_data["s1_addr3"][1], self.test_data["prv_amount"], privacy=0)
        INFO("Transaction ID: " + step3_result[0])
        assert step3_result[0] != 'Can not create tx'

        STEP(4, "Subcribe transaction")
        self.shard0ws.createConnection()
        ws_res4 = self.shard0ws.subcribePendingTransaction(step3_result[0])

        STEP(5, "Subcribe cross transaction by privatekey")
        self.shard1ws.createConnection()
        ws_res5 = self.shard1ws.subcribeCrossOutputCoinByPrivatekey(self.test_data["s1_addr3"][0])

        STEP(6, "Check address1 balance")
        step4_result = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("addr1_balance: " + str(step4_result))
        assert step4_result == step1_result - self.test_data["prv_amount"] - ws_res4[2]

        STEP(7, "Check address3 balance")
        step5_result = self.shard1.getBalance(self.test_data["s1_addr3"][0])
        INFO("Addr3_balance: " + str(step5_result))
        assert step5_result == step2_result + self.test_data["prv_amount"]

        STEP(8, "Check transaction privacy")
        step8_result = self.shard0.get_txbyhash(step3_result[0])
        assert_true(step8_result[2] == False, "transaction must be no privacy ")

    @pytest.mark.run
    def test_10_sendPRV_noPrivacy_Xshard_noAautoFee(self):
        print("""
         Verify send PRV (no privacy - no auto fee ) to another address Xshard successfully with no privacy
         Fee: 100 nanoPRV * transaction size
         """)
        INFO("test_10_sendPRV_no_privacy_Xshard_noAauto_fee")
        STEP(1, "Get address1 balance")
        step1_result = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("addr1_balance: " + str(step1_result))
        assert step1_result != "Invalid parameters"

        STEP(2, "Get address3 balance")
        step2_result = self.shard1.getBalance(self.test_data["s1_addr3"][0])
        INFO("addr3_balance: " + str(step2_result))
        assert step2_result != "Invalid parameters"

        STEP(3, "From address1 send prv to address3")
        step3_result = self.shard0.sendTransaction(self.test_data["s0_addr1"][0],
                                                   self.test_data["s1_addr3"][1], self.test_data["prv_amount"],
                                                   100, 0)
        INFO("Transaction ID: " + step3_result[0])
        assert step3_result[0] != 'Can not create tx'

        STEP(4, "Subcribe transaction")
        self.shard0ws.createConnection()
        ws_res4 = self.shard0ws.subcribePendingTransaction(step3_result[0])
        assert_true(ws_res4[2] % 100 == 0, "Invalid tx fee", "Tx fee is %d * %dKB" % (100, ws_res4[2] / 100))

        STEP(5, "Subcribe cross transaction by privatekey")
        self.shard1ws.createConnection()
        ws_res5 = self.shard1ws.subcribeCrossOutputCoinByPrivatekey(self.test_data["s1_addr3"][0])

        STEP(6, "Check address1 balance")
        step4_result = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("addr1_balance: " + str(step4_result))
        assert step4_result == step1_result - self.test_data["prv_amount"] - ws_res4[2]

        STEP(7, "Check address3 balance")
        step5_result = self.shard1.getBalance(self.test_data["s1_addr3"][0])
        INFO("Addr3_balance: " + str(step5_result))
        assert step5_result == step2_result + self.test_data["prv_amount"]

        STEP(8, "Check transaction privacy")
        step8_result = self.shard0.get_txbyhash(step3_result[0])
        assert_true(step8_result[2] == False, "transaction must be no privacy ")

    @pytest.mark.run
    def test_11_sendPRV_privacy_Xshard_autoFee(self):
        print("""
        Verify send PRV (privacy - auto fee ) to another address Xshard successfully
        """)
        INFO("test_11_sendPRV_privacy_Xshard_auto_fee")
        STEP(1, "Get address1 balance")
        step1_result = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("addr1_balance: " + str(step1_result))
        assert step1_result != "Invalid parameters"

        STEP(2, "Get address3 balance")
        step2_result = self.shard1.getBalance(self.test_data["s1_addr3"][0])
        INFO("addr3_balance: " + str(step2_result))
        assert step2_result != "Invalid parameters"

        STEP(3, "From address1 send prv to address3")
        step3_result = self.shard0.sendTransaction(self.test_data["s0_addr1"][0],
                                                   self.test_data["s1_addr3"][1], self.test_data["prv_amount"])
        INFO("Transaction ID: " + step3_result[0])
        assert step3_result[0] != 'Can not create tx'

        STEP(4, "Subcribe transaction")
        self.shard0ws.createConnection()
        ws_res4 = self.shard0ws.subcribePendingTransaction(step3_result[0])

        STEP(5, "Subcribe cross transaction by privatekey")
        self.shard1ws.createConnection()
        ws_res5 = self.shard1ws.subcribeCrossOutputCoinByPrivatekey(self.test_data["s1_addr3"][0])

        STEP(6, "Check address1 balance")
        step4_result = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("addr1_balance: " + str(step4_result))
        assert step4_result == step1_result - self.test_data["prv_amount"] - ws_res4[2]

        STEP(7, "Check address3 balance")
        step5_result = self.shard1.getBalance(self.test_data["s1_addr3"][0])
        INFO("Addr3_balance: " + str(step5_result))
        assert step5_result == step2_result + self.test_data["prv_amount"]

        STEP(8, "Check transaction privacy")
        step8_result = self.shard0.get_txbyhash(step3_result[0])
        assert_true(step8_result[2] == True, "transaction must be privacy ")

    @pytest.mark.run
    def test_12_sendPRV_privacy_Xshard_noAutoFee(self):
        print("""
           Verify send PRV (privacy - no Auto fee) to another address Xshard successfully
           Fee: 100 nanoPRV * transaction size
           """)
        INFO("test_12_sendPRV_privacy_Xshard_noAuto_fee")
        STEP(1, "Get address1 balance")
        step1_result = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("addr1_balance: " + str(step1_result))
        assert step1_result != "Invalid parameters"

        STEP(2, "Get address3 balance")
        step2_result = self.shard1.getBalance(self.test_data["s1_addr3"][0])
        INFO("addr3_balance: " + str(step2_result))
        assert step2_result != "Invalid parameters"

        STEP(3, "From address1 send prv to address3")
        step3_result = self.shard0.sendTransaction(self.test_data["s0_addr1"][0],
                                                   self.test_data["s1_addr3"][1], self.test_data["prv_amount"],
                                                   2)
        INFO("Transaction ID: " + step3_result[0])
        assert step3_result[0] != 'Can not create tx'

        STEP(4, "Subcribe transaction")
        self.shard0ws.createConnection()
        ws_res4 = self.shard0ws.subcribePendingTransaction(step3_result[0])
        assert_true(ws_res4[2] % 2 == 0, "Invalid tx fee", "Tx fee is %d * %dKB" % (2, ws_res4[2] / 2))

        STEP(5, "Subcribe cross transaction by privatekey")
        self.shard1ws.createConnection()
        ws_res5 = self.shard1ws.subcribeCrossOutputCoinByPrivatekey(self.test_data["s1_addr3"][0])

        STEP(6, "Check address1 balance")
        step4_result = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("addr1_balance: " + str(step4_result))
        assert step4_result == step1_result - self.test_data["prv_amount"] - ws_res4[2]

        STEP(7, "Check address3 balance")
        step5_result = self.shard1.getBalance(self.test_data["s1_addr3"][0])
        INFO("Addr3_balance: " + str(step5_result))
        assert step5_result == step2_result + self.test_data["prv_amount"]

        STEP(8, "Check transaction privacy")
        step8_result = self.shard0.get_txbyhash(step3_result[0])
        assert_true(step8_result[2] == True, "transaction must be privacy ")

    @pytest.mark.run
    def test_13_sendPRV_privacy_Xshard_insufficient_fund(self):
        print("""
        Verify send PRV to another address:
        - Not enough coin (insufficient fund)
        - Wrong input transaction
        """)

        INFO("test_13_sendPRV_privacy_Xshard_insufficient_fund")
        STEP(1, "Get address1 balance")
        step1_result = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("addr1_balance: " + str(step1_result))
        assert step1_result != "Invalid parameters"

        STEP(2, "Get address3 balance")
        step2_result = self.shard1.getBalance(self.test_data["s1_addr3"][0])
        INFO("addr3_balance: " + str(step2_result))
        assert_true(step2_result != 0, "addr3_balance = 0, stop this testcase")

        STEP(3, "From address3 send prv to address1 - Not enough coin")
        # send current balance + 10
        step3_result = self.shard1.sendTransaction(self.test_data["s1_addr3"][0],
                                                   self.test_data["s0_addr1"][1], step2_result + 10)
        INFO("Expecting: " + step3_result[0])
        INFO("StackTrace: " + step3_result[1])
        assert_true(step3_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'Not enough coin', step3_result[1]), "something went so wrong")

        # breakpoint()

        STEP(4, "From address3 send prv to address1 - Wrong input transaction")
        # send current balance (lacking of fee)
        step4_result = self.shard1.sendTransaction(self.test_data["s1_addr3"][0],
                                                   self.test_data["s0_addr1"][1], step2_result)
        INFO("Expecting: " + step4_result[0])
        INFO("StackTrace: " + step4_result[1])
        assert_true(step4_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'Wrong input transaction', step4_result[1]), "something went so wrong")
        estimated_fee = re.search(r'fee=(\d+)\n', step4_result[1])
        estimated_fee = estimated_fee.group(1)
        INFO("Estimated fee: " + estimated_fee)

        # breakpoint()

        STEP(5, "From address3 send prv to address1 - success")
        # send current balance - fee
        step5_result = self.shard1.sendTransaction(self.test_data["s1_addr3"][0],
                                                   self.test_data["s0_addr1"][1],
                                                   step2_result - int(estimated_fee))
        if step5_result[0] != 'Can not create tx':
            # assert_true(step5_result[0] != 'Can not create tx', step5_result[1])
            INFO("TxID: " + step5_result[0])
        else:
            estimated_fee = re.search(r'fee=(\d+)\n', step5_result[1])
            estimated_fee = estimated_fee.group(1)
            INFO("Estimated new fee: " + estimated_fee)
            step5_result = self.shard1.sendTransaction(self.test_data["s1_addr3"][0],
                                                       self.test_data["s0_addr1"][1],
                                                       step2_result - int(estimated_fee))
            assert_true(step5_result[0] != 'Can not create tx', step5_result[1])
            INFO("TxID: " + step5_result[0])

        STEP(6, "Subcribe transaction")
        self.shard1ws.createConnection()
        ws_res6 = self.shard1ws.subcribePendingTransaction(step5_result[0])

        STEP(7, "Subcribe cross transaction by privatekey")
        self.shard0ws.createConnection()
        ws_res7 = self.shard0ws.subcribeCrossOutputCoinByPrivatekey(self.test_data["s0_addr1"][0])

        STEP(8, "Check address1 balance")
        step8_result = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("addr1_balance: " + str(step8_result))
        assert step8_result == step1_result + step2_result - ws_res6[2]

        STEP(9, "Check address3 balance")
        step7_result = self.shard1.getBalance(self.test_data["s1_addr3"][0])
        INFO("Addr3_balance: " + str(step7_result))
        assert step7_result == 0

        STEP(10, "Check transaction privacy")
        step10_result = self.shard0.get_txbyhash(step5_result[0])
        assert_true(step10_result[2] == True, "transaction must be privacy ")

    @pytest.mark.run
    def test_14_sendPRV_privacy_1shard_insufficient_fund(self):
        print("""
            Verify send PRV to another address:
            - Not enough coin (insufficient fund)
            - Wrong input transaction
            """)
        INFO("test_14_sendPRV_privacy_1shard_insufficient_fund")
        STEP(1, "Get address1 balance")
        step1_result = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("addr1_balance: " + str(step1_result))
        assert step1_result != "Invalid parameters"

        STEP(2, "Get address2 balance")
        step2_result = self.shard0.getBalance(self.test_data["s0_addr2"][0])
        INFO("addr2_balance: " + str(step2_result))
        assert_true(step2_result != 0, "addr2_balance = 0, stop this testcase")

        STEP(3, "From address2 send prv to address1 - Not enough coin")
        # send current balance + 10
        step3_result = self.shard0.sendTransaction(self.test_data["s0_addr2"][0],
                                                   self.test_data["s0_addr1"][1], step2_result + 10)
        INFO("Expecting: " + step3_result[0])
        INFO("StackTrace: " + step3_result[1])
        assert_true(step3_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'Not enough coin', step3_result[1]), "something went so wrong")

        # breakpoint()

        STEP(4, "From address2 send prv to address1 - Wrong input transaction")
        # send current balance (lacking of fee)
        step4_result = self.shard0.sendTransaction(self.test_data["s0_addr2"][0],
                                                   self.test_data["s0_addr1"][1], step2_result)
        INFO("Expecting: " + step4_result[0])
        INFO("StackTrace: " + step4_result[1])
        assert_true(step4_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'Wrong input transaction', step4_result[1]), "something went so wrong")
        estimated_fee = re.search(r'fee=(\d+)\n', step4_result[1])
        estimated_fee = estimated_fee.group(1)
        INFO("Estimated fee: " + estimated_fee)

        # breakpoint()

        STEP(5, "From address2 send prv to address1 - success")
        # send current balance - fee
        step5_result = self.shard0.sendTransaction(self.test_data["s0_addr2"][0],
                                                   self.test_data["s0_addr1"][1],
                                                   step2_result - int(estimated_fee))
        if step5_result[0] != 'Can not create tx':
            # assert_true(step5_result[0] != 'Can not create tx', step5_result[1])
            INFO("TxID: " + step5_result[0])
        else:
            estimated_fee = re.search(r'fee=(\d+)\n', step5_result[1])
            estimated_fee = estimated_fee.group(1)
            INFO("Estimated new fee: " + estimated_fee)
            step5_result = self.shard0.sendTransaction(self.test_data["s0_addr2"][0],
                                                       self.test_data["s0_addr1"][1],
                                                       step2_result - int(estimated_fee))
            assert_true(step5_result[0] != 'Can not create tx', step5_result[1])
            INFO("TxID: " + step5_result[0])

        STEP(6, "Subcribe transaction")
        self.shard0ws.createConnection()
        ws_res6 = self.shard0ws.subcribePendingTransaction(step5_result[0])

        STEP(7, "Check address1 balance")
        step7_result = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("addr1_balance: " + str(step7_result))
        assert step7_result == step1_result + step2_result - ws_res6[2]

        STEP(8, "Check address2 balance")
        step8_result = self.shard0.getBalance(self.test_data["s0_addr2"][0])
        INFO("Addr2_balance: " + str(step8_result))
        assert step8_result == 0

        STEP(9, "Check transaction privacy")
        step9_result = self.shard0.get_txbyhash(step5_result[0])
        assert_true(step9_result[2] == True, "transaction must be privacy ")

    @pytest.mark.run
    def est_15_sendPRV_privacy_Xshard(self):
        print("""
            Verify send PRV to another address Xshard successfully
            Fee: 100 nanoPRV * transaction size
            """)

        STEP(1, "Get address1 balance")
        step1_result = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("addr1_balance: " + str(step1_result))
        assert step1_result != "Invalid parameters"

        STEP(2, "Get address4 balance")
        step2_result = self.shard2.getBalance(self.test_data["s2_addr4"][0])
        INFO("addr4_balance: " + str(step2_result))
        assert step2_result != "Invalid parameters"

        STEP(3, "From address1 send prv to address3")
        step3_result = self.shard0.sendTransaction(self.test_data["s0_addr1"][0],
                                                   self.test_data["s2_addr4"][1], self.test_data["prv_amount"],
                                                   5)
        INFO("Transaction ID: " + step3_result[0])
        INFO("StackTrace: " + str(step3_result[1]))
        assert step3_result[0] != 'Can not create tx'

        STEP(4, "Subcribe transaction")
        self.shard0ws.createConnection()
        ws_res4 = self.shard0ws.subcribePendingTransaction(step3_result[0])
        assert_true(ws_res4[2] % 5 == 0, "Invalid tx fee", "Tx fee is %d * %dKB" % (5, ws_res4[2] / 5))

        STEP(5, "Subcribe cross transaction by privatekey")
        self.shard2ws.createConnection()
        ws_res5 = self.shard2ws.subcribeCrossOutputCoinByPrivatekey(self.test_data["s2_addr4"][0])

        STEP(6, "Check address1 balance")
        step4_result = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("addr1_balance: " + str(step4_result))
        assert step4_result == step1_result - self.test_data["prv_amount"] - ws_res4[2]

        STEP(7, "Check address4 balance")
        step5_result = self.shard2.getBalance(self.test_data["s2_addr4"][0])
        INFO("addr4_balance: " + str(step5_result))
        assert step5_result == step2_result + self.test_data["prv_amount"]

    @pytest.mark.run
    def est_16_sendPRV_privacy_1shard(self):
        print("""
           Verify send PRV to another address 1Shard successfully
           """)

        STEP(1, "get s2_addr4 and s2_addr5 balance before sending")
        balance1b = self.shard2.getBalance(self.test_data["s2_addr4"][0])
        INFO("s2_addr4_balance: " + str(balance1b))
        assert balance1b != "Invalid parameters"

        balance2b = self.shard2.getBalance(self.test_data["s2_addr5"][0])
        INFO("s2_addr5_balance: " + str(balance2b))
        assert balance2b != "Invalid parameters"

        STEP(2, "from s2_addr4 send prv to s2_addr5")
        # send 1/4 of the balance
        send_amount = math.floor(balance1b / 4)
        tx_id = self.shard2.sendTransaction(self.test_data["s2_addr4"][0],
                                            self.test_data["s2_addr5"][1], send_amount)
        INFO("transaction id: " + tx_id[0])
        INFO("Send amount: " + str(send_amount))
        INFO("StackTrace: " + tx_id[1])
        assert tx_id[0] != 'Can not create tx'

        STEP(3, "subcribe transaction")
        self.shard2ws.createConnection()
        ws_res = self.shard2ws.subcribePendingTransaction(tx_id[0])

        STEP(4, "check s2_addr4 balance")
        balance1a = self.shard2.getBalance(self.test_data["s2_addr4"][0])
        INFO("s2_addr4_balance: " + str(balance1a))
        # Balance after = balance before - amount - fee
        assert balance1a == balance1b - send_amount - ws_res[2]

        STEP(5, "check s2_addr5 balance")
        balance2a = self.shard2.getBalance(self.test_data["s2_addr5"][0])
        INFO("s2_addr5_balance: " + str(balance2a))
        # Balance after = balance before + amount
        assert balance2a == balance2b + send_amount

    @pytest.mark.run
    def est_17_sendPRV_privacy_Xshard_max_value(self):
        print("""
         Verify send PRV to another address:
         -  > 10 mil PRV unsuccess
         - Tx fee = 100000000000 PRV success
         """)
        STEP(1, "Get address1 balance")
        step1_result = self.shard0.getBalance(self.test_data["s0_addr1"][0])
        INFO("addr1_balance: " + str(step1_result))
        assert step1_result != "Invalid parameters"

        STEP(2, "Get address3 balance")
        step2_result = self.shard1.getBalance(self.test_data["s1_addr3"][0])
        INFO("addr3_balance: " + str(step2_result))
        assert_true(step2_result != 0, "addr3_balance = 0, stop this testcase")

        STEP(3, "From address3 send prv to address1 - max value")
        # send amount = 1000000000000000000
        step3_result = self.shard1.sendTransaction(self.test_data["s1_addr3"][0],
                                                   self.test_data["s0_addr1"][1], 1000000000000000001)
        INFO("Expecting: " + step3_result[0])
        INFO("StackTrace: " + step3_result[1])
        assert_true(step3_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'Not enough coin', step3_result[1]), "something went so wrong")

        STEP(4, "From address3 send prv to address1 - max value fee ")
        # send with fee = 10000000000000 PRV
        step4_result = self.shard1.sendTransaction(self.test_data["s1_addr3"][0],
                                                   self.test_data["s0_addr1"][1], self.test_data["prv_amount"], fee=900000000000000)
        INFO("Expecting: " + step4_result[0])
        INFO("StackTrace: " + step4_result[1])
        assert_true(step4_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'input value less than output value', step4_result[1]), "something went so wrong")



    @pytest.mark.run
    def test_99_cleanup(self):
        print("""
        CLEAN UP
        """)
        self.shard0ws.closeConnection()
        self.shard1ws.closeConnection()
        self.shard2ws.closeConnection()
        self.shard3ws.closeConnection()
