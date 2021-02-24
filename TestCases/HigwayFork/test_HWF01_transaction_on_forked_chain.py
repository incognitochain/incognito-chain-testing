import pytest
from concurrent.futures.thread import ThreadPoolExecutor

from Configs.Constants import coin, ChainConfig
from Helpers.Logging import INFO, STEP, ERROR, DEBUG
from Helpers.Time import WAIT
from Objects.AccountObject import COIN_MASTER, Account, AccountGroup
from Objects.IncognitoTestCase import SUT
from TestCases.HigwayFork import acc_list_1_shard, get_block_height, calculated_and_create_fork

receiver_same_shard = acc_list_1_shard[0]
receiver_cross_shard = Account(
    '112t8rnakdKxvk7VMKUB9qmsPY4czwnP24b82BnepcxHLX6kJ1dYQsR8d6xNTzwC9nEhJdocr9u19NAr4iSYXCeTBRu3YET8iADMAP3szdfw')
sender_list = acc_list_1_shard[1:7]
COIN_MASTER.top_him_up_prv_to_amount_if(coin(2), coin(5), sender_list)
amount = 10000
min_blocks_wait_fork = 6  # Chain will be forked after at least {min_blocks_wait_fork} blocks
time_send_tx = 3  # create & send transaction before and after {time_send_tx} blocks


@pytest.mark.parametrize('cID1, num_of_branch1, cID2, num_of_branch2, at_transfer_next_epoch', [
    (0, 2, None, None, True),
    (0, 2, None, None, False),
    (255, 2, None, None, True),
    (255, 2, None, None, False),
    (1, 2, 255, 2, True),
    (1, 2, 255, 2, False),
    (1, 2, 0, 2, True),
    (1, 2, 0, 2, False),
])
def test_transaction_on_forked_chain(cID1, num_of_branch1, cID2, num_of_branch2, at_transfer_next_epoch):
    STEP(0, "Balance before")
    bal_b4_sender_dict = {}
    bal_b4_receiver = {}
    amount_receiver = {}
    fee_dict = {}
    for sender in sender_list:
        bal_b4_sender_dict[sender] = sender.get_prv_balance()
        fee_dict[sender] = []
    for receiver in [receiver_cross_shard, receiver_same_shard]:
        bal_b4_receiver[receiver] = receiver.get_prv_balance()
        amount_receiver[receiver] = 0

    STEP(1, f'Create fork on chain_id {cID1} & chain_id {cID2}')
    with ThreadPoolExecutor() as executor:
        if cID1 is not None:
            thread = executor.submit(calculated_and_create_fork, cID1, at_transfer_next_epoch=at_transfer_next_epoch,
                                     min_blocks_wait_fork=min_blocks_wait_fork, num_of_branch=num_of_branch1)
        if cID2 is not None:
            executor.submit(calculated_and_create_fork, cID2, at_transfer_next_epoch=at_transfer_next_epoch,
                            min_blocks_wait_fork=min_blocks_wait_fork, num_of_branch=num_of_branch2)
    height_current, block_fork_list, real_blocks_wait = thread.result()

    WAIT((real_blocks_wait - time_send_tx) * ChainConfig.BLOCK_TIME)

    STEP(2, "Create and send transaction")
    thread_pool = []
    thread_pool_view = []
    round_height = {}
    for height in range(height_current, block_fork_list[-1] + time_send_tx + 2):
        round_height[height] = 0
    while height_current < block_fork_list[-1] + time_send_tx:
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
            for sender in sender_list[0:3]:
                thread_send_prv = executor.submit(sender.send_prv_to, receiver_same_shard, amount, privacy=0)
                thread_pool.append(thread_send_prv)
            for sender in sender_list[3:6]:
                thread_send_prv = executor.submit(sender.send_prv_to, receiver_cross_shard, amount, privacy=0)
                thread_pool.append(thread_send_prv)
        height_current = thread_height.result()
        INFO(f'Block_height: {height_current}')
        round_height[height_current] += 1
        assert round_height[height_current] <= num_of_branch1 * 2 + 2, ERROR(f'Chain is stopped at {height_current}')
        WAIT(ChainConfig.BLOCK_TIME)

    WAIT(10 * ChainConfig.BLOCK_TIME)  # wait 10 blocks to balance update

    STEP(3, 'Get all view detail')
    for thread in thread_pool_view:
        result = thread.result()
        INFO(result.num_of_hash_follow_height())
    for thread in thread_pool:
        result = thread.result()
        try:
            tx = result.subscribe_transaction()
            height = tx.get_block_height()
            shard = tx.get_shard_id()
            INFO(f'Shard {shard}-height {height}')
            key = tx.get_input_coin_pub_key()
            sender = AccountGroup(*sender_list).find_account_by_key(key)
            fee_dict[sender].append(tx.get_fee())
            output_coin = tx.get_prv_proof_detail().get_output_coins()
            for coin in output_coin:
                if coin.get_value() == amount:
                    public_key = coin.get_public_key()
                    receiver = AccountGroup(*(receiver_same_shard, receiver_cross_shard)).find_account_by_key(
                        public_key)
                    amount_receiver[receiver] += amount
                    break
        except AssertionError:
            ERROR(result.get_error_msg())
            DEBUG(result)

    STEP(4, 'Verify balance')
    for sender in sender_list:
        assert sender.get_prv_balance() == bal_b4_sender_dict[sender] - sum(fee_dict[sender]) - amount * len(
            fee_dict[sender])
    for receiver in [receiver_cross_shard, receiver_same_shard]:
        assert receiver.get_prv_balance() == bal_b4_receiver[receiver] + amount_receiver[receiver]
