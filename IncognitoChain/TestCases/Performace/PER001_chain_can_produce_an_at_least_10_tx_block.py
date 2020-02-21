import random
from threading import Thread
from typing import List

from IncognitoChain.Drivers.Response import Response
from IncognitoChain.Helpers.Logging import STEP, INFO
from IncognitoChain.Objects.AccountObject import Account
from IncognitoChain.Objects.IncognitoTestCase import SUT
from IncognitoChain.TestCases.Performace import account_list

data_length = 12
account_list_len = len(account_list) - 1
accounts_send = account_list[0:data_length]
accounts_receive = account_list[account_list_len - data_length:account_list_len]

shard = accounts_send[0].shard

transactions_save_fullnode: List[Response] = []
transactions_save_shard: List[Response] = []

all_thread_list = list()

custom_fee = 100
# 2 random pair of account to send transaction in shard
random_i = [random.randrange(0, data_length), random.randrange(0, data_length)]
i_to_check_latest = data_length - 1
for i in range(data_length - 1, -1, -1):
    if i not in random_i:
        i_to_check_latest = i
        break
i_to_check_soonest = 0
for i in range(0, data_length):
    if i not in random_i:
        i_to_check_soonest = i
        break
for i in random_i:
    accounts_send[i].defragment_account()


def setup_function():
    transactions_save_fullnode.clear()
    INFO('get balance all accounts')
    for account in accounts_send + accounts_receive:
        account.get_prv_balance()


def test_max_tx_in_same_block():
    fullnode = -1
    STEP(1, "Prepare bunch of addresses that has PRV - same shard")

    STEP(2, 'Send 100 nano PRV to each others at the same time')
    everyone_send_prv_simultaneously(fullnode)
    wait_threads_to_complete()

    # subscribe the last transaction to make sure all transactions are handled
    transactions_save_fullnode[data_length - 1].subscribe_transaction()

    STEP(3, 'Get transaction by hash of each tx_id => check that them all in same block-height (or block-height + 1)')
    block_height = transactions_save_fullnode[0].get_transaction_by_hash().get_block_height()
    INFO(f'Expect all transactions must has same block height as {block_height} or {block_height + 1}')
    for index in range(0, data_length):
        transaction = transactions_save_fullnode[index]
        tx_block_height = transaction.get_transaction_by_hash().get_block_height()
        assert (block_height == tx_block_height or block_height + 1 == tx_block_height) \
               and INFO(f'{index}: tx = {transaction.get_tx_id()}, block height = {tx_block_height}')

    STEP(4, 'Verify that block contains at least 10 tx')
    tx_in_block_count = 0
    tx_hashes = SUT.full_node.system_rpc().retrieve_block_by_height(block_height, shard).get_tx_hashes()
    for transaction in transactions_save_fullnode:
        if transaction.get_tx_id() in tx_hashes:
            tx_in_block_count += 1
    assert tx_in_block_count >= 10 and INFO(f'Total tx in block {block_height} = {tx_in_block_count}')


def test_max_tx_in_same_block_with_some_fail():
    shard_thread = list()

    for i in random_i:
        accounts_send[i].get_prv_balance()

    STEP(1, "Prepare bunch of addresses that has PRV - same shard")

    STEP(3, 'Pick 2 pair of address, send 200 nano PRV to each other (send to shard)')
    for i in random_i:
        thread = Thread(target=sending_prv_thread, args=(
            accounts_send[i], accounts_receive[i], accounts_send[i].get_prv_balance_cache() - custom_fee, shard,
            custom_fee, transactions_save_shard,))
        thread.start()
        shard_thread.append(thread)
    for thread in shard_thread:
        thread.join()

    STEP(2, 'Send 100 nano PRV to each others at the same time, send request to shard, not full node')
    fullnode = -1
    everyone_send_prv_simultaneously(fullnode)
    wait_threads_to_complete()

    STEP(4, 'Wait 2 transactions above to complete')

    transactions_save_shard[1].subscribe_transaction()

    STEP(5, f'Wait {data_length} transactions at step 2 to complete')
    wait_threads_to_complete()
    # transactions_save_fullnode[i_to_check_latest].subscribe_transaction()

    STEP(6, 'Check mem pool, there are 2 transaction of step 2 got stuck')
    mem_pool_transaction = SUT.full_node.system_rpc().get_mem_pool().get_mem_pool_transactions_id_list()
    stuck_tx_count = 0
    for tx_id in mem_pool_transaction:
        INFO(f' ____ tx in mem pool {tx_id}')
        for transaction in transactions_save_fullnode:
            INFO(f' ___ tx in trans {transaction.get_tx_id()}')
            if tx_id == transaction.get_tx_id():
                stuck_tx_count += 1
                INFO(f'MATCH! BREAK')
                break

    assert stuck_tx_count == 2

    STEP(7.1,
         "Check all transactions sent to full node and shard, if they fall into the same block, except 2 fail ones")

    transactions_to_search = transactions_save_fullnode + transactions_save_shard
    block_height = transactions_save_fullnode[i_to_check_soonest].get_transaction_by_hash().get_block_height()

    fail_tx_count = 0
    for transaction in transactions_to_search:
        if transaction.get_error_msg() is not None:
            tx_block_height = transaction.get_transaction_by_hash().get_block_height()
            assert (tx_block_height == block_height or tx_block_height == block_height + 1) \
                   and INFO(f'{transaction.get_tx_id()} : {tx_block_height}')
        else:
            fail_tx_count += 1
    assert fail_tx_count == 2

    STEP(7.2, "Verify block tx hashes > 10")
    count_tx_in_block = 0
    tx_hashes_in_block = SUT.full_node.system_rpc().retrieve_block_by_height(block_height, shard).get_tx_hashes()
    for tx in transactions_to_search:
        if tx.get_tx_id() in tx_hashes_in_block:
            count_tx_in_block += 1
    assert count_tx_in_block > 10


def sending_prv_thread(sender: Account, receiver: Account, amount, shard_id, fee, transaction_save):
    tx = sender.send_prv_to(receiver, amount, shard_id=shard_id, fee=fee)
    transaction_save.append(tx)


def everyone_send_prv_simultaneously(shard_id):
    INFO(f"Creating {data_length} transactions ")
    for index in range(0, data_length):
        thread = Thread(target=sending_prv_thread,
                        args=(
                            accounts_send[index], accounts_receive[index], 222, shard_id, -1,
                            transactions_save_fullnode,))
        thread.start()
        all_thread_list.append(thread)


def wait_threads_to_complete():
    # wait for all sending thread to complete
    for thread in all_thread_list:
        thread.join()
