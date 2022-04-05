import concurrent
from concurrent.futures.thread import ThreadPoolExecutor

from Configs.Configs import ChainConfig
from Helpers.Logging import INFO
from Helpers.TestHelper import ChainHelper, l6
from Helpers.Time import WAIT
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import SUT
from TestCases.Staking import account_y, account_a, account_u, account_t


def get_epoch_swap_in_out_and_reward_committee(account_stake):
    """

    @param account_stake: Account
    @return:
    """
    INFO()
    reward = 0
    epoch_in = account_stake.stk_wait_till_i_am_committee(timeout=ChainConfig.get_epoch_n_block_time(100))
    bbd_b4 = SUT().get_beacon_best_state_detail_info()
    shard_id = bbd_b4.is_he_a_committee(account_stake)
    assert shard_id is not False
    epoch_out = account_stake.stk_wait_till_i_am_out_of_autostaking_list(
        timeout=ChainConfig.get_epoch_n_block_time(100))
    for epoch in range(epoch_in, epoch_out):
        instruction_beacon_height = ChainHelper.cal_first_height_of_epoch(epoch=epoch + 1)
        instruction_bb = SUT().get_latest_beacon_block(instruction_beacon_height)
        bb_reward_instruction_prv = instruction_bb.get_transaction_reward_from_instruction(bpv3=True)
        committees_state = SUT().get_committee_state(instruction_beacon_height - 1)
        committees = committees_state.get_shard_committee_list(shard_id)
        shard_committee_size = committees_state.get_shard_committee_size(shard_id)
        subset_id = committees.index(account_stake.committee_public_k) % 2
        if subset_id == 0:
            subset_size = int(shard_committee_size / 2) + shard_committee_size % 2
        else:
            subset_size = int(shard_committee_size / 2)
        print(
            f"Beacon_height: {instruction_beacon_height}, Shard {shard_id}, shard_committee_size: {subset_size}")
        try:
            reward += int(bb_reward_instruction_prv[str(shard_id)][str(subset_id)] / subset_size)
        except KeyError:
            reward += 0
    INFO(
        f'{l6(account_stake.validator_key)} is in committee shard {shard_id} from epoch {epoch_in} to {epoch_out}, Reward: {reward}')
    return epoch_in, epoch_out, reward, shard_id


def test_stake_for_multi_validator():
    INFO()
    COIN_MASTER.top_up_if_lower_than(account_y, ChainConfig.STK_AMOUNT * 4, ChainConfig.STK_AMOUNT * 5)
    from TestCases.Staking import token_id
    INFO(f'Run test with token: {token_id}')
    reward_b4 = {}
    for acc in [account_y, account_a, account_u, account_t]:
        reward_b4[acc] = acc.stk_get_reward_amount()

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
    bal_b4_stake = {}
    for acc in [account_y, account_a, account_u, account_t]:
        bal_b4_stake[acc] = acc.get_balance()

    INFO(f'Stake for validator 1')
    fee_tx1 = account_y.stake(account_y, auto_re_stake=False).subscribe_transaction().get_fee()
    INFO(f'Stake for validator 2')
    fee_tx2 = account_y.stake(account_a, auto_re_stake=False).subscribe_transaction().get_fee()
    INFO(f'Stake for validator 3')
    fee_tx3 = account_y.stake(account_u, auto_re_stake=False).subscribe_transaction().get_fee()
    INFO(f'Stake for validator 4')
    fee_tx4 = account_y.stake(account_t, auto_re_stake=False).subscribe_transaction().get_fee()
    stake_sum_fee_tx = fee_tx1 + fee_tx2 + fee_tx3 + fee_tx4
    WAIT(40)
    INFO('Verify balance after staking')
    bal_af_stake = {}
    for acc in [account_y, account_a, account_u, account_t]:
        bal_af_stake[acc] = acc.get_balance()
    assert bal_af_stake[account_y] == bal_b4_stake[account_y] - stake_sum_fee_tx - ChainConfig.STK_AMOUNT * 4
    for acc in [account_a, account_u, account_t]:
        assert bal_b4_stake[acc] == bal_af_stake[acc], executor.shutdown()

    concurrent.futures.wait(thread_pool)
    executor.shutdown()
    instruction_reward = 0
    for thread in thread_pool:
        epoch_in, epoch_out, reward, shard_committee = thread.result()
        instruction_reward += reward
    print(f'Instruction_reward = {instruction_reward}')
    WAIT(ChainConfig.get_epoch_n_block_time(num_of_epoch=0, number_of_block=5))  # Wait receive reward
    INFO(f'Verify balance after refund')
    for acc in [account_a, account_u, account_t]:
        assert reward_b4[acc] == acc.stk_get_reward_amount()
    assert account_y.get_balance() == bal_af_stake[account_y] + ChainConfig.STK_AMOUNT * 4
    assert account_y.stk_get_reward_amount() - reward_b4[account_y] == instruction_reward
