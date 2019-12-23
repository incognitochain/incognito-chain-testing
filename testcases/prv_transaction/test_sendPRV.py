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
    test_data_khanh = {
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

    # print("\nENV: " + str(NodeList.shard0[3]))
    # print("ENV: " + str(NodeList.shard1[3]))
    # print("ENV: " + str(NodeList.shard2[3]))
    print("ENV: " + str(NodeList.fullnode[0]))

    @pytest.mark.run
    def test_02_sendPRV_privacy_1shard(self):
        print("""
        Verify send PRV to another address 1Shard successfully
        """)

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

    @pytest.mark.run
    def test_03_sendPRV_privacy_Xshard(self):
        print("""
        Verify send PRV to another address Xshard successfully
        Fee: 100 nanoPRV * transaction size
        """)

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

    @pytest.mark.run
    def test_04_sendPRV_Xshard_insufficient_fund(self):
        print("""
        Verify send PRV to another address:
        - Not enough coin (insufficient fund)
        - Wrong input transaction
        """)
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
        assert_true(step5_result[0] != 'Can not create tx', "something went wrong, this tx must succeeded")
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

        STEP(7, "Check address3 balance")
        step7_result = self.shard1.getBalance(self.test_data["s1_addr3"][0])
        INFO("Addr3_balance: " + str(step7_result))
        assert step7_result == 0

    @pytest.mark.run
    def test_05_sendPRV_privacy_Xshard(self):
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
    def test_06_sendPRV_privacy_1shard(self):
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
    def test_99_cleanup(self):
        print("""
        CLEAN UP
        """)
        self.shard0ws.closeConnection()
        self.shard1ws.closeConnection()
        self.shard2ws.closeConnection()
