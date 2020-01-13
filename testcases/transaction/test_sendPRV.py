"""
Created Oct 11 2019
@Author: Khanh Le
"""

import re
import unittest, math
import pytest
import topology.NodeList as NodeList
from libs.AutoLog import INFO, STEP, assert_true, WAIT
from libs.Transaction import Transaction
from libs.WebSocket import WebSocket


class test_sendPRV(unittest.TestCase):
    """
    Test case: Send PRV
    """
    test_data_k = {
        's02_addr1': [
            "112t8rnXVMJJZzfF1naXvfE9nkTKwUwFWFeh8cfEyViG1vpA8A9khJk3mhyB1hDuJ4RbreDTsZpgJK4YcSxdEpXJKMEd8Vmp5UqKWwBcYzxv",
            "12RyJTSL2G8KvjN7SUFuiS9Ek4pvFFze3EMMic31fmXVw8McwYzpKPpxeW6TLsNo1UoPhCHKV3GDRLQwdLF41PED3LQNCLsGNKzmCE5"],
        's02_addr2': [
            "112t8rnX6USJnBzswUeuuanesuEEUGsxE8Pj3kkxkqvGRedUUPyocmtsqETX2WMBSvfBCwwsmMpxonhfQm2N5wy3SrNk11eYxEyDtwuGxw2E",
            "12RwbexYzKJwGaJDdDE7rgLEkNC1dL5cJf4xNaQ29EmpPN52C6oepWiTtQCpyHAoo6ZTHMx2Nt3A8p5jYqpYvbrVYGpVTen1rVstCpr"],
        's05_addr3': [
            "112t8rnXoEWG5H8x1odKxSj6sbLXowTBsVVkAxNWr5WnsbSTDkRiVrSdPy8QfMujntKRYBqywKMJCyhMpdr93T3XiUD5QJR1QFtTpYKpjBEx",
            "12RqmK5woGNeBTy16ouYepSw4QEq28gsv2m81ebcPQ82GgS5S8PHEY37NU2aTacLRruFvjTqKCgffTeMDL83snTYz5zDp1MTLwjVhZS"],
        's04_addr4': [
            "112t8rnZ5UZouZU9nFmYLfpHUp8NrvQkGLPD564mjzNDM8rMp9nc9sXZ6CFxCGEMuvHQpYN7af6KCPJnq9MfEnXQfntbM8hpy9LW8p4qzPxS",
            "12Rw9oesEgd8t5NGrfqxtWTCzh1eDif55miqZ1kFzj5zeQ6UQnNB9JXRn5Vc5QVbBaiFhoYdYPnQZ5tWwcBpse5EJXM3Av6qEV2wspv"],
        's04_addr5': [
            "112t8rnan3pbXtdvfKSk3kti1tFcFpVSq5wp7c3hhLk7E4jQih2zsv8ynjpP1UQivExGwbMf9Ezp9qmKBJuHhNZPAzheqX4WTV8LfrdZY5Mh",
            "12RxCyrWFCkpzfnMcnN8MuDrXkFAsEAkhyn4zHhy3n6CNZPYJ4cNDesBGycwu62PJn8rQ8uLiC5zSYDiXFa9hXtQMUJvVCMT2uUNn8G"],
        's04_addr4_d': [
            "112t8rnZ9qPE7C6RbrK6Ygat1H94kEkYGSd84fAGiU396yQHu8CBHmV1DDHE947d7orfHnDtKA9WCffDk7NS5zUu5CMCUHK8nkRtrv4nw6uu",
            "12Rrk9r3Chmt5Wibkmu2VcFSUffGZbkz2rzMWdmmB3GEu8t8RF4v2wc1gBQtkJFZmPfUP29bSXR4Wn8kDveLQBTBK5Hck9BoGRnuM7n"],
        's04_addr5_d': [
            "112t8rnaK4C17Chu8rEAPXHUaPYNeGz8VsjV7BzdeLA9VBc8oiYwQXNrc6XEABb4uNEfG9LFgvVfi4KQmVpQrwMWph4E1YoVS1m37HwrFDsE",
            "12RtmaJMoRbUCsYxLC4RatP2vWVR3QdZXpbkXR7LwZjVrZfXF46ZNL4QgpCU71SXjz2eCeruA7ZiHM91otTJXzqJiztq5mrdHA35yaf"],
        'prv_amount2': 0.123456789 * 1000000000,
        'prv_amount': 10
    }

    test_data = {
        's02_addr1': [
            "112t8rnX3VTd3MTWMpfbYP8HGY4ToAaLjrmUYzfjJBrAcb8iPLkNqvVDXWrLNiFV5yb2NBpR3FDZj3VW8GcLUwRdQ61hPMWP3YrREZAZ1UbH",
            "12S6R8HfTyL74bggg47LX88RSvBPaMPBMEMoo6yx9WQ4EgLiYERXXcE2Mv2HrCsFuKhBsTfrYMeH82Bus5MHQGt3xHwoxX4v2qM5jRE"
        ],
        's02_addr2': [
            "112t8rndq3phbUG44goJZyYSy9Qvm6nEJr8N672tD8E5VyzqPuJVQBb1wcHQSrQibsbBLkrGfQ14fzw8iNoAtu13gqKjktffPrw9ZxcoNsbk",
            "12Rq6XDGQVYcxop7krJUJZCgsWCCU2UpgDDWdhjtxfeuWbcuksHNdjDkBVBz5t98q9UKjTS77Y6BZDeVeKuvw7QZfMBT7wb3M3YWS4k",
        ],
        's05_addr3': [
            "112t8rngNKpZHv6WsKqaYqKPi8JvfEVY9oqob3QiSKmbHbfDrDFXZZtmqLAacnmfqTJKKR9P2UJ1kYvkmdHAHU4zPRHpv38kHRRjLtHNv4yN",
            "12S2NxoLzvEsKBpvL6g3gjECvErpxVQoAg7VpnhojLXa6S3TchxbwM5aHQYJoT3K1nkq7C7VjAwgVwn2De3uLzD1J8VkmWe3cDRLPef",
        ],
        's04_addr4': [
            "112t8rnendREF3cg2vuRC248dFymXonwBC7TMmfppXEzz9wFziktHj8NhsGebcRmtquyg2zbytkecPMSHFBVcw4yJewv7E3J6cHgDzYiHoJj",
            "12S4YzSA6hC12zuMF8L2rC7Tks1TtcfDUSWjcPeKeyT1ApV1KXqQnmtpCNEYbta88GrjhPiS6yFfuyfViDW5cmooqsZ5tvC8SRJZdCF",
        ],
        's04_addr5': [
            "112t8rnhdyiruPke58LNeqwpzxn3cGQsfnS4dqec6P9HWPwNH7VKPgdXw9svDXp5djM4mQrMZnxwW7sjk5NLBkHXC3pJHBMsoqJi8sNUd47G",
            "12S4HcgzM2zQeq41Bh9w8Ce5YETiQitoTZmTjCHLvvbwmoy8S9Py66wBjCqTgziWPbMpWEWPA2jRabwDmTk2TYV4nAzBN3SwjYN4zfE"
        ],
        's05_addr6': [
            "112t8rnh7v5oFHi6TuLKZ26pEPrtXfHFsiWsmeD1ZmKpNQzAjyAKX2bY5AB5DzyKgwarwKMgW9do6Ad8yEPZYtuFnVexk6rrEk14f6P9cwXP",
            "12S2VydiAis1ZSDHq5n3dacWUzsL6E1TgkTGPTXWUjsCRvvjMLVEZbDL4g4UciBj3gEQoRaytegy2Z8YA3oFM2gLx4C7A6yzLdQP4nk"
        ],
        's01_addr7': [
            "112t8roMtSrKYCL4eA4aXiQ8umGz78znHRTdMpzKAbSgL1Cj6JtbkS9i87jW1KFjbpN9fwM3PY7LNJq3QyawdHX61eTwN6beiiayMjN4yPwC",
            "12S4oseu3scZJJuoLeGSEYZka1mmxHBNg7VbC1tQ67ZDjTUqzuRY4ABf4Bjop7uR22U1AxsLEheixfenpcc63tVG7E7QxF1zy5r1SXv"
        ],
        's00_add8': [
            "112t8ro4yu78UE82jpto12rp3Cd8Z2Mse7fcavSyXXP82oApE1cg9y8hWq69Z74fFHGJrQyHz54vU8Mv1kx5qZ54cRQJPkF5Cb7DhNqL5Tgt",
            "12RyGbTyktYkXe7mNwmZeD4rktqxtHMe3Tsyf4XiZdKVGFssEHaF1ZUTpXZmpFACuDotVr7a6FEw8v6FTn8DEMqpHNxZ8fJW3KNN3i1",
        ],
        's03_addr9': [
            "112t8rnsqDitXckbWMPo4wGbjwyPtYHywApPqfZVQNatrMzfDLERCmHTBPsHUZjhzFLxdVmQ6m6W5ppbK4PZCzWVjEBvi3a7SVrtVpd6GZSL",
            "12S3Xv2N9KvGZivRESKUQWv6obrghwykAUxqc85nTcZQ9AJMxnJe4Ct97BjAm5vFJ9bhhaHXDCmGfbXEqbS766DyeMLLeYksDM1FmSg",
        ],
        's06_addr10': [
            "112t8rnuBJ9Qwgc3pUadn5oiN1B3xo7SE7ZJVoXxwBdB8Jeoy1bzdWYB36nKVn4pTUKEhCtqCQyCCcPQAFrGjN4PsCpm8J6MV73D72yTuNFW",
            "12RuwRs21ZaDFdDGDkDRdbfyBLEzsDKzXgEhewStoMvQsQc9atziJSBbUwC45W9JJj6QfkR2TQmGVymPUjbTGHtuiGdBrhrZDLxcQtb"
        ],
        's07_addr11': [
            "112t8rndqnxKCi4yVxcZYD8Uvy4kQsid7c3g4GwZxf7Scp6ennGAouiyAfyHT9YoYd4BYjeW3XDxLZzy56S3GzMJpdiuXt7A1YaFCya6q25H",
            "12S25PTudeEs5c38ovtoy6cLeeaESKbSWQgRX7coFHKZEvvHmKTPSQe26pWuq17czJbz7ymQBRnXmH4CJdSge8uLAWTAoxZMGp9Nave"
        ],
        'prv_amount2': 0.123456789 * 1000000000,
        'prv_amount': 1000
    }

    test_data_multi_output = {
        's00_add8': [
            "112t8ro4yu78UE82jpto12rp3Cd8Z2Mse7fcavSyXXP82oApE1cg9y8hWq69Z74fFHGJrQyHz54vU8Mv1kx5qZ54cRQJPkF5Cb7DhNqL5Tgt",
            "12RyGbTyktYkXe7mNwmZeD4rktqxtHMe3Tsyf4XiZdKVGFssEHaF1ZUTpXZmpFACuDotVr7a6FEw8v6FTn8DEMqpHNxZ8fJW3KNN3i1",
        ],
        's01_addr7': [
            "112t8roMtSrKYCL4eA4aXiQ8umGz78znHRTdMpzKAbSgL1Cj6JtbkS9i87jW1KFjbpN9fwM3PY7LNJq3QyawdHX61eTwN6beiiayMjN4yPwC",
            "12S4oseu3scZJJuoLeGSEYZka1mmxHBNg7VbC1tQ67ZDjTUqzuRY4ABf4Bjop7uR22U1AxsLEheixfenpcc63tVG7E7QxF1zy5r1SXv"
        ], ''
           's02_addr2': [
            "112t8rndq3phbUG44goJZyYSy9Qvm6nEJr8N672tD8E5VyzqPuJVQBb1wcHQSrQibsbBLkrGfQ14fzw8iNoAtu13gqKjktffPrw9ZxcoNsbk",
            "12Rq6XDGQVYcxop7krJUJZCgsWCCU2UpgDDWdhjtxfeuWbcuksHNdjDkBVBz5t98q9UKjTS77Y6BZDeVeKuvw7QZfMBT7wb3M3YWS4k",
        ],
        's03_addr9': [
            "112t8rnsqDitXckbWMPo4wGbjwyPtYHywApPqfZVQNatrMzfDLERCmHTBPsHUZjhzFLxdVmQ6m6W5ppbK4PZCzWVjEBvi3a7SVrtVpd6GZSL",
            "12S3Xv2N9KvGZivRESKUQWv6obrghwykAUxqc85nTcZQ9AJMxnJe4Ct97BjAm5vFJ9bhhaHXDCmGfbXEqbS766DyeMLLeYksDM1FmSg",
        ],
        's04_addr4': [
            "112t8rnendREF3cg2vuRC248dFymXonwBC7TMmfppXEzz9wFziktHj8NhsGebcRmtquyg2zbytkecPMSHFBVcw4yJewv7E3J6cHgDzYiHoJj",
            "12S4YzSA6hC12zuMF8L2rC7Tks1TtcfDUSWjcPeKeyT1ApV1KXqQnmtpCNEYbta88GrjhPiS6yFfuyfViDW5cmooqsZ5tvC8SRJZdCF",
        ],
        's05_addr3': [
            "112t8rngNKpZHv6WsKqaYqKPi8JvfEVY9oqob3QiSKmbHbfDrDFXZZtmqLAacnmfqTJKKR9P2UJ1kYvkmdHAHU4zPRHpv38kHRRjLtHNv4yN",
            "12S2NxoLzvEsKBpvL6g3gjECvErpxVQoAg7VpnhojLXa6S3TchxbwM5aHQYJoT3K1nkq7C7VjAwgVwn2De3uLzD1J8VkmWe3cDRLPef",
        ],
        's06_addr10': [
            "112t8rnuBJ9Qwgc3pUadn5oiN1B3xo7SE7ZJVoXxwBdB8Jeoy1bzdWYB36nKVn4pTUKEhCtqCQyCCcPQAFrGjN4PsCpm8J6MV73D72yTuNFW",
            "12RuwRs21ZaDFdDGDkDRdbfyBLEzsDKzXgEhewStoMvQsQc9atziJSBbUwC45W9JJj6QfkR2TQmGVymPUjbTGHtuiGdBrhrZDLxcQtb"
        ],
        's07_addr11': [
            "112t8rndqnxKCi4yVxcZYD8Uvy4kQsid7c3g4GwZxf7Scp6ennGAouiyAfyHT9YoYd4BYjeW3XDxLZzy56S3GzMJpdiuXt7A1YaFCya6q25H",
            "12S25PTudeEs5c38ovtoy6cLeeaESKbSWQgRX7coFHKZEvvHmKTPSQe26pWuq17czJbz7ymQBRnXmH4CJdSge8uLAWTAoxZMGp9Nave"
        ]
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
        STEP(1, "get balance of sender and receiver before sending")
        balance1b = self.shard3.getBalance(self.test_data["s05_addr6"][0])
        INFO("sender balance: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", " get sender balance wrong")

        balance2b = self.shard3.getBalance(self.test_data["s05_addr3"][0])
        INFO("receiver balance: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get receiver balance wrong")
        # sent with amount >0
        STEP(2, "from address1 send prv to address2 -- amount >0")
        step2_result = self.shard3.sendTransaction(self.test_data["s05_addr6"][0],
                                                   self.test_data["s05_addr3"][1], self.test_data["prv_amount"],
                                                   privacy=0)
        INFO("Expecting: " + step2_result[0])
        INFO("StackTrace: " + step2_result[1])
        assert_true(step2_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'not enough output coin', step2_result[1]), "something went so wrong")

        # sent with amount = 0
        STEP(3, "from address1 send prv to address2 -- amount =0")
        step3_result = self.shard3.sendTransaction(self.test_data["s05_addr6"][0],
                                                   self.test_data["s05_addr3"][1], amount_prv=0,
                                                   privacy=0)
        INFO("Expecting: " + step3_result[0])
        INFO("StackTrace: " + step3_result[1])
        assert_true(step3_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'input value less than output value', step3_result[1]), "something went so wrong")

        # sent with amount < 0
        STEP(4, "from address1 send prv to address2 -- amount < 0")
        step4_result = self.shard3.sendTransaction(self.test_data["s05_addr6"][0],
                                                   self.test_data["s05_addr3"][1], amount_prv=-1,
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
        STEP(1, "get sender and receiver balance before sending")
        balance1b = self.shard3.getBalance(self.test_data["s05_addr6"][0])
        INFO("sender balance: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", " get sender balance wrong")

        balance2b = self.shard0.getBalance(self.test_data["s02_addr2"][0])
        INFO("receiver balance: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get receiver balance wrong")
        # sent with amount >0
        STEP(2, "send PRR -- amount >0")
        step2_result = self.shard3.sendTransaction(self.test_data["s05_addr6"][0],
                                                   self.test_data["s02_addr2"][1], self.test_data["prv_amount"],
                                                   privacy=0)
        INFO("Expecting: " + step2_result[0])
        INFO("StackTrace: " + step2_result[1])
        assert_true(step2_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'not enough output coin', step2_result[1]), "something went so wrong")

        # sent with amount = 0
        STEP(3, "send PRV -- amount =0")
        step3_result = self.shard3.sendTransaction(self.test_data["s05_addr6"][0],
                                                   self.test_data["s02_addr2"][1], amount_prv=0,
                                                   privacy=0)
        INFO("Expecting: " + step3_result[0])
        INFO("StackTrace: " + step3_result[1])
        assert_true(step3_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'input value less than output value', step3_result[1]), "something went so wrong")

        # sent with amount < 0
        STEP(4, "Send PRV -- amount < 0")
        step4_result = self.shard3.sendTransaction(self.test_data["s05_addr6"][0],
                                                   self.test_data["s02_addr2"][1], amount_prv=-1,
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
        STEP(1, "get sender and receiver balance before sending")
        balance1b = self.shard3.getBalance(self.test_data["s05_addr6"][0])
        INFO("sender balance: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", " get sender balance wrong")

        balance2b = self.shard3.getBalance(self.test_data["s05_addr3"][0])
        INFO("receiver balance: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get receiver balance wrong")
        # sent with amount >0
        STEP(2, "from address1 send prv to address2 -- amount >0")
        step2_result = self.shard3.sendTransaction(self.test_data["s05_addr6"][0],
                                                   self.test_data["s05_addr3"][1], self.test_data["prv_amount"])
        INFO("Expecting: " + step2_result[0])
        INFO("StackTrace: " + step2_result[1])
        assert_true(step2_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'not enough output coin', step2_result[1]), "something went so wrong")

        # sent with amount = 0
        STEP(3, "send PRV -- amount =0")
        step3_result = self.shard3.sendTransaction(self.test_data["s05_addr6"][0],
                                                   self.test_data["s05_addr3"][1], amount_prv=0)
        INFO("Expecting: " + step3_result[0])
        INFO("StackTrace: " + step3_result[1])
        assert_true(step3_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'input value less than output value', step3_result[1]), "something went so wrong")

        # sent with amount < 0
        STEP(4, "send PRV-- amount < 0")
        step4_result = self.shard3.sendTransaction(self.test_data["s05_addr6"][0],
                                                   self.test_data["s05_addr3"][1], amount_prv=-1)
        INFO("Expecting: " + step4_result[0])
        INFO("StackTrace: " + step4_result[1])
        assert_true(step4_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'not enough output coin', step4_result[1]), "something went so wrong")

    @pytest.mark.run
    def test_04_sendPRV_privacy_Xshard_with_0_balance(self):
        print("""
                        Verify send PRV form account balance = 0  to another address XShard with no privacy
                        """)

        STEP(1, "get sender and receiver balance before sending")
        balance1b = self.shard3.getBalance(self.test_data["s05_addr6"][0])
        INFO("sender balance before: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", " get sender balance wrong")

        balance2b = self.shard0.getBalance(self.test_data["s02_addr2"][0])
        INFO("receiver balance before: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get receiver balance wrong")
        # sent with amount >0
        STEP(2, "send PRV -- amount >0")
        step2_result = self.shard3.sendTransaction(self.test_data["s05_addr6"][0],
                                                   self.test_data["s02_addr2"][1], self.test_data["prv_amount"])
        INFO("Expecting: " + step2_result[0])
        INFO("StackTrace: " + step2_result[1])
        assert_true(step2_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'not enough output coin', step2_result[1]), "something went so wrong")

        # sent with amount = 0
        STEP(3, "send PRV -- amount =0")
        step3_result = self.shard3.sendTransaction(self.test_data["s05_addr6"][0],
                                                   self.test_data["s02_addr2"][1], amount_prv=0)
        INFO("Expecting: " + step3_result[0])
        INFO("StackTrace: " + step3_result[1])
        assert_true(step3_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'input value less than output value', step3_result[1]), "something went so wrong")

        # sent with amount < 0
        STEP(4, "send PRV -- amount < 0")
        step4_result = self.shard3.sendTransaction(self.test_data["s05_addr6"][0],
                                                   self.test_data["s02_addr2"][1], amount_prv=-1)
        INFO("Expecting: " + step4_result[0])
        INFO("StackTrace: " + step4_result[1])
        assert_true(step4_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'not enough output coin', step4_result[1]), "something went so wrong")

    @pytest.mark.run
    def test_05_sendPRV_noPrivacy_1shard_autoFee(self):
        print("""
                Verify send PRV ( no privacy - Auto fee )to another address 1Shard successfully with no privacy
                """)
        STEP(1, "get sender and receiver balance before sending")
        balance1b = self.shard0.getBalance(self.test_data["s02_addr1"][0])
        INFO("sender balance before: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", " get sender balance wrong")

        balance2b = self.shard0.getBalance(self.test_data["s02_addr2"][0])
        INFO("receiver balance before: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get receiver balance wrong")

        STEP(2, "send PRV")
        tx_id = self.shard0.sendTransaction(self.test_data["s02_addr1"][0],
                                            self.test_data["s02_addr2"][1], self.test_data["prv_amount"], privacy=0)
        INFO("transaction id: " + tx_id[0])
        assert_true(tx_id[0] != 'Can not create tx', "transaction failed", "make transaction success")

        STEP(3, " subcribe transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(tx_id[0])

        STEP(4, "check sender balance")
        balance1a = self.shard0.getBalance(self.test_data["s02_addr1"][0])
        INFO("sender balance after: " + str(balance1a))
        # Balance after = balance before - amount - fee
        assert_true(balance1a == balance1b - self.test_data["prv_amount"] - ws_res[2],
                    "sender balance output incorrect")

        STEP(5, "check receiver balance")
        balance2a = self.shard0.getBalance(self.test_data["s02_addr2"][0])
        INFO("receiver balance after: " + str(balance2a))
        # Balance after = balance before + amount
        assert_true(balance2a == balance2b + self.test_data["prv_amount"], "receiver balance output incorrect")

        STEP(6, "Check transaction privacy")
        step6_result = self.shard0.check_is_privacy_prv(tx_id[0])
        assert_true(step6_result[1] == "noprivacy", "transaction must be no privacy ", "transaction is no privacy")

    @pytest.mark.run
    def test_06_sendPRV_noPivacy_1shard_noAutoFee(self):
        print("""
                    Verify send PRV ( no privacy - noAuto fee ) to another address 1Shard successfully with no privacy
                    """)

        STEP(1, "get sender and receiver balance before sending")
        balance1b = self.shard0.getBalance(self.test_data["s02_addr1"][0])
        INFO("sender balance before: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", " get sender balance wrong")

        balance2b = self.shard0.getBalance(self.test_data["s02_addr2"][0])
        INFO("receiver balance before: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get receiver balance wrong")

        STEP(2, "send PRV")
        tx_id = self.shard0.sendTransaction(self.test_data["s02_addr1"][0],
                                            self.test_data["s02_addr2"][1], self.test_data["prv_amount"], fee=2,
                                            privacy=0)
        INFO("transaction id: " + tx_id[0])
        assert_true(tx_id[0] != 'Can not create tx', "transaction failed", "make transaction success")

        STEP(3, " subcrib transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(tx_id[0])

        STEP(4, "check sender balance")
        balance1a = self.shard0.getBalance(self.test_data["s02_addr1"][0])
        INFO("sender balance after:" + str(balance1a))
        # Balance after = balance before - amount - fee
        assert_true(balance1a == balance1b - self.test_data["prv_amount"] - ws_res[2],
                    "sender balance output incorrect")

        STEP(5, "check receiver balance")
        balance2a = self.shard0.getBalance(self.test_data["s02_addr2"][0])
        INFO("receiver balance after: " + str(balance2a))
        # Balance after = balance before + amount
        assert_true(balance2a == balance2b + self.test_data["prv_amount"], "receiver balance incorrect")

        STEP(6, "check transaction privacy")
        step6_result = self.shard0.check_is_privacy_prv(tx_id[0])
        assert_true(step6_result[1] == "noprivacy", "transaction must be no privacy ", "transaction is not privacy")

    @pytest.mark.run
    def test_07_sendPRV_privacy_1shard_autoFee(self):
        print("""
            Verify send PRV ( privacy - auto fee ) to another address 1Shard successfully
            """)

        STEP(1, "get sender and receiver balance before sending")
        balance1b = self.shard0.getBalance(self.test_data["s02_addr1"][0])
        INFO("sender balance before: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", " get sender balance wrong")

        balance2b = self.shard0.getBalance(self.test_data["s02_addr2"][0])
        INFO("receiver balance before: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get receiver balance wrong")

        STEP(2, "send PRV")
        tx_id = self.shard0.sendTransaction(self.test_data["s02_addr1"][0],
                                            self.test_data["s02_addr2"][1], self.test_data["prv_amount"])
        INFO("transaction id: " + tx_id[0])
        assert_true(tx_id[0] != 'Can not create tx', "transaction failed", "make transaction success")

        STEP(3, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(tx_id[0])

        STEP(4, "check sender balance")
        balance1a = self.shard0.getBalance(self.test_data["s02_addr1"][0])
        INFO("sender balance after: " + str(balance1a))
        # Balance after = balance before - amount - fee
        assert_true(balance1a == balance1b - self.test_data["prv_amount"] - ws_res[2],
                    "sender balance output incorrect")

        STEP(5, "check receiver balance")
        balance2a = self.shard0.getBalance(self.test_data["s02_addr2"][0])
        INFO("receiver balance after: " + str(balance2a))
        # Balance after = balance before + amount
        assert_true(balance2a == balance2b + self.test_data["prv_amount"], "receiver balance output incorrect")

        STEP(6, "check transaction privacy")
        step6_result = self.shard0.check_is_privacy_prv(tx_id[0])
        assert_true(step6_result[1] == "privacy", "transaction must be privacy ", "transaction is privacy")

    @pytest.mark.run
    def test_08_sendPRV_privacy_1shard_noAutoFee(self):
        print("""
                Verify send PRV ( privacy - noAuto fee ) to another address 1Shard successfully
                """)
        STEP(1, "get sender and receiver balance before sending")
        balance1b = self.shard0.getBalance(self.test_data["s02_addr1"][0])
        INFO("sender balance before: " + str(balance1b))
        assert_true(balance1b != "Invalid parameters", " get sender balance wrong")

        balance2b = self.shard0.getBalance(self.test_data["s02_addr2"][0])
        INFO("receiver balance before: " + str(balance2b))
        assert_true(balance2b != "Invalid parameters", "get receiver balance wrong")

        STEP(2, "send PRV")
        tx_id = self.shard0.sendTransaction(self.test_data["s02_addr1"][0],
                                            self.test_data["s02_addr2"][1], self.test_data["prv_amount"], fee=5)
        INFO("transaction id: " + tx_id[0])
        assert_true(tx_id[0] != 'Can not create tx', "transaction failed", "make transaction success")

        STEP(3, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(tx_id[0])

        STEP(4, "check sender balance")
        balance1a = self.shard0.getBalance(self.test_data["s02_addr1"][0])
        INFO("receiver balance after:: " + str(balance1a))
        # Balance after = balance before - amount - fee
        assert_true(balance1a == balance1b - self.test_data["prv_amount"] - ws_res[2],
                    "sender balance output incorrect")

        STEP(5, "check receiver balance")
        balance2a = self.shard0.getBalance(self.test_data["s02_addr2"][0])
        INFO("receiver balance after:: " + str(balance2a))
        # Balance after = balance before + amount
        assert_true(balance2a == balance2b + self.test_data["prv_amount"], "receiver balance output incorrect")

        STEP(6, "check transaction privacy")
        step6_result = self.shard0.check_is_privacy_prv(tx_id[0])
        assert_true(step6_result[1] == "privacy", "transaction must be privacy ", "transaction is privacy")

    @pytest.mark.run
    def test_09_sendPRV_noPrivacy_Xshard_autoFee(self):
        print("""
             Verify send PRV (no privacy- auto fee ) to another address Xshard successfully with no privacy
             """)
        STEP(1, "Get sender balance")
        step1_result = self.shard0.getBalance(self.test_data["s02_addr1"][0])
        INFO("sender balance before: " + str(step1_result))
        assert_true(step1_result != "Invalid parameters", " get sender balance wrong")

        STEP(2, "Get receiver balance")
        step2_result = self.shard1.getBalance(self.test_data["s05_addr3"][0])
        INFO("receiver balance before: " + str(step2_result))
        assert_true(step2_result != "Invalid parameters", "get receiver balance wrong")

        STEP(3, " send PRV")
        step3_result = self.shard0.sendTransaction(self.test_data["s02_addr1"][0],
                                                   self.test_data["s05_addr3"][1], self.test_data["prv_amount"],
                                                   privacy=0)
        INFO("Transaction ID: " + step3_result[0])
        assert_true(step3_result[0] != 'Can not create tx', "transaction failed", "make transaction success")

        STEP(4, "Subcribe transaction")
        self.shard0ws.createConnection()
        ws_res4 = self.shard0ws.subcribePendingTransaction(step3_result[0])

        STEP(5, "Subcribe cross transaction by privatekey")
        self.shard1ws.createConnection()
        ws_res5 = self.shard1ws.subcribeCrossOutputCoinByPrivatekey(self.test_data["s05_addr3"][0])

        STEP(6, "Check sender balance")
        step4_result = self.shard0.getBalance(self.test_data["s02_addr1"][0])
        INFO("sender balance after: " + str(step4_result))
        assert_true(step4_result == step1_result - self.test_data["prv_amount"] - ws_res4[2], "something wrong")

        STEP(7, "Check receiver balance")
        step5_result = self.shard1.getBalance(self.test_data["s05_addr3"][0])
        for i in range(1, 10):
            step5_result_temp = self.shard1.getBalance(self.test_data["s05_addr3"][0])
            if step5_result_temp > step5_result:
                step5_result = step5_result_temp
                break
            else:
                WAIT(10)
        INFO("receiver balance after: " + str(step5_result))
        assert_true(step5_result == step2_result + self.test_data["prv_amount"], "something wrong")

        STEP(8, "Check transaction privacy")
        step8_result = self.shard0.check_is_privacy_prv(step3_result[0])
        assert_true(step8_result[1] == "noprivacy", "transaction must be no privacy ", "transaction is not privacy")

    @pytest.mark.run
    def test_10_sendPRV_noPrivacy_Xshard_noAautoFee(self):
        print("""
             Verify send PRV (no privacy - no auto fee ) to another address Xshard successfully with no privacy
             Fee: 100 nanoPRV * transaction size
             """)

        STEP(1, "Get sender balance")
        step1_result = self.shard0.getBalance(self.test_data["s02_addr1"][0])
        INFO("sender balance before: " + str(step1_result))
        assert_true(step1_result != "Invalid parameters", " get sender balance wrong")

        STEP(2, "Get receiver balance")
        step2_result = self.shard1.getBalance(self.test_data["s05_addr3"][0])
        INFO("receiver balance before: " + str(step2_result))
        assert_true(step2_result != "Invalid parameters", "get receiver balance wrong")

        STEP(3, "Send PRV Xshard")
        step3_result = self.shard0.sendTransaction(self.test_data["s02_addr1"][0],
                                                   self.test_data["s05_addr3"][1], self.test_data["prv_amount"],
                                                   100, 0)
        INFO("Transaction ID: " + step3_result[0])
        assert_true(step3_result[0] != 'Can not create tx', "transaction failed", "make transaction success")

        STEP(4, "Subcribe transaction")
        self.shard0ws.createConnection()
        ws_res4 = self.shard0ws.subcribePendingTransaction(step3_result[0])
        assert_true(ws_res4[2] % 100 == 0, "Invalid tx fee", "Tx fee is %d * %dKB" % (100, ws_res4[2] / 100))

        STEP(5, "Subcribe cross transaction by privatekey")
        self.shard1ws.createConnection()
        ws_res5 = self.shard1ws.subcribeCrossOutputCoinByPrivatekey(self.test_data["s05_addr3"][0])

        STEP(6, "Check sender balance")
        step4_result = self.shard0.getBalance(self.test_data["s02_addr1"][0])
        INFO("sender balance after: " + str(step4_result))
        assert_true(step4_result == step1_result - self.test_data["prv_amount"] - ws_res4[2], "something wrong")

        STEP(7, "Check receiver balance")
        step5_result = self.shard1.getBalance(self.test_data["s05_addr3"][0])
        for i in range(1, 10):
            step5_result_temp = self.shard1.getBalance(self.test_data["s05_addr3"][0])
            if step5_result_temp > step5_result:
                step5_result = step5_result_temp
                break
            else:
                WAIT(10)
        INFO("receiver balance after: " + str(step5_result))
        assert_true(step5_result == step2_result + self.test_data["prv_amount"], "something wrong")

        STEP(8, "Check transaction privacy")
        step8_result = self.shard0.check_is_privacy_prv(step3_result[0])
        assert_true(step8_result[1] == "noprivacy", "transaction must be no privacy ", "transaction is not privacy")

    @pytest.mark.run
    def test_11_sendPRV_privacy_Xshard_autoFee(self):
        print("""
            Verify send PRV (privacy - auto fee ) to another address Xshard successfully
            """)

        STEP(1, "Get sender balance")
        step1_result = self.shard0.getBalance(self.test_data["s02_addr1"][0])
        INFO("sender balance before: " + str(step1_result))
        assert_true(step1_result != "Invalid parameters", " get sender balance wrong")

        STEP(2, "Get receiver balance")
        step2_result = self.shard1.getBalance(self.test_data["s05_addr3"][0])
        INFO("receiver balance before: " + str(step2_result))
        assert_true(step2_result != "Invalid parameters", "get receiver balance wrong")

        STEP(3, "send PRV")
        step3_result = self.shard0.sendTransaction(self.test_data["s02_addr1"][0],
                                                   self.test_data["s05_addr3"][1], self.test_data["prv_amount"])
        INFO("Transaction ID: " + step3_result[0])
        assert_true(step3_result[0] != 'Can not create tx', "transaction failed", "make transaction success")

        STEP(4, "Subcribe transaction")
        self.shard0ws.createConnection()
        ws_res4 = self.shard0ws.subcribePendingTransaction(step3_result[0])

        STEP(5, "Subcribe cross transaction by privatekey")
        self.shard1ws.createConnection()
        ws_res5 = self.shard1ws.subcribeCrossOutputCoinByPrivatekey(self.test_data["s05_addr3"][0])

        STEP(6, "Check sender balance")
        step4_result = self.shard0.getBalance(self.test_data["s02_addr1"][0])
        INFO("sender balance after: " + str(step4_result))
        assert_true(step4_result == step1_result - self.test_data["prv_amount"] - ws_res4[2], "something wrong")

        STEP(7, "Check receiver balance")
        step5_result = self.shard1.getBalance(self.test_data["s05_addr3"][0])
        for i in range(1, 10):
            step5_result_temp = self.shard1.getBalance(self.test_data["s05_addr3"][0])
            if step5_result_temp > step5_result:
                step5_result = step5_result_temp
                break
            else:
                WAIT(10)
        INFO("receiver balance after: " + str(step5_result))
        assert_true(step5_result == step2_result + self.test_data["prv_amount"], "something wrong")

        STEP(8, "Check transaction privacy")
        step8_result = self.shard0.check_is_privacy_prv(step3_result[0])
        assert_true(step8_result[1] == "privacy", "transaction must be privacy ", "transaction is privacy")

    @pytest.mark.run
    def test_12_sendPRV_privacy_Xshard_noAutoFee(self):
        print("""
               Verify send PRV (privacy - no Auto fee) to another address Xshard successfully
               Fee: 100 nanoPRV * transaction size
               """)
        STEP(1, "Get sender balance")
        step1_result = self.shard0.getBalance(self.test_data["s02_addr1"][0])
        INFO("sender balance before: " + str(step1_result))
        assert_true(step1_result != "Invalid parameters", " get sender balance wrong")

        STEP(2, "Get receiver balance")
        step2_result = self.shard1.getBalance(self.test_data["s05_addr3"][0])
        INFO("receiver balance before: " + str(step2_result))
        assert_true(step2_result != "Invalid parameters", "get receiver balance wrong")

        STEP(3, "From address1 send prv to address3")
        step3_result = self.shard0.sendTransaction(self.test_data["s02_addr1"][0],
                                                   self.test_data["s05_addr3"][1], self.test_data["prv_amount"],
                                                   100)
        INFO("Transaction ID: " + step3_result[0])
        assert_true(step3_result[0] != 'Can not create tx', "transaction failed", "make transaction success")

        STEP(4, "Subcribe transaction")
        self.shard0ws.createConnection()
        ws_res4 = self.shard0ws.subcribePendingTransaction(step3_result[0])
        assert_true(ws_res4[2] % 100 == 0, "Invalid tx fee", "Tx fee is %d * %dKB" % (100, ws_res4[2] / 100))

        STEP(5, "Subcribe cross transaction by privatekey")
        self.shard1ws.createConnection()
        ws_res5 = self.shard1ws.subcribeCrossOutputCoinByPrivatekey(self.test_data["s05_addr3"][0])

        STEP(6, "Check sender balance")
        step4_result = self.shard0.getBalance(self.test_data["s02_addr1"][0])
        INFO("sender balance after: " + str(step4_result))
        assert_true(step4_result == step1_result - self.test_data["prv_amount"] - ws_res4[2], "something wrong")

        STEP(7, "Check receiver balance")
        step5_result = self.shard1.getBalance(self.test_data["s05_addr3"][0])
        for i in range(1, 10):
            step5_result_temp = self.shard1.getBalance(self.test_data["s05_addr3"][0])
            if step5_result_temp > step5_result:
                step5_result = step5_result_temp
                break
            else:
                WAIT(10)
        INFO("receiver balance after: " + str(step5_result))
        assert_true(step5_result == step2_result + self.test_data["prv_amount"], "something wrong")

        STEP(8, "Check transaction privacy")
        step8_result = self.shard0.check_is_privacy_prv(step3_result[0])
        assert_true(step8_result[1] == "privacy", "transaction must be privacy ", "transaction is privacy")

    @pytest.mark.run
    def test_13_sendPRV_privacy_Xshard_insufficient_fund(self):
        print("""
            Verify send PRV to another address:
            - Not enough coin (insufficient fund)
            - Wrong input transaction
            """)

        STEP(1, "Get receiver balance")
        step1_result = self.shard0.getBalance(self.test_data["s02_addr1"][0])
        INFO("receiver balance before: " + str(step1_result))
        assert_true(step1_result != "Invalid parameters", "get balance wrong")

        STEP(2, "Get sender balance")
        step2_result = self.shard1.getBalance(self.test_data["s05_addr3"][0])
        INFO("sender balance before: " + str(step2_result))
        assert_true(step2_result != 0, "addr3_balance = 0, stop this testcase")

        STEP(3, "send PRV - Not enough coin")
        # send current balance + 10
        step3_result = self.shard1.sendTransaction(self.test_data["s05_addr3"][0],
                                                   self.test_data["s02_addr1"][1], step2_result + 10)
        INFO("Expecting: " + step3_result[0])
        INFO("StackTrace: " + step3_result[1])
        assert_true(step3_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'Not enough coin', step3_result[1]), "something went so wrong")

        # breakpoint()

        STEP(4, "send PRV - Wrong input transaction")
        # send current balance (lacking of fee)
        step4_result = self.shard1.sendTransaction(self.test_data["s05_addr3"][0],
                                                   self.test_data["s02_addr1"][1], step2_result)
        INFO("Expecting: " + step4_result[0])
        INFO("StackTrace: " + step4_result[1])
        assert_true(step4_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'Wrong input transaction', step4_result[1]), "something went so wrong")
        estimated_fee = re.search(r'fee=(\d+)\n', step4_result[1])
        estimated_fee = estimated_fee.group(1)
        INFO("Estimated fee: " + estimated_fee)

        # breakpoint()

        STEP(5, "send PRV - success")
        # send current balance - fee
        step5_result = self.shard1.sendTransaction(self.test_data["s05_addr3"][0],
                                                   self.test_data["s02_addr1"][1],
                                                   step2_result - int(estimated_fee))
        if step5_result[0] != 'Can not create tx':
            # assert_true(step5_result[0] != 'Can not create tx', step5_result[1])
            INFO("TxID 1 : " + step5_result[0])
        else:
            estimated_fee = re.search(r'fee=(\d+)\n', step5_result[1])
            estimated_fee = estimated_fee.group(1)
            INFO("Estimated new fee: " + estimated_fee)
            step5_result = self.shard1.sendTransaction(self.test_data["s05_addr3"][0],
                                                       self.test_data["s02_addr1"][1],
                                                       step2_result - int(estimated_fee))
            assert_true(step5_result[0] != 'Can not create tx', step5_result[1])
            INFO("TxID: " + step5_result[0])

        STEP(6, "Subcribe transaction")
        self.shard0ws.createConnection()
        ws_res6 = self.shard0ws.subcribePendingTransaction(step5_result[0])

        STEP(7, "Subcribe cross transaction by privatekey")
        self.shard1ws.createConnection()
        ws_res7 = self.shard1ws.subcribeCrossOutputCoinByPrivatekey(self.test_data["s02_addr1"][0])

        STEP(8, "Check receiver balance")
        step8_result = self.shard0.getBalance(self.test_data["s02_addr1"][0])
        for i in range(1, 10):
            step8_result_temp = self.shard0.getBalance(self.test_data["s02_addr1"][0])
            if step8_result_temp > step8_result:
                step8_result = step8_result_temp
                break
            else:
                WAIT(10)
        INFO("receiver balance after: " + str(step8_result))
        assert_true(step8_result == step1_result + step2_result - ws_res6[2], "something wrong")

        STEP(9, "Check sender balance")
        step7_result = self.shard1.getBalance(self.test_data["s05_addr3"][0])
        INFO("sender balance after: " + str(step7_result))
        assert_true(step7_result == 0, "something wrong")

        STEP(10, "Check transaction privacy")
        step10_result = self.shard1.check_is_privacy_prv(step5_result[0])
        assert_true(step10_result[1] == "privacy", "transaction must be privacy ", "transaction is privacy")

    @pytest.mark.run
    def test_14_sendPRV_noprivacy_1shard_insufficient_fund(self):
        print("""
                Verify send PRV to another address:
                - Not enough coin (insufficient fund)
                - Wrong input transaction
                """)

        STEP(1, "Get receiver balance")
        step1_result = self.shard0.getBalance(self.test_data["s02_addr1"][0])
        INFO("receiver balance before: " + str(step1_result))
        assert_true(step1_result != "Invalid parameters", "get balance wrong")

        STEP(2, "Get sender balance")
        step2_result = self.shard0.getBalance(self.test_data["s02_addr2"][0])
        INFO("sender balance before: " + str(step2_result))
        assert_true(step2_result != 0, "addr2_balance = 0, stop this testcase")

        STEP(3, "From address2 send prv to address1 - Not enough coin")
        # send current balance + 10
        step3_result = self.shard0.sendTransaction(self.test_data["s02_addr2"][0],
                                                   self.test_data["s02_addr1"][1], step2_result + 10, privacy=0)
        INFO("Expecting: " + step3_result[0])
        INFO("StackTrace: " + step3_result[1])
        assert_true(step3_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'Not enough coin', step3_result[1]), "something went so wrong")

        # breakpoint()

        STEP(4, "send PRV - Wrong input transaction")
        # send current balance (lacking of fee)
        step4_result = self.shard0.sendTransaction(self.test_data["s02_addr2"][0],
                                                   self.test_data["s02_addr1"][1], step2_result, privacy=0)
        INFO("Expecting: " + step4_result[0])
        INFO("StackTrace: " + step4_result[1])
        assert_true(step4_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'Wrong input transaction', step4_result[1]), "something went so wrong")
        estimated_fee = re.search(r'fee=(\d+)\n', step4_result[1])
        estimated_fee = estimated_fee.group(1)
        INFO("Estimated fee: " + estimated_fee)

        # breakpoint()

        STEP(5, "Send PRV - success")
        # send current balance - fee
        step5_result = self.shard0.sendTransaction(self.test_data["s02_addr2"][0],
                                                   self.test_data["s02_addr1"][1],
                                                   step2_result - int(estimated_fee), privacy=0)
        if step5_result[0] != 'Can not create tx':
            # assert_true(step5_result[0] != 'Can not create tx', step5_result[1])
            INFO("TxID: " + step5_result[0])
        else:
            estimated_fee = re.search(r'fee=(\d+)\n', step5_result[1])
            estimated_fee = estimated_fee.group(1)
            INFO("Estimated new fee: " + estimated_fee)
            step5_result = self.shard0.sendTransaction(self.test_data["s02_addr2"][0],
                                                       self.test_data["s02_addr1"][1],
                                                       step2_result - int(estimated_fee))
            assert_true(step5_result[0] != 'Can not create tx', step5_result[1])
            INFO("TxID: " + step5_result[0])

        STEP(6, "Subcribe transaction")
        self.shard0ws.createConnection()
        ws_res6 = self.shard0ws.subcribePendingTransaction(step5_result[0])

        STEP(7, "Check receiver balance")
        step7_result = self.shard0.getBalance(self.test_data["s02_addr1"][0])
        INFO("receiver balance after: " + str(step7_result))
        assert_true(step7_result == step1_result + step2_result - ws_res6[2], "something wrong")

        STEP(8, "Check sender balance")
        step8_result = self.shard0.getBalance(self.test_data["s02_addr2"][0])
        INFO("sender balance after: " + str(step8_result))
        assert_true(step8_result == 0, "something wrong")

        STEP(9, "Check transaction privacy")
        step9_result = self.shard0.check_is_privacy_prv(step5_result[0])
        assert_true(step9_result[1] == "noprivacy", "transaction must be no privacy ", "transaction is not privacy")

    @pytest.mark.run
    def est_15_sendPRV_privacy_Xshard_max_value(self):
        print("""
             Verify send PRV to another address:
             -  > 10 mil PRV unsuccess
             - Tx fee = 100000000000 PRV success
             """)
        STEP(1, "Get address1 balance")
        step1_result = self.shard0.getBalance(self.test_data["s02_addr1"][0])
        INFO("addr1_balance: " + str(step1_result))
        assert step1_result != "Invalid parameters"

        STEP(2, "Get address3 balance")
        step2_result = self.shard1.getBalance(self.test_data["s05_addr3"][0])
        INFO("addr3_balance: " + str(step2_result))
        assert_true(step2_result != 0, "addr3_balance = 0, stop this testcase")

        STEP(3, "From address3 send prv to address1 - max value")
        # send amount = 1000000000000000000
        step3_result = self.shard1.sendTransaction(self.test_data["s05_addr3"][0],
                                                   self.test_data["s02_addr1"][1], 1000000000000000001)
        INFO("Expecting: " + step3_result[0])
        INFO("StackTrace: " + step3_result[1])
        assert_true(step3_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'Not enough coin', step3_result[1]), "something went so wrong")

        STEP(4, "From address3 send prv to address1 - max value fee ")
        # send with fee = 10000000000000 PRV
        step4_result = self.shard1.sendTransaction(self.test_data["s05_addr3"][0],
                                                   self.test_data["s02_addr1"][1], self.test_data["prv_amount"],
                                                   fee=900000000000000)
        INFO("Expecting: " + step4_result[0])
        INFO("StackTrace: " + step4_result[1])
        assert_true(step4_result[0] == 'Can not create tx', "something went wrong, this tx must failed")
        assert_true(re.search(r'input value less than output value', step4_result[1]), "something went so wrong")

    @pytest.mark.run
    def test_16_sendPRV_multi_output_privacy_1shard_noAutoFee(self):
        print("""
                   Verify send PRV ( privacy - noAuto fee ) to another address 1Shard successfully
                   """)
        output_payment_address = list()
        output_private_address = list()
        for k, v in self.test_data_multi_output.items():
            output_payment_address.append(v[1])
            output_private_address.append(v[0])

        STEP(1, "get sender balance before sending")
        sender_balance = self.shard0.getBalance(self.test_data["s02_addr1"][0])
        assert_true(sender_balance != "Invalid parameters", "get sender balance fail", "get sender balance success")
        INFO("sender balance before: " + str(sender_balance))

        STEP(2, "get receiver balance before sending")
        list_receiver_banace = list()
        for i in range(0, len(output_private_address)):
            temp_balance = self.shard0.getBalance(output_private_address[i])
            list_receiver_banace.append(temp_balance)
            INFO("reciver " + str(i + 1) + " balance before : " + str(temp_balance))

        STEP(3, "send PRV to multi output")
        tx_id = self.shard0.sendTransactionMultiOuputPRV(self.test_data["s02_addr1"][0], output_payment_address,
                                                         self.test_data["prv_amount"])
        assert_true(tx_id[0] != "Can not create tx", "transaction fail", "make successfull transaction")
        INFO("transaction id: " + tx_id[0])

        STEP(4, "subcribe transaction")
        self.shard0ws.createConnection()
        ws_res = self.shard0ws.subcribePendingTransaction(tx_id[0])

        STEP(5, "check sender balance after send")
        sender_balance_after = self.shard0.getBalance(self.test_data["s02_addr1"][0])
        assert_true(sender_balance_after != "Invalid parameters", "get sender balance fail",
                    "get sender balance success")
        INFO("sender balance after : " + str(sender_balance_after))
        # Balance after = balance before - (amount x n_payment)  - fee
        assert_true(
            sender_balance_after == sender_balance - (self.test_data["prv_amount"] * len(output_payment_address)) -
            ws_res[2], "balance of sender wrong", " balance of sender correct")

        STEP(6, "check receiver balance")
        for i in range(0, len(output_private_address)):
            temp_balance_receiver = self.shard0.getBalance(output_private_address[i])
            for j in range(0, 10):
                temp = self.shard0.getBalance(output_private_address[i])
                if temp > temp_balance_receiver:
                    temp_balance_receiver = temp
                    break
                else:
                    WAIT(10)
            INFO("receiver " + str(i + 1) + " balance after: " + str(temp_balance_receiver))
            # Balance after = balance before + amount
            assert_true(temp_balance_receiver == list_receiver_banace[i] + self.test_data["prv_amount"],
                        "balance incorrect", "balance addresss " + str(i + 1) + " correct")

        STEP(7, "check transaction privacy")
        step7_result = self.shard0.check_is_privacy_prv(tx_id[0])
        assert_true(step7_result[1] == "privacy", "transaction must be privacy ", "transaction is privacy")

    @pytest.mark.run
    def test_99_cleanup(self):
        print("""
            CLEAN UP
            """)
        self.shard0ws.closeConnection()
        self.shard1ws.closeConnection()
        self.shard2ws.closeConnection()
        self.shard3ws.closeConnection()
