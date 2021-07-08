import math
from concurrent.futures.thread import ThreadPoolExecutor

from Drivers.Response import Response
from Helpers.Logging import *
from Objects.AccountObject import get_accounts_in_shard
from Objects.IncognitoTestCase import SUT
from TestCases.Performace import account_list

dict_tx_save_fullnode = dict()
dict_tx_save_shard = dict()
# sender_account_payment_address_list = []
sender_account_list = get_accounts_in_shard(0, account_list)
receiver_account = get_accounts_in_shard(1, account_list)[0]


def setup_function():
    INFO('TEST SETUP:\nget balance all accounts:')
    dict_tx_save_fullnode.clear()
    dict_tx_save_shard.clear()
    for account in sender_account_list:
        account.get_balance()
    receiver_account.get_balance()


def teardown_function():
    INFO('TEST CLEANUP:\nsend PRV back')
    amount_to_send_back = math.floor((receiver_account.get_balance() - 100) / 20)
    sender_account_dict = {}
    if amount_to_send_back == 0:
        return
    for account in sender_account_list:
        sender_account_dict[account] = amount_to_send_back
    receiver_account.send_prv_to_multi_account(sender_account_dict, -1, 0)


def test_max_tx_in_same_block_with_some_fail():
    STEP(1, "Prepare bunch of addresses that has PRV - same shard")
    STEP(2, 'Pick 20 address, send 3/4 PRV to shard, and 1/2 to fullnode')
    with ThreadPoolExecutor() as executor:
        for sender_account in sender_account_list:
            send_amount = math.floor(sender_account.get_balance(cache=1) * 3 / 5)

            thread = executor.submit(sender_account.send_prv_to, receiver_account, send_amount, shard_handle=1)
            dict_tx_save_shard[sender_account] = thread

            thread = executor.submit(sender_account.send_prv_to, receiver_account, send_amount, )
            dict_tx_save_fullnode[sender_account] = thread

    STEP(3, 'find stuck and success transactions')
    INFO(f'transactions_save_shard: ')
    i = 0
    for account, thread in dict_tx_save_shard.items():
        tx = thread.result()
        tx_id = tx.get_tx_id()
        INFO(f' s{i} sender {account.private_key} - {tx_id}')
        i += 1

    INFO(f'transactions_save_fullnode: ')
    i = 0
    for account, thread in dict_tx_save_fullnode.items():
        tx = thread.result()
        INFO(f' f{i} sender {account.private_key} - {tx.get_tx_id()}')
        i += 1

    INFO(f'subscribe all success tx')
    count_tx_none_shard = 0
    count_tx_none_fullnode = 0
    try:  # wait all transaction to be sent
        INFO('no need to subscribe fullnode tx')
        for account, thread in dict_tx_save_fullnode.items():
            tx: Response = thread.result()
            if tx.get_tx_id() is None:
                count_tx_none_fullnode += 1
                continue

        INFO('subscribe shard tx')
        one_subscription_pass_already = False
        for account, thread in dict_tx_save_shard.items():
            tx: Response = thread.result()
            if tx.get_tx_id() is None:
                count_tx_none_shard += 1
                continue
            if not one_subscription_pass_already:
                try:
                    tx.subscribe_transaction()
                    one_subscription_pass_already = True
                except Exception as e:
                    ERROR(e)

        receiver_account.subscribe_cross_output_coin()
    except Exception as e:
        ERROR(e)

    STEP(4, 'Check mem pool, count fail tx in full node and shard')
    transactions_in_mem_pool = SUT().get_mem_pool_txs()
    stuck_tx_count_fullnode = 0
    stuck_tx_count_shard = 0
    if transactions_in_mem_pool is None:
        INFO("NO tx is stuck in mem pool")
    else:
        for tx_id in transactions_in_mem_pool:
            INFO(f' ____ tx in mem pool {tx_id}')
            for account, thread in dict_tx_save_fullnode.items():
                # INFO(f' ___ tx in trans {transaction.get_tx_id()}')
                transaction = thread.result()
                if transaction.get_error_msg() is not None:
                    continue
                if tx_id == transaction.get_tx_id():
                    stuck_tx_count_fullnode += 1
                    INFO(f'tx found in mem pool {transaction.get_tx_id()}')
                    break
            for account, thread in dict_tx_save_shard.items():
                # INFO(f' ___ tx in trans {transaction.get_tx_id()}')
                transaction = thread.result()
                if transaction.get_error_msg() is not None:
                    continue
                if tx_id == transaction.get_tx_id():
                    stuck_tx_count_shard += 1
                    INFO(f'tx found in mem pool {transaction.get_tx_id()}')
                    break

    STEP(5.1,
         "Check all transactions sent to full node and shard, if they fall into the same block, except 2 fail ones")
    block_height_0 = -1
    count_block_height_0_shard = 0
    count_block_height_0_fullnode = 0
    for account, thread in dict_tx_save_fullnode.items():
        transaction: Response = thread.result()
        if transaction.get_error_msg() is not None:
            continue
        try:
            tx_block_height = transaction.get_transaction_by_hash().get_block_height()
        except Exception:
            continue
        if tx_block_height == 0:
            count_block_height_0_fullnode += 1
            continue
        if block_height_0 == -1:
            block_height_0 = tx_block_height
            INFO(f'f:{transaction.get_tx_id()} : {tx_block_height}')
        else:
            # assert (0 <= tx_block_height - block_height_0 <= 1) and \
            INFO(f'f:{transaction.get_tx_id()} : {tx_block_height}')

    for account, thread in dict_tx_save_shard.items():
        transaction: Response = thread.result()
        if transaction.get_error_msg() is not None:
            continue
        try:
            tx_block_height = transaction.get_transaction_by_hash().get_block_height()
        except Exception:
            continue
        if tx_block_height == 0:
            count_block_height_0_shard += 1
            continue
        if block_height_0 == -1:
            block_height_0 = tx_block_height
            INFO(f's:{transaction.get_tx_id()} : {tx_block_height}')
        else:
            assert (0 <= tx_block_height - block_height_0 <= 1) and \
                   INFO(f's:{transaction.get_tx_id()} : {tx_block_height}')

    STEP(5.2, "Verify block tx hashes > 10")
    count_tx_in_block = 0
    INFO(f'block {block_height_0}')
    tx_hashes_in_block = SUT().get_shard_block_by_height(0, block_height_0).get_tx_hashes()
    output = "\n\t\t".join(tx_hashes_in_block)
    INFO(f'hashes:\n\t{output}')
    for account, thread in dict_tx_save_fullnode.items():
        tx = thread.result()
        if tx.get_error_msg() is not None:
            continue
        if tx.get_tx_id() in tx_hashes_in_block:
            count_tx_in_block += 1
    for account, thread in dict_tx_save_shard.items():
        tx = thread.result()
        if tx.get_error_msg() is not None:
            continue
        if tx.get_tx_id() in tx_hashes_in_block:
            count_tx_in_block += 1
    assert count_tx_in_block > 10 and INFO(f" sum tx in block {block_height_0} = {count_tx_in_block}")

    # Todo later, too hard for now :))     STEP(6, "Check balance after transaction success")

    INFO_HEADLINE('SUMMARY:')
    INFO(f'Tx in shard which fail to create (txId = None): {count_tx_none_shard}')
    INFO(f'Tx in full node which fail to create (txId = None): {count_tx_none_fullnode}')

    INFO(f'tx fail in shard: {stuck_tx_count_shard}: ')
    INFO(f'tx fail in fullnode: {stuck_tx_count_fullnode}')
    # assert stuck_tx_count_shard == 0
    # assert stuck_tx_count_fullnode == len(dict_tx_save_fullnode)

    INFO(f'number of shard tx which has block height=0: {count_block_height_0_shard}')
    INFO(f'number of fullnode tx which has block height=0: {count_block_height_0_fullnode}')
    # assert count_block_height_0_shard == 0
    # assert count_block_height_0_fullnode == len(dict_tx_save_fullnode)
