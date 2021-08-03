from concurrent.futures.thread import ThreadPoolExecutor

import pytest

from Configs.Constants import coin
from Configs.Configs import ChainConfig
from Helpers.Logging import INFO, STEP, ERROR
from Helpers.Time import WAIT
from Objects.AccountObject import COIN_MASTER, Account
from Objects.IncognitoTestCase import SUT
from TestCases.HigwayFork import acc_list_1_shard, get_block_height, calculated_and_create_fork

receiver_shard_0 = Account(
    '112t8rnakdKxvk7VMKUB9qmsPY4czwnP24b82BnepcxHLX6kJ1dYQsR8d6xNTzwC9nEhJdocr9u19NAr4iSYXCeTBRu3YET8iADMAP3szdfw')
receiver_shard_1 = acc_list_1_shard[0]
senders_from_1_to_0 = acc_list_1_shard[1:4]
senders_from_1_to_1 = acc_list_1_shard[4:7]
COIN_MASTER.top_up_if_lower_than(senders_from_1_to_1 + senders_from_1_to_0, coin(2), coin(5))
amount = 10000
min_blocks_wait_fork = 6  # Chain will be forked after at least {min_blocks_wait_fork} blocks
time_send_tx = 3  # create & send transaction before and after {time_send_tx} blocks


