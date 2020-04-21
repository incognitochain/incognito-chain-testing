import random

from IncognitoChain.Helpers.Logging import STEP
from IncognitoChain.Helpers.ThreadHelper import wait_threads_to_complete
from IncognitoChain.Objects.IncognitoTestCase import SUT, COIN_MASTER
from IncognitoChain.TestCases.Performace import *


def setup_function():
    transactions_save_fullnode.clear()
    INFO('get balance all accounts')
    for account in accounts_send + accounts_receive:
        account.calculate_shard_id()
        balance = account.get_prv_balance()
        if balance < 1300:
            COIN_MASTER.send_prv_to(account, 1300, privacy=0).subscribe_transaction()


def test_max_tx_in_same_block():
    fullnode = -1
    STEP(1, "Prepare bunch of addresses that has PRV - same shard")

    STEP(2, 'Send 100 nano PRV to each others at the same time')
    everyone_send_prv_simultaneously(fullnode)
    wait_threads_to_complete(all_thread_list)

    # subscribe the last transaction to make sure all transactions are handled
    for index in range(data_length - 1, -1, -1):
        if transactions_save_fullnode[index].get_tx_id() is not None:
            transactions_save_fullnode[index].subscribe_transaction()
            break

    STEP(3, 'Get transaction by hash of each tx_id => check that them all in same block-height (or block-height + 1)')
    block_height = None
    for tx in transactions_save_fullnode:
        if tx.get_tx_id() is not None:
            block_height = tx.get_transaction_by_hash().get_block_height()
            break
    # breakpoint()
    INFO(f'Expect all transactions must has same block height as {block_height} or {block_height} + 1')
    for index in range(0, data_length):
        transaction = transactions_save_fullnode[index]
        tx_block_height = transaction.get_transaction_by_hash().get_block_height()
        assert (block_height == tx_block_height or block_height + 1 == tx_block_height) and INFO(
            f'{index}: tx = {transaction.get_tx_id()}, block height = {tx_block_height}')

    STEP(4, 'Verify that block contains at least 10 tx')
    tx_in_block_count = 0
    tx_hashes = SUT.full_node.system_rpc().retrieve_block_by_height(block_height, shard).get_tx_hashes()
    INFO(f""" Tx Hashes
            {tx_hashes}""")
    for transaction in transactions_save_fullnode:
        if transaction.get_tx_id() in tx_hashes:
            tx_in_block_count += 1
    assert tx_in_block_count >= 10 and INFO(f'Total tx in block {block_height} = {tx_in_block_count}')


def test_x_shard_prv_ptoken_send_with_mix_privacy():
    ptoken_senders = account_list[0:10]
    prv_senders = account_list[10:20]
    receiver = account_list[20]
    privacy_options = list()
    for i in range(0, len(prv_senders)):
        privacy_options.append(random.randrange(0, 1))
    prv_amount = 100
    ptoken_amount = 200
    prv_send_results: List[Response] = []
    prv_send_threads: List[Thread] = []
    ptoken_send_results: List[Response] = []
    ptoken_send_threads: List[Thread] = []

    STEP(1, 'Create 10 prv transaction simultaneously ')
    for sender in prv_senders:
        thread = Thread(target=sending_prv_thread, args=(sender, receiver, prv_amount, -1, -1, prv_send_results,))
        thread.start()
        prv_send_threads.append(thread)

    STEP(2, 'Create 10 ptoken transaction simultaneously')
    for i in range(0, len(ptoken_senders)):
        sender = ptoken_senders[i]
        ptoken_privacy = privacy_options[i]
        thread = Thread(target=sending_ptoken_thread, args=(sender, receiver, ptoken_id, ptoken_amount, ptoken_privacy,
                                                            ptoken_send_results))
        thread.start()
        ptoken_send_threads.append(thread)

    STEP(3, 'Wait all sending transaction to complete')
    for thread in prv_send_threads + ptoken_send_threads:
        thread.join()
    try:
        receiver.subscribe_cross_output_token()
        receiver.subscribe_cross_output_coin()
    except Exception:
        pass

    STEP(4, 'Check if all 20 transactions are in the same block or the next block only')
    block_height = prv_send_results[0].get_transaction_by_hash().get_block_height()
    count_tx_in_block = {block_height: 0,
                         block_height + 1: 0,
                         0: 0}

    i = 1
    for result in prv_send_results + ptoken_send_results:
        tx_id = result.get_tx_id()
        block_h = result.get_transaction_by_hash().get_block_height()
        INFO(f'{i} tx: {tx_id}, block {block_h}')
        if tx_id is not None:
            count_tx_in_block[block_h] += 1
            if block_height != 0:
                assert (block_h == block_height or block_h == block_height + 1)
        i += 1

    STEP(5, f'Double check, must has at least 10 tx in block {block_height}')
    tx_in_block_count = 0
    tx_hashes = SUT.full_node.system_rpc().retrieve_block_by_height(block_height, shard).get_tx_hashes()
    INFO('List hashes to check : ')
    for tx in tx_hashes:
        INFO(tx)
    for transaction in prv_send_results + ptoken_send_results:
        INFO(f'checking tx: {transaction.get_tx_id()} ')
        if transaction.get_tx_id() in tx_hashes:
            tx_in_block_count += 1
    assert tx_in_block_count >= 10 and INFO(f'Total tx in block {block_height} = {tx_in_block_count}')
