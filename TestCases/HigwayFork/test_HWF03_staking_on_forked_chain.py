from concurrent.futures.thread import ThreadPoolExecutor

import pytest

from Configs.Constants import coin
from Configs.Configs import ChainConfig
from Helpers.KeyListJson import KeyListJson
from Helpers.Logging import INFO, STEP, ERROR
from Helpers.Time import WAIT
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import SUT
from TestCases.HigwayFork import acc_list_1_shard, get_block_height, calculated_and_create_fork

key_list_file = KeyListJson()
stakers = key_list_file.get_staker_accounts()
try:
    account_x = stakers[4]
    account_y = stakers[5]
except IndexError:
    raise EnvironmentError(f'Not enough staker in keylist file for the test. '
                           f'Check the file, and make sure nodes are run or else chain will be stuck')
account_a = acc_list_1_shard[0]
COIN_MASTER.top_up_if_lower_than([account_a, account_x], coin(1750), coin(1850))
min_blocks_wait_fork = 6  # Chain will be forked after at least {min_blocks_wait_fork} blocks
time_send_tx = 3  # create & send transaction before and after {time_send_tx} blocks
num_of_block_fork = 5


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
    balance_before = {}
    balance_after_stk = {}
    for acc in [account_a, account_x, account_y]:
        balance_before[acc] = acc.get_balance()

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

    STEP(2, "Staking")
    thread_dict = {}
    thread_pool_view = []
    thread_errors_pool = []
    thread_unstake_dict = {}
    round_height = {}
    for height in range(height_current, block_fork_list[-1] + time_send_tx + 2):
        round_height[height] = 0
    i = 0
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
            # if i != 0:
            #     thread1 = executor.submit(account_x.stake)
            #     thread_errors_pool.append(thread1)
            #     thread2 = executor.submit(account_a.stake, account_y)
            #     thread_errors_pool.append(thread2)
            if height_current == block_fork_list[round(num_of_block_fork / 2)] and i == 0:
                thread_stake1 = executor.submit(account_x.stake)
                thread_dict[account_x] = thread_stake1
                thread_stake2 = executor.submit(account_a.stake, account_y)
                thread_dict[account_a] = thread_stake2
                i += 1
            if height_current == block_fork_list[round(num_of_block_fork / 2) + 2] and i == 1:
                thread_unstake1 = executor.submit(account_x.stk_stop_auto_stake_me)
                thread_unstake_dict[account_x] = thread_unstake1
                thread_unstake2 = executor.submit(account_a.stk_stop_auto_stake_him, account_y)
                thread_unstake_dict[account_a] = thread_unstake2
                for acc in [account_a, account_x, account_y]:
                    thread = executor.submit(acc.get_balance)
                    balance_after_stk[acc] = thread
                i += 1
        height_current = thread_height.result()
        INFO(f'Block_height: {height_current}')
        round_height[height_current] += 1
        assert round_height[height_current] <= num_of_branch1 * 2 + 2, ERROR(f'Chain is stopped at {height_current}')
        WAIT(ChainConfig.BLOCK_TIME)

    INFO('Get beacon best state detail')
    bbd = SUT().get_beacon_best_state_detail_info()

    WAIT(10 * ChainConfig.BLOCK_TIME)  # wait 10 blocks to balance update
    STEP(3, 'Get all view detail')
    for thread in thread_pool_view:
        result = thread.result()
        INFO(result.num_of_hash_follow_height())

    STEP(4, 'Verify staking')
    for acc, thread in thread_dict.items():
        result = thread.result()
        tx = result.expect_no_error().get_transaction_by_hash()
        fee = tx.get_fee()
        height = tx.get_block_height()
        shard = tx.get_shard_id()
        INFO(f'Staking at Shard{shard}_height: {height}')
        assert balance_after_stk[acc].result() == balance_before[acc] - ChainConfig.STK_AMOUNT - fee
        assert balance_after_stk[account_y].result() == balance_before[account_y]

    for thread in thread_errors_pool:
        thread.result().expect_error()

    STEP(5, 'Verify stop auto staking')
    for acc, thread in thread_unstake_dict.items():
        result = thread.result()
        tx = result.expect_no_error().get_transaction_by_hash()
        fee = tx.get_fee()
        height = tx.get_block_height()
        shard = tx.get_shard_id()
        INFO(f'Unstake at Shard{shard}_height: {height}')
        assert balance_after_stk[acc].result() + ChainConfig.STK_AMOUNT - fee == acc.get_balance()
        assert balance_after_stk[account_y].result() == balance_before[account_y]

    for acc in [account_x, account_y]:
        assert bbd.get_auto_staking_committees(acc) is False

    account_x.stk_wait_till_i_am_out_of_autostaking_list(ChainConfig.BLOCK_TIME)
    account_y.stk_wait_till_i_am_out_of_autostaking_list(ChainConfig.BLOCK_TIME)