@pytest.mark.parametrize('cID1, num_of_branch1, cID2, num_of_branch2, at_transfer_next_epoch, num_of_block_fork', [
    (1, 2, 0, 2, True, 5),
    (1, 2, 0, 2, False, 5),
    (1, 2, 255, 2, True, 5),
    (1, 2, 255, 2, False, 5),
    (1, 2, None, None, True, 5),
    (1, 2, None, None, False, 5),
    (255, 2, None, None, True, 5),
    (255, 2, None, None, False, 5),
    (1, 2, 255, 2, True, 30)
])
def test_transaction_on_forked_chain(cID1, num_of_branch1, cID2, num_of_branch2, at_transfer_next_epoch,
                                     num_of_block_fork):
    STEP(0, "Balance before")
    bal_b4_sender_dict = {}
    bal_b4_receiver = {}
    amount_receiver = {}
    fee_dict = {}
    for sender in senders_from_1_to_1 + senders_from_1_to_0:
        bal_b4_sender_dict[sender] = sender.get_balance()
        fee_dict[sender] = []
    for receiver in [receiver_shard_1, receiver_shard_0]:
        bal_b4_receiver[receiver] = receiver.get_balance()
        amount_receiver[receiver] = 0

    STEP(1, f'Create fork on chain_id {cID1} & chain_id {cID2}')
    with ThreadPoolExecutor() as executor:
        if cID1 is not None:
            thread = executor.submit(calculated_and_create_fork, cID1, at_transfer_next_epoch=at_transfer_next_epoch,
                                     min_blocks_wait_fork=min_blocks_wait_fork, num_of_branch=num_of_branch1,
                                     num_of_block_fork=num_of_block_fork)
        if cID2 is not None:
            executor.submit(calculated_and_create_fork, cID2, at_transfer_next_epoch=at_transfer_next_epoch,
                            min_blocks_wait_fork=min_blocks_wait_fork, num_of_branch=num_of_branch2,
                            num_of_block_fork=num_of_block_fork)
    height_current, block_fork_list, real_blocks_wait = thread.result()

    WAIT((real_blocks_wait - time_send_tx) * ChainConfig.BLOCK_TIME)
    # WAIT(3000)
    STEP(2, "Create and send transaction")
    thread_tx_cross_shard = []
    thread_tx_same_shard = []
    thread_pool_view = []
    round_height = {}
    for height in range(height_current, block_fork_list[-1] + time_send_tx + 20):
        round_height[height] = 0
    while height_current < block_fork_list[-1] + time_send_tx:
        list_thread_same = []
        list_thread_cross = []
        with ThreadPoolExecutor() as executor:
            thread_height = executor.submit(get_block_height, cID1)
            for cID in [cID1, cID2]:
                if cID == 255:
                    REQ_HANDLER = SUT.beacons.get_node()
                    thread_view_detail = executor.submit(REQ_HANDLER.get_all_view_detail, -1)
                    thread_pool_view.append(thread_view_detail)
                elif cID is not None:
                    REQ_HANDLER = SUT.shards[cID].get_node()
                    thread_view_detail = executor.submit(REQ_HANDLER.get_all_view_detail, cID)
                    thread_pool_view.append(thread_view_detail)
            for sender in senders_from_1_to_1:
                thread_send_prv = executor.submit(sender.send_prv_to, receiver_shard_1, amount, privacy=0)
                list_thread_same.append(thread_send_prv)
            for sender in senders_from_1_to_0:
                thread_send_prv = executor.submit(sender.send_prv_to, receiver_shard_0, amount, privacy=0)
                list_thread_cross.append(thread_send_prv)
        thread_tx_cross_shard.append(list_thread_cross)
        thread_tx_same_shard.append(list_thread_same)
        height_current = thread_height.result()
        INFO(f'Block_height: {height_current}')
        round_height[height_current] += 1
        assert round_height[height_current] <= num_of_branch1 * 2 + 2, ERROR(f'Chain is stopped at {height_current}')
        if height_current in block_fork_list + [block_fork_list[0] - 1]:
            WAIT(ChainConfig.BLOCK_TIME * 4)
        else:
            WAIT(ChainConfig.BLOCK_TIME * 2)
        # WAIT(ChainConfig.BLOCK_TIME * 4)

    WAIT(10 * ChainConfig.BLOCK_TIME)  # wait 10 blocks to balance update

    STEP(3, 'Get all view detail')
    for i in range(len(thread_pool_view)):
        result = thread_pool_view[i].result()
        if cID2 is not None:
            if i % 2 == 0:
                INFO(f'Chain ID {cID1}: {result.num_of_hash_follow_height()}')
            else:
                INFO(f'Chain ID {cID2}: {result.num_of_hash_follow_height()}')
        else:
            INFO(f'Chain ID {cID1}: {result.num_of_hash_follow_height()}')
    INFO('Transaction same shard')
    for list_thread in thread_tx_same_shard:
        for i in range(len(list_thread)):
            result = list_thread[i].result()
            if result.get_error_msg() is None:
                INFO(f'Get transaction tx_id = {result.get_tx_id()}')
                tx_detail = result.get_transaction_by_hash()
                if not tx_detail.is_none():
                    height = tx_detail.get_block_height()
                    shard = tx_detail.get_shard_id()
                    INFO(f'Shard {shard}-height {height}')
                    if height:
                        fee_dict[senders_from_1_to_1[i]].append(tx_detail.get_fee())
                else:
                    msg_error = SUT().transaction().get_tx_by_hash(result.get_tx_id()).get_error_msg()
                    ERROR(msg_error)
            else:
                ERROR(result.get_error_msg())
    INFO('Transaction cross shard')
    for list_thread in thread_tx_cross_shard:
        for i in range(len(list_thread)):
            result = list_thread[i].result()
            if result.get_error_msg() is None:
                INFO(f'Get transaction tx_id = {result.get_tx_id()}')
                tx_detail = result.get_transaction_by_hash()
                if not tx_detail.is_none():
                    height = tx_detail.get_block_height()
                    shard = tx_detail.get_shard_id()
                    INFO(f'Shard {shard}-height {height}')
                    if height:
                        fee_dict[senders_from_1_to_0[i]].append(tx_detail.get_fee())
                else:
                    msg_error = SUT().transaction().get_tx_by_hash(result.get_tx_id()).get_error_msg()
                    ERROR(msg_error)
            else:
                ERROR(result.get_error_msg())

    STEP(4, 'Verify balance')
    diff_send_same = []
    diff_send_cross = []
    amount_send_same = 0
    amount_send_cross = 0
    for sender in senders_from_1_to_1:
        amount_send_same += amount * len(fee_dict[sender])
        diff = sender.get_balance() - (
                bal_b4_sender_dict[sender] - sum(fee_dict[sender]) - amount * len(fee_dict[sender]))
        diff_send_same.append(diff)
    INFO(f'Different balance sender same shard: {diff_send_same}')
    for sender in senders_from_1_to_0:
        amount_send_cross += amount * len(fee_dict[sender])
        diff = sender.get_balance() - (
                bal_b4_sender_dict[sender] - sum(fee_dict[sender]) - amount * len(fee_dict[sender]))
        diff_send_cross.append(diff)
    INFO(f'Different balance sender cross shard: {diff_send_cross}')
    diff_receiver_same = receiver_shard_1.get_balance() - (
            bal_b4_receiver[receiver_shard_1] + amount_send_same)
    INFO(f'Different balance receiver same shard: {diff_receiver_same}')
    diff_receiver_cross = receiver_shard_0.get_balance() - (
            bal_b4_receiver[receiver_shard_0] + amount_send_cross)
    INFO(f'Different balance receiver cross shard: {diff_receiver_cross}')

    assert sum(diff_send_same) == - diff_receiver_same
    assert sum(diff_send_cross) == - diff_receiver_cross
