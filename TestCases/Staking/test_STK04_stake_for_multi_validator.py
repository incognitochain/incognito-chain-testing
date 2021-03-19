import concurrent
from concurrent.futures.thread import ThreadPoolExecutor

from Configs.Constants import ChainConfig
from Helpers.Logging import INFO
from Helpers.TestHelper import ChainHelper
from Helpers.Time import WAIT
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import SUT
from TestCases.Staking import account_y, account_a, account_u, account_t

index_epoch_change = 0
block_per_epoch_b4 = 20
block_per_epoch_af = ChainConfig.BLOCK_PER_EPOCH


def get_epoch_swap_in_out_and_reward_committee(account_stake):
    """

    @param account_stake: Account
    @return:
    """
    reward = 0
    epoch_in = account_stake.stk_wait_till_i_am_committee()
    bbd_b4 = SUT().get_beacon_best_state_detail_info()
    shard_id = bbd_b4.is_he_a_committee(account_stake)
    assert shard_id is not False
    epoch_out = account_stake.stk_wait_till_i_am_swapped_out_of_committee()
    for epoch in range(epoch_in, epoch_out):
        instruction_beacon_height = ChainHelper.cal_first_height_of_epoch(epoch=epoch + 1,
                                                                          index_epoch_change=index_epoch_change,
                                                                          block_per_epoch_b4=block_per_epoch_b4,
                                                                          block_per_epoch_af=block_per_epoch_af)
        # instruction_beacon_height = (5000 + (epoch - 1 - 499) * 20) + 1
        instruction_bb = SUT().get_latest_beacon_block(instruction_beacon_height)
        bb_reward_instruction_prv = instruction_bb.get_transaction_reward_from_instruction()
        shard_committee_size = SUT().get_committee_state(instruction_beacon_height).get_shard_committee_size(shard_id)
        reward += bb_reward_instruction_prv[str(shard_id)] / shard_committee_size
    return epoch_in, epoch_out, reward, shard_id


def test_stake_for_multi_validator():
    COIN_MASTER.top_him_up_prv_to_amount_if(ChainConfig.STK_AMOUNT * 4, ChainConfig.STK_AMOUNT * 5, account_y)
    from TestCases.Staking import token_id
    INFO(f'Run test with token: {token_id}')
    reward_b4 = account_y.stk_get_reward_amount()
    if reward_b4 != 0:
        account_y.stk_withdraw_reward_to_me().subscribe_transaction()
        WAIT(40)
        reward_b4 = account_y.stk_get_reward_amount()
    assert reward_b4 == 0

    thread_pool = []
    executor = ThreadPoolExecutor()
    thread_validator1 = executor.submit(get_epoch_swap_in_out_and_reward_committee, account_y)
    thread_pool.append(thread_validator1)
    thread_validator2 = executor.submit(get_epoch_swap_in_out_and_reward_committee, account_a)
    thread_pool.append(thread_validator2)
    thread_validator3 = executor.submit(get_epoch_swap_in_out_and_reward_committee, account_u)
    thread_pool.append(thread_validator3)
    thread_validator4 = executor.submit(get_epoch_swap_in_out_and_reward_committee, account_t)
    thread_pool.append(thread_validator4)

    INFO('STAKING AND VERIFY BALANCE')
    bal_b4_stake = account_y.get_prv_balance()
    INFO(f'Stake for validator 1')
    fee_tx1 = account_y.stake(account_y, auto_re_stake=False).subscribe_transaction().get_fee()
    INFO(f'Stake for validator 2')
    fee_tx2 = account_y.stake(account_a, auto_re_stake=False).subscribe_transaction().get_fee()
    INFO(f'Stake for validator 3')
    fee_tx3 = account_y.stake(account_u, auto_re_stake=False).subscribe_transaction().get_fee()
    INFO(f'Stake for validator 4')
    fee_tx4 = account_y.stake(account_t, auto_re_stake=False).subscribe_transaction().get_fee()
    stake_sum_fee_tx = fee_tx1 + fee_tx2 + fee_tx3 + fee_tx4
    bal_af_stake = account_y.get_prv_balance()
    assert bal_af_stake == bal_b4_stake - stake_sum_fee_tx - ChainConfig.STK_AMOUNT * 4

    concurrent.futures.wait(thread_pool)
    instruction_reward = 0
    for thread in thread_pool:
        epoch_in, epoch_out, reward, shard_committee = thread.result()
        instruction_reward += reward

    reward_receive = account_y.stk_get_reward_amount()
    assert reward_receive == instruction_reward
