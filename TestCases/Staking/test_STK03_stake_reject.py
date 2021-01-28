import re

import pytest

from Configs import Constants
from Configs.Constants import coin
from Helpers.Logging import STEP, INFO
from Helpers.Time import WAIT
from Objects.AccountObject import COIN_MASTER
from Objects.IncognitoTestCase import SUT
from TestCases.Staking import stake_account, amount_stake_under_1750, \
    amount_stake_over_1750, staked_account, account_t


def setup_function():
    if staked_account.get_prv_balance() < coin(1750):
        COIN_MASTER.send_prv_to(staked_account, coin(1850) - staked_account.get_prv_balance_cache(),
                                privacy=0).subscribe_transaction()
        if staked_account.shard != COIN_MASTER.shard:
            staked_account.subscribe_cross_output_coin()


@pytest.mark.parametrize('amount_prv_stake', [
    amount_stake_under_1750,
    amount_stake_over_1750
])
def test_stake_under_over_1750_prv(amount_prv_stake):
    STEP(0, 'Get balance account before staking')
    balance_before_stake = staked_account.get_prv_balance()

    STEP(1, f"Send {amount_prv_stake} PRV to stake")
    stake_response = staked_account.stake_and_reward_me(amount_prv_stake, auto_re_stake=False)

    STEP(2, "Verify that the transaction was rejected and PRV was not sent")
    assert stake_response.get_error_msg() == 'Can not send tx', "something went wrong, this tx must failed"
    assert re.search(r'Reject not sansity tx transaction',
                     stake_response.get_error_trace().get_message()), "something went so wrong"
    assert balance_before_stake == staked_account.get_prv_balance()


@pytest.mark.parametrize('test_case, validator', [
    ('double', staked_account),  # double stake
    ('others', staked_account),  # other account stake for my validator
    ('others', account_t),  # 2 other accounts with same stake for acc_t
])
def test_stake_same_validator(test_case, validator):
    if test_case == 'double':
        staker_2 = staked_account
    else:
        staker_2 = stake_account
    if staked_account.get_prv_balance() < coin(3600):
        COIN_MASTER.send_prv_to(staked_account, coin(3700) - staked_account.get_prv_balance_cache(),
                                privacy=0).subscribe_transaction()

    STEP(1, 'Get epoch number')
    beacon_state = SUT().get_beacon_best_state_info()
    beacon_height = beacon_state.get_beacon_height()
    epoch_number = beacon_state.get_epoch()
    while beacon_height % Constants.ChainConfig.BLOCK_PER_EPOCH >= (Constants.ChainConfig.BLOCK_PER_EPOCH / 2) - 1:
        # -1 just to be sure that staking will be successful
        INFO(f'block height % block per epoch = {beacon_height % Constants.ChainConfig.BLOCK_PER_EPOCH}')
        WAIT((Constants.ChainConfig.BLOCK_PER_EPOCH - (beacon_height % Constants.ChainConfig.BLOCK_PER_EPOCH)) * 10)
        beacon_state = SUT().get_beacon_best_state_info()
        beacon_height = beacon_state.get_beacon_height()
        epoch_number = beacon_state.get_epoch()
    INFO(f'Ready to stake at epoch: {epoch_number}, beacon height: {beacon_height}')

    STEP(2, 'Stake the first time and check balance after staking')
    balance_before_stake_first = staked_account.get_prv_balance()
    stake_response = staked_account.stake(validator=validator, auto_re_stake=False)
    stake_response.subscribe_transaction()
    stake_fee = stake_response.get_transaction_by_hash().get_fee()
    WAIT(40)
    assert balance_before_stake_first == staked_account.get_prv_balance() + stake_fee + coin(1750)

    STEP(3, f'Wait until epoch {epoch_number} + n and Check if the stake become a committee')
    epoch_plus_n = validator.stk_wait_till_i_am_committee()
    beacon_bsd = SUT().get_beacon_best_state_detail_info()
    staked_shard = beacon_bsd.is_he_a_committee(validator)
    assert staked_shard is not False

    STEP(4, 'Stake the second time')
    balance_before_stake_second = staker_2.get_prv_balance()
    stake_response = staker_2.stake(validator=validator, auto_re_stake=False)
    print("stake_response = %s" % stake_response)

    STEP(5, 'Verify that the transaction was rejected and PRV was not sent')
    assert stake_response.get_error_msg() == 'Can not send tx', "something went wrong, this tx must failed"
    assert re.search(r'Double Spend With Current Blockchain',
                     stake_response.get_error_trace().get_message()), "something went so wrong"
    assert balance_before_stake_second == staker_2.get_prv_balance()

    STEP(6, "Wait for the stake to be swapped out")
    epoch_x = validator.stk_wait_till_i_am_swapped_out_of_committee()

    STEP(7, "Calculate avg PRV reward per epoch")
    prv_reward = staked_account.stk_get_reward_amount()
    avg_prv_reward = prv_reward / (epoch_x - epoch_plus_n)
    INFO(f'AVG prv reward = {avg_prv_reward}')

    STEP(8, 'Wait for staking refund and verify staking refund')
    bal_after_stake_refund = staked_account.wait_for_balance_change()
    assert balance_before_stake_first - stake_fee == bal_after_stake_refund

    STEP(9, 'Withdraw PRV reward and verify balance')
    prv_bal_withdraw_reward = staked_account.get_prv_balance()
    prv_reward_amount = staked_account.stk_get_reward_amount()
    withdraw_fee = staked_account.stk_withdraw_reward_to_me().subscribe_transaction().get_fee()
    prv_bal_after_withdraw_reward = staked_account.wait_for_balance_change(from_balance=prv_bal_withdraw_reward,
                                                                          timeout=180)
    INFO(f'Expect reward amount to received: {prv_reward_amount}')
    assert prv_bal_b4_withdraw + prv_reward_amount - withdraw_fee == prv_bal_after_withdraw, \
        f'bal b4={prv_bal_b4_withdraw}, reward amount={prv_reward_amount}, withdraw fee={withdraw_fee} ' \
        f'bal after={prv_bal_after_withdraw}'
