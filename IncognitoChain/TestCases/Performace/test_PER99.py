import concurrent
import json
import random
import time
from concurrent.futures.thread import ThreadPoolExecutor

import pytest

from IncognitoChain.Configs.Constants import coin
from IncognitoChain.Helpers.Logging import INFO, INFO_HEADLINE
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.AccountObject import Account, COIN_MASTER
from IncognitoChain.Objects.IncognitoTestCase import ACCOUNTS, SUT

LOOP = 4
TX_PER_LOOP = 40
TX_FEE = -1
TX_PRIVACY = 1
CROSS_SHARD_TX = False
SEND_AMOUNT = random.randrange(1000, 100000)


def create_proofs(senders, receivers, tx_fee, tx_privacy):
    proof_list = []
    thread_list = []
    for sender, receiver in zip(senders, receivers):
        sender: Account
        with ThreadPoolExecutor() as executor:
            thread = executor.submit(sender.create_tx_proof, receiver, SEND_AMOUNT, tx_fee, tx_privacy)
            thread_list.append(thread)
    concurrent.futures.wait(thread_list, timeout=180)
    for thread in thread_list:
        proof_list.append(thread.result())
    return proof_list


def prepare_proof_1_shard_in_1_shard(fee, privacy):
    # shard = random.randrange(len(ACCOUNTS))
    shard = 0
    num_of_acc = len(ACCOUNTS[shard])
    num_o_proof = num_of_proofs()
    if num_o_proof > num_of_acc / 2:
        raise IndexError(f"Need {num_o_proof * 2} Account to create tx, "
                         f"but there's only {num_of_acc} Account in shard {shard}")
    senders__ = ACCOUNTS[shard][:num_of_proofs()]
    receivers = ACCOUNTS[shard][-num_of_proofs():]
    COIN_MASTER.top_him_up_prv_to_amount_if(coin(3), coin(5), senders__)
    INFO_HEADLINE(f' PREPARE TEST DATA, 1 SHARD TX, SHARD {shard}')
    return create_proofs(senders__, receivers, fee, privacy)


def prepare_proof_1_shard_in_n_shard(fee, privacy):
    pass


def prepare_proof_x_shard_from_1_shard(fee, privacy):
    send____shard = random.randrange(len(ACCOUNTS))
    receive_shard = random.randrange(len(ACCOUNTS))
    senders__ = ACCOUNTS[send____shard][:num_of_proofs()]
    receivers = ACCOUNTS[receive_shard][:num_of_proofs()]
    return create_proofs(senders__, receivers, fee, privacy)


def num_of_proofs():
    return TX_PER_LOOP * LOOP


@pytest.mark.parametrize("proof_list", [
    prepare_proof_1_shard_in_1_shard(-1, 1),
    # prepare_proof_1_shard_in_1_shard(-1, 0),
])
def test_tx_machine_gun(proof_list):
    INFO_HEADLINE(f'Firing {len(proof_list)} txs at full node, {TX_PER_LOOP} round at a time')
    thread_list = []
    proof_list_len = len(proof_list)
    for i in range(proof_list_len):
        proof = proof_list[i]
        with ThreadPoolExecutor() as executor:
            thread = executor.submit(SUT.REQUEST_HANDLER.send_proof, proof)
            thread_list.append(thread)
        if (i + 1) % TX_PER_LOOP == 0:
            time.sleep(1)

    concurrent.futures.wait(thread_list)

    INFO_HEADLINE('Wait 40 for txs to be confirmed')
    WAIT(40)

    INFO_HEADLINE(f'Subscribe to txs to get block height')
    block_list = {}
    for response in thread_list:
        tx_hash = response.result().get_tx_id()
        with ThreadPoolExecutor() as executor:
            thread = executor.submit(response.result().subscribe_transaction)
        block_list[tx_hash] = thread

    summary = {}
    for tx_hash, result in block_list.items():
        block_height = result.result().get_block_height()
        INFO(f'{tx_hash} : {block_height}')
        try:
            summary[block_height] += 1
        except KeyError:
            summary[block_height] = 1

    INFO(f""" SUMMARY
            {json.dumps(summary, indent=3)}
        """)
