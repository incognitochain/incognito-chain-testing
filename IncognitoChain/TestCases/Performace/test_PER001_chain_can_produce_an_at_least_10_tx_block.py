import random
from concurrent.futures.thread import ThreadPoolExecutor

import pytest

from IncognitoChain.Configs.Constants import PRV_ID
from IncognitoChain.Helpers.Logging import STEP, INFO
from IncognitoChain.Helpers.TestHelper import l6
from IncognitoChain.Helpers.Time import WAIT
from IncognitoChain.Objects.AccountObject import COIN_MASTER
from IncognitoChain.Objects.IncognitoTestCase import SUT
from IncognitoChain.TestCases.Performace import *


def setup_function():
    INFO('get balance all accounts')
    COIN_MASTER.top_him_up_prv_to_amount_if(1300, 1300, accounts_send + accounts_receive)
    thread_list = []
    with ThreadPoolExecutor() as executor:
        for user in account_list:
            t = executor.submit(user.de_fragment_prv)
            thread_list.append(t)

    WAIT(40)


def test_max_tx_in_same_block():
    STEP(1, "Prepare bunch of addresses that has PRV - same shard")

    STEP(2, 'Send 100 nano PRV to each others at the same time')
    INFO(f"Creating {data_length} transactions ")
    full_node_send_thread = []
    with ThreadPoolExecutor() as executor:
        for index in range(0, data_length):
            thread = executor.submit(accounts_send[index].send_prv_to, accounts_receive[index], 234)
            full_node_send_thread.append(thread)

    # subscribe transaction to make sure all transactions are handled
    for index in range(data_length - 1, -1, -1):
        thread = full_node_send_thread[index]
        if thread.result().get_tx_id() is not None:
            thread.result().subscribe_transaction()
            break

    STEP(3, 'Get transaction by hash of each tx_id => check that them all in same block-height (or block-height + 1)')
    block_height = None
    for tx_thread in full_node_send_thread:
        tx = tx_thread.result()
        if tx.get_tx_id() is not None:
            block_height = tx.get_transaction_by_hash().get_block_height()
            break
    # breakpoint()
    INFO(f'Expect all transactions must has same block height as {block_height} or {block_height} + 1')
    for index in range(0, data_length):
        transaction = full_node_send_thread[index].result()
        tx_block_height = transaction.get_transaction_by_hash().get_block_height()
        assert INFO(f'{index}: tx = {transaction.get_tx_id()}, block height = {tx_block_height}') and \
               (block_height == tx_block_height or block_height + 1 == tx_block_height)
    STEP(4, 'Verify that block contains at least 10 tx')
    tx_in_block_count = 0
    tx_hashes = SUT().get_shard_block_by_height(shard, block_height).get_tx_hashes()
    INFO(f""" Tx Hashes
            {tx_hashes}""")
    for transaction in full_node_send_thread:
        if transaction.result().get_tx_id() in tx_hashes:
            tx_in_block_count += 1
    assert tx_in_block_count >= 10 and INFO(f'Total tx in block {block_height} = {tx_in_block_count}')


def test_x_shard_prv_ptoken_send_with_mix_privacy():
    token_senders = account_list[0:10]
    prv_senders = account_list[10:20]
    receiver = account_list[20]
    privacy_options = list()
    for i in range(0, len(prv_senders)):
        privacy_options.append(random.randrange(0, 1))
    prv_amount = 100
    token_amount = 200
    prv_send_threads = []
    token_send_threads = []

    STEP(0, f'Check if token can be use to pay fee')
    if not SUT().get_latest_pde_state_info().is_pair_existed(PRV_ID, ptoken_id):
        msg = f'pair {l6(PRV_ID)}-{l6(ptoken_id)} is not existed in DEX, cannot use toke to pay fee'
        INFO(msg)
        pytest.skip(msg)

    STEP(1, 'Create 10 prv transaction simultaneously ')
    with ThreadPoolExecutor() as executor:
        for sender in prv_senders:
            thread = executor.submit(sender.send_prv_to, receiver, prv_amount, -1, -1)
            prv_send_threads.append(thread)

    STEP(2, 'Create 10 ptoken transaction simultaneously')
    with ThreadPoolExecutor() as executor:
        for i in range(0, len(token_senders)):
            sender: Account = token_senders[i]
            token_privacy = privacy_options[i]
            thread = executor.submit(sender.send_token_to, receiver, ptoken_id, token_amount,
                                     token_privacy=token_privacy)
            token_send_threads.append(thread)

    STEP(3, 'Wait all sending transaction to complete')

    send_token_tx = []
    send_prv_tx = []
    with ThreadPoolExecutor() as executor:
        for thread in prv_send_threads:
            thread = executor.submit(thread.result().subscribe_transaction)
            send_prv_tx.append(thread)
        for thread in token_send_threads:
            thread = executor.submit(thread.result().subscribe_transaction)
            send_token_tx.append(thread)

    STEP(4, 'Check if all 20 transactions are in the same block or the next block only')
    block_height = send_prv_tx[0].result().get_block_height()
    count_tx_in_block = {block_height: 0,
                         block_height + 1: 0,
                         0: 0}

    i = 1
    for thread in send_prv_tx + send_token_tx:
        tx_id = thread.result().get_tx_id()
        block_h = thread.result().get_block_height()
        INFO(f'{i} tx: {tx_id}, block {block_h}')
        if tx_id is not None:
            count_tx_in_block[block_h] += 1
            if block_height != 0:
                assert (block_h == block_height or block_h == block_height + 1)
        i += 1

    STEP(5, f'Double check, must has at least 10 tx in block {block_height}')
    tx_in_block_count = 0
    tx_hashes = SUT().get_shard_block_by_height(shard, block_height).get_tx_hashes()
    INFO('List hashes to check : ')
    for tx in tx_hashes:
        INFO(tx)
    for thread in send_prv_tx + send_token_tx:
        transaction = thread.result()
        INFO(f'checking tx: {transaction.get_tx_id()} ')
        if transaction.get_tx_id() in tx_hashes:
            tx_in_block_count += 1
    assert tx_in_block_count >= 10 and INFO(f'Total tx in block {block_height} = {tx_in_block_count}')
